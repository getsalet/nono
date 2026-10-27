"""Bounded visible-prose feedback only; never modifies or approves an article."""
import re,unicodedata
from html.parser import HTMLParser
ALLOWED_LATIN={'afp','pe','uv','iso','cm','mm'}
class Visible(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.alts=[]
 def handle_data(self,data):self.parts.append(data)
 def handle_starttag(self,tag,attrs):
  if tag=='img':self.alts.append(dict(attrs).get('alt',''))
def language_feedback(post,allowed=ALLOWED_LATIN):
 if not isinstance(post,dict):return []
 values=[('title',post.get('title','')),('meta_description',post.get('meta_description',''))]
 if isinstance(post.get('tags'),list):values.extend(('tag',t)for t in post['tags']if isinstance(t,str))
 parser=Visible();parser.feed(post.get('html','')if isinstance(post.get('html'),str)else'')
 values.append(('body',' '.join(parser.parts)));values.extend(('image_alt',v)for v in parser.alts)
 found=[]
 for field,text in values:
  for token in re.findall(r'\S+',str(text)):
   value=re.sub(r'(?<!\w)(?:'+ '|'.join(map(re.escape,sorted(allowed)))+r')(?!\w)','',token,flags=re.I)if allowed else token
   foreign=any(unicodedata.category(c).startswith('L')and 'ARABIC'not in unicodedata.name(c,'')for c in value)
   if foreign or '\ufffd'in token or re.search(r'\?{2,}',token):
    entry={'field':field,'invalid_visible_token':token[:80]}
    if entry not in found:found.append(entry)
    if len(found)==8:return found
 return found

def rejected_text_seed(previous,item):
 """Return a rejected draft as repair input, never as a ready/approved result."""
 import copy
 if not isinstance(previous,dict)or previous.get('key')!=item.get('key'):return None
 if previous.get('published')or item.get('published')or previous.get('status')!='failed'or previous.get('failure_stage')!='text_validation':return None
 post=previous.get('post')
 if not isinstance(post,dict)or not all(isinstance(post.get(k),str)and post[k].strip()for k in ('title','html')):return None
 errors=previous.get('qa',{}).get('errors')
 if not isinstance(errors,list)or not errors:errors=[previous.get('last_error','Rejected text requires full validation')]
 return copy.deepcopy(post),[str(e)[:350]for e in errors[:12]]
