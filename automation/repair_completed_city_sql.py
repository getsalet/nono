#!/usr/bin/env python3
"""Regenerate completed post SQL with the current idempotent safety policy."""
from __future__ import annotations

import json
from pathlib import Path

import city_content_queue as base
import city_content_queue_cloudflare as backend
import text_cleanup_policy


def main() -> int:
    if not base.QUEUE.exists():
        print("queue.json is missing; no legacy SQL to repair")
        return 0
    state = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    repaired = 0
    missing = []
    for item in state.get("items", []):
        if item.get("status") != "completed":
            continue
        sid = str(item.get("source_id"))
        artifact = base.ITEMS / f"{sid}.json"
        if not artifact.exists():
            missing.append(str(artifact.relative_to(base.OUT)))
            continue
        data = json.loads(artifact.read_text(encoding="utf-8"))
        cleaned = text_cleanup_policy.cleanup_html(data.get("html", ""), item)
        if cleaned != data.get("html", ""):
            data["html"] = cleaned
            artifact.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            repaired += 1
        images = data.get("images") or item.get("images") or []
        if not images:
            missing.append(f"items/{sid}.json:images")
            continue
        insert, rollback, _ = backend.sql_for(item, data, images)
        insert = insert.replace("'draft','closed','closed'", "'publish','closed','closed'", 1)
        sql_path = base.SQL / f"{sid}.sql"
        rollback_path = base.ROLLBACK / f"{sid}.sql"
        if not sql_path.exists() or sql_path.read_text(encoding="utf-8") != insert:
            sql_path.write_text(insert, encoding="utf-8")
            repaired += 1
        if not rollback_path.exists() or rollback_path.read_text(encoding="utf-8") != rollback:
            rollback_path.write_text(rollback, encoding="utf-8")
            repaired += 1
    if missing:
        raise RuntimeError("Completed items have missing artifacts: " + ", ".join(missing[:20]))
    completed_sql = [p.read_text(encoding="utf-8") for p in sorted(base.SQL.glob("*.sql"))]
    completed_rollback = [p.read_text(encoding="utf-8") for p in sorted(base.ROLLBACK.glob("*.sql"))]
    (base.OUT / "create-all-completed.sql").write_text(
        "\n".join(["-- Idempotent reviewed city posts.", base.sql_preamble(), *completed_sql]),
        encoding="utf-8",
    )
    (base.OUT / "rollback-all-completed.sql").write_text(
        "\n".join(["-- Marker-protected rollback.", base.sql_preamble(), *completed_rollback]),
        encoding="utf-8",
    )
    print(json.dumps({"repaired_files": repaired, "completed_posts": len(completed_sql)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
