#!/usr/bin/env python3
"""Upload only new or changed city ZIP batches over explicit FTPS."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from upload_city_batches_ftps import PACKAGES, connect

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "artifacts" / "city-content-queue" / "ftps-upload-state.json"
SIGNAL_PATH = ROOT / "artifacts" / "city-content-queue" / ".new-batch-signal"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"files": {}}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"files": {}}
    except (OSError, json.JSONDecodeError):
        return {"files": {}}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def signaled_packages() -> list[Path]:
    """Return only ZIPs named by the durable new-batch signal."""
    if not SIGNAL_PATH.exists():
        return []
    names = []
    for raw in SIGNAL_PATH.read_text(encoding="utf-8").splitlines():
        name = Path(raw.strip()).name
        if not name:
            continue
        if not name.endswith(".zip"):
            name += ".zip"
        if name not in names:
            names.append(name)
    packages = []
    for name in names:
        path = PACKAGES / name
        if not path.exists():
            raise FileNotFoundError(f"Signaled package is missing: {name}")
        packages.append(path)
    return packages


def main() -> int:
    packages = signaled_packages()
    state = load_state()
    tracked = state.setdefault("files", {})
    if not packages:
        print("No newly signaled ZIP batch is available; nothing to upload.")
        return 0

    ftp = connect()
    pending = []
    skipped = 0
    missing_remote = []
    uploaded = 0
    try:
        # Only signaled packages are considered. Older ZIPs are never scanned
        # or uploaded again during a normal new-batch delivery.
        for path in packages:
            digest = sha256(path)
            size = path.stat().st_size
            previous = tracked.get(path.name, {})
            try:
                remote_size = ftp.size(path.name)
            except Exception:
                remote_size = None
            state_matches = (
                previous.get("sha256") == digest
                and int(previous.get("size", -1)) == size
            )
            if state_matches and remote_size == size:
                print(f"Remote file verified; skipped: {path.name}")
                skipped += 1
            else:
                if remote_size is None:
                    missing_remote.append(path.name)
                    print(f"Remote file missing; will restore: {path.name}")
                elif remote_size != size:
                    print(
                        f"Remote size mismatch; will replace: {path.name} "
                        f"local={size} remote={remote_size}"
                    )
                pending.append((path, digest, size))

        for path, digest, size in pending:
            with path.open("rb") as stream:
                ftp.storbinary(f"STOR {path.name}", stream, blocksize=1024 * 1024)
            remote_size = ftp.size(path.name)
            if remote_size != size:
                raise RuntimeError(
                    f"Size verification failed for {path.name}: local={size}, remote={remote_size}"
                )
            tracked[path.name] = {"sha256": digest, "size": size, "uploaded_at": now()}
            print(f"Uploaded and verified: {path.name} ({size} bytes)")
            uploaded += 1
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    state["last_run"] = {
        "uploaded": uploaded,
        "skipped": skipped,
        "checked": len(packages),
        "restored_missing_remote": missing_remote,
        "completed_at": now(),
    }
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state["last_run"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
