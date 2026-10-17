#!/usr/bin/env python3
"""One explicit, bounded recheck of distinct user-authorized accounts.
No repeated probe, no key8, no quota bypass and no post publication.
Only actual decodable image success may extend the production slot list.
"""
import datetime,hashlib,json,os,re,time
from pathlib import Path
import blog_generated_image as images
from audit_usable_agnes_keys import text_probe,image_probe
ROOT=Path(__file__).resolve().parents[1]
POLICY='distinct-account-image-expansion-v1'
REQUEST='data/blog-image-account-expansion-request.json'
LATEST='data/blog-image-account-expansion/latest.json'
CANDIDATES=('AGNES_API_KEY','AGNES_API_KEY4','AGNES_API_KEY5','AGNES_API_KEY9','AGNES_API_KEY14','AGNES_API_KEY15')

def successful(report,connection,current=None):
 """Return only fresh, unique, actually image-proven names. No text-only grants."""
 current=time.time()if current is None else current
 if not isinstance(report,dict)or report.get('policy')!=POLICY or report.get('status')!='completed' or report.get('connection')!=connection or report.get('post_submissions')!=0:return []
 try:stamp=datetime.datetime.fromisoformat(report['finished_at'].replace('Z','+00:00')).timestamp()
 except (KeyError,ValueError,AttributeError,TypeError):return []
 if not 0<=current-stamp<=72*3600:return []
 rows=report.get('keys',[])
 if not isinstance(rows,list)or any(not isinstance(r,dict)for r in rows):return []
 names=[r.get('secret_name')for r in rows]
 if len(names)!=len(set(names))or any(n not in CANDIDATES for n in names):return []
 result=[]
 for r in rows:
  text=r.get('text',{});image=r.get('image',{})
  if not isinstance(text,dict)or not isinstance(image,dict):continue
  w=image.get('width',0);h=image.get('height',0)
  if (text.get('status')=='healthy'and text.get('http_status')==200 and image.get('status')=='image_healthy'and image.get('http_status')==200
      and type(w)is int and type(h)is int and 512<=h<w<=10000 and re.fullmatch('[a-f0-9]{64}',str(image.get('image_sha256','')))):
   result.append(r['secret_name'])
 return result

def validate_request(request):
 if (request.get('policy')!=POLICY or not re.fullmatch('[a-f0-9]{32}',str(request.get('request_id','')))or request.get('slots')!=list(CANDIDATES)
     or request.get('max_image_requests')!=6 or request.get('minimum_interval_seconds')!=60 or request.get('account_ownership_confirmed_by_user')is not True):
  raise RuntimeError('One explicit six-account expansion request required')
 return 'data/blog-image-account-expansion/requests/'+request['request_id']+'.json'

def shared_open(root):
 # New independent candidates do not inherit another slot's capacity backoff.
 # Every GLOBAL stop, user pause, quota block and global image mutex still applies.
 from blog_image_runtime_control import generation_paused
 from blog_image_backpressure import retry_at,ImageProviderBusy
 from blog_image_key_router import state
 if generation_paused(root)or images.family_cancelled({'family':'tape20'},root):raise RuntimeError('User image stop active')
 s=state(root)
 if s.get('shared_block'):raise RuntimeError('Shared quota/billing block active; no expansion')
 stamp=max(retry_at(root),s.get('shared_retry_at_epoch',0))
 if stamp>time.time():raise ImageProviderBusy(stamp)

def stop_code(row):
 return row.get('http_status')in(402,429)or row.get('provider_code')=='insufficient_quota'

def main():
 from blog_image_connection import settings
 from blog_image_queue import provider_slot
 from blog_image_key_router import CONFIG,POLICY as ROUTER_POLICY
 request=json.loads((ROOT/REQUEST).read_text());ledger=validate_request(request)
 # Pre-dispatch ledger makes reruns safe even after a timeout or ambiguous response.
 images.git(['fetch','--quiet','origin','main'],ROOT)
 if (ROOT/ledger).exists()or images.git(['cat-file','-e','origin/main:'+ledger],ROOT,check=False).returncode==0:
  print('Expansion request already recorded; zero repeated probes.');return 0
 cfg=settings(images.roya.BASE.AGNES_BASE)
 report={'policy':POLICY,'request_id':request['request_id'],'connection':cfg,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'preflight','keys':[],'post_submissions':0,'max_image_requests':6,'minimum_interval_seconds':60,'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'visual_publication_approved':False,'promoted_slots':[]}
 def save():
  raw=json.dumps(report,indent=2).encode()
  # Keep live worktrees clean; publication state and original audit untouched.
  images.checkpoint_asset(ledger,raw,ROOT);images.checkpoint_asset(LATEST,raw,ROOT)
 save() # Reserve this request before touching any provider.
 try:
  shared_open(ROOT)
  pool=images.roya.BASE._key_pool;seen=set()
  for name in CANDIDATES:
   images.git(['fetch','--quiet','origin','main'],ROOT);shared_open(ROOT)
   matches=[key for key in pool.keys if pool.slots.get(key)==name]
   row={'secret_name':name,'text':{'status':'not_tested'},'image':{'status':'not_tested'}};report['keys'].append(row)
   if not matches or matches[0]in seen:
    row['text']['status']='not_configured_or_duplicate';continue
   key=matches[0];seen.add(key)
   # Reserve before tiny text completion as well; interruption never retries it.
   row['text']['status']='requested';save();row['text']=text_probe(key)
   if stop_code(row['text']):
    report['status']='stopped_quota_or_rate_limit';save();break
   if row['text'].get('status')!='healthy':save();continue
   item={'key':'account-expansion-'+name,'family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز؛ بررسی فاصله خطوط','summary':'بررسی قابلیت تولید تصویر با محصول مرجع AFP و خطوط نصب‌شده نوار تیپ در ردیف پیاز؛ فقط آزمون قابلیت اتصال است و برای انتشار استفاده نمی‌شود.'}}
   token=hashlib.sha256((request['request_id']+'|'+name).encode()).hexdigest()[:32]
   with provider_slot('accountexpand',token):
    images.git(['fetch','--quiet','origin','main'],ROOT);shared_open(ROOT)
    row['image']={'status':'requested','attempts':1};save()
    row['image']=image_probe(key,item,cfg);save()
    # The common provider lease enforces >=60 seconds start spacing with all blogs.
   if stop_code(row['image']):
    report['status']='stopped_quota_or_rate_limit';save();break
  else:report['status']='completed'
  report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
  names=successful(report,cfg)
  if names:
   # Read the latest remote config; never replace unrelated concurrent state.
   images.git(['fetch','--quiet','origin','main'],ROOT)
   config=json.loads(images.git(['show','origin/main:'+CONFIG],ROOT).stdout)
   if config.get('policy')!=ROUTER_POLICY or config.get('enabled')is not True:raise RuntimeError('Production pool not enabled; no automatic activation')
   config['slots']=list(dict.fromkeys(config['slots']+names))
   config['account_scope']='Distinct accounts confirmed by user; slot8 excluded; each newly added slot has fresh real image proof.'
   config['expansion_evidence']=LATEST
   images.checkpoint_asset(CONFIG,json.dumps(config,indent=2).encode(),ROOT)
   report['promoted_slots']=names;save()
 except Exception as exc:
  from blog_image_backpressure import ImageProviderBusy
  report['status']='deferred_shared_cooldown'if isinstance(exc,ImageProviderBusy)else'blocked_'+type(exc).__name__
  if isinstance(exc,ImageProviderBusy):report['retry_at_epoch']=exc.retry_at
 finally:
  report.setdefault('finished_at',datetime.datetime.now(datetime.timezone.utc).isoformat());save()
 print(json.dumps({'status':report['status'],'promoted_slots':report['promoted_slots'],'post_submissions':0}),flush=True)
 return 0 if report['status']=='completed'else 1
if __name__=='__main__':raise SystemExit(main())
