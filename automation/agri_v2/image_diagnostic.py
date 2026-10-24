"""One same-key, same-model differential probe. No publication or secret export."""
import hashlib,json,os,re,subprocess,time,urllib.error,urllib.request
from .queue import DATA,OUT,ROOT,load_json,atomic_json,utcnow,age_hours,get_topic
from .healthcheck import API_BASE,IMAGE_MODEL,SLOTS,MAX_RESPONSE
from .client import render_image,CapabilityError
from .media_policy import reference_images,image_prompt
from .progress import update
from automation.agnes_key_pool import AgnesProviderError
from automation.blog_image_queue import Queue,ImageQueueBusy
REQUEST_ID='pilot-image-differential-v1'
TOPIC='agri-af1a4b491d83'
class DiagnosticBlocked(ValueError):pass

def shared_guard(slot):
 # Read latest public routing/cooldown evidence; never read secret values from Git.
 subprocess.run(['git','fetch','--quiet','origin','main:refs/remotes/origin/main'],cwd=ROOT,check=True,capture_output=True)
 for path in ['data/blog-image-provider-backpressure.json','data/blog-image-key-pool-state.json']:
  p=subprocess.run(['git','show','origin/main:'+path],cwd=ROOT,check=True,capture_output=True)
  try:d=json.loads(p.stdout)
  except ValueError:raise DiagnosticBlocked('Unreadable shared provider evidence') from None
  if d.get('shared_block')=='billing_required':raise DiagnosticBlocked('Shared billing hold; no provider request')
  deadline=max(d.get('retry_at_epoch',0),d.get('shared_retry_at_epoch',0),d.get('keys',{}).get(slot,{}).get('retry_at_epoch',0))
  if not isinstance(deadline,(int,float)) or deadline>time.time():raise DiagnosticBlocked('Shared cooldown active; no provider request')
  if d.get('keys',{}).get(slot,{}).get('status') in ('authentication_rejected','image_scope_denied'):raise DiagnosticBlocked('Credential unavailable for image scope')

def payload(prompt,refs=True,omit_n=False):
 d={'model':IMAGE_MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json'}}
 if not omit_n:d['n']=1
 if refs:d['extra_body']['image']=reference_images()
 return d

def probe(key,body):
 began=time.monotonic()
 req=urllib.request.Request(API_BASE+'/images/generations',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'AFP-bounded-image-diagnostic'})
 try:
  with urllib.request.urlopen(req,timeout=180) as r:
   raw=r.read(MAX_RESPONSE+1)
   if len(raw)>MAX_RESPONSE:raise CapabilityError('Provider response too large')
   obj=json.loads(raw)
  image=render_image(obj)
  return {'http_status':200,'state':'verified_image_bytes','elapsed_seconds':round(time.monotonic()-began,2)},image
 except urllib.error.HTTPError as e:
  code=e.code;body=e.read(20000);retry=e.headers.get('Retry-After');e.close();safe=AgnesProviderError(code,body,retry)
  return {'http_status':code,'state':'provider_rejected','provider_code':safe.provider_code,'retry_after_seconds':safe.rate_limit_retry_after_seconds,'elapsed_seconds':round(time.monotonic()-began,2)},None
 except (TimeoutError,urllib.error.URLError):return {'http_status':None,'state':'network_or_timeout'},None
 except Exception:return {'http_status':None,'state':'response_decode_failed'},None

def stop_for_limits(row):
 return row.get('http_status') in (401,402,403,429) or row.get('provider_code') in ('image_queue_full','insufficient_quota','rate_limit_exceeded','rate_limit_error')

def run():
 req=load_json(DATA/'image-diagnostic-request.json')
 if req.get('request_id')!=REQUEST_ID or req.get('topic_id')!=TOPIC or req.get('max_provider_requests')!=4 or req.get('publication_authorized') is not False:raise DiagnosticBlocked('Explicit bounded diagnostic required')
 dest=OUT/'image-diagnostics'/REQUEST_ID;report_path=dest/'report.json'
 if report_path.exists():return {'status':'diagnostic_already_reserved','model_calls':0}
 report={'request_id':REQUEST_ID,'started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'model':IMAGE_MODEL,'max_provider_requests':4,'post_submissions':0,'cases':[],'manual_visual_review':False}
 atomic_json(report_path,report)
 def save():atomic_json(report_path,report)
 try:
  health=load_json(DATA/'health/latest.json')
  if age_hours(health['checked_at'])>24:raise DiagnosticBlocked('Capability evidence expired')
  names=health.get('eligible_image_slots',[])
  slot=next((x for x in names if x in SLOTS and os.environ.get(x,'').strip()),None)
  if not slot:raise DiagnosticBlocked('No healthy first-fifteen image slot available')
  report['slot']=slot;save();key=os.environ[slot].strip();topic=get_topic('new',TOPIC)
  rev=OUT/'new'/TOPIC/'revisions/site-style-v2'
  if not (rev/'image-1.webp').exists():raise DiagnosticBlocked('Preserved image missing')
  report['preserved_image_1_sha256']=hashlib.sha256((rev/'image-1.webp').read_bytes()).hexdigest();save()
  def case(name,body,target=None):
   if len(report['cases'])>=4:raise DiagnosticBlocked('Diagnostic request budget exhausted')
   shared_guard(slot)
   row={'name':name,'started_at':utcnow(),'prompt_sha256':hashlib.sha256(body['prompt'].encode()).hexdigest(),'reference':bool(body['extra_body'].get('image')),'omit_n':'n' not in body,'attempts':1}
   report['cases'].append(row);save()
   token=hashlib.sha256((REQUEST_ID+name).encode()).hexdigest()[:32]
   with Queue().slot('agri-diagnostic',token):
    shared_guard(slot)
    update('آزمون محدود تصویر: '+name,20,TOPIC,topic['title'],status='diagnosing_image')
    result,raw=probe(key,body);row.update(result,finished_at=utcnow())
    if raw:
     asset=dest/(name+'.webp');asset.write_bytes(raw);row.update(path=str(asset.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest())
     # Only exact production prompts can stage pending images. Controls never replace article images.
     if target and not (rev/target).exists():(rev/target).write_bytes(raw);row['staged_revision_path']=str((rev/target).relative_to(ROOT))
    save()
   return row,raw
  control,_=case('plain-control',payload('A plain green leaf on a clean white background. No words, logo or people. Capability check.',refs=False))
  if stop_for_limits(control):report['status']='stopped_account_or_shared_limit';return report
  full,raw=case('exact-image-2',payload(image_prompt(topic,2)),target='image-2.webp')
  if stop_for_limits(full):report['status']='stopped_account_or_shared_limit';return report
  omit_n=False
  if raw is None and control.get('http_status')==200:
   alternate,raw=case('exact-image-2-without-n',payload(image_prompt(topic,2),omit_n=True),target='image-2.webp');omit_n=True
   if stop_for_limits(alternate):report['status']='stopped_account_or_shared_limit';return report
  if raw is None:report['status']='no_production_image_received';return report
  if not (rev/'image-3.webp').exists():
   third,raw=case('exact-image-3',payload(image_prompt(topic,3),omit_n=omit_n),target='image-3.webp')
   if not raw:report['status']='image_2_staged_image_3_blocked';return report
  report['status']='pending_images_staged_visual_review_required';return report
 except ImageQueueBusy:
  report['status']='shared_queue_busy_no_bypass';return report
 except Exception as exc:
  report['status']='diagnostic_preflight_or_transport_blocked';report['error_type']=type(exc).__name__;return report
 finally:
  report['finished_at']=utcnow();save()
  update('آزمون تصویر پایان یافت؛ نتیجه در گزارش تشخیص ثبت شد',20,TOPIC,status='image_diagnostic_complete')
if __name__=='__main__':
 result=run();print(json.dumps({'status':result['status'],'post_submissions':0},ensure_ascii=False))
