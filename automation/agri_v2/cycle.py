"""One bounded, explicit production cycle; schedules accept only publication-authorized briefs."""
import argparse,json,tempfile
from pathlib import Path
from .queue import DATA,OUT,load_json,atomic_json,get_topic,age_hours,utcnow
from .pipeline import draft,check_brief,digest,validate_article,validate_for_publication
from .wordpress import WordPress,WPError
from .healthcheck import audit
from .progress import update,failed

def run(request_path=None,scheduled=False,_research_done=False):
 if scheduled and (DATA/'image-key-audit-request.json').exists():
  from .image_key_audit import run as audit_images
  audit_result=audit_images()
  if audit_result is not None:return audit_result
 if scheduled and (DATA/'image-tuning-resume-request.json').exists():
  from .tuning_resume import run as resume_tuning
  tuning=resume_tuning()
  if tuning is not None:return tuning
 config=load_json(DATA/'config.json')
 if not config.get('publication_enabled'):return {'status':'publication_disabled','model_calls':0}
 if scheduled and not config.get('automatic_generation'):return {'status':'automatic_generation_disabled','model_calls':0}
 if scheduled and (DATA/'pilot-resume-request.json').exists():
  from .pilot_resume import run as resume_pilot
  recovery=resume_pilot()
  if recovery is not None:return recovery
 if request_path:
  request=load_json(request_path)
  if request.get('publish_authorized') is not True or request.get('max_new_posts')!=1:raise ValueError('Single-post authorization required')
  candidates=[request['topic_id']]
 else:
  candidates=[]
  for p in sorted((DATA/'briefs').glob('*.json')):
   b=load_json(p)
   if b.get('publish_authorized') is True:candidates.append(b['topic_id'])
 for ident in candidates:
  if ident in config.get('publication_holds',{}):continue
  from .recovery import circuit_open
  if circuit_open():
   update('سرویس مدل در دوره انتظار یک‌ساعته است؛ انتشار انجام نشد',0,status='provider_cooldown')
   return {'status':'provider_cooldown','published_posts':0,'model_calls':0}
  get_topic('new',ident)
  rp=OUT/'new'/ident/'wordpress-receipt.json'
  if rp.exists() and load_json(rp).get('public_verified') is True:continue
  bp=DATA/'briefs'/f'{ident}.json';brief=load_json(bp);topic=get_topic('new',ident);check_brief(topic,brief)
  if brief.get('publish_authorized') is not True:raise ValueError('Brief publication not authorized')
  attempts_path=OUT/'new'/ident/'cycle-attempts.json';attempts=load_json(attempts_path) if attempts_path.exists() else {'attempts':0}
  if attempts['attempts']>=2:
   atomic_json(OUT/'research'/f'{ident}.json',{'topic_id':ident,'status':'needs_review','reason':'production_retry_budget_exhausted','at':utcnow()})
   continue
  update('بررسی اتصال و موضوع آماده',5,ident,topic['title'])
  print("Stage: authenticated WordPress preflight",flush=True)
  wp=WordPress();connection=wp.preflight();update('اتصال وردپرس تأیید شد',10)
  print("Stage: fresh public inventory",flush=True)
  inventory=wp.inventory() # failure/empty/pagination errors stop before any paid model call
  update('موجودی تازه سایت دریافت شد',20)
  hp=DATA/'health/latest.json'
  if not hp.exists() or age_hours(load_json(hp)['checked_at'])>24:
   report=audit();atomic_json(hp,report)
  attempts['attempts']+=1;attempts['last_started_at']=utcnow();atomic_json(attempts_path,attempts)
  with tempfile.TemporaryDirectory() as tmp:
   ip=Path(tmp)/'inventory.json';atomic_json(ip,inventory)
   print("Stage: generate or resume one draft and three images",flush=True)
   folder=OUT/'new'/ident;sp=folder/'state.json'
   staged=sp.exists() and load_json(sp).get('status')=='draft_created'
   if staged:
    if load_json(sp).get('brief_sha256')!=digest(brief):raise ValueError('Staged brief changed')
    validate_article(load_json(folder/'article.json'),topic,brief)
    if not (folder/'wordpress-draft-payload.json').exists() or not all((folder/f'image-{n}.webp').exists() for n in range(1,4)):raise ValueError('Staged artifacts incomplete')
   else:
    try:draft(ident,bp,ip,hp,allow_calls=True)
    except Exception as exc:
     from .client import CapabilityError
     if isinstance(exc,CapabilityError):
      from .recovery import open_circuit
      open_circuit()
     raise
  print("Stage: upload media, publish one owned post and verify public URL",flush=True)
  validate_for_publication(load_json(OUT/'new'/ident/'article.json'))
  update('بارگذاری رسانه و انتشار یک نوشته',80)
  result=wp.publish(OUT/'new'/ident,topic,brief,authorized=True)
  atomic_json(OUT/'latest-cycle.json',{'status':'success','topic_id':ident,'result':result,'connection':connection,'inventory_count':len(inventory['records']),'completed_at':utcnow()})
  update('انتشار و صفحه عمومی تأیید شد',100,status='success')
  return result
 if scheduled and not _research_done and config.get('research_feeder',{}).get('enabled'):
  from .research import prepare_one
  wp=WordPress();wp.preflight();inventory=wp.inventory()
  result=prepare_one(inventory)
  if result.get('status')=='brief_ready':return run(scheduled=True,_research_done=True)
  return result
 update('اجرای زمان‌بند پایان یافت؛ مقاله آماده برای انتشار وجود ندارد',0,topic_id='',topic_title='',status='idle')
 return {'status':'no_ready_unpublished_brief','model_calls':0,'published_posts':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--request');p.add_argument('--scheduled',action='store_true');a=p.parse_args()
 try:r=run(a.request,a.scheduled);print(json.dumps(r,ensure_ascii=False));return 0
 except Exception as e:
  failed()
  if isinstance(e,WPError):print("WordPress stage: "+str(e),flush=True)
  elif isinstance(e,ValueError):print("Validation blocked: "+str(e)[:160],flush=True)
  atomic_json(OUT/'latest-cycle-error.json',{'status':'blocked_or_failed','at':utcnow(),'reason':'Inspect sanitized job stages and tests; no raw provider/auth messages persisted.'})
  print('Cycle stopped safely; staged state preserved. No raw credential/provider error is logged.');return 2
if __name__=='__main__':raise SystemExit(main())
