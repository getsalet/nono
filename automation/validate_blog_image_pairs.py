#!/usr/bin/env python3
"""One bounded, manual/request-triggered pair validation. Never publishes a post.
No raw provider response, credential, fingerprint, prompt or account data on disk.
Uncertain/failed requests are never automatically repeated in the same request.
"""
import datetime,hashlib,json,os,re,time
from pathlib import Path
from blog_image_restore import POLICY,CONFIG,EVIDENCE,load
ROOT=Path(__file__).resolve().parents[1]
REQUEST='data/blog-image-pair-validation-request.json'
def main():
 import blog_generated_image as images
 from audit_usable_agnes_keys import image_probe
 from blog_image_connection import settings
 from blog_image_queue import provider_slot
 from blog_image_account_expansion import shared_open,configured_keys
 from blog_image_backpressure import defer
 request=json.loads((ROOT/REQUEST).read_text());c=load(ROOT)
 rid=request.get('request_id','')
 if request.get('policy')!=POLICY or not re.fullmatch('[a-f0-9]{32}',rid)or request.get('max_image_requests')!=14:raise RuntimeError('Explicit bounded fourteen-slot validation required')
 ledger='data/blog-image-pair-validation/requests/'+rid+'.json'
 images.git(['fetch','--quiet','origin','main'],ROOT)
 if (ROOT/ledger).exists()or images.git(['cat-file','-e','origin/main:'+ledger],ROOT,check=False).returncode==0:
  print('Pair validation request already reserved; no repeated provider calls.');return 0
 cfg=settings(images.roya.BASE.AGNES_BASE)
 report={'policy':POLICY,'request_id':rid,'key_pairs':c['key_pairs'],'connection':cfg,'status':'started','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'keys':[],'post_submissions':0,'visual_publication_approved':False,'production_activated':False,'max_image_requests':14}
 def save():
  raw=(json.dumps(report,indent=2)+'\n').encode()
  for path in (ledger,EVIDENCE):
   out=ROOT/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);images.checkpoint_asset(path,raw,ROOT)
 save() # Durable reservation before any billable provider call.
 names=[n for pair in c['key_pairs'].values()for n in pair];bindings=configured_keys(names);seen={}
 try:
  shared_open(ROOT)
  for blog,pair in c['key_pairs'].items():
   for name in pair:
    row={'blog':blog,'secret_name':name,'image':{'status':'not_tested'}};report['keys'].append(row)
    key=bindings.get(name)
    if not key:row['image']={'status':'not_configured'};save();continue
    if key in seen:row.update(duplicate_of=seen[key]);row['image']={'status':'skipped_duplicate'};save();continue
    seen[key]=name
    item={'key':'pair-validation-'+rid+'-'+blog,'family':'tape20','site_title':'بررسی نوار تیپ AFP','_image_article_context':{'title':'راهنمای بررسی اتصال نوار تیپ آبیاری','summary':'نمای آموزشی عمومی اتصال نوار تیپ برای توضیح کنترل اتصال و مسیر آب؛ بدون ادعای اجرای محلی یا نتیجه اندازه‌گیری در مزرعه.'}}
    token=hashlib.sha256((rid+'|'+name).encode()).hexdigest()[:32]
    with provider_slot('pairaudit',token) as lease:
     try:
      images.git(['fetch','--quiet','origin','main'],ROOT);shared_open(ROOT)
      row['image']={'status':'request_reserved','attempts':1};save()
      row['image']=image_probe(key,item,cfg);save()
      code=row['image'].get('http_status');provider=row['image'].get('provider_code')
      if code in (402,429)or provider=='insufficient_quota':
       if code==429:defer(ROOT,time.time()+max(3600,row['image'].get('retry_after_seconds',0)),images.checkpoint_asset)
       else:
        from blog_image_key_router import STATE,state
        s=state(ROOT);s['shared_block']='billing_required';s['updated_at_epoch']=time.time();images.checkpoint_asset(STATE,json.dumps(s,indent=2).encode(),ROOT)
       report['status']='stopped_shared_limit';return 2
      if provider=='image_queue_full':
       defer(ROOT,time.time()+max(300,row['image'].get('retry_after_seconds',0)),images.checkpoint_asset);report['status']='deferred_provider_queue';return 2
     except Exception:
      if lease is not None:lease.retain=True
      raise
  report['status']='completed'
  report['healthy_slots']=[x['secret_name']for x in report['keys']if x['image'].get('status')=='image_healthy']
  report['all_pairs_ready']=all(all(n in report['healthy_slots']for n in p)for p in c['key_pairs'].values())
  return 0 if report['all_pairs_ready']else 2
 except Exception:
  report['status']='stopped_preflight_or_transport';raise RuntimeError('Pair validation stopped safely; see sanitized report, no publication')from None
 finally:
  report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
if __name__=='__main__':raise SystemExit(main())
