#!/usr/bin/env python3
# Queue restart trigger after repository transfer to getsalet/nono.
"""Rebuild completed city images using exact, non-generated AFP product assets."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

import city_content_queue as base
import city_content_queue_cloudflare as backend
import image_prompt_policy
import image_quality_gate

POLICY = "strict-restoration-posts-567-632-20260929"
MODE = "article-parity-three-image-reference-conditioned-rerender"
OUT = Path(__file__).resolve().parents[1] / "artifacts" / "city-content-queue"
MARKER = OUT / "image-rebuild-article-parity-v14-three-image.json"
MODEL = os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.5-flash")
API = os.getenv("IMAGE_ENDPOINT") or os.getenv(
    "AGNES_API_BASE", "https://apihub.agnes-ai.com/v1"
).rstrip("/") + "/images/generations"
KEY = (os.getenv("IMAGE_API_KEY") or os.getenv("AGNES_API_KEY", "")).strip()
WORKERS = max(1, int(os.getenv("IMAGE_WORKERS", "2")))
RETRIES = max(2, int(os.getenv("IMAGE_RETRIES", "6")))
QA_ATTEMPTS = max(1, int(os.getenv("IMAGE_QA_ATTEMPTS", "10")))
SET_ATTEMPTS = max(1, int(os.getenv("IMAGE_SET_QA_ATTEMPTS", "3")))
FROM_POST = max(1, int(os.getenv("REBUILD_FROM_POST", "1")))
POST_LIMIT = max(1, int(os.getenv("REBUILD_POST_LIMIT", "1")))
POST_WORKERS = max(1, int(os.getenv("REBUILD_POST_WORKERS", "1")))
POST_STAGGER_SECONDS = max(0.0, float(os.getenv("REBUILD_POST_STAGGER_SECONDS", "0")))
COMPLETED_SINCE = os.getenv("REBUILD_COMPLETED_SINCE", "").strip()
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
        "extra_body": {
            "response_format": "b64_json",
            "image": image_prompt_policy.reference_images(kind, item),
        },
    }
    request = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + (base.next_agnes_key() if hasattr(base, "next_agnes_key") else KEY),
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
    stage = io.BytesIO()
    image.save(stage, "JPEG", quality=93, optimize=True)
    image = Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert("RGB")
    output = io.BytesIO()
    image.save(output, "WEBP", quality=60, method=6)
    blob = output.getvalue()
    if len(blob) < 10000:
        raise RuntimeError("Generated WebP is unexpectedly small")
    name = image_prompt_policy.seo_image_name(item, kind, "webp")
    output_dir = Path(item.get("_image_output_dir") or base.IMAGES)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / name).write_bytes(blob)
    return {
        "name": name,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "mime": "image/webp",
        "width": 1200,
        "height": 675,
    }


def generate(item: dict, kind: int) -> dict:
    image_dir = Path(item.get("_image_output_dir") or base.IMAGES)
    review_dir = Path(item.get("_image_review_dir") or (OUT / "image-reviews"))
    image_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    review_path = review_dir / f"{item['source_id']}-{kind}.json"
    feedback, history = "", []
    for qa_attempt in range(1, QA_ATTEMPTS + 1):
        candidate = dict(item)
        if feedback:
            candidate["_image_qa_feedback"] = feedback
        last = None
        for attempt in range(1, RETRIES + 1):
            try:
                result = generate_once(candidate, kind)
                break
            except Exception as exc:
                last = exc
                print(
                    f"exact_product_attempt source_id={item.get('source_id')} kind={kind} "
                    f"attempt={attempt}/{RETRIES} error={exc}",
                    flush=True,
                )
                if attempt < RETRIES:
                    message = str(exc).lower()
                    delay = min(300, 60 * 2 ** (attempt - 1)) if "429" in message or "rate_limit" in message else min(90, 10 * 2 ** (attempt - 1))
                    print(f"exact_product_backoff_seconds={delay}", flush=True)
                    time.sleep(delay)
        else:
            raise RuntimeError(f"image generation failed after {RETRIES} attempts: {last}") from last
        path = image_dir / result["name"]
        try:
            verdict = image_quality_gate.review_image(base, path, item, kind)
        except Exception as exc:
            verdict = {
                "pass": False,
                "score": 0,
                "reasons": [f"visual reviewer unavailable: {type(exc).__name__}"],
                "correction_prompt": "Regenerate and retry strict visual review.",
            }
        verdict["attempt"] = qa_attempt
        history.append(verdict)
        review_path.write_text(
            json.dumps(
                {
                    "source_id": item["source_id"],
                    "kind": kind,
                    "policy": image_quality_gate.REVIEW_POLICY,
                    "approved": bool(verdict.get("pass")),
                    "history": history,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            f"city_rebuild_image_qa source_id={item.get('source_id')} kind={kind} "
            f"attempt={qa_attempt} pass={verdict.get('pass')} score={verdict.get('score')} "
            f"reasons={verdict.get('reasons', [])}",
            flush=True,
        )
        if verdict.get("pass"):
            return result
        path.unlink(missing_ok=True)
        feedback = str(verdict.get("correction_prompt") or "; ".join(verdict.get("reasons", [])))
    reasons = history[-1].get("reasons", []) if history else []
    raise RuntimeError(f"image hard gate rejected role {kind} after {QA_ATTEMPTS} attempts: {reasons}")


def generate_set(item: dict) -> dict[int, dict]:
    source_id = str(item["source_id"])
    OUT.mkdir(parents=True, exist_ok=True)
    # Persist individually approved roles between scheduled runs. Publication
    # remains atomic: checkpointed files replace live images only after the
    # complete three-image set passes the unchanged diversity gate.
    staging_root = OUT / ".image-role-checkpoints" / source_id
    staging_images = staging_root / "images"
    staging_reviews = staging_root / "image-reviews"
    staging_images.mkdir(parents=True, exist_ok=True)
    staging_reviews.mkdir(parents=True, exist_ok=True)
    set_review_path = OUT / "image-reviews" / f"{source_id}-set.json"
    results, feedback, history = {}, {}, []
    if set_review_path.exists():
        try:
            history = list(
                json.loads(set_review_path.read_text(encoding="utf-8")).get("history")
                or []
            )[-20:]
        except (OSError, json.JSONDecodeError):
            history = []
    for kind in range(1, 4):
        name = image_prompt_policy.seo_image_name(item, kind, "webp")
        image_path = staging_images / name
        review_path = staging_reviews / f"{source_id}-{kind}.json"
        try:
            review = json.loads(review_path.read_text(encoding="utf-8"))
            review_history = review.get("history") or []
        except (OSError, json.JSONDecodeError):
            review_history = []
        if (
            image_path.exists()
            and image_path.stat().st_size > 10000
            and review_history
            and review_history[-1].get("pass")
        ):
            blob = image_path.read_bytes()
            results[kind] = {
                "name": name,
                "sha256": hashlib.sha256(blob).hexdigest(),
                "mime": "image/webp",
                "width": 1200,
                "height": 675,
            }
            print(
                f"city_rebuild_checkpoint_reused source_id={source_id} kind={kind}",
                flush=True,
            )
        elif review_history:
            last = review_history[-1]
            feedback[kind] = str(
                last.get("correction_prompt")
                or "; ".join(last.get("reasons") or [])
            ).strip()
    pending = set(range(1, 4)) - set(results)
    completed = False
    try:
        with ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix="city-rebuild-image") as pool:
            for set_attempt in range(1, SET_ATTEMPTS + 1):
                futures = {}
                for kind in sorted(pending):
                    candidate = dict(item)
                    candidate["_image_output_dir"] = str(staging_images)
                    candidate["_image_review_dir"] = str(staging_reviews)
                    if feedback.get(kind):
                        candidate["_image_qa_feedback"] = feedback[kind]
                    futures[pool.submit(generate, candidate, kind)] = kind
                for future in as_completed(futures):
                    kind = futures[future]
                    results[kind] = future.result()
                paths = [staging_images / results[kind]["name"] for kind in range(1, 4)]
                verdict = image_quality_gate.review_image_set(base, paths, item)
                verdict["set_attempt"] = set_attempt
                history.append(verdict)
                set_review_path.parent.mkdir(parents=True, exist_ok=True)
                set_review_path.write_text(
                    json.dumps({"source_id": source_id, "policy": POLICY, "history": history}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(
                    f"city_rebuild_set_qa source_id={source_id} attempt={set_attempt} "
                    f"pass={verdict.get('pass')} score={verdict.get('score')} "
                    f"duplicate_roles={verdict.get('duplicate_roles', [])} reasons={verdict.get('reasons', [])}",
                    flush=True,
                )
                if verdict.get("pass"):
                    base.IMAGES.mkdir(parents=True, exist_ok=True)
                    final_reviews = OUT / "image-reviews"
                    final_reviews.mkdir(parents=True, exist_ok=True)
                    for kind in range(1, 4):
                        staged = staging_images / results[kind]["name"]
                        if not staged.exists():
                            raise RuntimeError(f"Approved staged image is missing for role {kind}")
                        os.replace(staged, base.IMAGES / staged.name)
                        role_review = staging_reviews / f"{source_id}-{kind}.json"
                        if role_review.exists():
                            os.replace(role_review, final_reviews / role_review.name)
                    completed = True
                    return results
                pending = set(verdict.get("duplicate_roles") or range(1, 4))
                correction = str(verdict.get("correction_prompt") or "; ".join(verdict.get("reasons", [])))
                for kind in pending:
                    feedback[kind] = correction + f" Create a new role-{kind} scene clearly unlike the other roles."
                    if kind in results:
                        (staging_images / results[kind]["name"]).unlink(missing_ok=True)
                        results.pop(kind, None)
                    (staging_reviews / f"{source_id}-{kind}.json").unlink(missing_ok=True)
        raise RuntimeError(f"Image-set diversity gate rejected the three-image editorial set after {SET_ATTEMPTS} rounds")
    finally:
        if completed:
            shutil.rmtree(staging_root, ignore_errors=True)
        else:
            # Keep useful role images and reviews for the next scheduled run.
            # Remove only a truly empty checkpoint directory.
            try:
                if not any(staging_images.iterdir()) and not any(staging_reviews.iterdir()):
                    shutil.rmtree(staging_root, ignore_errors=True)
            except OSError:
                pass


def replace_names(path: Path, mapping: dict[str, str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in mapping.items():
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def remove_named_figures(path: Path, names: list[str]) -> None:
    if not path.exists() or not names:
        return
    text = path.read_text(encoding="utf-8")
    updated = text
    for name in names:
        updated = re.sub(r'<figure\b[^>]*>.*?' + re.escape(name) + r'.*?</figure>', '', updated, flags=re.S)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def save_marker(rebuilt, skipped, failures, total, remaining, final=False):
    previous = {}
    if MARKER.exists():
        try:
            previous = json.loads(MARKER.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    previous_remaining = int(previous.get("remaining_candidates", total))
    progressed = remaining < previous_remaining
    stalled_runs = (
        0
        if progressed
        else int(previous.get("consecutive_no_progress_runs", 0)) + 1
    )
    checkpoint_root = OUT / ".image-role-checkpoints"
    checkpoint_posts = (
        sum(1 for path in checkpoint_root.iterdir() if path.is_dir())
        if checkpoint_root.exists()
        else 0
    )
    MARKER.write_text(
        json.dumps(
            {
                "policy": POLICY,
                "mode": MODE,
                "completed": bool(final and not failures and remaining == 0),
                "completed_at": now() if final and not failures and remaining == 0 else None,
                "total_candidates": total,
                "remaining_candidates": remaining,
                "rebuilt_posts": sorted(rebuilt),
                "skipped": skipped,
                "failures": failures,
                "workers": WORKERS,
                "post_workers": POST_WORKERS,
                "post_limit": POST_LIMIT,
                "checkpoint_posts": checkpoint_posts,
                "consecutive_no_progress_runs": stalled_runs,
                "from_completed_post": FROM_POST,
                "last_progress_at": (
                    now()
                    if progressed or not previous
                    else previous.get("last_progress_at") or now()
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def previously_failed_ids() -> set[str]:
    if not MARKER.exists():
        return set()
    try:
        marker = json.loads(MARKER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {
        str(row.get("source_id") or "")
        for row in marker.get("failures", [])
        if row.get("source_id")
    }


def main() -> int:
    if not base.QUEUE.exists():
        raise RuntimeError("Queue file is missing")
    state = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    completed_all = [x for x in state.get("items", []) if x.get("status") == "completed"]
    if COMPLETED_SINCE:
        completed_all = [
            x for x in completed_all
            if str(x.get("completed_at") or "") >= COMPLETED_SINCE
        ]
    completed = completed_all[FROM_POST - 1:]
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

    def current_ids():
        result=[]
        for row in completed:
            sid=str(row.get("source_id") or "")
            path=base.ITEMS/f"{sid}.json"
            if not sid or not path.exists():continue
            try:data=json.loads(path.read_text(encoding="utf-8"))
            except (OSError,json.JSONDecodeError):continue
            if data.get("image_rebuild_policy")==POLICY:result.append(sid)
        return sorted(result)

    if not records:
        current=current_ids();remaining=max(0,len(completed)-len(current))
        save_marker(current, skipped, [], len(completed), remaining, final=True)
        print("exact_product_rebuild=already_current")
        return 0

    failed_before = previously_failed_ids()
    # The image provider currently renders layflat pairs with persistent human
    # staging. Keep the healthy drip-tape rebuild moving and leave layflat
    # records for a later dedicated policy instead of alternating back to the
    # same impossible references.
    selected_ids = sorted(
        records,
        key=lambda source_id: (
            image_prompt_policy.product_family({**records[source_id][0], **records[source_id][2]}) == "layflat",
            source_id in failed_before,
            source_id,
        ),
    )[:POST_LIMIT]
    records = {source_id: records[source_id] for source_id in selected_ids}
    results = {source_id: {} for source_id in records}
    failures = []
    with ThreadPoolExecutor(max_workers=POST_WORKERS, thread_name_prefix="city-rebuild-post") as post_pool:
        futures = {}
        record_rows = list(records.items())
        for index, (source_id, (item, _, data)) in enumerate(record_rows):
            futures[post_pool.submit(generate_set, {**item, **data})] = source_id
            if POST_STAGGER_SECONDS and index + 1 < len(record_rows):
                print(f"rebuild_post_stagger_seconds={POST_STAGGER_SECONDS:g}", flush=True)
                time.sleep(POST_STAGGER_SECONDS)
        for future in as_completed(futures):
            source_id = futures[future]
            try:
                results[source_id] = future.result()
            except Exception as exc:
                failures.append(
                    {"source_id": source_id, "kind": "set", "error": str(exc)[:1200]}
                )

    failed_ids = {x["source_id"] for x in failures}
    rebuilt, stamp = [], now()
    aggregate_mapping = {}
    for source_id, (item, path, data) in records.items():
        if source_id in failed_ids or len(results[source_id]) != 3:
            continue
        generated = [results[source_id][kind] for kind in range(1, 4)]
        old_images = data.get("images") or item.get("images") or []
        old_names = [
            Path(x.get("name") if isinstance(x, dict) else str(x)).name for x in old_images
        ]
        new_names = [x["name"] for x in generated]
        mapping = dict(zip(old_names[:3], new_names))
        extra_names = old_names[3:]
        aggregate_mapping.update(mapping)
        remove_named_figures(path, extra_names)
        remove_named_figures(OUT / "sql" / f"{source_id}.sql", extra_names)
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
        for old_name in extra_names:
            (base.IMAGES / old_name).unlink(missing_ok=True)
        replace_names(OUT / "sql" / f"{source_id}.sql", mapping)
        replace_names(OUT / "rollback" / f"{source_id}.sql", mapping)
        rebuilt.append(source_id)

    replace_names(OUT / "create-all-completed.sql", aggregate_mapping)
    replace_names(OUT / "rollback-all-completed.sql", aggregate_mapping)
    state["updated_at"] = now()
    base.QUEUE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    current=current_ids();remaining=max(0,len(completed)-len(current))
    save_marker(current, skipped, failures, len(completed), remaining, final=True)
    print(
        f"exact_product_rebuild rebuilt={len(rebuilt)} failures={len(failures)} "
        f"workers={WORKERS} post_workers={POST_WORKERS} post_limit={POST_LIMIT} remaining={remaining} policy={POLICY}",
        flush=True,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
