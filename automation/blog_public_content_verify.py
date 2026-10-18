"""Pure checks of the actual article body after native save, never a submit."""
from html.parser import HTMLParser
from urllib.parse import unquote
import re,unicodedata
class Body(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.hrefs=[];self.images=[];self.faqs=0
 def handle_data(self,text):self.parts.append(text)
 def handle_starttag(self,tag,attrs):
  data=dict(attrs)
  if tag=='a':self.hrefs.append(data.get('href',''))
  if tag=='img':self.images.append(data.get('src',''))
  if tag=='details':self.faqs+=1
 def normalized(self):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',' '.join(self.parts))).strip()
def verify_text_body(item,actual_html,links):
 expected=Body();expected.feed(item['post']['html']);actual=Body();actual.feed(actual_html)
 if expected.images or actual.images:raise RuntimeError('Unexpected image in text-only article')
 if not expected.normalized()or actual.normalized()!=expected.normalized():raise RuntimeError('Public full article differs from approved text; stop and reconcile, never resubmit')
 canonical=lambda url:unquote(url).rstrip('/')
 if len(actual.hrefs)!=2 or sorted(map(canonical,actual.hrefs))!=sorted(canonical(x['url'])for x in links):raise RuntimeError('Public article must retain exactly two approved contextual backlinks')
 if actual.faqs!=3:raise RuntimeError('Public article lost native FAQs')
 return True
