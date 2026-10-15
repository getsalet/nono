"""Select an article's declared/own image, never the first image in related cards."""
import html,re
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
POLICY='source-primary-image-v2-no-global-related-scan'
class SourceImages(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.declared=[];self.body=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs);marker=' '.join((attrs.get('class',''),attrs.get('id',''))).lower()
  if tag=='meta'and(attrs.get('property','').lower()=='og:image'or attrs.get('name','').lower()=='twitter:image'):
   self.declared.append(attrs.get('content',''))
  blocked=bool(re.search(r'related|recommend|sidebar|footer|header|menu|suggest',marker))or tag in('aside','header','footer','nav')
  content=tag in('article','main')or bool(re.search(r'entry-content|post-content|article-content|post-thumbnail|featured-image',marker))
  if tag=='img'and any(x[1]for x in self.stack)and not any(x[2]for x in self.stack):self.body.append(attrs.get('src')or attrs.get('data-src',''))
  if tag not in('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):self.stack.append((tag,content,blocked))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:self.stack=self.stack[:i];return

def primary_image(page,url):
 parser=SourceImages();parser.feed(page)
 for candidate in parser.declared+parser.body:
  candidate=urljoin(url,html.unescape(candidate));p=urlsplit(candidate)
  if p.scheme=='https'and p.hostname=='navar-abyari.ir'and p.path.startswith('/wp-content/uploads/')and re.search(r'\.(?:webp|jpe?g|png)$',p.path,re.I):return candidate
 return ''
