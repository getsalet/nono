#!/usr/bin/env python3
"""Blogsky adapter for the shared city generator. Export only; never log in/post.

BLOGSKY_DRY_RUN defaults to 1 (read-only, no provider calls or queue changes).
An explicit 0 uses existing Agnes secrets and produces at most one approved draft.
The native Blogsky publisher is intentionally NOT implemented/enabled here.
"""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BLOG = 'https://afp-pipe.blogsky.com'


def control(root=ROOT):
    value = json.loads((Path(root) / 'data/blogsky/generator-control.json').read_text())
    if (not isinstance(value, dict) or type(value.get('enabled')) is not bool
            or value.get('mode') != 'city_export_only' or value.get('blog') != BLOG
            or value.get('publication_enabled') is not False
            or type(value.get('max_count_per_run')) is not int
            or value['max_count_per_run'] != 1):
        raise RuntimeError('Invalid Blogsky export-only control; no work allowed')
    return value


def settings():
    if os.getenv('BLOGSKY_PUBLISH', '0') != '0':
        raise RuntimeError('Native Blogsky publication is not enabled by this adapter')
    dry = os.getenv('BLOGSKY_DRY_RUN', '1')
    count = os.getenv('BLOGSKY_COUNT', '1')
    if dry not in ('0', '1') or count not in ('0', '1'):
        raise RuntimeError('BLOGSKY_DRY_RUN and BLOGSKY_COUNT must be 0 or 1')
    target = os.getenv('BLOGSKY_TARGET', '').strip()
    if target and not re.fullmatch(r'city-[a-f0-9]{16}', target):
        raise RuntimeError('An exact existing city key is required')
    if os.getenv('BLOG_READY_IMAGE_HANDOFF') == '1':
        raise RuntimeError('Automatic image handoff is not enabled for Blogsky')
    return dry == '1', int(count), target


def validate_target(item):
    from blog_source_image import safe_page
    if (item.get('kind') != 'city' or item.get('family') not in ('tape20', 'hose')
            or not item.get('city_fa') or not safe_page(item.get('target_url'))
            or item.get('target_url') == item.get('hub_url')
            or item.get('reference_url') != item.get('target_url')
            or not re.fullmatch(r'city-[a-f0-9]{16}', item.get('key', ''))):
        raise RuntimeError('Blogsky requires an existing, exact official city target')


def preview(root=ROOT):
    """Use the real queue builder in a disposable tree, never mutate production."""
    from city_backlink_policy import build_queue
    root = Path(root)
    with tempfile.TemporaryDirectory(prefix='blogsky-preflight-') as temp:
        tree = Path(temp)
        for name in ('data/blog-city-title-matrix.json', 'data/roya/backlink-queue.json',
                     'data/blog-city-priority.json', 'data/blog-city-crop-evidence.json',
                     'data/blogsky/backlink-queue.json', 'data/blogsky/title-inventory-control.json',
                     'data/blog-generated-image-control.json'):
            source = root / name
            if source.exists():
                dest = tree / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        queue = build_queue('blogsky', tree)
        for item in queue['items']:
            validate_target(item)
        return queue


@contextlib.contextmanager
def shared_engine(root=ROOT, count=1, target=''):
    """Load a private engine instance; never retarget other blog modules on import."""
    root = Path(root)
    spec = importlib.util.spec_from_file_location('_blogsky_city_engine', ROOT / 'automation/farsiblog_backlink_queue.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.ROOT = root
    engine.CITY_BLOG = 'blogsky'
    engine.BLOG = BLOG
    engine.QUEUE = root / 'data/blogsky/backlink-queue.json'
    engine.ART = root / 'artifacts/blogsky-backlink-queue'
    engine.STATE = root / 'state/blogsky-backlink-progress.json'
    overrides = {'FARSIBLOG_COUNT': str(count), 'FARSIBLOG_TARGET': target,
                 'FARSIBLOG_DRY_RUN': '0', 'FARSIBLOG_PUBLISH': '0',
                 'FARSIBLOG_PUBLISH_LIMIT': '0'}
    previous = {k: os.environ.get(k) for k in overrides}
    import roya_backlink_queue as lookup
    previous_cache = lookup.IMAGE_CACHE
    try:
        os.environ.update(overrides)
        yield engine
    finally:
        lookup.IMAGE_CACHE = previous_cache
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main(root=ROOT):
    root = Path(root)
    dry, count, target = settings()
    cfg = control(root)
    from check_blog_pipeline_control import decision
    if not cfg['enabled'] or not decision('blogsky', root)['proceed']:
        print('Blogsky blocked by user control; no queue, API or publication changes.')
        return 0
    from city_backlink_policy import matrix_ready
    if not matrix_ready(root):
        raise RuntimeError('Approved independent title matrix required')
    queue = preview(root)
    if target:
        row = next((x for x in queue['items'] if x['key'] == target), None)
        if row is None:
            raise RuntimeError('Named city target not found; no provider request')
        from blog_generated_image import family_enabled
        if not family_enabled(row, root):
            raise RuntimeError('Named city product family is held; no provider request')
    from blog_source_image import source_preferred
    if not source_preferred({'family': 'tape20'}, 'blogsky', root):
        raise RuntimeError('Explicit exact-source image policy required for Blogsky')
    if dry:
        print(json.dumps({'blog': BLOG, 'mode': 'configuration_check',
                          'city_targets': len(queue['items']), 'provider_calls': 0,
                          'queue_mutated': False, 'publication_attempted': False}, ensure_ascii=False))
        return 0
    from check_blog_run_budget import decision as budget
    if not budget('blogsky', root)['proceed']:
        print('Blogsky rolling budget exhausted; no new generation or publication.')
        return 0
    with shared_engine(root, count, target) as engine:
        code = engine.main()
    from export_blogsky_posts import export
    result = export(root)
    print('Blogsky QA-approved HTML exports:', result['count'], '; publication attempted: false')
    return code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # Provider responses, credential values and raw HTML never enter CLI logs.
        print('Blogsky generator stopped: ' + type(exc).__name__ + '; inspect control/QA checkpoints.', file=sys.stderr)
        sys.exit(1)
