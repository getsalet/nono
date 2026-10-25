"""Pre-request routing among independently image-verified slots; no limit evasion."""
import time
from .queue import OUT,load_json,atomic_json
from .healthcheck import SLOTS
from .image_transport import AdmissionBlocked
BLOCKED={'authentication_rejected','image_scope_denied','invalid_auth','forbidden','quota_limited','rate_limited','billing_required','disabled'}
def choose(pool,cursor,evidence,now):
 """Return one candidate without sending requests or relaxing shared limits."""
 seen=set();unique=[]
 for name,key in pool:
  if name not in SLOTS:raise AdmissionBlocked('Out-of-scope image credential')
  if key and key not in seen:unique.append((name,key));seen.add(key)
 if not unique:raise AdmissionBlocked('No unique image-verified credential')
 for d in evidence:
  if not isinstance(d,dict):raise AdmissionBlocked('Invalid shared image evidence')
  if d.get('shared_block')=='billing_required':raise AdmissionBlocked('Shared billing hold')
  for field in ('retry_at_epoch','shared_retry_at_epoch'):
   value=d.get(field,0)
   if not isinstance(value,(int,float)) or value>now:raise AdmissionBlocked('Shared image cooldown active')
 for offset in range(len(unique)):
  index=(cursor+offset)%len(unique);name,key=unique[index];available=True
  for d in evidence:
   state=d.get('keys',{}).get(name,{})
   deadline=state.get('retry_at_epoch',0)
   if not isinstance(deadline,(int,float)) or deadline>now or state.get('status') in BLOCKED:available=False;break
  if available:return (name,key),index+1
 raise AdmissionBlocked('No currently available image-verified credential')
def route(pool,cursor,env):
 if env.get('GITHUB_ACTIONS')!='true':return choose(pool,cursor,[],time.time())[0]
 from .recovery import circuit_open
 from .image_transport import shared_evidence
 if circuit_open():raise AdmissionBlocked('Local shared provider cooldown active')
 path=OUT/'image-key-routing.json';state=load_json(path) if path.exists() else {}
 selected,next_cursor=choose(pool,state.get('cursor',cursor),shared_evidence(),time.time())
 # Slot names only. Never save credentials or fingerprints. Shared workflow
 # concurrency serializes this cursor; the lease rechecks admission afterward.
 atomic_json(path,{'version':1,'cursor':next_cursor,'last_selected_slot':selected[0],'selected_at_epoch':time.time(),'scope':'pre-request verified-pool selection; no automatic retry after provider error'})
 return selected
