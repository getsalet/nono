#!/usr/bin/env python3
"""Rebuild completed city images using exact, non-generated AFP product assets."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

import city_content_queue as base
import city_content_queue_cloudflare as backend
import image_prompt_policy

POLICY = "exact-asset-composite-v1"
MODE = "exact-approved-asset-composite"
OUT = Path(__file__).resolve().parents[1] / "artifacts" / "city-content-queue"
MARKER = OUT / "image-rebuild-exact-asset-composite-v1.json"
MODEL = os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.5-flash")
API = os.getenv("IMAGE_ENDPOINT") or os.getenv(
    "AGNES_API_BASE", "https://apihub.agnes-ai.com/v1"
).rstrip("/") + "/images/generations"
KEY = (os.getenv("IMAGE_API_KEY") or os.getenv("AGNES_API_KEY", "")).strip()
WORKERS = max(1, int(os.getenv("IMAGE_WORKERS", "8")))
RETRIES = max(2, int(os.getenv("IMAGE_RETRIES", "4")))
image_prompt_policy.install(backend)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def neutral_input() -> str:
    image = Image.new("RGB", (1024, 576), (232, 234, 228))
    buffer = io.BytesIO()
    image.save(buffer, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


NEUTRAL_INPUT = neutral_input()


def generate_once(item: dict, kind: int) -> dict:
    if not KEY:
        raise RuntimeError("IMAGE_API_KEY/AGNES_API_KEY is missing")
    payload = {
        "model": MODEL,
        "prompt": image_prompt_policy.image_prompt(item, kind),
        "size": "1024x768",
        "return_base64": True,
        "extra_body": {"response_format": "b64_json", "image": [NEUTRAL_INPUT]},
    }
    request = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "navar-exact-product-rebuild/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1200]
        raise RuntimeError(f"Agnes Image HTTP {exc.code}: {detail}") from exc
    row = (data.get("data") or [{}])[0]
    if row.get("b64_json"):
        blob = base64.b64decode(row["b64_json"])
    elif row.get("url"):
        with urllib.request.urlopen(row["url"], timeout=300) as response:
            blob = response.read()
    else:
        raise RuntimeError("Agnes image response has neither b64_json nor url")

    image = Image.open(io.BytesIO(blob)).convert("RGB")
    width, height = image.size
    target = 16 / 9
    if width / height > target:
        new_width = int(height * target)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    image = image.resize((1200, 675), Image.Resampling.LANCZOS)
    image = image_prompt_policy.composite_product(image, item, kind)
    stage = io.BytesIO()
    image.save(stage, "JPEG", quality=93, optimize=True)
    image = Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert("RGB")
    output = io.BytesIO()
    image.save(output, "WEBP", quality=60, method=6)
    blob = output.getvalue()
    if len(blob) < 10000:
        raise RuntimeError("Generated WebP is unexpectedly small")
    name = f"{item['source_id']}-{kind}.webp"
    (base.IMAGES / name).write_bytes(blob)
    return {
        "name": name,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "mime": "image/webp",
        "width": 1200,
        "height": 675,
    }


def generate(item: dict, kind: int) -> dict:
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            return generate_once(item, kind)
        except Exception as exc:
            last = exc
            print(
                f"exact_product_attempt source_id={item.get('source_id')} kind={kind} "
                f"attempt={attempt}/{RETRIES} error={exc}",
                flush=True,
            )
            if attempt < RETRIES:
                time.sleep(min(60, 5 * 2 ** (attempt - 1)))
    raise RuntimeError(f"image generation failed after {RETRIES} attempts: {last}") from last


def replace_names(path: Path, mapping: dict[str, str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in mapping.items():
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def save_marker(rebuilt, skipped, failures, total, final=False):
    MARKER.write_text(
        json.dumps(
            {
                "policy": POLICY,
                "mode": MODE,
                "completed": bool(final and not failures),
                "completed_at": now() if final and not failures else None,
                "total_candidates": total,
                "rebuilt_posts": sorted(rebuilt),
                "skipped": skipped,
                "failures": failures,
                "workers": WORKERS,
                "last_progress_at": now(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    if not base.QUEUE.exists():
        raise RuntimeError("Queue file is missing")
    state = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in state.get("items", []) if x.get("status") == "completed"]
    records, skipped = {}, []
    for item in completed:
        source_id = str(item.get("source_id") or "")
        path = base.ITEMS / f"{source_id}.json"
        if not source_id or not path.exists():
            skipped.append({"source_id": source_id, "reason": "item JSON missing"})
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("image_rebuild_policy") == POLICY:
            continue
        records[source_id] = (item, path, data)

    if not records:
        save_marker([], skipped, [], len(completed), final=True)
        print("exact_product_rebuild=already_current")
        return 0

    results = {source_id: {} for source_id in records}
    failures = []
    with ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix="exact-product") as pool:
        futures = {}
        for source_id, (item, _, data) in records.items():
            enriched = {**item, **data}
            for kind in range(1, 6):
                futures[pool.submit(generate, enriched, kind)] = (source_id, kind)
        for future in as_completed(futures):
            source_id, kind = futures[future]
            try:
                results[source_id][kind] = future.result()
            except Exception as exc:
                failures.append(
                    {"source_id": source_id, "kind": kind, "error": str(exc)[:1200]}
                )

    failed_ids = {x["source_id"] for x in failures}
    rebuilt, stamp = [], now()
    aggregate_mapping = {}
    for source_id, (item, path, data) in records.items():
        if source_id in failed_ids or len(results[source_id]) != 5:
            continue
        generated = [results[source_id][kind] for kind in range(1, 6)]
        old_images = data.get("images") or item.get("images") or []
        old_names = [
            Path(x.get("name") if isinstance(x, dict) else str(x)).name for x in old_images
        ]
        new_names = [x["name"] for x in generated]
        mapping = dict(zip(old_names, new_names))
        aggregate_mapping.update(mapping)
        replace_names(path, mapping)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(
            images=new_names,
            image_sha256=[x["sha256"] for x in generated],
            image_generation_mode=MODE,
            image_rebuild_policy=POLICY,
            image_rebuilt_at=stamp,
            product_family=image_prompt_policy.product_family({**item, **data}),
        )
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        item.update(
            images=new_names,
            image_sha256=[x["sha256"] for x in generated],
            image_generation_mode=MODE,
            image_rebuild_policy=POLICY,
            image_rebuilt_at=stamp,
        )
        for old_name, new_name in mapping.items():
            if old_name and old_name != new_name:
                (base.IMAGES / old_name).unlink(missing_ok=True)
        replace_names(OUT / "sql" / f"{source_id}.sql", mapping)
        replace_names(OUT / "rollback" / f"{source_id}.sql", mapping)
        rebuilt.append(source_id)
        save_marker(rebuilt, skipped, failures, len(completed), final=False)

    replace_names(OUT / "create-all-completed.sql", aggregate_mapping)
    replace_names(OUT / "rollback-all-completed.sql", aggregate_mapping)
    state["updated_at"] = now()
    base.QUEUE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    save_marker(rebuilt, skipped, failures, len(completed), final=True)
    print(
        f"exact_product_rebuild rebuilt={len(rebuilt)} failures={len(failures)} "
        f"workers={WORKERS} policy={POLICY}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())