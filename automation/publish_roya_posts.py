#!/usr/bin/env python3
"""Publish generated Roya backlink posts to the Roya blog panel.

Reads artifacts/roya-backlink-queue/publish-queue.json, exports every ready post
as HTML + JSON, and, when ROYA_PUBLISH=1 with ROYA_USERNAME/ROYA_PASSWORD set,
publishes it through the panel with Playwright.

Panel shape (verified on www.royablog.ir/User/AddPost/):
  form#fbmyposting.npost
    input[name=ptitle]  -> post title
    input[name=plink]   -> slug
    TinyMCE 'pshort'    -> teaser (ادامه مطلب)
    TinyMCE 'pfull'     -> full article HTML

Env: ROYA_PUBLISH ROYA_USERNAME ROYA_PASSWORD ROYA_PUBLISH_LIMIT ROYA_QUEUE_FILE
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / 'data' / 'roya' / 'backlink-queue.json'
PUBLISH_QUEUE = ROOT / 'artifacts' / 'roya-backlink-queue' / 'publish-queue.json'
ITEMS = ROOT / 'artifacts' / 'roya-backlink-queue' / 'items'
EXPORT = ROOT / 'artifacts' / 'roya-backlink-queue' / 'publish'
LOGIN_URL = 'https://www.royablog.ir/'
ADD_URL = 'https://www.royablog.ir/User/AddPost/'
LIMIT = int(os.getenv('ROYA_PUBLISH_LIMIT', '3'))
DO_PUBLISH = os.getenv('ROYA_PUBLISH', '0') == '1'


def load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return default


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')


def export_post(item_file, item):
    post = item.get('post', {})
    EXPORT.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9._-]+', '_', item['key'])
    (EXPORT / f'{safe}.html').write_text(
        f"<!-- {post.get('title','')} -->\n{post.get('html','')}\n", encoding='utf-8')
    save(EXPORT / f'{safe}.json', {'key': item['key'], 'target_url': item.get('target_url'),
                                   'title': post.get('title'), 'slug': post.get('slug'),
                                   'meta_description': post.get('meta_description'),
                                   'focus_keyword': post.get('focus_keyword'),
                                   'tags': post.get('tags'), 'html': post.get('html')})
    return safe


def publish_with_panel(ready):
    from playwright.sync_api import sync_playwright
    user, password = os.getenv('ROYA_USERNAME', ''), os.getenv('ROYA_PASSWORD', '')
    if not (user and password):
        raise RuntimeError('ROYA_USERNAME/ROYA_PASSWORD are required for publishing')
    published = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--no-sandbox'])
        page = browser.new_page()
        page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)
        user_box = page.query_selector('input[name*=user i], input[name*=email i], input[type=email], input[type=text]')
        pass_box = page.query_selector('input[type=password]')
        if not (user_box and pass_box):
            raise RuntimeError('login form not found on the Roya panel')
        user_box.fill(user)
        pass_box.fill(password)
        pass_box.press('Enter')
        page.wait_for_timeout(6000)
        if page.query_selector('input[type=password]') and 'AddPost' not in page.url:
            page.goto(ADD_URL, wait_until='domcontentloaded', timeout=60000)
        for entry in ready[:LIMIT]:
            item = load(entry['item_file'], {})
            post = item.get('post', {})
            page.goto(ADD_URL, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_selector('#ptitle', timeout=30000)
            page.fill('#ptitle', post.get('title', ''))
            if post.get('slug') and page.query_selector('#plink'):
                page.fill('#plink', post['slug'])
            page.wait_for_timeout(2500)
            page.evaluate("""(payload) => {
                const set = (id, html) => {
                    if (window.tinymce && tinymce.get(id)) { tinymce.get(id).setContent(html); return true; }
                    const ta = document.getElementById(id); if (ta) { ta.value = html; return true; }
                    return false;
                };
                set('pfull', payload.html);
                set('pshort', payload.teaser);
            }""", {'html': post.get('html', ''), 'teaser': (post.get('meta_description') or '')[:400]})
            page.wait_for_timeout(1200)
            page.evaluate("""() => {
                const form = document.querySelector('form.npost') || document.querySelector('#fbmyposting');
                if (window.jQuery && form) { jQuery(form).submit(); return; }
                if (form) { form.submit(); }
            }""")
            page.wait_for_timeout(8000)
            published.append({'key': entry['key'], 'url': page.url})
            print('published ' + entry['key'] + ' -> ' + page.url, flush=True)
        browser.close()
    return published


def main():
    queue = load(QUEUE, {'items': []})
    pq = load(PUBLISH_QUEUE, {'items': []})
    ready = pq.get('items', [])
    if not ready:
        print('nothing ready to publish')
        return 0
    for entry in ready[:LIMIT]:
        export_post(entry['item_file'], load(entry['item_file'], {}))
    print(f'exported {min(LIMIT, len(ready))} post(s) to {EXPORT}')
    if not DO_PUBLISH:
        print('ROYA_PUBLISH is not 1; skipping panel publish')
        return 0
    results = publish_with_panel(ready)
    by_key = {i['key']: i for i in queue.get('items', [])}
    for row in results:
        item = by_key.get(row['key'])
        if item:
            item['published'] = True
            item['published_url'] = row['url']
    save(QUEUE, queue)
    save(PUBLISH_QUEUE, {'generated_at': pq.get('generated_at'), 'blog': pq.get('blog'),
                         'count': len([i for i in queue.get('items', []) if i.get('status') == 'completed' and not i.get('published')]),
                         'items': [i for i in pq.get('items', []) if not by_key.get(i['key'], {}).get('published')]})
    print(f'published {len(results)} post(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
