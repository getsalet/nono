"""Reject corrupt generated prose; never silently delete or translate words."""
import re,unicodedata
from bs4 import BeautifulSoup
ALLOWED=re.compile(r'(?<!\w)(?:AFP|PE|UV|ISO|cm|mm)(?!\w)',re.I)
def visible_text_errors(post):
 soup=BeautifulSoup(post.get('html',''),'html.parser')
 values=[post.get('title',''),post.get('meta_description',''),soup.get_text(' ',strip=True)]
 if isinstance(post.get('tags'),list):values.extend(x for x in post['tags']if isinstance(x,str))
 values.extend(x.get('alt','')for x in soup.select('img'))
 errors=[]
 for text in values:
  value=ALLOWED.sub('',str(text))
  if any(unicodedata.category(c).startswith('L')and 'ARABIC'not in unicodedata.name(c,'')for c in value):
   errors.append('Unexpected foreign or mixed-script word in visible Persian text')
  if '\ufffd'in value or re.search(r'\?{2,}',value):errors.append('Corrupt replacement characters in visible Persian text')
 return list(dict.fromkeys(errors))
