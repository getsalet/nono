"""Bounded scheduled recovery of the same owned pilot, with provider-aware cooldown."""
import datetime,hashlib,time
from .queue import DATA,OUT,load_json,atomic_json,utcnow,age_hours
from .client import ImageProviderError,CapabilityError
from .progress import update
from .recovery import circuit_open
from automation.blog_image_queue import ImageQueueBusy
from .image_transport import AdmissionBlocked
TOPIC='agri-af1a4b491d83';REQUEST='queue-aware-pilot-resume-v1'
def validate_request(req):
 if req.get('request_id')!=REQUEST or req.get('topic_id')!=TOPIC or req.get('post_id')!=524163 or req.get('max_additional_cycles')!=2 or req.get('max_new_posts')!=0 or req.get('diagnostic_run_id')!=40117693942:raise ValueError('Explicit bounded same-post recovery required')

def defer_provider(exc):
 p=OUT/'provider-circuit.json';old=load_json(p) if p.exists() else {};now=time.time()
 old_deadline=old.get('retry_at_epoch',0)
 if old.get('open') and 'retry_at_epoch' not in old:
  old_deadline=datetime.datetime.fromisoformat(old['at']).timestamp()+3600
 failures=min(4,old.get('queue_full_count',0)+1);delay=min(1800,300*2**(failures-1))
 deadline=max(old_deadline,now+delay,now+(exc.retry_after_seconds or 0))
 atomic_json(p,{'open':True,'at':utcnow(),'retry_at_epoch':deadline,'retry_at':datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat(),'reason':exc.provider_code or exc.category,'queue_full_count':failures,'backoff_seconds':delay,'scope':'image generation only; never rotate a key around provider limits'})
 return deadline

def run():
 req=load_json(DATA/'pilot-resume-request.json');validate_request(req)
 config=load_json(DATA/'config.json')
 if TOPIC not in config.get('publication_holds',{}):return None
 receipt_path=OUT/'pilot-resume'/REQUEST/'receipt.json';state=load_json(receipt_path) if receipt_path.exists() else {'request_id':REQUEST,'cycles_started':0,'status':'waiting'}
 if state.get('status')=='verified':return None
 if state['cycles_started']>=2:
  update('بودجه بازیابی مقاله تمام شد؛ بررسی سرویس لازم است',0,TOPIC,status='awaiting_review');return {'status':'pilot_recovery_budget_exhausted','published_posts':0}
 if circuit_open():
  update('صف تصویر سرویس پر است؛ منتظر پایان دوره انتظار برای ادامه همان مقاله',20,TOPIC,status='provider_cooldown');return {'status':'provider_cooldown','published_posts':0,'model_calls':0}
 from .revise import run as revise
 rev=OUT/'new'/TOPIC/'revisions/site-style-v2';rp=rev/'receipt.json';before=load_json(rp)['attempts']
 state.update(cycles_started=state['cycles_started']+1,status='resuming',at=utcnow());atomic_json(receipt_path,state)
 try:
  result=revise(recovery_extension=req)
  if result.get('status') not in ('revised','already_revised'):raise ValueError('Same-post recovery not verified')
  config=load_json(DATA/'config.json');config['publication_holds'].pop(TOPIC,None);atomic_json(DATA/'config.json',config)
  atomic_json(OUT/'provider-circuit.json',{'open':False,'at':utcnow(),'reason':'same_pilot_verified'})
  state.update(status='verified',completed_at=utcnow(),result=result);atomic_json(receipt_path,state)
  return {'status':'pilot_revised_verified','result':result,'new_posts_created':0}
 except (ImageQueueBusy,AdmissionBlocked):
  # No provider request was admitted; do not burn the reserved recovery budget.
  current=load_json(rp);current['attempts']=before;atomic_json(rp,current)
  state.update(cycles_started=state['cycles_started']-1,status='shared_admission_deferred',at=utcnow());atomic_json(receipt_path,state)
  update('صف مشترک یا دوره انتظار فعال است؛ درخواست تصویر ارسال نشد',20,TOPIC,status='provider_cooldown')
  return {'status':'shared_image_admission_deferred','model_calls':0,'published_posts':0}
 except ImageProviderError as exc:
  deadline=defer_provider(exc)
  if exc.http_status in (401,402,403) or exc.provider_code=='insufficient_quota':state['cycles_started']=2
  state.update(status='provider_deferred',reason=exc.provider_code or exc.category,retry_at_epoch=deadline,at=utcnow());atomic_json(receipt_path,state)
  update('ادامه مقاله به‌دلیل محدودیت سرویس تصویر به تعویق افتاد',20,TOPIC,status='provider_cooldown')
  return {'status':'provider_deferred','reason':exc.provider_code or exc.category,'published_posts':0}
 except Exception as exc:
  state.update(status='blocked',cycles_started=2,error_type=type(exc).__name__,at=utcnow());atomic_json(receipt_path,state)
  update('بازیابی همان مقاله متوقف شد؛ خروجی موجود حفظ شد',20,TOPIC,status='awaiting_review')
  return {'status':'pilot_recovery_blocked','published_posts':0}
