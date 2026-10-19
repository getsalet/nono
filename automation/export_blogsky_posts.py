#!/usr/bin/env python3
"""Revalidate RAW city articles, then wrap for Blogsky. Never publish or mark live.

The manifest is the authoritative current export list; old immutable HTML files
are not evidence of readiness/publication. Footers are intentionally outside QA.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def export(root=ROOT):
    from blogsky_backlink_queue import BLOG, control, validate_target
    from check_blog_pipeline_control import decision
    from city_backlink_policy import links_for, qa
    from blog_generated_image import family_enabled
    from farsiblog_backlink_queue import load, save, now
    root = Path(root)
    folder = root / 'artifacts/blogsky-backlink-queue'
    index = folder / 'exports/index.json'
    cfg = control(root)
    if not cfg['enabled'] or not decision('blogsky', root)['proceed']:
        raise RuntimeError('Blogsky export blocked by user control')
    manifest = {'blog': BLOG, 'generated_at': now(), 'status': 'not_ready',
                'count': 0, 'items': [], 'publication_attempted': False,
                'native_publication_verified': False}
    # Invalidate any old list BEFORE revalidation, even if the next item fails QA.
    save(index, manifest)
    template_path = root / 'templates/blogsky/afp-single-post.html'
    template = template_path.read_text()
    if (template.count('{{ARTICLE_HTML}}') != 1
            or 'class="afp-article-body"' not in template
            or 'id="afp-post"' not in template):
        raise RuntimeError('Exact single-article Blogsky wrapper required')
    queue = load(root / 'data/blogsky/backlink-queue.json', {'items': []})
    entries = []
    for item in queue['items']:
        if item.get('status') != 'completed' or item.get('published'):
            continue
        validate_target(item)
        if not family_enabled(item, root):
            continue  # A later family hold applies to old approved drafts too.
        record = load(folder / 'items' / (item['key'] + '.json'), {})
        if (record.get('key') != item['key'] or record.get('blog') != BLOG
                or record.get('qa', {}).get('passed') is not True
                or record.get('target_url') != item['target_url']
                or not isinstance(record.get('post'), dict)
                or any(record.get(k) != item.get(k) for k in ('kind', 'family', 'city_fa', 'source_key'))):
            raise RuntimeError('Intact approved Blogsky draft checkpoint required')
        # Final generation fields (e.g. exact-source image provenance) are saved
        # with the item; use the current authoritative queue metadata as well.
        merged = {**record, **item}
        post = dict(record['post'])
        errors, _ = qa(merged, post, links_for(item), 'blogsky', root)
        if errors:
            raise RuntimeError('Blogsky raw article failed current full QA')
        raw = post['html']
        if re.search(r'afp-post|\{\{ARTICLE_HTML\}\}', raw):
            raise RuntimeError('Draft must be raw article HTML, not a wrapped layout')
        wrapped = template.replace('{{ARTICLE_HTML}}', raw)
        digest = hashlib.sha256(wrapped.encode()).hexdigest()
        path = folder / 'exports/items' / (item['key'] + '.' + digest[:16] + '.html')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(wrapped)
        entries.append({'key': item['key'], 'title': post['title'], 'slug': post['slug'],
                        'meta_description': post['meta_description'], 'tags': post['tags'],
                        'target_url': item['target_url'], 'body_file': str(path.relative_to(root)),
                        'body_sha256': digest, 'article_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                        'template_sha256': hashlib.sha256(template.encode()).hexdigest(),
                        'contextual_links': links_for(item), 'qa_passed': True,
                        'native_publication_verified': False})
    manifest.update(status='ready_for_manual_review' if entries else 'empty',
                    count=len(entries), items=entries)
    save(index, manifest)
    summary = folder / 'exports/README.md'
    summary.write_text('# Blogsky city article exports\n\n'
                       'HTML body fragments for manual review. No native post has been submitted.\n'
                       'Use only items in the current index.json; file presence is not publication.\n'
                       'Title/tags are separate Blogsky fields; paste body_file in the HTML body editor.\n'
                       'QA checks exactly two contextual article links, not navigation/footer links.\n')
    return manifest


if __name__ == '__main__':
    try:
        print('Blogsky exports:', export()['count'], '; published: false')
    except Exception as exc:
        print('Blogsky export stopped: ' + type(exc).__name__ + '; no native submission.', file=sys.stderr)
        sys.exit(1)
