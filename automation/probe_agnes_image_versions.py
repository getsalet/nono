#!/usr/bin/env python3
"""Two documented alternate image versions; one same-key request each, no publishing."""
import base64,datetime,hashlib,io,json,os,re,time,urllib.error,urllib.request
from pathlib import Path
from PIL import Image
import blog_generated_image as images
from agnes_key_pool import AgnesProviderError
ROOT=Path(__file__).resolve().parents[1]
REQUEST='data/agnes-image-version-test-request.json'
MODELS=('agnes-image-2.0-flash','agnes-image-2.1-flash')
SLOT='AGNES_API_KEY3'
ENDPOINT='https://apihub.agnes-ai.com/v1/images/generations'
POLICY='bounded-agnes-alternate-image-versions-v1'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def validate(r):
 if (r.get('policy')!=POLICY or not re.fullmatch('[a-f0-9]{32}',str(r.get('request_id','')))or r.get('models')!=list(MODELS)or r.get('slot')!=SLOT or r.get('max_requests')!=2 or r.get('minimum_interval_seconds')!=60):raise RuntimeError('Explicit bounded alternate-version test required')
 return 'data/agnes-image-version-tests/'+r['request_id']+'/report.json'
def material():
 import blog_reference_scene as scene
 item={'key':'matched-alternate-version-test-tape20-onion','family':'tape20','site_title':'نوار تیپ پیاز','_image_article_context':{'title':'فاصله خطوط نوار تیپ در کشت پیاز','summary':'نمای نزدیک ردیف‌های پیاز با برگ‌های باریک لوله‌ای و خطوط نوار تیپ نصب‌شده کنار ریشه؛ یک بسته واقعی نوار تیپ AFP جدا از اتصالات روی خاک قرار دارد. تصویر باید ساده، مرتبط با فاصله خطوط و بدون انسان باشد.'}}
 return scene.prompt(item,'loxblog'),scene.references(item)
def payload(model,prompt,refs):return {'model':model,'size':'1024x768','return_base64':True,'prompt':prompt,'extra_body':{'response_format':'b64_json','image':refs}}
def decode(data):
 row=(data.get('data')or[{}])[0]
 if row.get('b64_json'):raw=base64.b64decode(row['b64_json'],validate=True)
 elif isinstance(row.get('url'),str)and row['url'].startswith('https://'):
  with urllib.request.urlopen(row['url'],timeout=45)as r:raw=r.read(12*1024*1024+1)
 else:raise ValueError('No image')
 if len(raw)>12*1024*1024:raise ValueError('Image too large')
 pic=Image.open(io.BytesIO(raw));pic.verify();pic=Image.open(io.BytesIO(raw)).convert('RGB');w,h=pic.size
 if not 512<=h<w<=10000:raise ValueError('Invalid dimensions')
 from blog_image_watermark import apply,present,TEXT
 marked=apply(pic);out=io.BytesIO();marked.save(out,'WEBP',quality=94,method=6)
 encoded=out.getvalue()
 if not present(Image.open(io.BytesIO(encoded))):raise ValueError('Watermark verification failed')
 return encoded,{'width':w,'height':h,'source_sha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(encoded).hexdigest(),'watermark':TEXT}
def probe(key,body):
 began=time.monotonic();req=urllib.request.Request(ENDPOINT,data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=180)as r:data=json.load(r)
  raw,meta=decode(data);return {**meta,'status':'image_received','http_status':200,'elapsed_seconds':round(time.monotonic()-began,2),'manual_visual_acceptance':False},raw
 except urllib.error.HTTPError as exc:
  code=exc.code
  try:error=AgnesProviderError(code,exc.read(8192),exc.headers.get('Retry-After'))
  except Exception:error=AgnesProviderError(code)
  exc.close();row={'status':{401:'authentication_rejected',402:'billing_required',403:'model_scope_denied',404:'model_or_endpoint_not_found',429:'rate_limited',503:'temporarily_unavailable'}.get(code,'provider_error'),'http_status':code,'elapsed_seconds':round(time.monotonic()-began,2)}
  if error.provider_code:row['provider_code']=error.provider_code
  if code==429 and error.rate_limit_retry_after_seconds is not None:row['retry_after_seconds']=error.rate_limit_retry_after_seconds
  return row,None
 except Exception as exc:return {'status':'transport_or_image_format_failure','error_type':type(exc).__name__,'elapsed_seconds':round(time.monotonic()-began,2)},None

def record_limit(row,lease):
 from blog_image_key_router import state,persist
 from blog_image_backpressure import write_state,retry_at
 code=row.get('http_status')
 if code not in(402,429)and row.get('provider_code')!='insufficient_quota':return
 values=state(ROOT)
 if code==402 or row.get('provider_code')=='insufficient_quota':values['shared_block']='billing_required'
 if code==429:
  stamp=max(time.time()+max(300,row.get('retry_after_seconds',0)),values.get('shared_retry_at_epoch',0),retry_at(ROOT))
  values['shared_retry_at_epoch']=stamp
 persist(ROOT,values,images.checkpoint_asset,lease)
 if code==429:
  try:write_state(ROOT,{'reason':'provider_rate_limited','retry_at_epoch':stamp,'last_failure_epoch':time.time(),'consecutive_queue_full':0,'post_submissions':0},images.checkpoint_asset)
  except Exception:
   if lease is not None:lease.retain=True
   raise RuntimeError('Shared limit checkpoint failed; lease retained')from None

def main():
 from blog_image_account_expansion import shared_open
 from blog_image_key_router import available_at
 from blog_image_queue import provider_slot
 from blog_image_backpressure import ImageProviderBusy
 request=json.loads((ROOT/REQUEST).read_text());path=validate(request)
 images.git(['fetch','--quiet','origin','main'],ROOT)
 if images.git(['cat-file','-e','origin/main:'+path],ROOT,check=False).returncode==0:
  print('Version test already reserved; zero repeated probes.');return 0
 report={'policy':POLICY,'request_id':request['request_id'],'started_at':now(),'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'status':'preflight','slot':SLOT,'endpoint':ENDPOINT,'max_requests':2,'post_submissions':0,'production_model_changed':False,'manual_visual_acceptance':False,'cases':[],'source_docs':['https://agnes-ai.com/doc/agnes-image-20-flash','https://agnes-ai.com/doc/agnes-image-21-flash']}
 def save():
  raw=json.dumps(report,ensure_ascii=False,indent=2).encode();p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);images.checkpoint_asset(path,raw,ROOT)
 save()
 try:
  key=os.getenv(SLOT,'').strip()
  if not key or re.search(r'[,\s]',key):raise RuntimeError('Configured test slot unavailable')
  images.git(['fetch','--quiet','origin','main'],ROOT);shared_open(ROOT)
  stamp=available_at(ROOT,[SLOT])
  if stamp>time.time():raise ImageProviderBusy(stamp)
  prompt,refs=material();report.update(prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),reference_sha256=[hashlib.sha256(x.encode()).hexdigest()for x in refs],size='1024x768',status='testing');save()
  for model in MODELS:
   row={'model':model,'status':'waiting_shared_queue','attempts':0};report['cases'].append(row);save()
   token=hashlib.sha256((request['request_id']+model).encode()).hexdigest()[:32]
   with provider_slot('versiontest',token)as lease:
    images.git(['fetch','--quiet','origin','main'],ROOT);shared_open(ROOT)
    stamp=available_at(ROOT,[SLOT])
    if stamp>time.time():raise ImageProviderBusy(stamp)
    row.update(status='requested',attempts=1,started_at=now());save()
    result,raw=probe(key,payload(model,prompt,refs));row.update(result,finished_at=now())
    if raw:
     asset=path.rsplit('/',1)[0]+'/'+model+'.webp';p=ROOT/asset;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
     row['asset_url']=images.checkpoint_asset(asset,raw,ROOT);row['asset_path']=asset
    save();record_limit(row,lease)
   # Billing, authentication and rate limits stop this same-key experiment.
   if row.get('http_status')in(401,402,429)or row.get('provider_code')=='insufficient_quota':report['status']='stopped_auth_quota_or_rate_limit';break
  else:report['status']='completed'
 except Exception as exc:
  report['status']='deferred_shared_cooldown'if isinstance(exc,ImageProviderBusy)else'blocked_'+type(exc).__name__
  if isinstance(exc,ImageProviderBusy):report['retry_at_epoch']=exc.retry_at
 finally:report['finished_at']=now();save()
 print(json.dumps({'status':report['status'],'cases':[{k:r.get(k)for k in('model','status','http_status')}for r in report['cases']],'post_submissions':0}),flush=True)
 return 0 if report['status']=='completed'else 1
if __name__=='__main__':raise SystemExit(main())
