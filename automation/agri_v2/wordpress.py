"""Restricted WordPress Author connection. No SQL, redirects, deletion or edits to unrelated posts."""
import base64,html,json,os,re,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from .queue import atomic_json,load_json,utcnow
from .pipeline import norm
def illustrated_content(content,media,crop):
 def figure(m):return '<figure class="wp-block-image"><img src="'+html.escape(m['url'],quote=True)+'" alt="'+html.escape('تصویرسازی هوش مصنوعی درباره '+crop+'؛ تصویر مستند مزرعه نیست',quote=True)+'" loading="lazy"/><figcaption>تصویرسازی هوش مصنوعی؛ نه تصویر مستند مزرعه.</figcaption></figure>'
 # Section boundaries are top-level; never insert a figure inside paragraphs or lists.
 matches=list(re.finditer(r'<h2>',content));at=matches[len(matches)//2].start() if len(matches)>1 else len(content)
 return content[:at]+figure(media[1])+content[at:]+figure(media[2])

class WPError(RuntimeError):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None
class WordPress:
 def __init__(self,env=None):
  e=os.environ if env is None else env;self.site=e.get('AFP_WP_BASE_URL','').rstrip('/')
  if self.site!='https://navar-abyari.ir':raise WPError('Unapproved WordPress origin')
  user=e.get('AFP_WP_USERNAME','');password=e.get('AFP_WP_APP_PASSWORD','')
  if not user or not password:raise WPError('WordPress Secrets missing')
  self.auth='Basic '+base64.b64encode((user+':'+password).encode()).decode();self.opener=urllib.request.build_opener(NoRedirect())
 def call(self,path,method='GET',data=None,blob=None,headers=None):
  if not re.match(r'^(posts|media|users/me)([/?]|$)',path):raise WPError('Unapproved WordPress route')
  h={'Authorization':self.auth,'Accept':'application/json','User-Agent':'AFP-agri-v2'}
  if headers:h.update(headers)
  if data is not None:blob=json.dumps(data,ensure_ascii=False).encode();h['Content-Type']='application/json'
  req=urllib.request.Request(self.site+'/wp-json/wp/v2/'+path,data=blob,method=method,headers=h)
  try:
   with self.opener.open(req,timeout=90) as r:
    raw=r.read(16*1024*1024);obj=json.loads(raw);return obj,dict(r.headers)
  except urllib.error.HTTPError as e:raise WPError('WordPress HTTP '+str(e.code)) from None
  except Exception:raise WPError('WordPress transport/JSON failure; reconcile by slug before retry') from None
 def preflight(self):
  me,_=self.call('users/me?context=edit');caps=me.get('capabilities',{})
  if not caps.get('publish_posts') or not caps.get('upload_files'):raise WPError('Publisher requires Author publish/media permissions')
  self.user_id=me['id'];return {'user_id':me['id'],'roles':me.get('roles',[]),'can_publish':True,'checked_at':utcnow()}
 def inventory(self):
  rows=[];page=1;pages=1
  while page<=pages:
   batch,h=self.call('posts?per_page=100&page='+str(page)+'&status=publish&_fields=id,title,link,status,modified,slug')
   if not isinstance(batch,list):raise WPError('Inventory shape invalid')
   if page==1:pages=int(next((v for k,v in h.items() if k.lower()=='x-wp-totalpages'),'0'))
   if pages<1 or pages>300:raise WPError('Inventory pagination invalid')
   rows.extend({'id':p['id'],'title':html.unescape(p['title']['rendered']),'url':p['link'],'status':p['status'],'modified':p['modified'],'slug':p['slug']} for p in batch);page+=1
  if not rows:raise WPError('Empty inventory; fail closed')
  return {'source_generated_at':utcnow(),'scope':'all public posts, all languages; Author cannot audit other users private drafts','records':rows}
 def publish(self,folder,topic,brief,authorized=False):
  if not authorized or brief.get('publish_authorized') is not True:raise WPError('Explicit publication authorization required')
  folder=Path(folder);rp=folder/'wordpress-receipt.json';r=load_json(rp) if rp.exists() else {'topic_id':topic['id'],'media':[],'status':'starting'}
  marker='<!-- afp-agri-v2:'+topic['id']+' -->';payload=load_json(folder/'wordpress-draft-payload.json');slug=payload['slug']
  self.preflight()
  # Reconcile slug first, including this account's drafts; never overwrite another post.
  found=[]
  for status in ['publish','draft','pending','future','private']:
   matches,_=self.call('posts?slug='+urllib.parse.quote(slug)+'&status='+status+'&context=edit')
   found.extend(matches)
  if len(found)>1:raise WPError('Ambiguous slug; stop')
  if found:
   post=found[0]
   if marker not in post.get('content',{}).get('raw','') or post.get('author')!=self.user_id:raise WPError('Existing post is not owned by this job')
   r['post_id']=post['id']
   if post['status']=='publish':r.update(status='published',url=post['link']);atomic_json(rp,r);return self.verify(post['id'],topic,rp)
  elif r.get('post_id'):raise WPError('Receipt post missing; do not recreate automatically')
  else:
   # A public post owned by somebody else with this slug is also a hard conflict.
   public,_=self.call('posts?slug='+urllib.parse.quote(slug))
   if public:raise WPError('Public slug already exists')
   draft=dict(payload,content=marker+'\n'+payload['content'],categories=[35],comment_status='closed',ping_status='closed',status='draft')
   post,_=self.call('posts','POST',draft);r.update(post_id=post['id'],status='draft_created');atomic_json(rp,r)
  for i in range(1,4):
   if any(x['index']==i for x in r['media']):continue
   name=topic['id']+'-image-'+str(i);existing,_=self.call('media?slug='+name+'&context=edit')
   if len(existing)>1:raise WPError('Ambiguous media slug')
   if existing:
    media=existing[0]
    if media.get('author')!=self.user_id or media.get('post') not in (0,r['post_id']):raise WPError('Existing media is not owned by this job')
   else:
    data=(folder/f'image-{i}.webp').read_bytes()
    media,_=self.call('media','POST',blob=data,headers={'Content-Type':'image/webp','Content-Disposition':'attachment; filename="'+name+'.webp"'})
   media,_=self.call('media/'+str(media['id']),'POST',{'post':r['post_id'],'title':topic['title']+' — تصویرسازی','alt_text':'تصویرسازی هوش مصنوعی مرتبط با '+topic['crop']+'؛ تصویر مستند مزرعه نیست','caption':'تصویرسازی با هوش مصنوعی؛ شاهد علمی یا تصویر واقعی مزرعه نیست.'})
   r['media'].append({'index':i,'id':media['id'],'url':media['source_url']});atomic_json(rp,r)
  media=sorted(r['media'],key=lambda m:m['index']);content=illustrated_content(payload['content'],media,topic['crop'])
  content+='<p><em>این مطلب با کمک هوش مصنوعی و بررسی منابع دانشگاهی تهیه شده و تأیید انسانیِ کارشناس کشاورزی برای آن ثبت نشده است. راهنمای عمومی است؛ زمان و شرایط برداشت باید با رقم، وضعیت مزرعه، تجهیزات و نظر کارشناس محلی تطبیق داده شود.</em></p>'
  # Update only our marker-owned draft, then explicitly publish one post.
  current,_=self.call('posts/'+str(r['post_id'])+'?context=edit')
  if current['author']!=self.user_id or marker not in current['content']['raw'] or current['status']!='draft':raise WPError('Draft ownership/status changed; stop')
  self.call('posts/'+str(r['post_id']),'POST',{'content':marker+'\n'+content,'featured_media':media[0]['id'],'categories':[35],'status':'draft'})
  post,_=self.call('posts/'+str(r['post_id']),'POST',{'status':'publish'});r.update(status='published',url=post['link'],published_at=utcnow());atomic_json(rp,r)
  return self.verify(post['id'],topic,rp)
 def verify(self,post_id,topic,receipt_path):
  post,_=self.call('posts/'+str(post_id));r=load_json(receipt_path)
  if post['status']!='publish' or norm(html.unescape(post['title']['rendered']))!=norm(topic['title']) or not post.get('featured_media'):raise WPError('Published post verification failed')
  if len(r.get('media',[]))!=3:raise WPError('Media receipt incomplete')
  for m in r['media'][1:]:
   if m['url'] not in post['content']['rendered']:raise WPError('Inline image verification failed')
  if not post['link'].startswith(self.site+'/'):raise WPError('Unexpected public origin')
  try:
   with urllib.request.urlopen(post['link'],timeout=45) as x:body=x.read(3*1024*1024).decode('utf-8','replace');status=x.status
  except Exception:raise WPError('Public URL fetch failed') from None
  if status!=200 or topic['title'] not in html.unescape(body):raise WPError('Public HTML/title verification failed')
  r.update(public_http_status=status,verified_at=utcnow(),featured_media=post['featured_media'],public_verified=True);atomic_json(receipt_path,r);return {k:r[k] for k in ['post_id','url','status','public_verified']}
