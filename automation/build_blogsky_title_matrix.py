#!/usr/bin/env python3
"""Export Blogsky's current, evidence-safe generator titles without changing its queue.
The generator still reads the shared title policy plus assigned queue titles. This
is a reproducible review view of those same inputs, not a second title authority.
No AI provider, image creation, publication, login, or schedule changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter
from blogsky_backlink_queue import preview
from city_backlink_policy import matrix_title
from blog_city_editorial import matching_evidence, title_errors
from blog_generated_image import family_enabled

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('data/blog-city-title-matrix.json', 'data/blogsky/backlink-queue.json',
          'data/roya/backlink-queue.json', 'data/blog-city-crop-evidence.json',
          'data/blog-city-priority.json', 'data/blog-generated-image-control.json')

def build(root=ROOT):
    root = Path(root)
    queue = preview(root)
    rows = []
    held = Counter()
    for position, item in enumerate(queue['items'], 1):
        if not family_enabled(item, root):
            held[item['family']] += 1
            continue
        published = bool(item.get('published'))
        title = (item.get('title') or matrix_title(item, 'blogsky', root)) if published else matrix_title(item, 'blogsky', root)
        errors = title_errors(item, title, root)
        if not published and errors:
            raise RuntimeError('Unsafe new title: ' + item['key'])
        evidence = matching_evidence(item, title, root)
        if not 12 <= len(title) <= 65:
            raise RuntimeError('Title length outside current generator limits')
        rows.append({'key': item['key'], 'queue_position': position,
                     'city': item['city_fa'], 'province': item.get('province_fa', ''),
                     'family': item['family'], 'title': title, 'target_url': item['target_url'],
                     'angle': item.get('angle', ''),
                     'locality': 'reviewed_crop_scope' if evidence else 'no_local_crop_claim',
                     'evidence_ids': [r['id'] for r in evidence if r.get('id')],
                     'state': 'published_locked' if published else 'title_ready_not_article_approved',
                     'legacy_title_review_required': bool(errors)})
    if len(rows) != len({r['key'] for r in rows}) or len(rows) != len({r['title'] for r in rows}):
        raise RuntimeError('Duplicate generator key or title')
    fingerprints = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                    for name in INPUTS if (root / name).exists()}
    return {'schema': 'afp-blogsky-generator-title-matrix-v1',
            'blog': 'https://afp-pipe.blogsky.com',
            'generator': 'automation/blogsky_backlink_queue.py',
            'title_authority': 'data/blog-city-title-matrix.json + data/blogsky/backlink-queue.json assigned_title',
            'note': 'Review/export only. Rebuild after title-policy, crop-evidence or queue changes. Title readiness is not article QA or publication permission. Published rows are locked; held families remain excluded.',
            'input_sha256': fingerprints,
            'summary': {'total_titles': len(rows),
                        'future_titles': sum(r['state'] != 'published_locked' for r in rows),
                        'published_locked': sum(r['state'] == 'published_locked' for r in rows),
                        'reviewed_crop_titles': sum(bool(r['evidence_ids']) for r in rows),
                        'crop_free_titles': sum(not r['evidence_ids'] for r in rows),
                        'excluded_held_families': dict(held)},
            'titles': rows}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    value = build(args.root)
    output = args.output or args.root / 'data/blogsky/title-matrix.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(json.dumps(value['summary'], ensure_ascii=False))

if __name__ == '__main__':
    main()
