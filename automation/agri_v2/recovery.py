"""One explicitly requested recovery, never a scheduled infinite retry."""
from .queue import DATA,OUT,load_json,atomic_json,utcnow,age_hours
import datetime,time
from .client import CapabilityError
from .progress import update

def circuit_open():
 p=OUT/'provider-circuit.json'
 if not p.exists():return False
 d=load_json(p)
 if d.get('open') is not True:return False
 return d['retry_at_epoch']>time.time() if 'retry_at_epoch' in d else age_hours(d['at'])<1

def open_circuit():
 atomic_json(OUT/'provider-circuit.json',{'open':True,'at':utcnow(),'cooldown_hours':1,'reason':'provider_transient_failure','no_secrets':True})

def recover_once():
 from .revise import run
 request=load_json(DATA/'research-request.json');authorization=request.get('pilot_recovery',{})
 if request.get('request_id')!='research-feeder-rollout-v1':raise ValueError('Unrecognized one-off request')
 ident='agri-af1a4b491d83'
 if authorization.get('topic_id')!=ident or authorization.get('max_additional_cycles')!=1 or authorization.get('authorized') is not True:raise ValueError('One explicit pilot recovery required')
 gate=OUT/'recovery'/f"{request['request_id']}.json"
 if gate.exists():return {'status':'recovery_already_attempted'}
 if ident not in load_json(DATA/'config.json').get('publication_holds',{}):return {'status':'pilot_not_held'}
 atomic_json(gate,{'status':'started','at':utcnow(),'max_additional_cycles':1})
 try:
  result=run()
  if result.get('status') not in ('revised','already_revised'):raise ValueError('Recovery not verified')
  config=load_json(DATA/'config.json');config['publication_holds'].pop(ident,None);atomic_json(DATA/'config.json',config)
  atomic_json(gate,{'status':'verified','at':utcnow(),'result':result})
  atomic_json(OUT/'provider-circuit.json',{'open':False,'at':utcnow()})
  return result
 except CapabilityError:
  open_circuit();atomic_json(gate,{'status':'provider_failed','at':utcnow(),'hold_retained':True})
  update('بازیابی تصویر ناموفق؛ توقف موقت درخواست تصویر و حفظ پیشرفت',0,ident,status='provider_cooldown')
  return {'status':'recovery_provider_failed','hold_retained':True}
 except Exception:
  atomic_json(gate,{'status':'blocked','at':utcnow(),'hold_retained':True});raise
if __name__=='__main__':
 import json
 print(json.dumps(recover_once(),ensure_ascii=False))
