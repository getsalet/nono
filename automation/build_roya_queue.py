#!/usr/bin/env python3
"""Build or refresh data/roya/backlink-queue.json from the sitemap target map.

Targets come from data/roya/backlink-targets.json (navar-abyari.ir sitemaps).
When data/roya/page-titles.json exists (a snapshot of each page <title>), city
names and product families are taken from the live pages, otherwise they are
derived from the URL slug. Each item carries a prepared Persian blog title so the
queue is ready to run. Existing statuses and generated titles are preserved.
"""
import json, re, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / 'data' / 'roya' / 'backlink-targets.json'
TITLES = ROOT / 'data' / 'roya' / 'page-titles.json'
QUEUE = ROOT / 'data' / 'roya' / 'backlink-queue.json'

FILLER = ['نوار', 'تیپ', 'خرید', 'قیمت', 'لوله', 'نخی', 'تاشو', 'آبیاری', 'سانتی', 'سانتیمتری',
          'متری', 'عمده', 'کارخانه', 'روز', 'لیست', 'و', 'در', 'برای', 'افزایش', 'فروش']
SHORT_TEMPLATES = {
    'tape20': 'خرید نوار تیپ ۲۰ سانتی در {city}',
    'hose': 'خرید لوله نخی و تاشو در {city}',
    'hub': 'نوار تیپ و لوله آبیاری در {city}',
}
TITLE_TEMPLATES = {
    'tape20': ['خرید نوار تیپ ۲۰ سانتی در {city} + راهنمای انتخاب',
               'نوار تیپ ۲۰ سانتی در {city}: راهنمای خرید و مشخصات فنی',
               'راهنمای خرید نوار تیپ ۲۰ سانتی برای کشاورزان {city}',
               'نوار تیپ ۲۰ سانتی در {city}؛ ضخامت، فاصله قطره‌چکان و مشاوره'],
    'hose': ['راهنمای خرید لوله نخی و تاشو در {city}',
             'لوله نخی و تاشو در {city}: انتخاب سایز، فشار و اتصالات',
             'خرید لوله نخی و تاشو در {city} + نکات نصب در مزرعه',
             'لوله نخی و تاشو در {city}؛ راهنمای انتخاب برای خطوط آبیاری'],
    'hub': ['نوار تیپ در {city}: راهنمای خرید برای کشاورزان استان',
            'راهنمای انتخاب نوار تیپ و لوله آبیاری در {city}',
            'خرید نوار تیپ و لوله نخی در {city} + مشاوره فنی'],
}


def family_of(text, url):
    low = (text or '') + ' ' + urllib.parse.unquote(url or '')
    if 'لوله' in low or 'looleh' in low or 'nakhi' in low or 'tashoo' in low or 'tasho' in low:
        return 'hose'
    if 'نوار' in low or 'navar' in low or 'tip' in low:
        return 'tape20'
    return 'tape20'


def city_of(slug, title, province_fa):
    m = re.search(r' در (.+?)\s*\|', title or '')
    if m:
        return m.group(1).strip()
    s = urllib.parse.unquote(slug or '')
    s = re.sub(r'-(navar-tip-20cm|navar-tip|looleh-nakhi-tashoo|layflat|nakhi|tashoo)(-\d+)?$', '', s)
    s = re.sub(r'[-_]+', ' ', s)
    s = re.sub(r'[A-Za-z0-9]+', ' ', s)
    toks = [t for t in s.split() if t not in FILLER and t not in (province_fa or '').split()]
    return ' '.join(toks[:2]).strip() or (province_fa or '')


def targets_from_queue():
    q = json.loads(QUEUE.read_text(encoding='utf-8'))
    return [{'key': i['key'], 'province': i['key'].split('/', 1)[0],
             'province_fa': i['province_fa'], 'city_fa': i['city_fa'], 'family': i['family'],
             'url': i['target_url'], 'hub_url': i.get('hub_url', ''), 'is_hub': i['family'] == 'hub'}
            for i in q.get('items', [])]


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
        page_title = snap.get('page_title', '')
        family = 'hub' if t.get('is_hub') else family_of(page_title, t.get('url'))
        city = t.get('province_fa') if t.get('is_hub') else city_of(t.get('city_slug'), page_title, t.get('province_fa'))
        variants = [t.format(city=city) for t in TITLE_TEMPLATES[family]]
        variants += [SHORT_TEMPLATES[family].format(city=city),
                     SHORT_TEMPLATES[family].format(city=' '.join(city.split()[:2]))]
        variants = [v for v in variants if len(v) <= 65]
        if not variants:
            variants = [SHORT_TEMPLATES[family].format(city=' '.join(city.split()[:2]))[:65]]
        title = next((v for v in variants if used_titles.get(v, 0) == 0), None)
        if title is None:
            base_title = variants[0]
            suffix = t.get('province_fa', '')
            title = base_title[:65]
            n = 2
            while used_titles.get(title, 0) > 0:
                tag = f' — {suffix}' if suffix else ''
                room = max(1, 64 - len(tag) - len(str(n)) - 1)
                title = (base_title[:room] + f' {n}' + tag)[:65]
                n += 1
        used_titles[title] = used_titles.get(title, 0) + 1
        prev = old.get(key, {})
        item = {'key': key, 'province': t['province'], 'province_fa': t['province_fa'], 'city_fa': city,
                'family': family, 'target_url': t['url'], 'hub_url': t.get('hub_url', ''),
                'prepared_title': title, 'page_title': page_title,
                'status': prev.get('status', 'pending'), 'attempts': prev.get('attempts', 0),
                'title': prev.get('title', ''), 'slug': prev.get('slug', ''),
                'generated_at': prev.get('generated_at'), 'published': prev.get('published', False),
                'published_url': prev.get('published_url')}
        items.append(item)
        counter += 1
    QUEUE.write_text(json.dumps({'generated_at': __import__('datetime').datetime.now(
        __import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'navar-abyari.ir sitemaps', 'count': len(items), 'items': items},
        ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'queue built: {len(items)} items -> {QUEUE}')
    for i in items[:5]:
        print('  ', i['province_fa'], '|', i['city_fa'][:28], '|', i['family'], '|', i['prepared_title'][:62])
    return 0


if __name__ == '__main__':
    sys.exit(main())
