"""Audited round-robin image routing under the existing global provider lease.
One credential/request per invocation; no quota/rate-limit bypass, no key values on disk.
"""
import datetime,json,os,re,subprocess,time
from pathlib import Path
POLICY='audited-image-key-pool-v1'
CONFIG='data/blog-image-key-pool.json'
STATE='data/blog-image-key-pool-state.json'
CACHE='artifacts/blog-image-runtime/key-pool.json'
def enabled():return os.getenv('IMAGE_KEY_POOL_ENABLED')=='1'
def read_json(path):
 try:return json.loads(Path(path).read_text())
 except (OSError,ValueError):raise RuntimeError('Image key-pool evidence unreadable; no request')from None
def evidence(root):
 root=Path(root);cfg=read_json(root/CONFIG)
 if cfg.get('policy')!=POLICY or cfg.get('enabled')is not True:raise RuntimeError('Audited image key pool unavailable; no legacy fallback')
 names=cfg.get('slots',[])
 from agnes_key_pool import NAMES
 if not names or len(names)!=len(set(names))or any(n not in NAMES or n=='AGNES_API_KEY8'for n in names):raise RuntimeError('Invalid image key-pool slot configuration')
 latest=read_json(root/'data/agnes-usable-key-audit/latest.json');old=read_json(root/'data/agnes-image-key-health/latest.json')
 from blog_image_connection import settings
 connection=settings('https://apihub.agnes-ai.com/v1')
 if latest.get('complete_text')is not True or latest.get('complete_image')is not True or latest.get('connection')!=connection:raise RuntimeError('Matching complete image key audit required')
 historical={r['secret_name'] for r in old.get('keys',[])if r.get('status')=='image_healthy'and r.get('http_status')==200}if old.get('complete')is True and old.get('endpoint')==connection['endpoint']and old.get('model')==connection['model']else set()
 try:
  tested=datetime.datetime.fromisoformat(latest['finished_at'].replace('Z','+00:00')).timestamp()
  if not 0<=time.time()-tested<=72*3600:raise ValueError()
 except (KeyError,ValueError,TypeError,AttributeError):raise RuntimeError('Image key audit expired or timestamp invalid; fresh audit required')from None
 try:
  old_at=datetime.datetime.fromisoformat(old['tested_at'].replace('Z','+00:00')).timestamp()
  if not 0<=time.time()-old_at<=7*86400:historical=set()
 except (KeyError,ValueError,TypeError,AttributeError):historical=set()
 rows={r['secret_name']:r for r in latest.get('keys',[])};allowed=[]
 # Optional one-shot expansion evidence does not refresh the original audit or
 # promote text-only/queue-full candidates. Every added account needs real bytes.
 extra=root/'data/blog-image-account-expansion/latest.json'
 if extra.exists():
  from blog_image_account_expansion import successful
  report=read_json(extra);fresh=set(successful(report,connection))
  for row in report['keys']if fresh else[]:
   if isinstance(row,dict)and row.get('secret_name')in fresh:rows[row['secret_name']]=row
 for name in names:
  row=rows.get(name,{});text=row.get('text',{});image=row.get('image',{})
  if text.get('status')!='healthy'or text.get('http_status')!=200:continue
  if image.get('http_status')in(401,402,403,429):continue
  if image.get('status')=='image_healthy'and image.get('http_status')==200:allowed.append(name)
  elif name in historical and image.get('provider_code')=='image_queue_full':allowed.append(name)
 if not allowed:raise RuntimeError('No credential has real image-capability evidence')
 return allowed

def state(root):
 root=Path(root);values=[]
 for p in (root/STATE,root/CACHE):
  if p.exists():values.append(read_json(p))
 if os.getenv('GITHUB_ACTIONS')=='true'and(root/'.git').exists():
  result=subprocess.run(['git','show','origin/main:'+STATE],cwd=root,capture_output=True)
  if result.returncode==0:
   try:values.append(json.loads(result.stdout))
   except ValueError:raise RuntimeError('Remote key routing state unreadable')from None
 for value in values:
  if value.get('policy')!=POLICY or not isinstance(value.get('keys'),dict):raise RuntimeError('Invalid image key routing state')
  for field in ('updated_at_epoch','shared_retry_at_epoch'):
   number=value.get(field,0)
   if isinstance(number,bool)or not isinstance(number,(int,float))or not 0<=number<4102444800:raise RuntimeError('Invalid routing state timestamp')
  cursor=value.get('cursor',0)
  if isinstance(cursor,bool)or not isinstance(cursor,int)or not 0<=cursor<=25:raise RuntimeError('Invalid routing state cursor')
  if value.get('shared_block')not in(None,'billing_required'):raise RuntimeError('Unknown shared image-key block')
  for row in value['keys'].values():
   if not isinstance(row,dict)or isinstance(row.get('failures',0),bool)or not isinstance(row.get('failures',0),int)or not 0<=row.get('failures',0)<=100:raise RuntimeError('Invalid per-key failure state')
   stamp=row.get('retry_at_epoch',0)
   if isinstance(stamp,bool)or not isinstance(stamp,(int,float))or not 0<=stamp<4102444800:raise RuntimeError('Invalid per-key cooldown')
 return max(values,key=lambda v:v.get('updated_at_epoch',0),default={'policy':POLICY,'updated_at_epoch':0,'cursor':0,'keys':{}})

def available_at(root,names=None,current=None):
 current=time.time()if current is None else current
 names=names or evidence(root);s=state(root)
 if s.get('shared_block')=='billing_required':raise RuntimeError('Image account billing/quota requires review; no rotation around account limits')
 if not isinstance(s.get('shared_retry_at_epoch',0),(int,float)):raise RuntimeError('Invalid shared key-pool cooldown')
 dates=[max(current,s['keys'].get(n,{}).get('retry_at_epoch',0))for n in names if s['keys'].get(n,{}).get('status')not in('authentication_rejected','image_scope_denied')]
 if not dates:raise RuntimeError('All verified image credentials disabled; explicit review required')
 return max(min(dates),s.get('shared_retry_at_epoch',0))

def persist(root,s,checkpoint,lease):
 try:
  s['updated_at_epoch']=time.time();raw=json.dumps(s,indent=2).encode();path=Path(root)/CACHE;path.parent.mkdir(parents=True,exist_ok=True)
  tmp=path.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(path)
  checkpoint(STATE,raw,root)
 except Exception:
  if lease is not None:lease.retain=True
  raise RuntimeError('Image key routing checkpoint failed; provider lease retained')from None

def generate(item,blog,root,pool,operation,checkpoint,lease):
 from blog_image_backpressure import ImageProviderBusy
 names=evidence(root)
 # Runtime de-duplication also protects against changed/duplicate secret bindings.
 seen=set();configured=[]
 for name in names:
  matching=[key for key in pool.keys if pool.slots.get(key)==name]
  if matching and matching[0]not in seen:configured.append(name);seen.add(matching[0])
 if not configured:raise RuntimeError('Verified image credentials not configured; no fallback')
 now=time.time();s=state(root);stamp=available_at(root,configured,now)
 if stamp>now:
  busy=ImageProviderBusy(stamp);busy.key_scoped=True;busy.shared_cooldown_attempted=True;raise busy
 cursor=int(s.get('cursor',0))%len(configured);ordered=configured[cursor:]+configured[:cursor]
 name=next(n for n in ordered if s['keys'].get(n,{}).get('retry_at_epoch',0)<=now and s['keys'].get(n,{}).get('status')not in('authentication_rejected','image_scope_denied'))
 prior=s['keys'].get(name,{});failures=int(prior.get('failures',0));s['cursor']=(configured.index(name)+1)%len(configured)
 s['keys'][name]={**prior,'status':'reserved','retry_at_epoch':now+120,'last_attempt_at_epoch':now}
 persist(root,s,checkpoint,lease) # Fail closed before ANY API request.
 item['_image_key_route']={'policy':POLICY,'slot':name,'mode':'verified'if prior.get('status')=='image_healthy'else'controlled_recovery','max_provider_requests':1}
 try:raw=operation(item,blog,slots=[name],max_attempts=1)
 except Exception as exc:
  rows=item.get('_image_provider_attempts',[]);attempt=rows[-1]if rows else{};code=attempt.get('http_status')
  # Cooldown starts after the response, not before a possibly 600s request.
  # Respect the provider's explicit queue-full retry time; never shorten it.
  delay=min(1800,300*2**min(failures,3));retry=time.time()+delay
  if isinstance(exc,ImageProviderBusy):retry=max(retry,exc.retry_at)
  row={'status':'temporary_failure','failures':min(100,failures+1),'retry_at_epoch':retry,'last_attempt_at_epoch':now,'http_status':code}
  if code==401:row['status']='authentication_rejected'
  if code==403:row['status']='image_scope_denied'
  if code==402 or attempt.get('provider_code')=='insufficient_quota':s['shared_block']='billing_required';row['status']='billing_required'
  if code==429:
   row['status']='rate_limited';s['shared_retry_at_epoch']=max(s.get('shared_retry_at_epoch',0),time.time()+max(300,attempt.get('retry_after_seconds',0)))
  s['keys'][name]=row
  if code not in(401,402,403,429) and attempt.get('provider_code')!='image_queue_full':s['shared_retry_at_epoch']=max(s.get('shared_retry_at_epoch',0),time.time()+300)
  persist(root,s,checkpoint,lease)
  if code==429:
   # Also notify non-pool generators; quota/rate limits are never treated as per-key capacity.
   from blog_image_backpressure import write_state,retry_at
   stamp=max(s['shared_retry_at_epoch'],retry_at(root))
   try:write_state(root,{'reason':'provider_rate_limited','retry_at_epoch':stamp,'retry_at':datetime.datetime.fromtimestamp(stamp,datetime.timezone.utc).isoformat(),'last_failure_epoch':time.time(),'consecutive_queue_full':0,'post_submissions':0},checkpoint)
   except Exception:
    if lease is not None:lease.retain=True
    raise RuntimeError('Rate-limit checkpoint failed; lease retained')from None
  if attempt.get('provider_code')=='image_queue_full' or code==429:
   busy=ImageProviderBusy(max(time.time()+60,available_at(root,configured)));busy.key_scoped=True;busy.shared_cooldown_attempted=True;raise busy from None
  raise
 else:
  s['keys'][name]={'status':'image_healthy','failures':0,'retry_at_epoch':0,'last_attempt_at_epoch':now,'last_success_at_epoch':time.time(),'http_status':200}
  persist(root,s,checkpoint,lease);return raw
