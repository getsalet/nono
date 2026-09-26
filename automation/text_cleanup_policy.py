#!/usr/bin/env python3
"""Deterministically repair common generated-content QA failures."""
import re
from urllib.parse import unquote, urlparse
IMAGE_1_MARKER='[[[IMAGE_1]]]'
CYRILLIC_RE=re.compile(r'[\u0400-\u04ff]+')
CJK_RE=re.compile(r'[\u3400-\u9fff]+')
FULLWIDTH_RE=re.compile(r'[，。；：！？]+')
LATIN_RE=re.compile(r'\b[A-Za-z]{3,}\b')
HEX_UTF8_RE=re.compile(r'\b(?:[0-9A-Fa-f]{2}){4,}\b')
ALLOWED_LATIN={'FAQ','AFP'}
TAG_SPLIT_RE=re.compile(r'(<[^>]+>)')
FAQ_SECTION_RE=re.compile(r'<h3[^>]*>\s*(?:پرسش|سوال|سؤالات|سوالات).*?(?:متداول|FAQ).*?</h3>.*?(?=<h2|<h3|$)',re.I|re.S)
CONTACT_RE=re.compile(
 r'<p>\s*برای دریافت مشاوره یا سفارش محصول،?\s*از طریق\s*'
 r'<a\b[^>]*href=["\']https://wa\.me/989134922013["\'][^>]*>'
 r'\s*واتساپ با ما در ارتباط باشید\s*</a>\s*[.。]?\s*</p>',
 re.I|re.S,
)
RELATED_P_RE=re.compile(
 r'<p\b[^>]*>\s*برای مقایسه و تصمیم‌گیری بهتر،?.*?</p>',
 re.I|re.S,
)
ANCHOR_RE=re.compile(
 r'<a\b(?P<attrs>[^>]*)href=["\'](?P<href>[^"\']+)["\'](?P<rest>[^>]*)>'
 r'(?P<label>.*?)</a>',
 re.I|re.S,
)
ARABIC_ONLY_RE=re.compile(r'[ةۀؤإأٱ]')
FOREIGN_URL_RE=re.compile(r'(?:^|[/_.?&=-])(ar|arabic|en|english|tr|turkish)(?:[/_.?&=-]|$)',re.I)

def _decode_hex_label(match):
 try:value=bytes.fromhex(match.group(0)).decode('utf-8')
 except (ValueError,UnicodeDecodeError):return match.group(0)
 return value if re.search(r'[\u0600-\u06ff]',value) else match.group(0)

def _foreign_related_link(match):
 """Remove a related-post paragraph when its target or label is not Persian."""
 paragraph=match.group(0)
 anchor=ANCHOR_RE.search(paragraph)
 if not anchor:return ''
 href=unquote(anchor.group('href'))
 label=re.sub(r'<[^>]+>',' ',anchor.group('label'))
 parsed=urlparse(href)
 path_and_query=f'{parsed.path}?{parsed.query}'
 if FOREIGN_URL_RE.search(path_and_query):return ''
 if CYRILLIC_RE.search(label) or CJK_RE.search(label) or re.search(r'[A-Za-z]{3,}',label):return ''
 if ARABIC_ONLY_RE.search(label):return ''
 return paragraph

def clean_title(title,item):
 title=(title or '').strip();topic=item.get('topic');city=item.get('city','').strip()
 if topic=='layflat':base=f'خرید لوله نخی و تاشو در {city}'
 elif topic=='tape20':base=f'خرید نوار تیپ ۲۰ سانتی در {city}'
 else:base=title
 return base[:68].strip()

def _clean_text_nodes(html,item=None):
 item=item or {};parts=TAG_SPLIT_RE.split(html or '')
 for index in range(0,len(parts),2):
  text=CYRILLIC_RE.sub('',parts[index])
  text=CJK_RE.sub('',text)
  text=FULLWIDTH_RE.sub('،',text)
  text=HEX_UTF8_RE.sub(_decode_hex_label,text)
  text=LATIN_RE.sub(lambda m:m.group(0) if m.group(0) in ALLOWED_LATIN else '',text)
  if item.get('topic')=='tape20':
   text=re.sub(r'\bPVC\b|پلی[‌\- ]?وینیل', 'پلی‌اتیلن', text, flags=re.I)
  elif item.get('topic')=='layflat':
   text=text.replace('رول نوار تیپ','رول لوله نخی و تاشو')
   text=text.replace('خرید نوار تیپ ۲۰','خرید لوله نخی و تاشو')
   text=text.replace('فاصله قطره‌چکان ۲۰','انتخاب سایز و فشار لوله تاشو')
  text=re.sub(r'[ \t]{2,}',' ',text)
  parts[index]=text
 return ''.join(parts)

def _faq_html(item):
 city=item.get('city','').strip();topic=item.get('topic')
 if topic=='layflat':
  subject='لوله نخی و تاشو';questions=[
   ('برای انتخاب سایز لوله نخی و تاشو چه مواردی بررسی شود؟','دبی موردنیاز، طول مسیر، اختلاف ارتفاع، فشار پمپ، نوع اتصال و دیتاشیت سازنده باید پیش از خرید بررسی شود.'),
   ('فشار کار لوله تاشو چگونه تعیین می‌شود؟','فشار مجاز باید از روی مشخصات همان محصول انتخاب شود و فشار واقعی ابتدا و انتهای مسیر نیز هنگام راه‌اندازی اندازه‌گیری شود.'),
   ('چطور از لوله نخی در مزرعه نگهداری کنیم؟','از کشیدن روی لبه تیز، تاخوردگی شدید و عبور ماشین‌آلات جلوگیری کنید و پس از تخلیه آب، لوله را تمیز و دور از تابش طولانی نگه دارید.')]
 else:
  subject='نوار تیپ ۲۰ سانتی‌متر';questions=[
   ('نوار تیپ ۲۰ سانتی‌متر برای چه کشت‌هایی مناسب است؟','تناسب نوار با نوع کشت، بافت خاک، کیفیت آب، طول ردیف و طراحی آبیاری باید پیش از خرید بررسی شود.'),
   ('فشار و فیلتراسیون مناسب چگونه انتخاب می‌شود؟','فشار کار و فیلتر باید مطابق دیتاشیت سازنده، دبی منبع و کیفیت آب انتخاب و در مزرعه اندازه‌گیری شود.'),
   ('در زمان نصب نوار تیپ چه نکاتی مهم است؟','نوار بدون پیچ‌خوردگی نصب شود، اتصالات نشتی نداشته باشند و مسیرها پیش از بهره‌برداری به‌آرامی شست‌وشو و کنترل شوند.')]
 contact='<p>برای دریافت مشاوره یا سفارش محصول، از طریق <a href="https://wa.me/989134922013">واتساپ با ما در ارتباط باشید</a>.</p>'
 heading=f'<h3 id="faq">پرسش‌های متداول درباره {subject} در {city}</h3>'
 return contact+heading+''.join(f'<details><summary>{q}</summary>{a}<br><br></details>' for q,a in questions)

def cleanup_html(html,item=None):
 item=item or {};html=(html or '').replace(IMAGE_1_MARKER,'')
 html=_clean_text_nodes(html,item)
 html=RELATED_P_RE.sub(_foreign_related_link,html)
 html=FAQ_SECTION_RE.sub('',html)
 html=CONTACT_RE.sub('',html)
 html=re.sub(r'<p>\s*</p>','',html).strip()
 topic=item.get('topic');visible=re.sub(r'<[^>]+>',' ',html)
 if topic=='layflat' and not any(x in visible for x in ('لوله نخی','لوله تاشو')):html='<p>لوله نخی و لوله تاشو برای انتقال آب در مزرعه به‌کار می‌رود و انتخاب سایز، فشار، اتصال و دوام آن باید بر اساس دبی، طول مسیر و دیتاشیت سازنده انجام شود.</p>'+html
 if topic=='tape20' and not re.search(r'(?:۲۰|20)\s*سانتی',visible):html='<p>این راهنما بر انتخاب و کاربرد نوار تیپ با فاصله قطره‌چکان ۲۰ سانتی‌متر تمرکز دارد و مشخصات نهایی باید با طراحی مزرعه و دیتاشیت سازنده تطبیق داده شود.</p>'+html
 html+=_faq_html(item)
 return html.strip()

def apply(obj,item):
 if not isinstance(obj,dict):return obj
 topic=item.get('topic');city=item.get('city','').strip();product='لوله نخی و تاشو' if topic=='layflat' else 'نوار تیپ ۲۰ سانتی‌متر'
 obj['title']=clean_title(obj.get('title',''),item);obj['meta_title']=clean_title(obj.get('meta_title') or obj.get('title',''),item)
 obj['meta_description']=(obj.get('meta_description') or f'راهنمای کاربردی انتخاب، خرید، نصب و نگهداری {product} در {city} بر اساس نیاز مزرعه و مشخصات فنی.').strip()
 obj['focus_keyword']=(obj.get('focus_keyword') or f'خرید {product} در {city}').strip()
 obj['excerpt']=(obj.get('excerpt') or f'نکات فنی و عملی انتخاب و استفاده از {product} در {city} برای تصمیم‌گیری مطمئن‌تر.').strip()
 obj['html']=cleanup_html(obj.get('html',''),item)
 return obj
