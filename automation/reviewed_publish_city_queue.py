#!/usr/bin/env python3
"""Generate, review, validate, and package publish-ready missing-city posts."""
import hashlib,json,os,re,time
import city_content_queue as base
import city_content_queue_cloudflare as queue
import content_layout_policy

ORIGINAL_MAKE=queue.make_content
ORIGINAL_IMAGE=queue.generate_image
ORIGINAL_SQL=queue.sql_for
QUALITY_GATE_VERSION=6
CYRILLIC_RE=re.compile(r'[\u0400-\u04ff]')
CJK_RE=re.compile(r'[\u3400-\u9fff]')
FULLWIDTH_RE=re.compile(r'[，。；：！？]')
LATIN_RE=re.compile(r'\b[A-Za-z]{3,}\b')
ALLOWED_LATIN={'FAQ','AFP'}
TAG_RE=re.compile(r'<[^>]+>')
ANCHOR_RE=re.compile(r'<a\b[^>]*>(.*?)</a>',re.I|re.S)
BLOCKED_LINK_TERMS=('wp_global_styles','حریم-خصوصی','حریم%20خصوصی','سیاست-حفظ','تماس-با-ما','قوانین','برگه-نمونه','روال-کار')
BLOCKED_TITLE_TERMS=('حریم خصوصی','تماس با ما','قوانین','برگه نمونه','روال کار')
PREFERRED_LINK_TERMS=('نوار','آبیاری','قطره','تیپ','لوله')
TECHNICAL_PATTERNS=(
    (re.compile(r'PVC|پلی[‌\- ]?وینیل',re.I),'PVC claim for irrigation tape'),
    (re.compile(r'۱۵\s*تا\s*۳۰\s*میکرون'),'implausible 15–30 micron thickness'),
    (re.compile(r'مخصوصااً'),'Persian typo مخصوصااً'),
)

def visible_text(html):
    return TAG_RE.sub(' ',html or '')

def language_errors(html):
    visible=visible_text(html);errors=[]
    if CYRILLIC_RE.search(visible):errors.append('Cyrillic characters')
    if CJK_RE.search(visible):errors.append('CJK characters')
    if FULLWIDTH_RE.search(visible):errors.append('full-width punctuation')
    bad=sorted({x for x in LATIN_RE.findall(visible) if x not in ALLOWED_LATIN})
    if bad:errors.append('unexpected Latin words: '+', '.join(bad[:12]))
    return errors

def technical_errors(html):
    return [label for pattern,label in TECHNICAL_PATTERNS if pattern.search(html or '')]

def safe_links(links):
    def blocked(link):
        url=str(link.get('url',''));title=str(link.get('title',''))
        return any(x in url for x in BLOCKED_LINK_TERMS) or any(x in title for x in BLOCKED_TITLE_TERMS)
    clean=[x for x in links if x.get('url') and x.get('title') and not blocked(x)]
    chosen=[];seen=set()
    for link in clean:
        if link['url'] in seen:continue
        chosen.append(link);seen.add(link['url'])
    return chosen

def rebuild_internal_links(obj,links):
    body=obj.get('html','')
    body=ANCHOR_RE.sub(lambda m:m.group(1),body)
    body=content_layout_policy.distribute_image_markers(body)
    approved=safe_links(links)
    if len(approved)<base.MIN_LINKS:raise RuntimeError('Not enough safe internal links')
    seed='|'.join(str(obj.get(key,'')) for key in ('title','focus_keyword','meta_title'))
    selected=content_layout_policy.select_internal_links(approved,seed,body,base.MIN_LINKS)
    obj['html']=content_layout_policy.insert_internal_links(body,selected)
    obj['internal_link_selection']=[{'title':x['title'],'url':x['url']} for x in selected]
    return obj

def validate_reviewed(obj,item,links):
    body=obj.get('html','');errors=language_errors(body)+technical_errors(body)
    approved=safe_links(links);allowed={x['url'] for x in approved};used=base.internal_links(body)
    if base.words(body)<base.MIN_WORDS:errors.append('word count below minimum')
    if len(used)!=base.MIN_LINKS:errors.append('internal link count must equal minimum')
    if used-allowed:errors.append('unsafe or unapproved internal link')
    if any(term in body for term in BLOCKED_LINK_TERMS):errors.append('blocked utility link')
    for i in range(2,6):
        if body.count(f'[[[IMAGE_{i}]]]')!=1:errors.append(f'IMAGE_{i} marker invalid')
    for key in ('title','meta_title','meta_description','focus_keyword','excerpt','html'):
        if not obj.get(key):errors.append(f'missing {key}')
    if item['city'] not in obj.get('title',''):errors.append('city missing from title')
    return errors

def reviewed_make_content(item,links):
    draft=ORIGINAL_MAKE(item,links)
    review_prompt=f'''به‌عنوان ویراستار ارشد فارسی، متخصص سئو و بازبین فنی آبیاری، مقاله زیر را بازبینی و اصلاح کن. همه نویسه‌های روسی، چینی، علائم تمام‌عرض و واژه‌های لاتین ناخواسته را حذف یا به فارسی روان تبدیل کن؛ فقط FAQ مجاز است. همه لینک‌های HTML را حذف کن و هیچ لینک تازه‌ای نساز؛ سامانه پس از بازبینی لینک‌های امن را اضافه می‌کند. ادعاهای ساختگی درباره اقلیم محلی، قیمت، نمایندگی، موجودی، ارسال و مشخصات محصول را حذف کن. نوار تیپ را PVC معرفی نکن؛ جنس رایج آن پلی‌اتیلن است. فشار، ضخامت، عمر و فاصله قطره‌چکان را قانون قطعی و یکسان برای همه محصولات اعلام نکن و انتخاب نهایی را به دیتاشیت سازنده، کیفیت آب، نوع کشت و طراحی متخصص وابسته کن. توصیه شیمیایی و اسیدشویی فقط با هشدار بررسی کیفیت آب، دستور سازنده و نظر متخصص مجاز است. تناقض، وعده قطعی، عبارت مبهم و خطاهای تایپی را اصلاح کن. متن نهایی حداقل {base.MIN_WORDS} کلمه باشد و ساختار HTML و نشانگرهای [[[IMAGE_2]]], [[[IMAGE_3]]], [[[IMAGE_4]]], [[[IMAGE_5]]] را هرکدام دقیقاً یک بار حفظ کند. عنوان باید شامل شهر {item['city']} باشد. فقط JSON معتبر با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.\n\nپیش‌نویس:\n{json.dumps(draft,ensure_ascii=False)}'''
    last=[]
    for attempt in range(1,4):
        obj=rebuild_internal_links(base.agnes(review_prompt),links)
        errors=validate_reviewed(obj,item,links)
        if not errors:
            obj['editorial_review']={'passed':True,'review_model':base.AGNES_MODEL,'attempt':attempt,'quality_gate_version':QUALITY_GATE_VERSION,'checks':['Persian language','technical plausibility','SEO fields','minimum length','safe internal links','image markers']}
            return obj
        last=errors
        review_prompt+='\nبازبینی قبلی رد شد. این خطاها را بدون حذف جزئیات اصلاح کن: '+'; '.join(errors)
    raise RuntimeError('Editorial review failed: '+'; '.join(last))

def reuse_or_generate(item,kind):
    artifact=base.ITEMS/f"{item['source_id']}.json"
    approved=False
    if artifact.exists():
        try:
            approved=json.loads(artifact.read_text(encoding='utf-8')).get('image_rebuild_policy')=='reference-rerender-3d-v5-approved-scales-topic-first'
        except Exception:approved=False
    if approved:
        path=base.IMAGES/f"{item['source_id']}-{kind}.webp"
        if path.exists() and path.stat().st_size>10000:
            blob=path.read_bytes();return path.name,hashlib.sha256(blob).hexdigest()
    return ORIGINAL_IMAGE(item,kind)

def publish_sql(item,obj,image_names):
    insert,rollback,body=ORIGINAL_SQL(item,obj,image_names)
    insert=insert.replace("'draft','closed','closed'","'publish','closed','closed'",1)
    body=re.sub(r'<p>(<figure\b.*?</figure>)</p>',r'\1',body,flags=re.S)
    insert=re.sub(r'<p>(<figure\b.*?</figure>)</p>',r'\1',insert,flags=re.S)
    return insert,rollback,body

queue.make_content=reviewed_make_content
queue.generate_image=reuse_or_generate
queue.sql_for=publish_sql
base.IMAGE_MODEL=queue.MODEL
state=base.initialize(False)
queue.migrate(state)
state['rules'].update({'draft_only':False,'post_status':'publish','editorial_review_required':True,'review_model':base.AGNES_MODEL,'quality_gate_version':QUALITY_GATE_VERSION,'reject_cyrillic':True,'reject_cjk':True,'reject_unexpected_latin':True,'reject_fullwidth_punctuation':True,'rebuild_safe_internal_links':True,'technical_plausibility_required':True,'post_delay_seconds':30})
REPAIRABLE_FAILURES=(
    'Cyrillic characters','CJK characters','full-width punctuation',
    'unexpected Latin words','unexpected Latin after cleanup',
    'three details FAQ items required at end','word count below minimum',
    'missing meta_description','missing focus_keyword','missing excerpt',
    '20cm product focus missing','layflat product focus missing',
    'layflat article still focuses on drip tape','PVC claim for irrigation tape',
)
for item in state['items']:
    if item.get('status')=='failed' and any(signal in str(item.get('last_error','')) for signal in REPAIRABLE_FAILURES):
        item['status']='pending';item['attempts']=0
        for k in ('completed_at','last_error','failed_at','started_at','word_count','failed_stage'):item.pop(k,None)
        continue
    if item.get('status')=='completed':
        artifact=base.ITEMS/f"{item['source_id']}.json";passed=False
        if artifact.exists():
            try:
                review=json.loads(artifact.read_text(encoding='utf-8')).get('editorial_review',{})
                passed=bool(review.get('passed')) and review.get('review_model')==base.AGNES_MODEL and int(review.get('quality_gate_version',0))>=QUALITY_GATE_VERSION
            except Exception:passed=False
        if not passed:
            item['status']='pending';item['attempts']=0
            for k in ('completed_at','last_error','failed_at','started_at','word_count'):item.pop(k,None)
state['updated_at']=base.now();base.QUEUE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
previously_completed={item['source_id'] for item in state['items'] if item.get('status')=='completed'}
# The queue coordinator processes the selected batch concurrently and remains
# the only writer of queue state, SQL and item metadata.
queue.process(state)
for item in state['items']:
    artifact=base.ITEMS/f"{item['source_id']}.json"
    if item.get('status')=='completed' and artifact.exists():
        data=json.loads(artifact.read_text(encoding='utf-8'));data['status']='completed';data['completed_at']=item.get('completed_at');data['word_count']=item.get('word_count')
        if item['source_id'] not in previously_completed:
            data['image_generation_mode']='reference-conditioned-3d-rerender-approved-scales-topic-first';data['image_rebuild_policy']='reference-rerender-3d-v5-approved-scales-topic-first'
            item['image_generation_mode']='reference-conditioned-3d-rerender-approved-scales-topic-first';item['image_rebuild_policy']='reference-rerender-3d-v5-approved-scales-topic-first'
        artifact.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
combined=base.OUT/'create-all-completed.sql'
if combined.exists():
    text=combined.read_text(encoding='utf-8').replace('-- Review before importing. All generated posts are drafts.','-- Editorially reviewed. Generated posts use publish status.')
    combined.write_text(text,encoding='utf-8')
