"""Native Parsiblog forms: account guard, draft readback, one-shot submissions."""
import os,re,html,json,time
from urllib.parse import urlsplit
from parsiblog_policy import normalized_title,urlkey
PANEL='http://www.parsiblog.com';BLOG='http://afp.parsiblog.com';NOTES=PANEL+'/Notes.aspx';SEP='$#PB'
class NativeError(RuntimeError):pass
def title_matches(expected,actual):
 # The provider drops ZWNJ in persisted titles. Keep all other words exact.
 variants={normalized_title(expected),normalized_title(expected.replace('\u200c',''))}
 return normalized_title(actual)in variants
def guard(page):
 if urlsplit(page.url).hostname!='www.parsiblog.com':raise NativeError('Unexpected admin host')
 page.wait_for_selector('#Title',state='attached',timeout=30000)
 if page.evaluate('typeof TheHost!=="undefined" ? TheHost : ""')!='afp':raise NativeError('Wrong active blog; refusing submission')
def login(page):
 page.goto(NOTES+'?Post',wait_until='domcontentloaded',timeout=60000)
 if not page.locator('#Title').count():
  user=os.getenv('PARSIBLOG_USERNAME');password=os.getenv('PARSIBLOG_PASSWORD')
  if not user or not password:raise NativeError('Set PARSIBLOG_USERNAME and PARSIBLOG_PASSWORD repository secrets')
  page.goto(PANEL+'/',wait_until='domcontentloaded',timeout=60000)
  if not page.locator('#beuser').count():raise NativeError('Login form changed; manual inspection required')
  page.locator('#beuser').fill(user);page.locator('#bepass').fill(password)
  if page.locator('#savepass').count():page.locator('#savepass').check()
  buttons=page.locator('button[onclick*="GetAsyncVal"]')
  if buttons.count()!=1:raise NativeError('Ambiguous login action')
  buttons.click();page.wait_for_url('**/Main.aspx*',timeout=45000)
  page.goto(NOTES+'?Post',wait_until='domcontentloaded',timeout=60000)
 guard(page);print('Parsiblog protected native form and AFP account verified',flush=True)
def native_request(page,payload):
 # Same payload produced by the site's own controls, single request, never retry a write.
 result=page.evaluate(r'''async payload=>{const r=await fetch('Notes.aspx?Post',{method:'POST',body:payload,credentials:'same-origin',redirect:'error'});const type=r.headers.get('content-type')||'';const match=type.match(/charset\s*=\s*["']?([^;\s"']+)/i);const encoding=match?match[1]:document.characterSet;const bytes=await r.arrayBuffer();return {status:r.status,text:new TextDecoder(encoding).decode(bytes)}}''',payload)
 if result['status']!=200:raise NativeError('Native endpoint HTTP failure; reconcile before any retry')
 return result['text']
def read_post(page,pid):
 guard(page);body=native_request(page,page.evaluate('(id)=>GetEParams("EditBtn",String(id))',str(pid)))
 if not body.startswith('OK'+SEP):raise NativeError('Saved post cannot be read back')
 parts=body.split(SEP)
 if len(parts)<7:raise NativeError('Unexpected native edit response')
 return {'title':html.unescape(parts[2]),'html':parts[3],'id':str(parts[4]),'published':parts[5].lower()=='true','tags':parts[7]if len(parts)>7 and parts[7].startswith('Sub=')else''}
def first_page_posts(page):
 # ?Post is a new-note view: its list can be empty even after a successful save.
 if urlsplit(page.url).query:page.goto(NOTES,wait_until='domcontentloaded',timeout=60000)
 guard(page);ids=page.locator('div[id^="NT"]').evaluate_all('(es)=>es.map(e=>e.id).filter(x=>/^NT[0-9]+$/.test(x)).map(x=>x.slice(2))')
 if len(ids)>100:raise NativeError('Unexpected native listing size')
 return [read_post(page,pid)for pid in ids]
def normalized_body(value):
 # Observed provider canonicalization: U+FF0C becomes ASCII comma on persistence.
 # No broad Unicode folding: all other text/words remain exact.
 return normalized_title(value).replace('\uff0c',',')
def persisted_errors(item,expected,actual):
 errors=[]
 if not title_matches(expected['title'],actual['title']):errors.append('Saved title mismatch')
 from city_backlink_policy import Inspect
 p=Inspect();p.feed(actual['html']);q=Inspect();q.feed(expected['html'])
 if len(p.links)!=3 or {urlkey(x)for x in p.links}!={urlkey(x)for x in q.links}:errors.append('Saved three-link contract failed')
 # Compare normalized visible text, not irrelevant whitespace/entity serialization.
 a=normalized_body(' '.join(p.plain));e=normalized_body(' '.join(q.plain))
 if a!=e:errors.append('Saved article text differs from approved draft')
 if len(p.images)!=1 or p.images[0].get('src')!=item.get('image_url'):errors.append('Saved image missing or changed')
 if p.tags.count('h3')!=q.tags.count('h3') or p.tags.count('h2')!=q.tags.count('h2'):errors.append('Saved FAQ/section structure changed')
 return errors
def save_post(page,item,publish=False,pid=None,checkpoint=None):
 checkpoint=checkpoint or (lambda phase,pid=None:None)
 checkpoint('editor_validation',pid)
 # The full listing exposes controls but initializes TinyMCE only in ?Post.
 page.goto(NOTES+'?Post',wait_until='domcontentloaded',timeout=60000)
 guard(page)
 page.wait_for_function('typeof tinyMCE!=="undefined"&&tinyMCE.get("PBEdit")&&tinyMCE.get("PBEdit").initialized',timeout=45000)
 post=item['post']
 if any(SEP in value for value in [post['title'],post['html']]+post['tags']):raise NativeError('Native protocol delimiter present in content')
 page.locator('#Title').fill(post['title'])
 result=page.evaluate('''x=>{CurNoteID=x.id||'-1';tinyMCE.get('PBEdit').setContent(x.body);document.getElementById('SubjectDL').value=x.tags;return tinyMCE.get('PBEdit').getContent()}''',{'body':post['html'],'tags':'+'.join(post['tags']),'id':str(pid)if pid else None})
 check={'title':post['title'],'html':result};errors=persisted_errors(item,post,check)
 if errors:raise NativeError('Editor changed approved content; '+','.join(errors))
 page.evaluate('''publish=>{for(const [id,value]of Object.entries({Publish:publish,AllowComment:true,ConstCB:false,DateViewCB:false,PassCheckbox:false})){const e=document.getElementById(id);if(e)e.checked=value}}''',publish)
 payload=page.evaluate('()=>{if(!GetNValue())throw Error("Editor not ready");return GetNParams("SaveBtn")}')
 checkpoint('request_pending',pid)
 response=native_request(page,payload)
 match=re.match(r'^OK([1-9][0-9]*)\$#PB',response)
 # Native updates can return OK alone; known ID may be retained, then strict readback.
 saved_id=match.group(1)if match else str(pid)if pid and response.startswith('OK') else None
 if not saved_id:raise NativeError('Native save acknowledgement missing; do not blindly resubmit')
 checkpoint('acknowledged',saved_id)
 readback=read_post(page,saved_id);errors=persisted_errors(item,post,readback)
 if readback['published']!=publish:errors.append('Publication checkbox not persisted')
 if errors:raise NativeError('Native readback rejected: '+','.join(errors))
 return saved_id
def find_public_article(page,item):
 # Public PostID is the blog-local ordinal, not the internal native database ID.
 cards=page.locator('.post-card');matches=[]
 for i in range(cards.count()):
  card=cards.nth(i);title=card.locator('.post-title')
  if title.count()==1 and title_matches(item['post']['title'],title.inner_text()):matches.append(card)
 if len(matches)!=1:raise NativeError('Public article title absent or ambiguous')
 return matches[0]
def _verify_public_once(context,item,pid):
 page=context.new_page()
 try:
  page.set_extra_http_headers({'Cache-Control':'no-cache','Pragma':'no-cache'})
  page.goto(BLOG+'/',wait_until='domcontentloaded',timeout=60000)
  card=find_public_article(page,item);link=card.locator('.post-title a')
  if link.count()!=1:raise NativeError('Public permalink missing')
  url=link.get_attribute('href');from urllib.parse import urljoin
  url=urljoin(BLOG+'/',url)
  if urlsplit(url).hostname!='afp.parsiblog.com':raise NativeError('Wrong public post host')
  page.goto(url,wait_until='domcontentloaded',timeout=60000)
  article=find_public_article(page,item);body=article.locator('.post-content')
  if body.count()!=1:raise NativeError('Native public article missing')
  actual={'title':article.locator('.post-title').inner_text(),'html':body.inner_html()}
  errors=persisted_errors(item,item['post'],actual)
  if errors:raise NativeError('Public verification rejected: '+','.join(errors))
  return url
 finally:page.close()

def verify_public(context,item,pid):
 # Retrying a public GET is safe; native save_post is never retried here.
 from playwright.sync_api import TimeoutError as BrowserTimeout
 waits=(5,15,30,60)  # Provider listings can lag after a successful native acknowledgement.
 for attempt in range(5):
  try:return _verify_public_once(context,item,pid)
  except (NativeError,BrowserTimeout):
   if attempt==4:raise
   time.sleep(waits[attempt])
