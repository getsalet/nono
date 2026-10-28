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

CITY_TOKEN='AFP_CITY'
_CITY_TOKEN_RE=re.compile(r'(?<!\w)AFP_CITY(?!\w)')
def render_city_token(item,post):
 # The writer selects wording; the approved matrix owns the place spelling.
 # Resolve only an explicit standalone token, never guess/translate mixed words.
 # URLs, slugs, attributes, assigned title and non-placeholder prose stay intact.
 if not isinstance(post,dict):return 0
 city=item.get('city_fa')
 if not isinstance(city,str)or not city.strip()or language_errors(city)or any(c in city for c in '<>\r\n'):
  raise ValueError('Approved Persian locality required for token rendering')
 count=0
 def render(value):
  nonlocal count
  if not isinstance(value,str):return value
  result,n=_CITY_TOKEN_RE.subn(lambda m:city,value);count+=n;return result
 if isinstance(post.get('meta_description'),str):post['meta_description']=render(post['meta_description'])
 if isinstance(post.get('tags'),list):post['tags']=[render(x)for x in post['tags']]
 body=post.get('html')
 if isinstance(body,str)and _CITY_TOKEN_RE.search(body):
  soup=BeautifulSoup(body,'html.parser')
  for node in list(soup.find_all(string=True)):
   value=render(str(node))
   if value!=str(node):node.replace_with(value)
  post['html']=str(soup)
 return count
