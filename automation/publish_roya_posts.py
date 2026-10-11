#!/usr/bin/env python3
"""Publish generated Roya backlink posts to the Roya blog panel (afp.royablog.ir).

Reads artifacts/roya-backlink-queue/publish-queue.json, exports every ready post as
HTML + JSON and - when ROYA_PUBLISH=1 with ROYA_USERNAME/ROYA_PASSWORD - publishes it
through the panel with Playwright.

Panel behaviour verified on the live panel (2026-10-12):
  * Roya has **no bulk/CSV/WordPress import**. مهاجرت (User/Transfer) only accepts
    بلاگفا / میهن‌بلاگ / لوکس‌بلاگ blogs, so every post is created one at a time.
  * The only save path that really persists a post is the panel's own form submit:
    fill form#fbmyposting, sync TinyMCE, then `jQuery('.npost').submit()` and let the
    browser navigate. The post is written and the browser lands on /User/Posts/.
  * Do NOT use fetch/XHR to /User/AddPost/ (neither the mb81_ajax_publish helper nor a
    plain FormData fetch): the server answers {"status":"ok","pid":N} but writes nothing.
  * Fields: ptitle, plink (latin slug), pshort = article HTML (main body),
    pfull = ادامه مطلب, ppublic (1 منتشر شود، 2 پیش نویس، 3 انتشار در آینده).
  * Delete: POST /Op/ with othReq=rmps_<pid> and header X-Requested-With: XMLHttpRequest.

Env: ROYA_PUBLISH ROYA_USERNAME ROYA_PASSWORD ROYA_PUBLISH_LIMIT ROYA_DRAFT
     ROYA_DELAY_SECONDS ROYA_QUEUE_FILE ROYA_BLOG_URL ROYA_PANEL_URL
"""
import json, os, random, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / 'data' / 'roya' / 'backlink-queue.json'
ART = ROOT / 'artifacts' / 'roya-backlink-queue'
PUBLISH_QUEUE = ART / 'publish-queue.json'
EXPORT = ART / 'publish'
STATE = ROOT / 'state' / 'roya-backlink-progress.json'
LOG = ART / 'publish-log.jsonl'

PANEL = os.getenv('ROYA_PANEL_URL', 'https://www.royablog.ir').rstrip('/')
BLOG = os.getenv('ROYA_BLOG_URL', 'https://afp.royablog.ir').rstrip('/')
ADD_URL = PANEL + '/User/AddPost/'
POSTS_URL = PANEL + '/User/Posts/'
LIMIT = int(os.getenv('ROYA_PUBLISH_LIMIT', '3'))
DO_PUBLISH = os.getenv('ROYA_PUBLISH', '0') == '1'
DRAFT = os.getenv('ROYA_DRAFT', '0') == '1'
DELAY = float(os.getenv('ROYA_DELAY_SECONDS', '10'))


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
    safe = re.sub(r'[^A-Za-z0-9._-]+', '_', item['key'])[:80]
    (EXPORT / f'{safe}.html').write_text(
        f"<!-- {post.get('title','')} -->\n{post.get('html','')}\n", encoding='utf-8')
    save(EXPORT / f'{safe}.json', {'key': item['key'], 'target_url': item.get('target_url'),
                                   'site_title': item.get('site_title'),
                                   'title': post.get('title'), 'slug': post.get('slug'),
                                   'meta_description': post.get('meta_description'),
                                   'focus_keyword': post.get('focus_keyword'),
                                   'tags': post.get('tags'), 'html': post.get('html')})
    return safe


def panel_rows(page):
    return page.eval_on_selector_all(
        'table.poststable tbody tr',
        'rows => rows.map(r => r.innerText.replace(/\\s+/g, " ").trim())')


def find_pid(page, title):
    return page.evaluate("""(title) => {
        const head = title.trim().slice(0, 25);
        const row = [...document.querySelectorAll('table.poststable tbody tr')]
            .find(tr => (tr.innerText || '').includes(head));
        if (!row) return null;
        const a = row.querySelector('a.actionedit');
        return a ? (a.getAttribute('href') || '').match(/(\\d+)/)[1] : null;
    }""", title)


def publish_with_panel(todo):
    from playwright.sync_api import sync_playwright
    user, password = os.getenv('ROYA_USERNAME', ''), os.getenv('ROYA_PASSWORD', '')
    if not (user and password):
        raise RuntimeError('ROYA_USERNAME/ROYA_PASSWORD are required for publishing')
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--no-sandbox'])
        ctx = browser.new_context(locale='fa-IR', viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        page.on('dialog', lambda d: d.accept())

        page.goto(PANEL + '/', wait_until='domcontentloaded', timeout=90000)
        if page.query_selector('input[name=passwd]'):
            page.fill('input[name=username]', user)
            page.fill('input[name=passwd]', password)
            page.click('input[name=login]')
            page.wait_for_load_state('domcontentloaded')
        page.goto(ADD_URL, wait_until='domcontentloaded', timeout=90000)
        page.wait_for_selector('#ptitle', timeout=60000)
        if page.query_selector('input[name=passwd]'):
            raise RuntimeError('Roya panel login failed (check ROYA_USERNAME/ROYA_PASSWORD)')

        for n, entry in enumerate(todo):
            item = load(entry['item_file'], {})
            post = item.get('post', {})
            title = (post.get('title') or item.get('prepared_title') or '')[:120]
            slug = (post.get('slug') or re.sub(r'[^a-z0-9]+', '-', entry['key'].split('/')[-1].lower()))[:60].strip('-')
            row = {'key': entry['key'], 'title': title, 'slug': slug,
                   'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
            for attempt in (1, 2):
                try:
                    page.goto(ADD_URL, wait_until='domcontentloaded', timeout=90000)
                    page.wait_for_selector('#ptitle', timeout=60000)
                    page.fill('#ptitle', title)
                    if slug:
                        page.fill('#plink', slug)
                    page.evaluate("""(payload) => {
                        const tags = (payload.tags || []).join(',');
                        const k = document.querySelector('#keyword'); if (k) k.value = tags;
                        const kw = document.querySelector('#kw'); if (kw) kw.value = tags;
                        const pub = document.querySelector('input[name=ppublic][value="' + payload.ppublic + '"]');
                        if (pub) pub.checked = true;
                        if (window.tinymce && tinymce.get('pshort')) tinymce.get('pshort').setContent(payload.html);
                        else { const ta = document.querySelector('#pshort'); if (ta) ta.value = payload.html; }
                    }""", {'html': post.get('html', ''), 'tags': post.get('tags') or [item.get('city_fa', '')],
                           'ppublic': '2' if DRAFT else '1'})
                    page.wait_for_timeout(1200)
                    with page.expect_navigation(timeout=90000):
                        page.evaluate("() => window.jQuery ? window.jQuery('.npost').submit() "
                                      ": document.querySelector('form.npost').submit()")
                    page.wait_for_timeout(2500)
                    if '/User/Posts/' not in page.url:
                        page.goto(POSTS_URL, wait_until='domcontentloaded', timeout=90000)
                    pid = find_pid(page, title)
                    if not pid:
                        raise RuntimeError('post not found in the panel list after submit')
                    url = f'{BLOG}/post/{pid}/{slug}/' if slug else f'{BLOG}/post/{pid}/'
                    page.goto(url, wait_until='domcontentloaded', timeout=90000)
                    live_html = page.content()
                    if title.split('|')[0].strip()[:20] not in live_html:
                        raise RuntimeError(f'published page did not verify at {url}')
                    row.update({'pid': pid, 'url': url, 'verified': True, 'draft': DRAFT,
                                'attempts': attempt})
                    print(f'[{n+1}/{len(todo)}] {"draft" if DRAFT else "published"} '
                          f'{entry["key"]} -> {url}', flush=True)
                    break
                except Exception as exc:
                    row.update({'error': str(exc)[:300]})
                    print(f'[{n+1}/{len(todo)}] attempt {attempt} failed for {entry["key"]}: {exc}',
                          flush=True)
                    page.wait_for_timeout(4000)
            results.append(row)
            with LOG.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + '\n')
            if n + 1 < len(todo) and DELAY:
                time.sleep(DELAY + random.uniform(0, DELAY / 2))
        browser.close()
    return results


def main():
    queue = load(QUEUE, {'items': []})
    pq = load(PUBLISH_QUEUE, {'items': []})
    ready = [e for e in pq.get('items', []) if Path(e.get('item_file', '')).exists()]
    if not ready:
        print('nothing ready to publish')
        return 0
    todo = ready[:LIMIT]
    for entry in todo:
        export_post(entry['item_file'], load(entry['item_file'], {}))
    print(f'exported {len(todo)} post(s) to {EXPORT}')
    if not DO_PUBLISH:
        print('ROYA_PUBLISH is not 1; skipping panel publish')
        return 0
    if not (os.getenv('ROYA_USERNAME') and os.getenv('ROYA_PASSWORD')):
        print('ROYA_USERNAME/ROYA_PASSWORD are not set; skipping panel publish')
        return 0

    results = publish_with_panel(todo)
    by_key = {i['key']: i for i in queue.get('items', [])}
    ok = {}
    for row in results:
        if not row.get('pid'):
            continue
        ok[row['key']] = row
        item = by_key.get(row['key'])
        if item:
            item['published'] = not DRAFT
            item['published_url'] = row['url']
            item['published_at'] = row['at']
            item['pid'] = row['pid']
            if not DRAFT:
                item['status'] = 'published'
    save(QUEUE, queue)
    state = load(STATE, {})
    state['last_publish_run'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    state.setdefault('published', []).extend(
        {'key': k, 'pid': v['pid'], 'url': v['url'], 'at': v['at']} for k, v in ok.items())
    save(STATE, state)
    pq['items'] = [e for e in pq.get('items', []) if e['key'] not in ok]
    pq['count'] = len(pq['items'])
    save(PUBLISH_QUEUE, pq)
    print(f'published {len(ok)} post(s), {len(results) - len(ok)} failed')
    return 0 if len(ok) == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
