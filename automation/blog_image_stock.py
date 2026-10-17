"""Durable per-article image requests. Producers never call the image provider.
Independent worker uses the existing reference recipe, image mutex and QA gates.
Only allowlisted article data is persisted; credentials/response bodies are not.
"""
import contextlib,copy,json,os,re,subprocess,time
from pathlib import Path
from blog_image_queue import ImageQueueBusy
CONFIG='data/blog-image-stock-control.json'
DIRECTORY='data/blog-image-stock/requests'
POLICY='afp-article-image-stock-v1'
ACTIVE={'requested','processing','ready'}

class ImagePending(ImageQueueBusy):
 def __init__(self,reason='requested'):
  self.retry_at=time.time()+900
  self.args=('Independent image stock waiting: '+reason+'; saved draft retained, no producer image API',)

def control(root):
 path=Path(root)/CONFIG
 if not path.exists():return {'enabled':False,'target':12,'per_blog_limit':3}
 value=json.loads(path.read_text())
 if not isinstance(value,dict)or type(value.get('enabled'))is not bool or value.get('target')!=12 or value.get('per_blog_limit')!=3 or ('text_preflight_required'in value and type(value['text_preflight_required'])is not bool):
  raise RuntimeError('Invalid independent image stock control; no fallback')
 return value

def enabled(root):return control(root)['enabled']
def hosted():return os.getenv('GITHUB_ACTIONS')=='true'
def refresh(root):
 if hosted():
  from blog_generated_image import git
  git(['fetch','--quiet','origin','main'],root)
def read(root,path,default=None):
 root=Path(root)
 if hosted():
  result=subprocess.run(['git','show','origin/main:'+path],cwd=root,capture_output=True)
  if result.returncode:
   # Distinguish absent entries from repository/transport failures.
   check=subprocess.run(['git','ls-tree','origin/main','--',path],cwd=root,capture_output=True)
   if check.returncode or check.stdout:raise RuntimeError('Image stock read failed closed')
   return copy.deepcopy(default)
  return json.loads(result.stdout)
 return json.loads((root/path).read_text())if(root/path).exists()else copy.deepcopy(default)
def rows(root):
 if hosted():
  result=subprocess.run(['git','ls-tree','-r','--name-only','origin/main','--',DIRECTORY],cwd=root,capture_output=True)
  if result.returncode:raise RuntimeError('Image stock listing unavailable')
  paths=result.stdout.decode().splitlines()
 else:paths=[str(p.relative_to(root))for p in(Path(root)/DIRECTORY).glob('*.json')]
 result=[]
 for path in paths:
  if not re.fullmatch(DIRECTORY+r'/[a-f0-9]{32}\.json',path):raise RuntimeError('Invalid image stock request path')
  row=read(root,path)
  if not isinstance(row,dict)or row.get('policy')!=POLICY or path!=request_path(row.get('asset_id','')):raise RuntimeError('Invalid image stock request')
  if row.get('blog')not in('roya','farsiblog','rozblog','blogfa','loxblog')or row.get('status')not in ACTIVE|{'consumed','cancelled','superseded','rejected','needs_text_repair'}or not isinstance(row.get('key'),str):raise RuntimeError('Invalid stock owner or status')
  result.append(row)
 return result

def request_path(asset):
 if not re.fullmatch('[a-f0-9]{32}',str(asset)):raise ValueError('Safe asset identity required')
 return DIRECTORY+'/'+asset+'.json'
def persist(root,row):
 path=request_path(row['asset_id']);raw=json.dumps(row,ensure_ascii=False,indent=2).encode()
 if hosted():
  from blog_generated_image import checkpoint_asset
  checkpoint_asset(path,raw,root)
 else:
  out=Path(root)/path;out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(out)

@contextlib.contextmanager
def admission(root,blog,asset):
 # Serialize cap checks and per-request transitions with the existing mutex.
 # Release BEFORE worker generation, which acquires its own provider lease.
 if hosted():
  from blog_image_queue import Queue
  with Queue(minimum_interval=0,wait=30).slot(blog,asset):
   refresh(root);yield
 else:yield

def snapshot(item):
 fields=('key','family','kind','topic','angle','site_title','matrix_title','assigned_title','city_fa','province_fa','_image_article_context','_image_qa_feedback')
 value={k:copy.deepcopy(item[k])for k in fields if k in item}
 from blog_reference_scene import article
 article(value)  # Require a real final-draft title/body summary, not a generic topic.
 return value

def awaiting(item,root):
 """Do not regenerate prose while its durable request is waiting."""
 if not enabled(root):return False
 asset=item.get('_image_stock_request')
 if not asset:return False
 row=read(root,request_path(asset))
 if not row:return False
 return row.get('status')in('requested','processing')

def require_generation_open(root):
 if not enabled(root):
  from blog_image_backpressure import require_open
  require_open(root)
 # Async producers can prepare prose during provider cooldown. Admission still
 # caps saved requests and no producer can bypass it to call the provider.

def request_image(item,blog,root):
 from blog_generated_image import identity,family_enabled,prepare_now,existing_asset
 from blog_image_gate import review
 if not family_enabled(item,root):raise RuntimeError('Image family cancelled or held')
 asset=identity(item,blog);path=request_path(asset)
 with admission(root,blog,asset):
  row=read(root,path)
  if row and row.get('status')in('ready','consumed'):
   # Never fall into generation if an allegedly ready asset is missing.
   url=existing_asset('assets/blog-generated/'+blog+'/'+asset+'.webp',root)
   if not url:raise RuntimeError('Ready image stock asset missing; no inline generation')
   review(item,url,root=root)
   # prepare_now only reads that verified immutable cache, and attaches full metadata.
   url=prepare_now(item,blog,root,max_rounds=1,allow_generate=False)
   row.update(status='consumed',consumed_at=time.time());persist(root,row)
   item['_image_stock_request']=asset
   return url
  if row and row.get('status')in('rejected','cancelled','superseded','needs_text_repair'):
   raise RuntimeError('Image stock request needs review: '+row['status'])
  if row:
   item['_image_stock_request']=asset
   raise ImagePending(row['status'])
  current=rows(root);cfg=control(root)
  for prior in current:
   if prior['blog']==blog and prior['key']==item['key']and prior['status']in ACTIVE:
    prior.update(status='superseded');persist(root,prior)
  if sum(x['status']in ACTIVE for x in current)>=cfg['target']:raise ImagePending('stock capacity reached')
  if sum(x['status']in ACTIVE and x['blog']==blog for x in current)>=cfg['per_blog_limit']:raise ImagePending('blog capacity reached')
  row={'policy':POLICY,'asset_id':asset,'blog':blog,'key':item['key'],'status':'requested','created_at':time.time(),'attempts':0,'item':snapshot(item)}
  persist(root,row);item['_image_stock_request']=asset
 raise ImagePending()

def checkpoint_evidence(root,blog,asset):
 if not hosted():return
 from blog_generated_image import checkpoint_asset
 candidates=list((Path(root)/'artifacts/blog-image-reviews').glob('*.json'))
 directory=Path(root)/f'artifacts/{blog}-backlink-queue/generated-images'
 candidates+=list(directory.glob(asset+'.webp'))+list((directory/'rejected').glob(asset+'-*.webp'))
 for file in candidates:
  path=str(file.relative_to(root));raw=file.read_bytes()
  previous=subprocess.run(['git','show','origin/main:'+path],cwd=root,capture_output=True)
  if previous.returncode==0 and previous.stdout==raw:continue
  checkpoint_asset(path,raw,root)

def worker_once(root):
 from blog_generated_image import identity,rollout_enabled,family_enabled,prepare_now
 from blog_image_runtime_control import generation_paused
 from blog_image_backpressure import require_open,ImageProviderBusy
 root=Path(root)
 if not enabled(root)or generation_paused(root):return {'status':'paused','provider_requests':0}
 refresh(root)
 # Prefer never/less-attempted drafts. With a 20-minute worker, a five-minute
 # per-item retry alone would otherwise select the same oldest failure forever.
 pending=sorted((r for r in rows(root)if r['status']in('requested','processing')),key=lambda r:(r.get('attempts',0),r.get('started_at',r['created_at']),r['created_at']))
 waiting_result=None
 for row in pending:
  blog=row['blog'];item=copy.deepcopy(row['item']);asset=row['asset_id']
  with admission(root,blog,asset):
   latest=read(root,request_path(asset))
   if not latest or latest['status']not in('requested','processing'):continue
   row=latest
   # A completed/cancelled run can resume a processing row. A live workflow
   # is protected by workflow concurrency, and the provider mutex still applies.
   remote_control=read(root,'data/blog-generated-image-control.json',{})
   if remote_control.get('pause_image_production')is True:return {'status':'paused','provider_requests':0}
   source=read(root,'data/'+blog+'/backlink-queue.json',{'items':[]})
   matches=[x for x in source['items']if x.get('key')==row['key']]
   if len(matches)!=1 or matches[0].get('published')or matches[0].get('status')=='published'or not family_enabled(item,root):
    row.update(status='cancelled');persist(root,row);continue
   if identity(item,blog)!=asset or(matches[0].get('_image_stock_request')and matches[0]['_image_stock_request']!=asset):
    row.update(status='superseded');persist(root,row);continue
   from blog_draft_preflight import active,check_saved,DraftUnavailable
   if active(root):
    try:errors=check_saved(row,matches[0],root)
    except DraftUnavailable:
     row.update(status='requested',retry_at=time.time()+300,last_error='saved_draft_unavailable');persist(root,row);continue
    if errors:
     row.update(status='needs_text_repair',last_error='text_preflight_failed',text_errors=errors[:12]);persist(root,row);continue
   # Text triage is local and must not wait for an IMAGE retry/cooldown.
   if row.get('retry_at',0)>time.time():continue
   if not rollout_enabled(blog,root):raise RuntimeError('Worker rollout acceptance unavailable')
   try:require_open(root)
   except ImageProviderBusy as exc:
    waiting_result={'status':'waiting_provider','retry_at':exc.retry_at,'provider_requests':0};continue
   row.update(status='processing',attempts=row['attempts']+1,started_at=time.time());persist(root,row)
  try:
   url=prepare_now(item,blog,root,max_rounds=1)
  except (ImageProviderBusy,ImageQueueBusy)as exc:
   row.update(status='requested',retry_at=exc.retry_at,last_error=type(exc).__name__)
  except Exception as exc:
   # Retain safe type only, never raw provider responses. Definitive visual
   # rejection is not an automatic retry; transport errors receive slow retries.
   rejected=str(exc).startswith('Product image rejected:')
   row.update(status='rejected'if rejected and row.get('visual_rejections',0)>=2 else'requested',retry_at=time.time()+1800,last_error='visual_rejection'if rejected else type(exc).__name__)
   if rejected:
    row['visual_rejections']=row.get('visual_rejections',0)+1
    row['item']=snapshot(item)  # Carry bounded corrective QA feedback to next run.
  else:
   row.update(status='ready',url=url,ready_at=time.time(),review_sha256=item['image_review']['sha256'])
   row.pop('last_error',None);row.pop('retry_at',None)
  checkpoint_evidence(root,blog,asset)
  with admission(root,blog,asset):
   current=read(root,request_path(asset))
   if current.get('status')!='processing':
    return {'status':current['status'],'asset_id':asset,'publication_attempted':False}
   persist(root,row)
  return {'status':row['status'],'asset_id':asset,'blog':blog,'publication_attempted':False}
 return waiting_result or {'status':'idle','provider_requests':0,'publication_attempted':False}

def main():
 root=Path(__file__).resolve().parents[1]
 result=worker_once(root)
 print(json.dumps(result))
 path=root/'artifacts/blog-image-stock/status.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2))
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as out:out.write('\n## Independent image stock: '+result['status']+'\n\nTarget: 12 article-owned images, not current ready count. No publication in worker.\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
