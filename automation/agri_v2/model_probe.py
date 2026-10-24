"""User-authorized alternate-model test: exact pending production image, no publication."""
import hashlib,json,os,time,urllib.request,urllib.error
from .queue import DATA,OUT,ROOT,load_json,atomic_json,get_topic,utcnow,age_hours
from .healthcheck import API_BASE,SLOTS,MAX_RESPONSE
from .client import render_image
from .image_transport import admission,AdmissionBlocked
from .image_diagnostic import stop_for_limits
from .media_policy import image_prompt,reference_images
from .progress import update
from .recovery import circuit_open
from automation.agnes_key_pool import AgnesProviderError
from automation.blog_image_queue import ImageQueueBusy
ID='image-model-switch-21-v1';TOPIC='agri-af1a4b491d83';MODELS=['agnes-image-2.1-flash','agnes-image-2.0-flash']
def validate(req):
 if req.get('request_id')!=ID or req.get('models')!=MODELS or req.get('max_requests')!=2 or req.get('topic_id')!=TOPIC or req.get('publication_authorized') is not False:raise ValueError('Explicit bounded model-switch test required')
def payload(model,topic):
 if model not in MODELS:raise ValueError('Unapproved alternate model')
 return {'model':model,'prompt':image_prompt(topic,2),'size':'1024x768','return_base64':True,'extra_body':{'image':reference_images(),'response_format':'b64_json'}}
def probe(key,body):
 req=urllib.request.Request(API_BASE+'/images/generations',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'AFP-user-authorized-model-switch'})
 start=time.monotonic()
 try:
  with urllib.request.urlopen(req,timeout=240) as r:
   raw=r.read(MAX_RESPONSE+1)
   if len(raw)>MAX_RESPONSE:raise ValueError('Response too large')
   obj=json.loads(raw)
  if obj.get('model') and obj['model']!=body['model']:return {'state':'model_mismatch','http_status':200},None
  image=render_image(obj)
  return {'state':'verified_image_bytes','http_status':200,'elapsed_seconds':round(time.monotonic()-start,2),'declared_model':obj.get('model')},image
 except urllib.error.HTTPError as exc:
  status=exc.code;raw=exc.read(20000);retry=exc.headers.get('Retry-After');exc.close();safe=AgnesProviderError(status,raw,retry)
  return {'state':'provider_rejected','http_status':status,'provider_code':safe.provider_code,'retry_after_seconds':safe.rate_limit_retry_after_seconds,'elapsed_seconds':round(time.monotonic()-start,2)},None
 except Exception as e:return {'state':'transport_or_decode_failed','error_type':type(e).__name__,'http_status':None},None

def run():
 req=load_json(DATA/'model-switch-request.json');validate(req);dest=OUT/'model-switch'/ID;rp=dest/'report.json'
 if rp.exists():return {'status':'already_reserved','model_calls':0}
 report={'request_id':ID,'started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'cases':[],'max_requests':2,'post_submissions':0,'production_changed':False,'manual_visual_review':False}
 atomic_json(rp,report)
 try:
  if circuit_open():report['status']='provider_cooldown_honored';return report
  hp=load_json(DATA/'health/latest.json')
  if age_hours(hp['checked_at'])>24:raise ValueError('Previous credential capability evidence expired')
  slot=next((s for s in hp.get('eligible_image_slots',[]) if s in SLOTS and os.environ.get(s,'').strip()),None)
  if not slot:raise ValueError('No first-fifteen credential with image evidence')
  report['slot']=slot;atomic_json(rp,report);key=os.environ[slot].strip();topic=get_topic('new',TOPIC)
  first=OUT/'new'/TOPIC/'revisions/site-style-v2/image-1.webp'
  report['preserved_image_1_sha256']=hashlib.sha256(first.read_bytes()).hexdigest()
  for model in req['models']:
   body=payload(model,topic)
   with admission(slot,body,os.environ):
    row={'model':model,'attempts':1,'started_at':utcnow(),'prompt_sha256':hashlib.sha256(body['prompt'].encode()).hexdigest(),'reference_conditioned':True};report['cases'].append(row);atomic_json(rp,report)
    update('آزمون مدل تصویر جایگزین: '+model,40,TOPIC,topic['title'],status='diagnosing_image')
    result,raw=probe(key,body);row.update(result,finished_at=utcnow())
    if raw:
     path=dest/(model+'.webp');path.write_bytes(raw);row.update(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),manual_visual_review=False)
    atomic_json(rp,report)
   if raw:report.update(status='candidate_requires_visual_review',candidate=model);return report
   if stop_for_limits(row):report['status']='stopped_shared_or_account_limit';return report
   # A second model is tested only for availability/request rejection, never around quota/rate/queue limits.
  report['status']='no_verified_alternate_model';return report
 except (AdmissionBlocked,ImageQueueBusy):report['status']='shared_admission_deferred';return report
 except Exception as e:report.update(status='preflight_blocked',error_type=type(e).__name__);return report
 finally:
  report['finished_at']=utcnow();atomic_json(rp,report)
  update('آزمون مدل جایگزین پایان یافت؛ نتیجه و تصویر نیازمند بررسی است',40,TOPIC,status='image_diagnostic_complete')
if __name__=='__main__':
 r=run();print(json.dumps({'status':r['status'],'candidate':r.get('candidate'),'post_submissions':0},ensure_ascii=False))
