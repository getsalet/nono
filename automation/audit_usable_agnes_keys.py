#!/usr/bin/env python3
"""Explicit key comparison: tiny text checks and one image per unique healthy slot.
No failover, post publication, raw responses, key values or key fingerprints.
"""
import datetime,hashlib,io,json,os,time,urllib.request,urllib.error
from pathlib import Path
from PIL import Image
import blog_generated_image as images
from agnes_key_pool import AgnesProviderError
ROOT=Path(__file__).resolve().parents[1]
OUT='data/agnes-usable-key-audit/latest.json'
PRIORITY=('AGNES_API_KEY6','AGNES_API_KEY7','AGNES_API_KEY11')
def selected(pool):
 return sorted(pool.keys,key=lambda k:(PRIORITY.index(pool.slots[k]) if pool.slots[k] in PRIORITY else len(PRIORITY),pool.slots[k]))
def text_probe(key):
 payload={'model':'agnes-2.5-flash','messages':[{'role':'user','content':'Return exactly AFP_OK and nothing else.'}],'max_tokens':64,'temperature':0}
 req=urllib.request.Request(images.roya.BASE.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=35)as response:data=json.load(response)
  content=data.get('choices',[{}])[0].get('message',{}).get('content')
  if isinstance(content,list):content=''.join(x.get('text','')for x in content if isinstance(x,dict))
  return {'status':'healthy' if isinstance(content,str) and content.strip()=='AFP_OK' else 'nonconforming_response','http_status':200,'attempts':1}
 except urllib.error.HTTPError as exc:
  code=exc.code;exc.close();return {'status':'authentication_rejected' if code==401 else 'billing_required' if code==402 else 'rate_limited' if code==429 else 'provider_error','http_status':code,'attempts':1}
 except Exception:return {'status':'transport_or_format_failure','attempts':1}
def image_probe(key,item,cfg):
 import blog_reference_scene as scene
 payload={'model':cfg['model'],'size':cfg['size'],'return_base64':True,'prompt':scene.prompt(item,'loxblog'),'extra_body':{'response_format':'b64_json','image':scene.references(item)}}
 req=urllib.request.Request(cfg['endpoint'],data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=90)as response:data=json.load(response)
  row=(data.get('data')or[{}])[0]
  import base64
  if row.get('b64_json'):raw=base64.b64decode(row['b64_json'],validate=True)
  elif isinstance(row.get('url'),str) and row['url'].startswith('https://'):
   with urllib.request.urlopen(row['url'],timeout=45)as response:raw=response.read(12*1024*1024+1)
  else:return {'status':'no_usable_image','http_status':200,'attempts':1}
  if len(raw)>12*1024*1024:raise ValueError()
  pic=Image.open(io.BytesIO(raw));pic.verify();pic=Image.open(io.BytesIO(raw));w,h=pic.size
  if min(w,h)<512 or max(w,h)>10000 or w<=h:raise ValueError()
  return {'status':'image_healthy','http_status':200,'attempts':1,'width':w,'height':h,'image_sha256':hashlib.sha256(raw).hexdigest(),'visual_publication_approved':False}
 except urllib.error.HTTPError as exc:
  code=exc.code
  try:error=AgnesProviderError(code,exc.read(8192),exc.headers.get('Retry-After'))
  except Exception:error=AgnesProviderError(code)
  exc.close()
  row={'status':{401:'authentication_rejected',402:'billing_required',403:'image_scope_denied',429:'rate_limited',503:'temporarily_unavailable'}.get(code,'provider_error'),'http_status':code,'attempts':1}
  if error.provider_code:row['provider_code']=error.provider_code
  return row
 except Exception:return {'status':'transport_or_format_failure','attempts':1}
def main():
 from blog_image_connection import settings
 from blog_image_queue import provider_slot
 from blog_image_backpressure import require_open,ImageProviderBusy,defer,mark_success
 cfg=settings(images.roya.BASE.AGNES_BASE);pool=images.roya.BASE._key_pool;keys=selected(pool)
 report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'connection':cfg,'scope':'One tiny text completion per unique previously healthy key; at most one image request per freshly healthy unique key. Diagnostic comparison only, no automatic production rerouting.','post_submissions':0,'complete_text':False,'complete_image':False,'status':'checking_text','keys':[]}
 def save():
  raw=json.dumps(report,indent=2).encode();path=ROOT/OUT;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  images.checkpoint_asset(OUT,raw,ROOT)
 try:
  for key in keys:
   name=pool.slots[key];report['keys'].append({'secret_name':name,'text':text_probe(key),'image':{'status':'not_tested'}})
  report['complete_text']=True;report['status']='waiting_shared_cooldown';save()
  deadline=time.monotonic()+1200
  while True:
   images.git(['fetch','--quiet','origin','main'],ROOT)
   try:require_open(ROOT);break
   except ImageProviderBusy as busy:
    report['retry_at_epoch']=busy.retry_at
    if time.monotonic()>=deadline:report['status']='image_deferred_shared_cooldown';return 0
    time.sleep(min(30,max(1,busy.retry_at-time.time())))
  token=hashlib.sha256(('key-audit|'+os.getenv('GITHUB_RUN_ID','')).encode()).hexdigest()[:32]
  with provider_slot('keyaudit',token):
   images.git(['fetch','--quiet','origin','main'],ROOT)
   require_open(ROOT)
   last_start=0;last_result=None
   for key,row in zip(keys,report['keys']):
    if row['text']['status']!='healthy':row['image']={'status':'not_tested_text_not_healthy'};continue
    time.sleep(max(0,60-(time.monotonic()-last_start)))
    last_start=time.monotonic()
    item={'key':'key-audit-'+row['secret_name'],'family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'بررسی فاصله خطوط نوار تیپ پیاز','summary':'آزمون قابلیت تصویر با محصول مرجع و خطوط نصب شده نوار تیپ در ردیف پیاز؛ این تصویر فقط برای آزمون است و هیچ پست یا تصویر تجاری منتشر نخواهد شد.'}}
    row['image']=image_probe(key,item,cfg);last_result=row['image'];report['status']='checking_images';save()
    print(json.dumps(row),flush=True)
    # Compare distinct credentials at <=1 image/minute under one exclusive lock.
    # A rate-limit response ends the comparison, never rotates around a quota.
    if last_result.get('http_status')==429:report['status']='stopped_rate_limit';break
   else:report['status']='completed';report['complete_image']=True
   if last_result and last_result.get('status')=='image_healthy':mark_success(ROOT,images.checkpoint_asset)
   elif last_result and last_result.get('provider_code')=='image_queue_full':defer(ROOT,time.time()+300,images.checkpoint_asset)
 except Exception as exc:
  report['status']='blocked_'+type(exc).__name__
 finally:
  report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 return 0
if __name__=='__main__':raise SystemExit(main())
