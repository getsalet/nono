"""Persian visible-text boundary. URLs/slugs and JSON keys are not article prose."""
import re,unicodedata
from bs4 import BeautifulSoup

def visible_text(html):return BeautifulSoup(html,'html.parser').get_text(' ',strip=True)
def language_errors(text):
 # Allow only the known AFP mark outside Arabic-script letters. This catches
 # Cyrillic, Greek, CJK and isolated foreign letters, not just Latin words.
 value=re.sub(r'(?<!\w)AFP(?!\w)','',str(text),flags=re.I)
 if any(unicodedata.category(c).startswith('L')and 'ARABIC'not in unicodedata.name(c,'')for c in value):return ['Unexpected foreign-language text in Persian article']
 if '\ufffd'in value or re.search(r'\?{2,}',value):return ['Corrupt replacement characters in Persian article']
 return []
def post_language_errors(post):
 values=[post.get('title',''),post.get('meta_description','')]
 if isinstance(post.get('tags'),list):values.extend(x for x in post['tags']if isinstance(x,str))
 soup=BeautifulSoup(post.get('html',''),'html.parser');values.append(soup.get_text(' ',strip=True));values.extend(i.get('alt','')for i in soup.find_all('img'))
 return list(dict.fromkeys(e for value in values for e in language_errors(value)))
def source_context(item):
 # Do not feed family=tape20, internal booleans or pipeline keys to the writer.
 return {'برند':'AFP','گروه محصول':'نوار آبیاری قطره‌ای'if item['family']=='tape20'else'لوله نخی و تاشو برای انتقال آب','محدوده جغرافیایی':item['city_fa']}
