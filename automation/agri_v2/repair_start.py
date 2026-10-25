"""One owner-authorized repaired cycle, after existing provider deadlines; no budget reset."""
import json,time
from .queue import DATA,OUT,load_json,atomic_json,utcnow
from .recovery import circuit_open
from .safe_activation import authorized
from .image_quality import REVIEW_POLICY
from .media_policy import POLICY
from .progress import update,failed
from .failure_diagnostics import failure_details
ID='owner-repair-topic-routed-v1'
def validate(req):
 if (req.get('request_id')!=ID or req.get('authorized') is not True
     or req.get('max_cycle_invocations')!=1 or req.get('max_posts_per_run')!=1
     or req.get('preserve_publication_holds') is not True
     or req.get('review_policy')!=REVIEW_POLICY or req.get('scene_policy')!=POLICY
     or req.get('max_wait_seconds')!=2700):raise ValueError('Exact bounded repaired-cycle request required')
def deadline():
 p=OUT/'provider-circuit.json';row=load_json(p) if p.exists() else {}
 if row.get('open') is not True:return 0
 if 'retry_at_epoch' in row:return row['retry_at_epoch']
 import datetime
 return datetime.datetime.fromisoformat(row['at']).timestamp()+3600

def run():
 req=load_json(DATA/'repair-start-request.json');validate(req)
 if not authorized(DATA):raise ValueError('Owner startup authorization missing')
 path=OUT/'repair-start'/ID/'receipt.json'
 old=load_json(path) if path.exists() else {}
 if old.get('cycle_invocations',0)>=1:return {'status':'repair_cycle_already_reserved','model_calls':0}
 end=time.time()+req['max_wait_seconds']
 state={'request_id':ID,'status':'waiting_existing_provider_deadline','cycle_invocations':0,'started_at':utcnow(),'scene_policy':POLICY,'review_policy':REVIEW_POLICY,'no_budget_reset':True}
 atomic_json(path,state)
 update('اصلاحات اعمال شد؛ پیش از پایان انتظار سرویس درخواست جدیدی ارسال نمی‌شود',0,topic_id='',topic_title='',status='repair_waiting_provider')
 while circuit_open():
  due=deadline()
  if due>end or time.time()>=end:
   state.update(status='existing_deadline_exceeds_wait_budget',completed_at=utcnow());atomic_json(path,state)
   return {'status':state['status'],'model_calls':0,'published_posts':0}
  time.sleep(min(30,max(1,due-time.time())))
 state.update(status='cycle_reserved',cycle_invocations=1,reserved_at=utcnow());atomic_json(path,state)
 from .cycle import run as cycle
 try:
  result=cycle(scheduled=True)
 except Exception as exc:
  state.update(status='cycle_stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(path,state)
  failed('چرخه اصلاح‌شده متوقف شد؛ دسته خطای امن در رسید ثبت شد')
  return {'status':state['status'],'failure':state['failure']}
 state.update(status='cycle_finished',result=result,completed_at=utcnow());atomic_json(path,state)
 return {'status':state['status'],'result':result}
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
