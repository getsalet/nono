"""Build Roya's crop + city + Search Console demand topic matrix.

Each topic targets ONE approved navar-abyari.ir crop article (found in GSC with
real impressions) plus the homepage keyword link. The city is only the reader
audience: no claim that the crop is grown there (no evidence registry needed,
no locality claim permitted). Run offline: python automation/build_roya_crop_city_topics.py GSC_Pages.csv
"""
import csv, hashlib, json, re, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/roya/crop-city-topics.json'
CROP_HINT = re.compile(r'هکتار|کاشت|کشت|بذر|برداشت|تناژ|عملکرد')
TEMPLATES = ('{topic}؛ راهنمای کشاورزان {city}',
             '{topic} برای کشاورزان {city}',
             'راهنمای کشاورزان {city}: {topic}')
ARTICLES, PER_ARTICLE = 40, 6


def short_topic(title):
    t = re.split(r'\s*[:|؛]\s*|\s+-\s+', title)[0]
    t = re.sub(r'\s+با\s+(?:استفاده\s+از\s+)?(?:نوار\s+تیپ|آبیاری\s+قطره[\u200c ]?ای)(?:\s+و\s+نوار\s+تیپ)?$', '', t)
    t = re.sub(r'\s+با\s+(?:سیستم[\u200c ]?(?:های)?\s+)?آبیاری\s+قطره[\u200c ]?ای.*$', '', t).strip()
    return t


def build(pages_csv, posts_txt=None, root=ROOT):
    inv = json.loads((root / 'data/blog-site-article-targets.json').read_text())['targets']
    by_url = {urllib.parse.unquote(x['target_url']).rstrip('/'): x for x in inv
              if x.get('kind') == 'article' and x.get('family') == 'tape20'}
    live = set()
    if posts_txt:
        live = {urllib.parse.unquote(l.strip()).rstrip('/') for l in open(posts_txt, encoding='utf-8') if l.strip()}
    rows = list(csv.reader(open(pages_csv, encoding='utf-8')))[1:]
    picked = []
    for r in sorted(rows, key=lambda r: -int(r[2])):
        url = urllib.parse.unquote(r[0]).rstrip('/')
        src = by_url.get(url)
        path = urllib.parse.urlsplit(url).path.strip('/')
        if not src and url in live and '/' not in path and 'لوله' not in path and url.startswith('https://navar-abyari.ir/'):
            src = {'key': 'gsc-' + hashlib.sha256(url.encode()).hexdigest()[:12],
                   'target_url': 'https://navar-abyari.ir/' + urllib.parse.quote(path) + '/', 'site_title': path.replace('-', ' ')}
        if src and CROP_HINT.search(src['site_title']) and src['key'] not in [p['source_key'] for p in picked]:
            picked.append({'source_key': src['key'], 'target_url': src['target_url'], 'site_title': src['site_title'],
                           'topic': short_topic(src['site_title']), 'gsc_clicks': int(r[1]), 'gsc_impressions': int(r[2])})
        if len(picked) == ARTICLES:
            break
    pri = json.loads((root / 'data/blog-city-priority.json').read_text())
    queue = json.loads((root / 'data/roya/backlink-queue.json').read_text())
    prov = {}
    for x in queue['items']:
        if x.get('kind') != 'article' and x.get('family') == 'tape20' and x.get('city_fa'):
            prov.setdefault(x['city_fa'], x.get('province_fa', ''))
    cities = [c for c in dict.fromkeys(pri['major_cities'] + pri['provincial_capitals'] + pri['important_county_cities'])
              if c in prov][:60]
    topics, used = [], set()
    for a_index, art in enumerate(picked):
        for n in range(PER_ARTICLE):
            city = cities[(a_index * PER_ARTICLE + n) % len(cities)]
            for k in range(len(TEMPLATES)):
                title = TEMPLATES[(a_index + n + k) % len(TEMPLATES)].format(topic=art['topic'], city=city)
                if len(title) <= 65 and title not in used:
                    break
            else:
                continue
            used.add(title)
            key = 'cropcity-' + hashlib.sha256((art['source_key'] + '|' + city).encode()).hexdigest()[:16]
            topics.append(dict(key=key, source_key=art['source_key'], target_url=art['target_url'],
                               site_title=art['site_title'], topic=art['topic'], audience_city=city,
                               audience_province=prov[city], matrix_title=title,
                               gsc_impressions=art['gsc_impressions']))
    return {'policy': 'roya-crop-city-gsc-v1', 'enabled': True, 'retire_unpublished_legacy': True,
            'note': 'City is reader audience only; no local cultivation claim. Links: crop article + homepage keyword.',
            'articles': picked, 'topics': topics}


if __name__ == '__main__':
    data = build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(len(data['articles']), 'articles', len(data['topics']), 'topics')
