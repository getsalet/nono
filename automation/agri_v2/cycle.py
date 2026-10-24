"""One bounded, explicit production cycle; schedules accept only publication-authorized briefs."""
import argparse,json,tempfile
from pathlib import Path
from .queue import DATA,OUT,load_json,atomic_json,get_topic,age_hours,utcnow
from .pipeline import draft,check_brief
from .wordpress import WordPress,WPError
from .healthcheck import audit

def run(request_path=None,scheduled=False):
 config=load_json(DATA/'config.json')
 if scheduled and not config.get('automatic_generation'):return {'status':'automatic_generation_disabled','model_calls':0}
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
  get_topic('new',ident)
  rp=OUT/'new'/ident/'wordpress-receipt.json'
  if rp.exists() and load_json(rp).get('public_verified') is True:continue
  bp=DATA/'briefs'/f'{ident}.json';brief=load_json(bp);topic=get_topic('new',ident);check_brief(topic,brief)
  if brief.get('publish_authorized') is not True:raise ValueError('Brief publication not authorized')
  attempts_path=OUT/'new'/ident/'cycle-attempts.json';attempts=load_json(attempts_path) if attempts_path.exists() else {'attempts':0}
  if attempts['attempts']>=2:raise ValueError('Retry budget exhausted; human inspection required')
  print("Stage: authenticated WordPress preflight",flush=True)
  wp=WordPress();connection=wp.preflight()
  print("Stage: fresh public inventory",flush=True)
  inventory=wp.inventory() # failure/empty/pagination errors stop before any paid model call
  hp=DATA/'health/latest.json'
  if not hp.exists() or age_hours(load_json(hp)['checked_at'])>24:
   report=audit();atomic_json(hp,report)
  attempts['attempts']+=1;attempts['last_started_at']=utcnow();atomic_json(attempts_path,attempts)
  with tempfile.TemporaryDirectory() as tmp:
   ip=Path(tmp)/'inventory.json';atomic_json(ip,inventory)
   print("Stage: generate or resume one draft and three images",flush=True)
   draft(ident,bp,ip,hp,allow_calls=True)
  print("Stage: upload media, publish one owned post and verify public URL",flush=True)
  result=wp.publish(OUT/'new'/ident,topic,brief,authorized=True)
  atomic_json(OUT/'latest-cycle.json',{'status':'success','topic_id':ident,'result':result,'connection':connection,'inventory_count':len(inventory['records']),'completed_at':utcnow()})
  return result
 return {'status':'no_ready_unpublished_brief','model_calls':0,'published_posts':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--request');p.add_argument('--scheduled',action='store_true');a=p.parse_args()
 try:r=run(a.request,a.scheduled);print(json.dumps(r,ensure_ascii=False));return 0
 except Exception as e:
  if isinstance(e,WPError):print("WordPress stage: "+str(e),flush=True)
  elif isinstance(e,ValueError):print("Validation blocked: "+str(e)[:160],flush=True)
  atomic_json(OUT/'latest-cycle-error.json',{'status':'blocked_or_failed','at':utcnow(),'reason':'Inspect sanitized job stages and tests; no raw provider/auth messages persisted.'})
  print('Cycle stopped safely; staged state preserved. No raw credential/provider error is logged.');return 2
if __name__=='__main__':raise SystemExit(main())
