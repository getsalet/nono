#!/usr/bin/env python3
"""Build or refresh data/roya/backlink-queue.json from the sitemap target map.

Targets come from data/roya/backlink-targets.json (navar-abyari.ir sitemaps).
When data/roya/page-titles.json exists (a snapshot of each page <title>), city
names and product families are taken from the live pages, otherwise they are
derived from the URL slug. Each item carries a prepared Persian blog title so the
queue is ready to run. Existing statuses and generated titles are preserved.
"""
import copy, hashlib, json, re, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / 'data' / 'roya' / 'backlink-targets.json'
TITLES = ROOT / 'data' / 'roya' / 'page-titles.json'
QUEUE = ROOT / 'data' / 'roya' / 'backlink-queue.json'

FILLER = ['نوار', 'تیپ', 'خرید', 'قیمت', 'لوله', 'نخی', 'تاشو', 'آبیاری', 'سانتی', 'سانتیمتری',
          'متری', 'عمده', 'کارخانه', 'روز', 'لیست', 'و', 'در', 'برای', 'افزایش', 'فروش']
TITLE_MAX = 65
TITLE_TEMPLATES = {
    'tape20': [
        'خرید نوار تیپ ۲۰ سانتی در {city} + راهنمای انتخاب',
        'نوار تیپ ۲۰ سانتی در {city}: راهنمای خرید و مشخصات فنی',
        'راهنمای خرید نوار تیپ ۲۰ سانتی برای کشاورزان {city}',
        'نوار تیپ ۲۰ سانتی در {city}؛ ضخامت، فاصله قطره‌چکان و مشاوره',
        'نوار تیپ ۲۰ سانتی برای {city}؛ انتخاب ضخامت و فاصله قطره‌چکان',
        'خرید نوار تیپ ۲۰ سانتی {city}؛ مشاوره فنی AFP',
        'نوار تیپ ۲۰ سانتی در {city}، استان {province}',
        'خرید نوار تیپ ۲۰ سانتی در {city} برای آبیاری قطره‌ای',
        '{city}: راهنمای خرید نوار تیپ ۲۰ سانتی و لوله آبیاری',
        'نوار تیپ ۲۰ سانتی در {city}؛ نصب، فشار و نگهداری',
        'راهنمای فنی نوار تیپ ۲۰ سانتی برای مزارع {city}',
        'خرید نوار تیپ ۲۰ سانتی در {city} + نکات نصب در مزرعه',
        'نوار تیپ ۲۰ سانتی در {city}، {province}؛ راهنمای خرید',
        'انتخاب نوار تیپ ۲۰ سانتی برای {city}: ضخامت و فاصله',
    ],
    'hose': [
        'راهنمای خرید لوله نخی و تاشو در {city}',
        'لوله نخی و تاشو در {city}: انتخاب سایز، فشار و اتصالات',
        'خرید لوله نخی و تاشو در {city} + نکات نصب در مزرعه',
        'لوله نخی و تاشو در {city}؛ راهنمای انتخاب برای خطوط آبیاری',
        'لوله نخی و تاشو برای {city}؛ سایز، فشار و اتصالات',
        'خرید لوله نخی و تاشو {city}؛ مشاوره فنی AFP',
        'لوله نخی و تاشو در {city}، استان {province}',
        'خرید لوله نخی و تاشو در {city} برای آبیاری قطره‌ای',
        '{city}: راهنمای خرید لوله نخی و تاشو',
        'لوله نخی و تاشو در {city}؛ نصب، فشار و نگهداری',
        'راهنمای فنی لوله نخی و تاشو برای مزارع {city}',
        'خرید لوله نخی و تاشو در {city} + انتخاب سایز مناسب',
        'لوله نخی و تاشو در {city}، {province}؛ راهنمای خرید',
        'انتخاب لوله نخی و تاشو برای {city}: سایز و فشار',
    ],
    'hub': [
        'نوار تیپ در {city}: راهنمای خرید برای کشاورزان استان',
        'راهنمای انتخاب نوار تیپ و لوله آبیاری در {city}',
        'خرید نوار تیپ و لوله نخی در {city} + مشاوره فنی',
        'نوار تیپ و لوله آبیاری در {city}؛ راهنمای خرید',
    ],
}


def pick_title(family, city, province_fa, key, used):
    """Deterministic, unique, <=65 char Persian title that always contains the city."""
    pool = [t.format(city=city, province=province_fa) for t in TITLE_TEMPLATES[family]]
    h = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % len(pool)
    ordered = pool[h:] + pool[:h]
    for v in ordered:
        v = re.sub(r'\s+', ' ', v).strip()
        if len(v) <= TITLE_MAX and used.get(v, 0) == 0:
            return v
    base = ordered[0][:TITLE_MAX]
    for n in range(2, 500):
        tail = f' {n}'
        cand = (base[:TITLE_MAX - len(tail)] + tail).strip()
        if used.get(cand, 0) == 0:
            return cand
    return base


def family_of(text, url):
    low = (text or '') + ' ' + urllib.parse.unquote(url or '')
    if 'لوله' in low or 'looleh' in low or 'nakhi' in low or 'tashoo' in low or 'tasho' in low:
        return 'hose'
    if 'نوار' in low or 'navar' in low or 'tip' in low:
        return 'tape20'
    return 'tape20'


def clean_city(raw):
    s = re.sub(r'\s+', ' ', (raw or '')).strip(' ،،.|-')
    s = re.sub(r'^(استان|شهر)\s+', '', s)
    s = re.sub(r'\s+(استان|شهر)$', '', s)
    return s.strip()


def city_of(slug, title, province_fa):
    """City name from the live page title, then from the slug."""
    t = re.sub(r'\s+', ' ', (title or '')).strip()
    for rx in (r' در ([^|]+?)\s*$', r' در ([^|]+?)\s*\|',
               r'^(?:خرید |فروش )?نوار تیپ ([^|]+?)\s*\|',
               r'^(?:خرید |فروش )?لوله نخی و تاشو ([^|]+?)\s*\|'):
        m = re.search(rx, t)
        if m:
            c = clean_city(m.group(1))
            if c and c not in ('استان',):
                return c
    s = urllib.parse.unquote(slug or '')
    s = re.sub(r'-(navar-tip-20cm|navar-tip|looleh-nakhi-tashoo|layflat|nakhi|tashoo)(-\d+)?$', '', s)
    s = re.sub(r'[-_]+', ' ', s)
    s = re.sub(r'[A-Za-z0-9]+', ' ', s)
    toks = [x for x in s.split() if x not in FILLER and x not in (province_fa or '').split()]
    return clean_city(' '.join(toks[:2])) or (province_fa or '')


def targets_from_queue():
    q = json.loads(QUEUE.read_text(encoding='utf-8'))
    return [{'key': i['key'], 'province': i['key'].split('/', 1)[0],
             'province_fa': i['province_fa'], 'city_fa': i['city_fa'], 'family': i['family'],
             'url': i['target_url'], 'hub_url': i.get('hub_url', ''), 'is_hub': i['family'] == 'hub',
             'site_title': i.get('site_title', '')}
            for i in q.get('items', []) if i.get('kind') != 'article']


# Explicit non-secret runtime fields. Rebuilding source metadata must not erase
# async ownership, retry controls or the reviewed-image provenance.
RUNTIME_FIELDS = (
    'failure_stage', 'last_error', 'next_retry_at', 'image_retry_at', 'preflight_recovery',
    '_image_stock_request', '_image_article_context', '_image_qa_feedback',
    '_image_rejections', 'image_generation', 'image_review', 'image_width',
    'image_height', 'image_alt', 'image_policy_retry', 'text_policy_retry',
    'editorial_image_required', 'editorial_image_decision', 'image_source', 'source_image_review',
)

def retained_runtime(prev, key):
    result = {field: copy.deepcopy(prev[field]) for field in RUNTIME_FIELDS if field in prev}
    # Repair previously stripped fields only from the matching authoritative
    # failed-draft checkpoint. Never resurrect a published or ambiguous record.
    if (prev.get('status') != 'failed' or prev.get('published')
        or prev.get('published_url') or prev.get('pid')):
        return result
    path = ROOT / 'artifacts/roya-backlink-queue/items' / (re.sub(r'[^A-Za-z0-9._-]+', '_', key) + '.json')
    try:
        record = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return result
    if (not isinstance(record, dict) or record.get('key') != key
        or record.get('status') != 'failed' or record.get('published')
        or record.get('published_url') or record.get('pid')
        or not prev.get('generated_at') or record.get('generated_at') != prev['generated_at']):
        return result
    for field in RUNTIME_FIELDS:
        if field not in result and field in record:
            result[field] = copy.deepcopy(record[field])
    if not result.get('last_error'):
        errors = record.get('qa', {}).get('errors', []) if isinstance(record.get('qa'), dict) else []
        if isinstance(errors, list) and errors and all(isinstance(error, str) for error in errors):
            result['last_error'] = '; '.join(errors)[:400]
    return result


def append_approved_articles(items, old, root):
    """Bounded opt-in supplement; never reset historical failures or receipts."""
    manifest = root / 'data/roya/approved-article-topics.json'
    if not manifest.exists():
        return items
    config = json.loads(manifest.read_text(encoding='utf-8'))
    keys = config.get('source_keys', [])
    if config.get('enabled') is not True:
        return items
    if not isinstance(keys, list) or len(keys) > 12 or len(set(keys)) != len(keys):
        raise ValueError('Invalid bounded Roya topic approval')
    inventory = json.loads((root / 'data/blog-site-article-targets.json').read_text(encoding='utf-8'))
    sources = {x['key']: x for x in inventory['targets']}
    seen = {urllib.parse.unquote(x['target_url']).rstrip('/') for x in items}
    for source_key in keys:
        src = sources.get(source_key, {})
        url = src.get('target_url', '')
        parsed = urllib.parse.urlsplit(url)
        if (src.get('kind') != 'article' or src.get('family') != 'tape20'
            or parsed.scheme != 'https' or parsed.netloc != 'navar-abyari.ir'
            or parsed.query or parsed.fragment or parsed.path in ('', '/')
            or not src.get('site_title')):
            raise ValueError('Unapproved Roya article source: ' + str(source_key))
        key = 'article-' + hashlib.sha256(source_key.encode()).hexdigest()[:16]
        canonical = urllib.parse.unquote(url).rstrip('/')
        if canonical in seen:
            continue
        prev = old.get(key)
        if prev is not None:
            if prev.get('kind') != 'article' or prev.get('target_url') != url:
                raise ValueError('Roya article identity conflict: ' + key)
            item = copy.deepcopy(prev)
        else:
            item = dict(key=key, kind='article', source_key=source_key,
                family='tape20', target_url=url, reference_url=url,
                site_title=src['site_title'], page_title=src['site_title'],
                topic=src['site_title'], province='technical', province_fa='', city_fa='',
                hub_url='', status='pending', attempts=0, title='', prepared_title='',
                slug='', generated_at=None, published=False, published_url=None,
                pid=None, image_url=None)
            from city_backlink_policy import title_candidates
            candidates = title_candidates(item, 'royablog', root)
            if not candidates:
                raise ValueError('No approved Roya article title: ' + key)
            item['prepared_title'] = candidates[0]
        items.append(item)
        seen.add(canonical)
    return items


def main():
    if TARGETS.exists():
        data = json.loads(TARGETS.read_text(encoding='utf-8'))
        targets = data['targets'] if isinstance(data, dict) else data
    else:
        targets = targets_from_queue()
        print('backlink-targets.json not found; refreshing from the existing queue')
    titles = {}
    if TITLES.exists():
        snap = json.loads(TITLES.read_text(encoding='utf-8'))
        titles = {t['url']: t for t in (snap['targets'] if isinstance(snap, dict) else snap)}
    old = {}
    if QUEUE.exists():
        q = json.loads(QUEUE.read_text(encoding='utf-8'))
        old = {i['key']: i for i in q.get('items', [])}
    items, counter, used_titles = [], 0, {}
    for t in targets:
        key = t['key']
        snap = titles.get(t['url'], {})
        page_title = snap.get('page_title', '') or t.get('site_title', '')
        family = 'hub' if t.get('is_hub') else family_of(page_title, t.get('url'))
        city = t.get('province_fa') if t.get('is_hub') else city_of(t.get('city_slug'), page_title, t.get('province_fa'))
        title = pick_title(family, city, t.get('province_fa', ''), key, used_titles)
        used_titles[title] = used_titles.get(title, 0) + 1
        prev = old.get(key, {})
        item = {'key': key, 'province': t['province'], 'province_fa': t['province_fa'], 'city_fa': city,
                'family': family, 'target_url': t['url'], 'hub_url': t.get('hub_url', ''),
                'site_title': prev.get('site_title', t.get('page_title', '')),
                'prepared_title': title, 'page_title': page_title,
                'status': prev.get('status', 'pending'), 'attempts': prev.get('attempts', 0),
                'title': prev.get('title', ''), 'slug': prev.get('slug', ''),
                'generated_at': prev.get('generated_at'), 'published': prev.get('published', False),
                'published_url': prev.get('published_url'), 'pid': prev.get('pid'),
                'image_url': prev.get('image_url')}
        item.update(retained_runtime(prev, key))
        items.append(item)
        counter += 1
    items = append_approved_articles(items, old, ROOT)
    from blog_city_priority import prioritize_queue
    ranked=prioritize_queue({'items':items},ROOT);items=ranked['items']
    QUEUE.write_text(json.dumps({'city_priority_policy':ranked.get('city_priority_policy'),'generated_at': __import__('datetime').datetime.now(
        __import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'navar-abyari.ir sitemaps', 'count': len(items), 'items': items},
        ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'queue built: {len(items)} items -> {QUEUE}')
    for i in items[:5]:
        print('  ', i['province_fa'], '|', i['city_fa'][:28], '|', i['family'], '|', i['prepared_title'][:62])
    return 0


if __name__ == '__main__':
    sys.exit(main())
