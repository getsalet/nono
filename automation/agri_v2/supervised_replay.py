"""Wait for admission, then consume the existing two-image request once; no new budget."""
import json,time
from .queue import DATA,OUT,load_json,atomic_json,utcnow
from .recovery import circuit_open
from .tuning_resume import run as resume
ID='one-hour-supervised-replay-v1'
def run():
 req=load_json(DATA/'one-hour-supervision-request.json');target=load_json(DATA/'image-tuning-resume-request.json')
 if req.get('request_id')!=ID or req.get('existing_resume_request_id')!='verified-pool-scene-resume-v1' or target['request_id']!=req['existing_resume_request_id'] or req.get('max_resume_invocations')!=1 or req.get('max_new_image_budget')!=0 or req.get('max_post_mutations')!=0 or not isinstance(req.get('window_end_epoch'),(int,float)):raise ValueError('Exact one-window existing-budget supervision required')
 path=OUT/'supervision'/ID/'receipt.json'
 if path.exists():return {'status':'supervision_already_reserved'}
 state={'request_id':ID,'started_at':utcnow(),'resume_invocations':0,'new_image_budget':0,'post_mutations':0,'status':'waiting_existing_deadline'};atomic_json(path,state)
 while time.time()<req['window_end_epoch']:
  circuit=load_json(OUT/'provider-circuit.json');deadline=max(target['not_before_epoch'],circuit.get('retry_at_epoch',0) if circuit.get('open') else 0)
  if time.time()<deadline or circuit_open():time.sleep(min(30,max(1,req['window_end_epoch']-time.time())));continue
  state.update(resume_invocations=1,status='consuming_existing_request',at=utcnow());atomic_json(path,state)
  state.update(result=resume(),status='existing_request_finished',finished_at=utcnow());atomic_json(path,state);return {'status':state['status'],'result':state['result']}
 state.update(status='window_ended_before_admission',finished_at=utcnow());atomic_json(path,state);return {'status':state['status'],'model_calls':0}
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
