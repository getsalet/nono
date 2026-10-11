#!/usr/bin/env python3
"""Roya blog (afp.royablog.ir) city backlink queue.

One item = one Persian city article (500-1000 words) for the AFP Roya blog that
links back to the matching navar-abyari.ir city landing page, its province hub and
the shop pages. Idempotent per city; artifacts, queue and state are committed.

Env: ROYA_COUNT ROYA_TARGET ROYA_DRY_RUN ROYA_RETRY_FAILED ROYA_MIN_WORDS
     ROYA_MAX_WORDS ROYA_MIN_LINKS ROYA_MAX_LINKS ROYA_ATTEMPTS
     AGNES_API_KEY AGNES_API_KEYS AGNES_API_BASE AGNES_MODEL
"""
import datetime, json, os, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
QUEUE_PATH = ROOT / 'data' / 'roya' / 'backlink-queue.json'
LINKS_PATH = ROOT / 'data' / 'roya' / 'link-library.json'
STATE_PATH = ROOT / 'state' / 'roya-backlink-progress.json'
ART = ROOT / 'artifacts' / 'roya-backlink-queue'
ITEMS = ART / 'items'
PUBLISH_QUEUE = ART / 'publish-queue.json'
STATUS_MD = ART / 'status.md'

BLOG = os.getenv('ROYA_BLOG_URL', 'https://afp.royablog.ir').rstrip('/')
COUNT = int(os.getenv('ROYA_COUNT', '3'))
ATTEMPTS = int(os.getenv('ROYA_ATTEMPTS', '3'))
MIN_WORDS = int(os.getenv('ROYA_MIN_WORDS', '500'))
MAX_WORDS = int(os.getenv('ROYA_MAX_WORDS', '1000'))
MIN_LINKS = int(os.getenv('ROYA_MIN_LINKS', '3'))
MAX_LINKS = int(os.getenv('ROYA_MAX_LINKS', '5'))
DRY_RUN = os.getenv('ROYA_DRY_RUN', '0') == '1'
RETRY_FAILED = os.getenv('ROYA_RETRY_FAILED', '0') == '1'
ONLY = os.getenv('ROYA_TARGET', '').strip()
BANNED = ['نمایندگی', 'موجود در انبار', 'ارسال رایگان', 'قیمت تومان', 'بهترین خاک',
          'خاک مناسب', 'اقلیم', 'آب و هوای', 'شوری خاک', 'گارانتی', 'تخفیف']
LATIN_OK = {'afp', 'navar', 'cm', 'mm', 'pe', 'uv', 'iso', 'drip'}
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


class Agnes:
    def __init__(self):
        raw = os.getenv('AGNES_API_KEYS') or os.getenv('AGNES_API_KEY') or ''
        self.AGNES_KEYS = [k.strip() for k in re.split(r'[,\s]+', raw) if k.strip()]
        self.AGNES_KEY = self.AGNES_KEYS[0] if self.AGNES_KEYS else ''
        self.AGNES_BASE = (os.getenv('AGNES_API_BASE') or os.getenv('AGNES_BASE')
                           or 'https://apihub.agnes-ai.com/v1').rstrip('/')
        self.AGNES_MODEL = os.getenv('AGNES_MODEL', 'agnes-2.5-flash')
        self._i = 0

    def next_agnes_key(self):
        if not self.AGNES_KEYS:
            return ''
        self._i = (self._i + 1) % len(self.AGNES_KEYS)
        return self.AGNES_KEYS[self._i]

    def fetch_json(self, url, headers, payload, timeout=180):
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                     headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8', 'replace'))


BASE = Agnes()
try:
    import agnes_json_client as agnes_client
except Exception:
    agnes_client = None


def parse_object(raw):
    if agnes_client:
        return agnes_client.parse_object(raw)
    text = str(raw or '').strip()
    text = re.sub(r'^```(?:json)?|```$', '', text, flags=re.M).strip()
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end <= start:
        raise ValueError('no JSON object in response')
    return json.loads(text[start:end + 1])


def agnes(prompt):
    if agnes_client:
        return agnes_client.call(BASE, prompt)
    if not BASE.AGNES_KEY:
        raise RuntimeError('AGNES_API_KEY is missing')
    last = None
    for attempt in range(1, ATTEMPTS + 2):
        payload = {'model': BASE.AGNES_MODEL,
                   'messages': [{'role': 'system', 'content': 'شما نویسنده و سئوکار ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط یک شیء JSON معتبر برگردانید؛ هیچ متن یا Markdown اضافه‌ای ننویسید.'},
                                {'role': 'user', 'content': prompt}],
                   'temperature': 0.45, 'max_tokens': 8000}
        try:
            data = BASE.fetch_json(BASE.AGNES_BASE + '/chat/completions',
                                   {'Authorization': 'Bearer ' + (BASE.next_agnes_key() or BASE.AGNES_KEY),
                                    'Content-Type': 'application/json',
                                    'User-Agent': 'roya-backlink-queue-v1'}, payload, timeout=180)
            return parse_object(data.get('choices', [{}])[0].get('message', {}).get('content', ''))
        except Exception as exc:
            last = exc
            print(f'agnes_retry attempt={attempt} error={str(exc)[:200]}', flush=True)
            time.sleep(min(20, 2 ** attempt))
    raise RuntimeError('Agnes JSON response invalid: ' + str(last))


def words(html):
    return len(re.findall(r'[\u0600-\u06FF]+', re.sub(r'<[^>]+>', ' ', html or '')))


def hrefs(html):
    return re.findall(r'<a\s[^>]*href=["\']([^"\']+)["\']', html or '', flags=re.I)


def approved_links(item, lib):
    fam = lib['families'].get(item.get('family', 'tape20'), lib['families']['tape20'])
    links = [
        {'url': item['target_url'], 'anchor': f"{fam['anchor']} {item['city_fa']}", 'role': 'city'},
        {'url': item['hub_url'], 'anchor': f"{fam['anchor']} {item['province_fa']}", 'role': 'province'},
        {'url': lib['shop']['url'], 'anchor': lib['shop']['anchor'], 'role': 'shop'},
    ]
    extra = lib['after_sales'] if item.get('family') == 'hose' else lib['faq']
    links.append({'url': extra['url'], 'anchor': extra['anchor'], 'role': 'extra'})
    if item.get('family') == 'hub':
        links.append({'url': lib['contact']['url'], 'anchor': lib['contact']['anchor'], 'role': 'contact'})
    seen, unique = set(), []
    for link in links:
        if link['url'] in seen:
            continue
        seen.add(link['url'])
        unique.append(link)
    return unique


def build_prompt(item, links):
    fam = item.get('family', 'tape20')
    product = 'نوار تیپ ۲۰ سانتی‌متری (قطره‌چکان ۲۰ سانتی)' if fam != 'hose' else 'لوله نخی و لوله تاشو'
    link_lines = '\n'.join(f"- {x['url']}  ←  لنگر پیشنهادی: {x['anchor']} ({x['role']})" for x in links)
    return f'''برای شهر {item['city_fa']} در استان {item['province_fa']} یک مقاله تازه، کاربردی و سئوشده فارسی درباره {product} بنویس.
این مقاله در وبلاگ آموزشی AFP (نشانی {BLOG}) منتشر می‌شود و هدف آن راهنمایی کشاورزان همان شهر است؛ در متن به‌طور طبیعی به لینک‌های زیر به سایت navar-abyari.ir اشاره کن.

لینک‌های مجاز (فقط و فقط همین‌ها، هیچ لینک دیگری اضافه نکن):
{link_lines}

قواعد محتوا:
1. طول متن بین {MIN_WORDS} و {MAX_WORDS} کلمه فارسی باشد (نه کمتر، نه بیشتر).
2. ساختار: یک پاراگراف مقدمه، سپس حداقل ۳ بخش با تگ h2 (و در صورت نیاز h3)، یک لیست ul یا ol برای نکات فنی، و در پایان بخش «سوالات متداول» با دقیقاً ۳ سوال که هر کدام در ساختار <details><summary>پرسش</summary>پاسخ</details> نوشته شود. بعد از بخش سوالات متداول هیچ بخش h2 یا h3 جدیدی نساز.
3. هر ۴ لینک بالا را با لنگر طبیعی و متفاوت در متن پخش کن؛ لنگر باید معنادار باشد (نه «اینجا کلیک کنید») و حداکثر یک بار برای هر URL.
4. هیچ قیمت، عدد ریالی/تومانی، تخفیف، موجودی، نمایندگی، زمان قطعی ارسال یا ادعای محلی درباره خاک، آب، شوری، اقلیم و فصل کشت شهر را ننویس؛ به جای آن بنویس که کارشناس AFP شرایط زمین را بررسی می‌کند و قیمت روز را استعلام بگیرد.
5. مشخصات فنی را فقط در حد عمومی بنویس: ضخامت ۱۷۵ تا ۲۰۰ میکرون، قطر لوله‌های آبیاری، فاصله قطره‌چکان، فشار کار، مقاومت در برابر UV. از ادعای عددی جدید و نادرست پرهیز کن.
6. متن فقط فارسی باشد؛ تنها واژه‌های لاتین مجاز: AFP، navar، cm، mm، PE، UV، ISO.
7. فقط HTML ساده: p، h2، h3، ul، ol، li، strong، a، details، summary، table. هیچ script، style، iframe، تصویر یا Markdown (بدون ``` و بدون **) استفاده نکن.
8. عنوان مقاله حداکثر ۶۵ کاراکتر، شامل نام شهر، و سئویی باشد. برای وبلاگ رویا بلاگ، عنوان را از الگوهایی مثل «خرید نوار تیپ ۲۰ سانتی در {item['city_fa']} + راهنمای انتخاب» یا «راهنمای خرید لوله نخی و تاشو در {item['city_fa']}» بساز و از تکرار عین عنوان سایت اصلی پرهیز کن.

خروجی را فقط به شکل این شیء JSON برگردان:
{{"title":"...","slug":"latin-lowercase-hyphenated-max-60","meta_title":"...","meta_description":"...","focus_keyword":"...","tags":["..."],"html":"...","links_used":["..."]}}'''


def qa(item, obj, links):
    errors = []
    html = obj.get('html', '') or ''
    title = (obj.get('title', '') or '').strip()
    n = words(html)
    if n < MIN_WORDS:
        errors.append(f'too short: {n} words < {MIN_WORDS}')
    if n > MAX_WORDS:
        errors.append(f'too long: {n} words > {MAX_WORDS}')
    allowed = {x['url'] for x in links}
    found = hrefs(html)
    bad = [h for h in found if h.split('#')[0] not in allowed]
    if bad:
        errors.append('unapproved links: ' + ', '.join(sorted(set(bad))[:4]))
    if len(found) < MIN_LINKS:
        errors.append(f'only {len(found)} links < {MIN_LINKS}')
    if len(found) > MAX_LINKS:
        errors.append(f'{len(found)} links > {MAX_LINKS}')
    if item['target_url'] not in found:
        errors.append('missing the city landing page link')
    if item['hub_url'] not in found:
        errors.append('missing the province hub link')
    if not title or len(title) > 65:
        errors.append(f'title length {len(title)} (max 65)')
    if item['city_fa'] and item['city_fa'] not in (title + ' ' + html):
        errors.append('city name missing from title/body')
    if len(re.findall(r'<details', html, flags=re.I)) < 3:
        errors.append('three FAQ details blocks required at end')
    faq_pos = max(html.find('<details'), 0)
    if faq_pos and html.lower().find('<h2', faq_pos) > -1:
        errors.append('no h2 allowed after the FAQ block')
    low = html + ' ' + title
    for term in BANNED:
        if term in low:
            errors.append(f'banned claim: {term}')
    if re.search(r'(قیمت|نرخ)[^<]{0,25}\d', low) or re.search(r'\d+\s*(تومان|ریال)', low):
        errors.append('numeric price claim')
    if re.search(r'```|<script|<style|style=|\*\*|!\[', html, flags=re.I):
        errors.append('markdown, script, style or image markup found')
    latin = {w.lower() for w in re.findall(r'[A-Za-z]+', re.sub(r'<[^>]+>', ' ', html))}
    stray = sorted(w for w in latin if w not in LATIN_OK)
    if stray:
        errors.append('unexpected latin words: ' + ', '.join(stray[:5]))
    slug = (obj.get('slug', '') or '').strip()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,59}', slug):
        errors.append('slug must be latin lowercase hyphenated (max 60)')
    if not (obj.get('meta_description') or '').strip():
        errors.append('meta_description is required')
    return errors, {'words': n, 'links': found, 'title': title, 'slug': slug}


def offline_sample(item, links):
    city, prov = item['city_fa'], item['province_fa']
    fam = item.get('family', 'tape20')
    product = 'نوار تیپ ۲۰ سانتی‌متری' if fam != 'hose' else 'لوله نخی و تاشو'
    filler = ('آبیاری قطره‌ای یکی از کارآمدترین روش‌ها برای کاهش هدررفت آب در مزرعه است و '
              'انتخاب درست تجهیزات، بیشترین اثر را روی هزینه و بازدهی دارد. ') * 22
    html = (f'<p>اگر به دنبال خرید {product} در {city} هستید، این راهنما کمک می‌کند '
            f'گزینه مناسب زمین خود را انتخاب کنید.</p>'
            f'<h2>چرا {product} برای کشاورزی {city} مناسب است</h2><p>{filler}</p>'
            f'<h2>نکات فنی انتخاب</h2><ul><li>ضخامت ۱۷۵ تا ۲۰۰ میکرون</li>'
            f'<li>فاصله قطره‌چکان ۲۰ سانتی‌متر</li><li>مقاومت در برابر UV</li></ul>'
            f'<h2>خرید و مشاوره</h2><p>برای استعلام قیمت روز و مشاوره فنی می‌توانید به '
            f'<a href="{item["target_url"]}">نوار تیپ {city}</a> و '
            f'<a href="{item["hub_url"]}">نوار تیپ {prov}</a> مراجعه کنید یا از '
            f'<a href="{links[2]["url"]}">{links[2]["anchor"]}</a> سفارش دهید.</p>'
            f'<h2>سوالات متداول</h2><details><summary>چه ضخامتی مناسب است؟</summary>'
            f'۱۷۵ تا ۲۰۰ میکرون برای کشت ردیفی رایج است.</details>'
            f'<details><summary>ارسال به {city} چگونه است؟</summary>هماهنگی بار توسط کارشناس انجام می‌شود.</details>'
            f'<details><summary>مشاوره فنی رایگان است؟</summary>بله، بررسی زمین و انتخاب محصول رایگان است.</details>')
    return {'title': f'خرید {product} در {city} + راهنمای انتخاب',
            'slug': f'navar-{item["province"]}-{re.sub(r"[^a-z0-9]+", "-", city.lower())[:20]}'.strip('-'),
            'meta_title': f'خرید {product} در {city}', 'meta_description': f'راهنمای خرید {product} در {city} و مشاوره فنی AFP.',
            'focus_keyword': f'{product} {city}', 'tags': [city, prov, product],
            'html': html, 'links_used': [x['url'] for x in links]}


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')


def pick(queue, state, count):
    pending = [i for i in queue['items']
               if i.get('status') == 'pending' or (RETRY_FAILED and i.get('status') == 'failed')]
    if ONLY:
        pending = [i for i in pending if i['key'] == ONLY] or [i for i in queue['items'] if i['key'] == ONLY]
    buckets, order = {}, []
    for item in pending:
        if item['province'] not in buckets:
            buckets[item['province']] = []
            order.append(item['province'])
    for item in pending:
        buckets[item['province']].append(item)
    start = int(state.get('rotation', 0)) % max(1, len(order)) if order else 0
    chosen = []
    while len(chosen) < count and order:
        progressed = False
        for offset in range(len(order)):
            prov = order[(start + offset) % len(order)]
            if buckets.get(prov):
                chosen.append(buckets[prov].pop(0))
                progressed = True
                if len(chosen) >= count:
                    break
        if not progressed:
            break
    state['rotation'] = (start + 1) % max(1, len(order)) if order else 0
    return chosen


def main():
    queue = load_json(QUEUE_PATH, {'items': []})
    if not queue.get('items'):
        print('queue is empty; run automation/build_roya_queue.py first', file=sys.stderr)
        return 1
    lib = load_json(LINKS_PATH, {})
    state = load_json(STATE_PATH, {})
    state.setdefault('completed_keys', [])
    state.setdefault('failed', {})
    in_progress = state.get('in_progress')
    if in_progress:
        for item in queue['items']:
            if item['key'] == in_progress and item.get('status') == 'processing':
                item['status'] = 'pending'
                item['last_error'] = 'recovered interrupted run'
        state['in_progress'] = None
    ITEMS.mkdir(parents=True, exist_ok=True)
    targets = pick(queue, state, COUNT)
    print(f'picked {len(targets)} target(s) of {len(queue["items"])} queued', flush=True)
    completed = []
    for item in targets:
        item['status'] = 'processing'
        item['attempts'] = int(item.get('attempts', 0)) + 1
        state['in_progress'] = item['key']
        links = approved_links(item, lib)
        errors, obj = ['not generated'], None
        for attempt in range(1, ATTEMPTS + 1):
            try:
                if DRY_RUN or not (BASE.AGNES_KEY or BASE.AGNES_KEYS):
                    obj = offline_sample(item, links)
                elif attempt == 1:
                    obj = agnes(build_prompt(item, links))
                else:
                    obj = agnes(build_prompt(item, links) + '\n\nپاسخ قبلی این ایرادها را داشت؛ همه را برطرف کن و JSON کامل بده: ' + '; '.join(errors))
            except Exception as exc:
                errors = ['agnes error: ' + str(exc)[:200]]
                print(f'{item["key"]} attempt={attempt} {errors[0]}', flush=True)
                continue
            errors, info = qa(item, obj, links)
            print(f'{item["key"]} attempt={attempt} words={info["words"]} links={len(info["links"])} errors={len(errors)}', flush=True)
            if not errors:
                break
        record = dict(item)
        record.update({'status': 'completed' if not errors else 'failed',
                       'generated_at': now(), 'qa': {'passed': not errors, 'errors': errors},
                       'post': obj, 'blog': BLOG})
        if not errors:
            item['status'] = 'completed'
            item['title'] = obj.get('title', item.get('title', ''))
            item['slug'] = obj.get('slug', '')
            item['generated_at'] = record['generated_at']
            item.pop('last_error', None)
            if item['key'] not in state['completed_keys']:
                state['completed_keys'].append(item['key'])
            state['failed'].pop(item['key'], None)
            completed.append(item['key'])
        else:
            item['status'] = 'failed'
            item['last_error'] = '; '.join(errors)[:400]
            state['failed'][item['key']] = item['last_error']
        save_json(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json'), record)
        state['in_progress'] = None
        save_json(QUEUE_PATH, queue)
        save_json(STATE_PATH, state)
    ready = [i for i in queue['items'] if i.get('status') == 'completed' and not i.get('published')]
    save_json(PUBLISH_QUEUE, {'generated_at': now(), 'blog': BLOG, 'count': len(ready),
                              'items': [{'key': i['key'], 'title': i.get('title', ''), 'slug': i.get('slug', ''),
                                         'target_url': i['target_url'], 'city_fa': i['city_fa'],
                                         'province_fa': i['province_fa'], 'family': i.get('family'),
                                         'item_file': str(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', i['key']) + '.json'))}
                                        for i in ready]})
    done, total = len(state['completed_keys']), len(queue['items'])
    STATUS_MD.write_text(
        '# صف بک‌لینک وبلاگ AFP\n\n'
        '| مورد | مقدار |\n|---|---:|\n'
        f'| کل صف | {total} |\n| تولیدشده | {done} |\n| ناموفق | {len(state["failed"])} |\n'
        f'| باقی‌مانده | {total - done} |\n| پیشرفت | {round(100 * done / max(1, total), 2)}% |\n'
        f'| آخرین اجرا | {now()} |\n| مدل | `{BASE.AGNES_MODEL}` |\n\n'
        'هر آیتم یک مقاله ۵۰۰ تا ۱۰۰۰ کلمه فارسی برای وبلاگ AFP است که به صفحه شهری متناظر در '
        'navar-abyari.ir، صفحه استان و فروشگاه لینک می‌دهد.\n', encoding='utf-8')
    print('completed: ' + (', '.join(completed) or 'none'), flush=True)
    return 0 if completed else 1


if __name__ == '__main__':
    sys.exit(main())
