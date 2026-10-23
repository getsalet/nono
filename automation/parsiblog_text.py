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

def language_feedback(post):
 # Targeted repair feedback only; never silently translate/delete article text.
 # Slugs, URLs and HTML attributes are not Persian prose and stay excluded.
 values=[('title',post.get('title','')),('meta_description',post.get('meta_description',''))]
 if isinstance(post.get('tags'),list):values.extend(('tag',x)for x in post['tags']if isinstance(x,str))
 soup=BeautifulSoup(post.get('html',''),'html.parser');values.append(('body',soup.get_text(' ',strip=True)))
 values.extend(('image_alt',x.get('alt',''))for x in soup.find_all('img'))
 found=[]
 for field,text in values:
  for token in re.findall(r'\S+',str(text)):
   value=re.sub(r'(?<!\w)AFP(?!\w)','',token,flags=re.I)
   if any(unicodedata.category(c).startswith('L')and 'ARABIC'not in unicodedata.name(c,'')for c in value):
    entry={'field':field,'invalid_visible_token':token[:80]}
    if entry not in found:found.append(entry)
    if len(found)==8:return found
 return found
