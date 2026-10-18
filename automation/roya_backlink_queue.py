#!/usr/bin/env python3
"""Roya blog (afp.royablog.ir) city backlink queue.

One item = one Persian city article (500-1000 words) for the AFP Roya blog that
links to the matching navar-abyari.ir city landing page and one relevant primary
keyword destination (homepage for tape, shop for hose). Idempotent per city; artifacts, queue and state are committed.

Env: ROYA_COUNT ROYA_TARGET ROYA_DRY_RUN ROYA_RETRY_FAILED ROYA_MIN_WORDS
     ROYA_MAX_WORDS ROYA_MIN_LINKS ROYA_MAX_LINKS ROYA_ATTEMPTS
     AGNES_API_KEY AGNES_API_KEYS AGNES_API_BASE AGNES_MODEL
"""
import datetime, hashlib, html as html_lib, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
from content_originality import check_corpus

ROOT = HERE.parent
sys.path.insert(0, str(HERE))
QUEUE_PATH = ROOT / 'data' / 'roya' / 'backlink-queue.json'
LINKS_PATH = ROOT / 'data' / 'roya' / 'link-library.json'
STATE_PATH = ROOT / 'state' / 'roya-backlink-progress.json'
ART = ROOT / 'artifacts' / 'roya-backlink-queue'
ITEMS = ART / 'items'
PUBLISH_QUEUE = ART / 'publish-queue.json'
STATUS_MD = ART / 'status.md'
IMAGE_CACHE = ART / 'image-cache.json'

BLOG = os.getenv('ROYA_BLOG_URL', 'https://afp.royablog.ir').rstrip('/')
COUNT = int(os.getenv('ROYA_COUNT', '3'))
ATTEMPTS = int(os.getenv('ROYA_ATTEMPTS', '3'))
MIN_WORDS = int(os.getenv('ROYA_MIN_WORDS', '500'))
MAX_WORDS = int(os.getenv('ROYA_MAX_WORDS', '1000'))
MIN_LINKS = 2  # Exact user policy, not an overridable legacy range.
MAX_LINKS = 2
ROTATE_EVERY = max(1, int(os.getenv('AGNES_KEY_ROTATE_EVERY', '25')))
DRY_RUN = os.getenv('ROYA_DRY_RUN', '0') == '1'
RETRY_FAILED = os.getenv('ROYA_RETRY_FAILED', '0') == '1'
ONLY = os.getenv('ROYA_TARGET', '').strip()
BANNED = ['نمایندگی', 'موجود در انبار', 'ارسال رایگان', 'قیمت تومان', 'بهترین خاک',
          'خاک مناسب', 'اقلیم', 'آب و هوای', 'شوری خاک', 'گارانتی', 'تخفیف']
GENERIC_ANCHORS = {'اینجا', 'کلیک کنید', 'اینجا کلیک کنید', 'لینک', 'ادامه مطلب', 'مشاهده'}
LATIN_OK = {'afp', 'navar', 'cm', 'mm', 'pe', 'uv', 'iso', 'drip'}
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


class Agnes:
    def __init__(self):
        from agnes_key_pool import AgnesKeyPool
        self._key_pool = AgnesKeyPool()
        self.AGNES_KEYS = self._key_pool.keys
        self.AGNES_KEY = self.AGNES_KEYS[0] if self.AGNES_KEYS else ''
        self.AGNES_BASE = (os.getenv('AGNES_API_BASE') or os.getenv('AGNES_BASE')
                           or 'https://apihub.agnes-ai.com/v1').rstrip('/')
        self.AGNES_MODEL = os.getenv('AGNES_MODEL', 'agnes-2.5-flash')
        self._i = 0
        self.calls = 0

    def current_key(self):
        active=[k for k in self.AGNES_KEYS if k not in self._key_pool._disabled]
        return active[self._i % len(active)] if active else self._key_pool.next()

    def rotate_key(self):
        self._i += 1
        return self.current_key()

    def key_for_call(self):
        if self.calls and self.calls % ROTATE_EVERY == 0:
            self.rotate_key()
        self.calls += 1
        return self.current_key()

    def next_agnes_key(self):
        return self.key_for_call()

    def fetch_json(self, url, headers, payload, timeout=180):
        return self._key_pool.fetch_json(url, headers, payload, timeout)


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


def agnes(prompt,temperature=None):
    if agnes_client:
        return agnes_client.call(BASE, prompt, temperature=temperature)
    if not BASE.AGNES_KEY:
        raise RuntimeError('AGNES_API_KEY is missing')
    last = None
    for attempt in range(1, ATTEMPTS + 2):
        payload = {'model': BASE.AGNES_MODEL,
                   'messages': [{'role': 'system', 'content': 'شما نویسنده و سئوکار ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط یک شیء JSON معتبر برگردانید؛ هیچ متن یا Markdown اضافه‌ای ننویسید.'},
                                {'role': 'user', 'content': prompt}],
                   'temperature': 0.45 if temperature is None else temperature, 'max_tokens': 8000}
        try:
            data = BASE.fetch_json(BASE.AGNES_BASE + '/chat/completions',
                                   {'Authorization': 'Bearer ' + (BASE.key_for_call() or BASE.AGNES_KEY),
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


def anchor_pairs(html):
    return [(m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2)).strip())
            for m in re.finditer(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html or '', flags=re.I | re.S)]


def hrefs(html):
    return re.findall(r'<a\s[^>]*href=["\']([^"\']+)["\']', html or '', flags=re.I)


def approved_links(item, lib):
    fam = lib['families'].get(item.get('family', 'tape20'), lib['families']['tape20'])
    site_title = re.split(r'\s*\|\s*', item.get('site_title') or '')[0].strip()
    city_anchor = site_title if len(site_title) >= 8 else f"{fam['anchor']} {item['city_fa']}"
    city = {'url': item['target_url'], 'anchor': city_anchor,
            'title': site_title or city_anchor, 'role': 'city'}
    if item.get('family', 'tape20') in ('tape20', 'hub'):
        anchors = ('نوار تیپ', 'نوار آبیاری', 'نوار تیپ AFP',
                   'نوار آبیاری قطره‌ای AFP', 'آبگستر فرا پارسیان', 'وب‌سایت AFP')
        bucket = int(hashlib.sha256(item['key'].encode('utf-8')).hexdigest()[:8], 16) % len(anchors)
        primary = {'url': lib['home']['url'], 'anchor': anchors[bucket],
                   'title': 'نوار تیپ | خرید نوار آبیاری قطره‌ای AFP', 'role': 'home'}
    else:
        primary = {'url': lib['shop']['url'], 'anchor': 'لوله نخی و تاشو AFP',
                   'title': 'بررسی لوله‌های انتقال آب AFP', 'role': 'shop'}
    if city['url'].rstrip('/') == primary['url'].rstrip('/'):
        raise RuntimeError('Related target and primary keyword destination must differ')
    return [city, primary]


def assign_roya_titles(queue, root=None):
    """Assign independent titles only to ungenerated items; preserve old posts."""
    # Lazy import: city policy imports Roya's image/link helpers at module load.
    from city_backlink_policy import title_candidates, matrix_ready
    root = root or ROOT
    if not matrix_ready(root):
        raise RuntimeError('Independent Roya title matrix awaiting approval')
    used = {x.get('title') for x in queue['items'] if x.get('title')}
    for item in queue['items']:
        if item.get('published') or item.get('status') not in ('pending', 'failed', 'needs_title_review'):
            continue
        pool = title_candidates(item, 'royablog', root)
        previous = item.get('assigned_title')
        title = previous if previous in pool and previous not in used else next((t for t in pool if t not in used), None)
        if title:
            item['assigned_title'] = title
            used.add(title)
            if item.get('status') == 'needs_title_review':
                item['status'] = 'pending'
                item.pop('last_error', None)
        else:
            item['status'] = 'needs_title_review'
            item['last_error'] = 'No unique meaningful Roya matrix title; manual review required'
    queue['title_matrix'] = 'data/blog-city-title-matrix.json'
    return queue


def build_prompt(item, links):
    fam = item.get('family', 'tape20')
    product = 'نوار تیپ ۲۰ سانتی‌متری (قطره‌چکان ۲۰ سانتی)' if fam != 'hose' else 'لوله نخی و لوله تاشو'
    technical = ('لوله نخی و تاشو مسیر انتقال آب هستند؛ لوله نخی را نوار تیپ یا لوله دارای قطره‌چکان معرفی نکن. برای خود لوله نخی «قطره‌چکان‌گذاری» ننویس؛ اتصال به شبکه توزیع یا نوارهای فرعی را جداگانه توضیح بده. مشخصات قطر، فشار و اتصالات را فقط با برگه فنی همان مدل مطرح کن؛ ضخامت یا فاصله قطره‌چکان نوار تیپ را به لوله انتقال آب نسبت نده.' if fam == 'hose' else 'مشخصات فاصله خروجی، دبی، ضخامت و فشار را برای همان مدل از برگه فنی بخواه؛ بدون مرجع، مقدار عددی تجویز نکن و قابلیت جبران فشار را به همه نوارها نسبت نده.')
    link_lines = '\n'.join(
        f"- href=\"AFP_LINK_{index}\"\n  عنوان پست مقصد در سایت: {x.get('title', '')}\n  لنگر پیشنهادی: {x['anchor']} ({x['role']})"
        for index, x in enumerate(links, 1))
    return f'''برای شهر {item['city_fa']} در استان {item['province_fa']} یک مقاله تازه، کاربردی و سئوشده فارسی درباره {product} بنویس.
این مقاله در وبلاگ آموزشی AFP منتشر می‌شود و هدف آن راهنمایی کشاورزان همان شهر است؛ در متن به‌طور طبیعی از لینک‌های زیر با لنگر فارسی تعیین‌شده استفاده کن. نام دامنه یا نشانی لاتین را در متن قابل‌نمایش ننویس؛ نشانی فقط در href قرار می‌گیرد. برای اشاره متنی از «وب‌سایت AFP» استفاده کن.

شناسه‌های لینک مجاز (فقط همین شناسه‌ها را عیناً در href بگذار؛ برنامه مقصد تأییدشده را جایگزین می‌کند. هیچ URL واقعی، لینک به وبلاگ یا شناسه دیگری نساز):
{link_lines}

قواعد محتوا:
1. طول متن بین {MIN_WORDS} و {MAX_WORDS} کلمه فارسی باشد (نه کمتر، نه بیشتر).
2. ساختار: یک پاراگراف مقدمه، سپس حداقل ۳ بخش با تگ h2 (و در صورت نیاز h3)، یک لیست ul یا ol برای نکات فنی، و در پایان بخش «سوالات متداول» با دقیقاً ۳ سوال که هر کدام در ساختار <details><summary>پرسش</summary>پاسخ</details> نوشته شود. بعد از بخش سوالات متداول هیچ بخش h2 یا h3 جدیدی نساز.
3. دقیقاً دو لینک در بدنه بیاور: لینک کلیدواژه اصلی و لینک صفحه شهری متناظر. لینک استان، تماس یا خدمات اضافه نکن. هر لینک بالا را با لنگر طبیعی در متن پخش کن؛ لنگر لینک صفحه شهری باید همان «عنوان پست مقصد» یا نزدیک‌ترین عبارت طبیعی به آن باشد (مثلاً «خرید نوار تیپ ۲۰ سانتی در قندمان») تا بک‌لینک معنادار شود. لنگر باید شامل نام شهر باشد، معنادار باشد (نه «اینجا کلیک کنید») و برای هر URL حداکثر یک بار بیاید. در متن به موضوع همان پست مقصد اشاره کن تا لینک زمینه‌دار شود.
4. هیچ قیمت، عدد ریالی/تومانی، تخفیف، موجودی، نمایندگی، زمان قطعی ارسال یا ادعای محلی درباره خاک، آب، شوری، اقلیم و فصل کشت شهر را ننویس؛ به جای آن بنویس که کارشناس AFP شرایط زمین را بررسی می‌کند و قیمت روز را استعلام بگیرد.
5. {technical}
5الف. منبع برگه فنی در این ورودی ارائه نشده است: جنس PE، افزودنی یا مقاومت UV، تفاوت قطعی انعطاف/هزینه/سرعت نصب لوله نخی و تاشو را ادعا نکن. فقط بررسی مشخصات همان مدل را توصیه کن. هواگیری را به عبور لوله از نقاط کم‌ارتفاع نسبت نده؛ طراحی نقاط هواگیری و تخلیه باید با بررسی اختلاف ارتفاع و نظر متخصص انجام شود. مقدمه درباره کشت محصول در این شهر مشروط باشد: «اگر در ... ... کشت می‌کنید»؛ وجود مزارع آن محصول را قطعی نگو.
6. متن فقط فارسی باشد؛ تنها واژه‌های لاتین مجاز: AFP، navar، cm، mm، PE، UV، ISO.
7. فقط HTML ساده: p، h2، h3، ul، ol، li، strong، a، details، summary، table. هیچ script، style، iframe، تصویر یا Markdown (بدون ``` و بدون **) استفاده نکن.
8. اگر لینک با نقش home در فهرست مجاز هست، آن را فقط یک بار در یک پاراگراف توضیحی مرتبط با انتخاب تجهیزات نوار تیپ بیاور؛ متن لنگر همین لینک را دقیقاً همان «لنگر پیشنهادی» آن بنویس. عبارت مستقل «نوار تیپ» یا «نوار آبیاری» فقط به صفحه نخست اشاره کند؛ لینک شهر همچنان نام شهر و زمینه محصول خود را داشته باشد؛ لینک استان اضافه نکن. دو کلیدواژه اصلی را کنار هم به شکل دو لینک تکراری به صفحه نخست نچین. لینک صفحه نخست را در سوالات متداول یا یک پاراگراف صرفاً تبلیغاتی قرار نده. اگر لینک home در فهرست نیست، آن را اضافه نکن و کلمات نوار تیپ را به متن مربوط به لوله تحمیل نکن.
9. اولویت مقاله پاسخ دقیق به نیاز خواننده است، نه تکرار کلیدواژه یا افزایش تعداد بک‌لینک. بدون مقدمه و جمله تبلیغاتی قالبی، توصیه کاربردی مرتبط با موضوع بده.
10. عنوان دقیق از ماتریس مستقل رویابلاگ: {item['assigned_title']}. آن را بدون تغییر استفاده کن؛ حداکثر ۶۵ کاراکتر است و نام شهر را دارد.
موضوع و مسئله فنی عنوان باید از مقدمه در متن واقعی حاضر باشد؛ مقاله قیمت و خرید عمومی را فقط با تعویض عنوان تحویل نده.
11. اگر عنوان نام محصول کشت ردیفی دارد، متن، چک‌لیست و FAQ به کاربرد آبیاری همان محصول پاسخ دهند. مثال‌ها مشروط باشند؛ رایج بودن کشت آن در شهر یا تناسب قطعی با خاک و اقلیم را ادعا نکن. فاصله، فشار، دبی و نیاز آبی را بدون مرجع معتبر به محصول نسبت نده.
12. زاویه اختصاصی رویا: برنامه‌ریزی آبیاری، نیازسنجی مزرعه، تناسب تجهیزات و تصمیم‌های پیش از اجرا. مقدمه، مثال، چک‌لیست و FAQ را از صفر و با همین زاویه بنویس؛ متن فارسی‌بلاگ، رز‌بلاگ و سایت اصلی را کپی یا بازنویسی سطحی نکن. نام شهر فقط زمینه مخاطب است، نه شاهد ویژگی‌های اقلیم یا خاک.

نام شهر «{item['city_fa']}»، نام استان «{item['province_fa']}» و واژه‌های عنوان را عیناً با حروف فارسی کپی کن؛ بخشی از کلمه فارسی را با حرف لاتین جایگزین نکن.
پیش از خروجی، همه hrefها را بررسی کن: هر شناسه بالا دقیقاً یک بار در متن و به همان شکل AFP_LINK_عدد بیاید؛ شناسه نباید متن قابل‌نمایش مقاله باشد. links_used هم همین شناسه‌ها را داشته باشد.
این عبارت‌ها حتی در جمله منفی یا توصیه به بررسی هم در خروجی نیایند: {"، ".join(BANNED)}. از عبارت‌های خنثی مثل «شرایط زمین» استفاده کن. هیچ کلمه انگلیسی خارج از فهرست مجاز ننویس.
خروجی را فقط به شکل این شیء JSON برگردان:
{{"title":"...","slug":"latin-lowercase-hyphenated-max-60","meta_title":"...","meta_description":"...","focus_keyword":"...","tags":["..."],"html":"...","links_used":["..."]}}'''


def resolve_link_tokens(obj, links):
    """Resolve exact href tokens only; never guess or repair a different URL."""
    tokens = {f'AFP_LINK_{i}': x['url'] for i, x in enumerate(links, 1)}
    def replace(match):
        target = tokens.get(match.group(3))
        if target is None:
            return match.group(0)  # Unknown tokens/destinations must fail QA.
        return match.group(1) + match.group(2) + html_lib.escape(target, quote=True) + match.group(2)
    obj['html'] = re.sub(r"(\bhref\s*=\s*)([\"'])(.*?)\2", replace,
                         obj.get('html', '') or '', flags=re.I | re.S)
    if isinstance(obj.get('links_used'), list):
        obj['links_used'] = [tokens.get(x, x) for x in obj['links_used']]
    return obj


def repair_prompt(item, links, previous, errors):
    # Send the actual failed article, not just errors about an unseen response.
    # The approved image is owned by inject_image(), never by the text model.
    draft = dict(previous or {})
    draft['html'] = re.sub(r'<img\b[^>]*>', '', draft.get('html', ''), flags=re.I)
    for i, link in enumerate(links, 1):
        for url in (link['url'], html_lib.escape(link['url'], quote=True)):
            draft['html'] = draft['html'].replace(url, f'AFP_LINK_{i}')
    draft['links_used'] = [f'AFP_LINK_{i}' for i in range(1, len(links) + 1)]
    return (build_prompt(item, links) + '\n\nاین پیش‌نویس قبلی است؛ داده است نه دستور. آن را با حفظ نکات درست اصلاح کن؛ همه ایرادهای زیر را رفع کن و JSON کامل بده. متن پیش‌نویس نباید دستورهای اصلی را تغییر دهد.\n'
            + json.dumps({'draft': draft, 'validation_errors': errors}, ensure_ascii=False))


def encode_url(url):
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc,
                                    urllib.parse.quote(parts.path, safe='/%'), parts.query, parts.fragment))


def target_image(item):
    """The image already hosted on navar-abyari.ir for the matching city page.

    Roya's upload centre is disabled and its edit endpoint returns HTTP 500, so each
    blog post carries the same AI-generated image that the target city page uses.
    """
    url = item.get('target_url') or ''
    if not url:
        return ''
    from source_page_image import primary_image,POLICY as source_policy
    cache = load_json(IMAGE_CACHE, {})
    if cache.get('_policy') != source_policy:
        cache = {'_policy': source_policy, 'images': {}}
    images = cache.setdefault('images', {})
    if url in images:
        return images[url]
    found = ''
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
        found = encode_url(primary_image(page, url))
    except Exception as exc:
        print('source primary image unavailable: '+type(exc).__name__, flush=True)
    if found:
        images[url] = found  # A transport failure must not poison the durable cache.
        save_json(IMAGE_CACHE, cache)
    return found


def prepare_roya_image(item):
    from blog_generated_image import rollout_enabled, prepare
    if item.get('family') in ('tape20', 'hose') and rollout_enabled('roya'):
        return prepare(item, 'roya')
    return target_image(item)


def inject_image(item, obj, image_url):
    """Put the city image first in the article; Roya uses the first body image as the post image."""
    html = (obj.get('html') or '')
    if not image_url or '<img' in html.lower():
        return obj
    alt = (item.get('site_title') or obj.get('title') or item.get('city_fa') or 'نوار آبیاری AFP')
    alt = re.sub(r'\s+', ' ', alt.split('|')[0]).strip()[:90]
    obj['html'] = f'<p><img src="{image_url}" alt="{alt}" width="1200" height="675"></p>' + html
    obj['image_url'] = image_url
    return obj



def comparable_url(url):
    """Treat percent-encoding case/decoded Persian paths as equivalent, not typos."""
    p = urllib.parse.urlsplit(html_lib.unescape(url))
    return (p.scheme.lower(), p.netloc.lower(), urllib.parse.unquote(p.path).rstrip('/'), p.query)


def normalize_approved_hrefs(obj, links):
    """Canonicalize only URLs equivalent to an already-approved destination."""
    approved = {comparable_url(x['url']): x['url'] for x in links}
    def replace(match):
        target = approved.get(comparable_url(match.group(3)))
        if not target:
            return match.group(0)  # Wrong destinations must still fail QA.
        return match.group(1) + match.group(2) + html_lib.escape(target, quote=True) + match.group(2)
    obj['html'] = re.sub(r"(\bhref\s*=\s*)([\"'])(.*?)\2", replace, obj.get('html', '') or '', flags=re.I | re.S)
    return obj



def has_numeric_price(markup):
    """Product dimensions in price questions are not monetary amounts."""
    text = html_lib.unescape(re.sub(r'<[^>]+>', ' ', markup or ''))
    amount = r'[0-9۰-۹٠-٩]+(?:[.,٬٫][0-9۰-۹٠-٩]+)*'
    if re.search(amount + r'\s*(?:(?:هزار|میلیون|میلیارد)\s*)?(?:تومان|ریال)', text):
        return True
    quantity = amount + r'(?:\s*(?:تا|الی|[-–])\s*' + amount + r')?'
    units = r'(?:سانتی(?:[\s‌-]*متر(?:ی)?)?|میلی[\s‌-]*متر(?:ی)?|میکرون|متر(?:ی)?|اینچ(?:ی)?|بار|درصد|لیتر(?:ی)?|cm|mm)'
    text = re.sub(quantity + r'\s*' + units, ' ', text, flags=re.I)
    return bool(re.search(r'(?:قیمت|نرخ)[^.!؟<]{0,25}' + amount, text))

def product_semantics_errors(item,markup):
    plain = html_lib.unescape(re.sub(r'<[^>]+>', ' ', markup or ''))
    errors = []
    if '\ufffd' in (markup or ''):
        errors.append('Replacement characters indicate corrupted article text')
    if item.get('family') == 'hose':
        if re.search(r'لوله[\s‌]+نخی[\s‌]*[（(][\s‌]*نوار[\s‌]+تیپ', plain):
            errors.append('Layflat transfer hose must not be defined as drip tape')
        if re.search(r'قطره[\s‌-]*چکان[\s‌-]*گذاری[\s‌]+لوله', plain):
            errors.append('Transfer hose must not be described as an emitter-installation line')
        # No model-specific datasheet is supplied to this generator. Reject these
        # unsupported categorical claims rather than inventing a material spec.
        if re.search(r'(?:جنس|ساخته|تولید)[^.!؟]{0,90}\bPE\b|(?:افزودنی|مقاوم|مقاومت)[^.!؟]{0,60}\bUV\b|\bUV\b[^.!؟]{0,60}(?:مقاوم|مقاومت)',plain):
            errors.append('Unsupported hose material or UV claim without model datasheet')
        if re.search(r'(?:کم[\s‌-]*ارتفاع|پایین[\s‌-]*دست)[^.!؟]{0,100}هواگیری|هواگیری[^.!؟]{0,100}(?:کم[\s‌-]*ارتفاع|پایین[\s‌-]*دست)',plain):
            errors.append('Air release must not be attributed to routing through low points')
        if re.search(r'لوله[\s‌]+(?:نخی|تاشو)[^.!؟]{0,50}(?:سریع[\s‌-]*تر|به[\s‌-]*صرفه[\s‌-]*تر|انعطاف[\s‌]+بیشتر|نصب[\s‌]+سریع)',plain):
            errors.append('Unsupported categorical comparison of transfer hose types')
    return errors


def qa(item, obj, links, root=None, require_image=True):
    errors = []
    # Encoding differences are not invalid destinations. Normalize only approved equivalents.
    html = normalize_approved_hrefs(obj, links).get('html', '') or ''
    title = (obj.get('title', '') or '').strip()
    if item.get('assigned_title') and title != item['assigned_title']:
        errors.append('title differs from assigned independent Roya matrix')
    for crop in load_json(Path(root or ROOT) / 'data/blog-city-title-matrix.json', {}).get('row_crops', []):
        if item.get('assigned_title') and crop in title and crop not in re.sub(r'<[^>]+>', ' ', html):
            errors.append('Title crop must be addressed in article body')
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
    if len(links) != 2 or len(allowed) != 2 or len(found) != 2 or set(found) != allowed:
        errors.append('Exactly two distinct approved contextual destinations, each once')
    if not title or len(title) > 65:
        errors.append(f'title length {len(title)} (max 65)')
    pairs = anchor_pairs(html)
    # Defragment and normalize root trailing slash to catch repeated homepage links.
    normalized = [urllib.parse.urldefrag(h)[0].rstrip('/') for h in found]
    if len(normalized) != len(set(normalized)):
        errors.append('each destination URL may be linked at most once')
    home_url = 'https://navar-abyari.ir'
    home_pairs = [(h, a) for h, a in pairs if urllib.parse.urldefrag(h)[0].rstrip('/') == home_url]
    if len(home_pairs) > 1:
        errors.append('homepage may be linked at most once')
    expected_home = next((x for x in links if x.get('role') == 'home'), None)
    if expected_home:
        if len(home_pairs) != 1:
            errors.append('one contextual homepage link is required for this tape article')
        elif home_pairs[0][1] != expected_home['anchor']:
            errors.append('homepage anchor must use the assigned natural variant')
    for destination, anchor in pairs:
        plain = re.sub(r'\s+', ' ', anchor.replace('ي', 'ی').replace('ك', 'ک').replace('\u200c', ' ')).strip()
        if plain in ('نوار تیپ', 'نوار آبیاری') and urllib.parse.urldefrag(destination)[0].rstrip('/') != home_url:
            errors.append('standalone primary keyword anchors must point to the homepage')
    city_anchor = next((a for h, a in pairs if h.split('#')[0] == item['target_url']), '')
    if not city_anchor:
        errors.append('city backlink anchor text missing')
    else:
        if len(city_anchor) < 8:
            errors.append('city backlink anchor too short')
        if item['city_fa'] and item['city_fa'] not in city_anchor:
            errors.append('city backlink anchor must contain the city name')
    if any(a in GENERIC_ANCHORS for _, a in pairs):
        errors.append('generic anchor text found')
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
    if has_numeric_price(low):
        errors.append('numeric price claim')
    if re.search(r'```|<script|<style|style=|\*\*|!\[', html, flags=re.I):
        errors.append('markdown, script, style or image markup found')
    if require_image:
        imgs = re.findall(r'<img\b[^>]*>', html, flags=re.I)
        if len(imgs) != 1:
            errors.append(f'exactly one post image is required, found {len(imgs)}')
        else:
            src = re.search(r'src=["\']([^"\']+)["\']', imgs[0], flags=re.I)
            alt = re.search(r'alt=["\']([^"\']+)["\']', imgs[0], flags=re.I)
            from blog_image_gate import approved_url, validate_record
            if not src or not approved_url(src.group(1)):
                errors.append('post image must use an approved source or immutable generated asset URL')
            if item.get('image_generation'):
                errors.extend(validate_record(item))
                if src and src.group(1) != item.get('image_url'):
                    errors.append('generated post image differs from reviewed image')
            if not alt or len(alt.group(1).strip()) < 4:
                errors.append('post image needs a descriptive alt text')
            if html.strip().find(imgs[0]) > 30:
                errors.append('post image must be the first element of the article')
    latin = {w.lower() for w in re.findall(r'[A-Za-z]+', re.sub(r'<[^>]+>', ' ', html))}
    stray = sorted(w for w in latin if w not in LATIN_OK)
    if stray:
        errors.append('unexpected latin words: ' + ', '.join(stray[:5]))
    slug = (obj.get('slug', '') or '').strip()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,59}', slug):
        errors.append('slug must be latin lowercase hyphenated (max 60)')
    if not (obj.get('meta_description') or '').strip():
        errors.append('meta_description is required')
    if require_image and item.get('family') in ('tape20', 'hose'):
        from blog_image_gate import generated_record_errors
        errors.extend(generated_record_errors(item, 'roya', root))
    errors.extend(product_semantics_errors(item, html))
    errors.extend(check_corpus(root or ROOT, 'roya', item['key'], html))
    return errors, {'words': n, 'links': found, 'title': title, 'slug': slug,
                    'city_anchor': city_anchor, 'key_index': BASE._i, 'agnes_calls': BASE.calls}


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
            + ' و '.join(f'<a href="{x["url"]}">{x["anchor"]}</a>' for x in links) + ' مراجعه کنید.</p>' +
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


DOMAIN_REPAIR_POLICY = 'visible-domain-anchor-v1'

def domain_repair_draft(record, item, current=None):
    """One bounded repair of the known contradictory visible-domain instruction."""
    if (item.get('status') != 'failed' or item.get('published')
        or item.get('published_url') or item.get('pid')
        or item.get('text_policy_retry') == DOMAIN_REPAIR_POLICY
        or record.get('text_policy_retry') == DOMAIN_REPAIR_POLICY
        or item.get('failure_stage') != 'text_validation'
        or record.get('status') != 'failed' or record.get('published')
        or record.get('published_url') or record.get('pid')
        or record.get('failure_stage') != 'text_validation'
        or record.get('key') != item.get('key') or not item.get('generated_at')
        or record.get('generated_at') != item['generated_at']):
        return None
    if item.get('next_retry_at'):
        try:
            due = datetime.datetime.fromisoformat(item['next_retry_at'].replace('Z', '+00:00'))
            if due.tzinfo is None or due > (current or datetime.datetime.now(datetime.timezone.utc)):
                return None
        except (ValueError, TypeError, AttributeError):
            return None
    errors = record.get('qa', {}).get('errors', []) if isinstance(record.get('qa'), dict) else []
    allowed = {'unexpected latin words: abyari', 'unexpected latin words: abyari, ir'}
    if not errors or any(not isinstance(e, str) or e not in allowed for e in errors):
        return None
    post = record.get('post')
    if not isinstance(post, dict) or not all(isinstance(post.get(k), str) and post[k].strip() for k in ('title', 'slug', 'html')):
        return None
    visible = re.sub(r'<[^>]+>', ' ', post['html'])
    if not re.search(r'navar\s*-\s*abyari(?:\s*\.\s*ir)?', visible, re.I):
        return None
    from blog_draft_preflight import clean
    return clean(post)  # Not a QA pass; corrected prompt + full text/image QA still run.


def pick(queue, state, count):
    from blog_image_draft_recovery import capacity_retry_due,recover
    pending=[]
    for item in queue['items']:
        if item.get('published') or item.get('status') not in ('pending','failed'):continue
        eligible=item.get('status')=='pending' or RETRY_FAILED or (os.getenv('BLOG_READY_IMAGE_HANDOFF')=='1' and bool(ONLY) and item['key']==ONLY)
        if not eligible and capacity_retry_due(item):
            path=ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json')
            eligible=recover(load_json(path,{})) is not None
        if not eligible and item.get('failure_stage')=='text_validation':
            path=ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json')
            eligible=domain_repair_draft(load_json(path,{}),item) is not None
        if eligible:pending.append(item)
    if ONLY:
        pending = [i for i in pending if i['key'] == ONLY]
    from blog_generated_image import family_enabled
    pending=[i for i in pending if family_enabled(i,ROOT)]
    from blog_image_stock import awaiting
    pending=[i for i in pending if not awaiting(i,ROOT)]
    from blog_image_stock_preflight import eligible
    pending=eligible(pending,'roya',ROOT)
    from blog_city_priority import enabled as city_priority_enabled,ordered as city_priority_ordered
    if city_priority_enabled(ROOT):return city_priority_ordered(pending,ROOT)[:count]
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
    from blog_image_runtime_control import generation_paused
    if generation_paused(ROOT):
        print('Generation intentionally paused by user control; no text API, image API or new ready item.');return 0
    if DRY_RUN:
        print('Configuration check only; offline samples are not queued for publication.')
        return 0
    if not (BASE.AGNES_KEY or BASE.AGNES_KEYS):
        raise RuntimeError('Agnes API key required; refusing fake publishable sample fallback')
    ready_handoff=os.getenv('BLOG_READY_IMAGE_HANDOFF')=='1'
    if ready_handoff and not ONLY:raise RuntimeError('Explicit saved article target required for cached-only handoff')
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
    assign_roya_titles(queue)
    from blog_city_priority import prioritize_queue
    prioritize_queue(queue,ROOT)
    save_json(QUEUE_PATH, queue)
    targets = pick(queue, state, 1 if ready_handoff else COUNT)
    print(f'picked {len(targets)} target(s) of {len(queue["items"])} queued', flush=True)
    completed = [];failed=[];waiting=[];blocked_until=None
    for item in targets:
        from blog_image_backpressure import require_open,ImageProviderBusy
        from blog_image_queue import ImageQueueBusy
        from blog_image_stock import require_generation_open,ImagePending
        try:require_generation_open(ROOT)
        except ImageProviderBusy as busy:
            blocked_until=busy.retry_at
            print('Shared image-provider cooldown active; no new text/image calls.');break
        from blog_image_draft_recovery import recover
        image_retry_draft=recover(load_json(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json'),{}))
        if ready_handoff and image_retry_draft is None:raise RuntimeError('Saved image-stage draft required; no source/text generation')
        if image_retry_draft is None:
            saved_record=load_json(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json'),{})
            image_retry_draft=domain_repair_draft(saved_record,item)
            if image_retry_draft is not None:item['text_policy_retry']=DOMAIN_REPAIR_POLICY
        item['status'] = 'processing'
        item['attempts'] = int(item.get('attempts', 0)) + 1
        state['in_progress'] = item['key']
        links = approved_links(item, lib)
        image_url = None
        errors, obj = ['not generated'], None
        shared_image_deferred=False;stock_pending=False
        image_retry_at=None
        stage='generation'
        for attempt in range(1, (1 if ready_handoff else ATTEMPTS) + 1):
            try:
                if DRY_RUN or not (BASE.AGNES_KEY or BASE.AGNES_KEYS):
                    obj = offline_sample(item, links)
                elif attempt == 1 and image_retry_draft is not None:
                    obj = image_retry_draft
                elif attempt == 1:
                    stage='generation'
                    obj = agnes(build_prompt(item, links))
                else:
                    stage='generation'
                    obj = agnes(repair_prompt(item, links, obj, errors),temperature=0.1)
                obj['title'] = item['assigned_title']
                obj = resolve_link_tokens(obj, links)
                from blog_draft_preflight import active,check
                if active(ROOT):
                    stage='text_validation'
                    errors=check(item,obj,'roya',ROOT,links)
                    if errors:continue
                from blog_reference_scene import context_from_post
                context=context_from_post(obj)
                if image_url is None or context!=item.get('_image_article_context'):
                    item['_image_article_context'] = context
                    stage='image'
                    image_url = prepare_roya_image(item)
            except Exception as exc:
                errors = ['agnes error: ' + str(exc)[:200]]
                print(f'{item["key"]} attempt={attempt} {errors[0]}', flush=True)
                if isinstance(exc,(ImageProviderBusy,ImageQueueBusy)):
                    shared_image_deferred=True;stock_pending=isinstance(exc,ImagePending)
                    image_retry_at=exc.retry_at
                    break
                continue
            # Titles are owned by the approved matrix, not an AI spelling choice.
            obj['title'] = item['assigned_title']
            obj = resolve_link_tokens(obj, links)
            obj = inject_image(item, obj, image_url)
            stage='validation'
            errors, info = qa(item, obj, links)
            print(f'{item["key"]} attempt={attempt} words={info["words"]} links={len(info["links"])} errors={len(errors)}', flush=True)
            if not errors:
                break
        if image_retry_at is not None:
            item['next_retry_at']=datetime.datetime.fromtimestamp(image_retry_at,datetime.timezone.utc).isoformat().replace('+00:00','Z')
        elif not errors:
            item.pop('next_retry_at',None)
            item.pop('failure_stage',None)
        record = dict(item)
        record.update({'status': 'completed' if not errors else 'failed',
                       'generated_at': now(), 'qa': {'passed': not errors, 'errors': errors},
                       'post': obj, 'blog': BLOG, 'failure_stage':stage if errors else None})
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
            if stock_pending:waiting.append(item['key'])
            else:failed.append(item['key'])
            item['status'] = 'failed'
            item['generated_at']=record['generated_at']
            item['failure_stage']=stage
            item['last_error'] = '; '.join(errors)[:400]
            state['failed'][item['key']] = item['last_error']
        save_json(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', item['key']) + '.json'), record)
        state['in_progress'] = None
        save_json(QUEUE_PATH, queue)
        save_json(STATE_PATH, state)
        if shared_image_deferred and not stock_pending:break  # Actual provider block.
        if stock_pending and not item.get('_image_stock_request'):break  # Stock capacity reached.
    ready = [i for i in queue['items'] if i.get('status') == 'completed' and not i.get('published')]
    save_json(PUBLISH_QUEUE, {'generated_at': now(), 'blog': BLOG, 'count': len(ready),
                              'items': [{'key': i['key'], 'title': i.get('title', ''), 'slug': i.get('slug', ''),
                                         'target_url': i['target_url'], 'city_fa': i['city_fa'],
                                         'province_fa': i['province_fa'], 'family': i.get('family'),
                                         'item_file': str(ITEMS / (re.sub(r'[^A-Za-z0-9._-]+', '_', i['key']) + '.json'))}
                                        for i in ready]})
    from blog_generation_status import write as write_generation_status
    from blog_image_stock_preflight import waiting_keys
    run_status=write_generation_status(ROOT,'roya',completed,failed,blocked_until,waiting=waiting or waiting_keys('roya',ROOT))
    done, total = len(state['completed_keys']), len(queue['items'])
    STATUS_MD.write_text(
        '# صف بک‌لینک وبلاگ AFP\n\n'
        f'وضعیت این اجرا: {run_status["status"]}؛ این گزارش تأیید انتشار نیست.\n\n'
        '| مورد | مقدار |\n|---|---:|\n'
        f'| کل صف | {total} |\n| تولیدشده | {done} |\n| ناموفق | {len(state["failed"])} |\n'
        f'| باقی‌مانده | {total - done} |\n| پیشرفت | {round(100 * done / max(1, total), 2)}% |\n'
        f'| آخرین اجرا | {now()} |\n| مدل | `{BASE.AGNES_MODEL}` |\n\n'
        'هر آیتم یک مقاله ۵۰۰ تا ۱۰۰۰ کلمه فارسی برای وبلاگ AFP است که به صفحه شهری متناظر در '
        'navar-abyari.ir، صفحه استان و فروشگاه لینک می‌دهد؛ مطالب مرتبط با نوار تیپ یک ارجاع '
        'متنی به صفحه نخست دارند که جایگزین لینک جانبی است و مقاله‌های لوله کلیدواژه اجباری ندارند.\n', encoding='utf-8')
    print('completed: ' + (', '.join(completed) or 'none'), flush=True)
    return 1 if failed and not completed else 0


if __name__ == '__main__':
    sys.exit(main())
