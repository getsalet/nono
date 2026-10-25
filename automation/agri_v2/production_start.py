"""Explicit start of one normal cycle; recurring work remains on the existing scheduler."""
import json,os
from .queue import DATA,OUT,load_json,atomic_json,utcnow
from .safe_activation import authorized
from .failure_diagnostics import failure_details
from .progress import failed
ID='continuous-editorial-start-v4'
def run():
 req=load_json(DATA/'production-start-request.json')
 if (req.get('request_id')!=ID or req.get('authorized') is not True or req.get('max_new_posts')!=1 or req.get('max_topics_per_cycle')!=1 or req.get('max_text_health_probes_per_6h')!=1 or req.get('max_image_health_probes')!=0):raise ValueError('Exact bounded normal-cycle start required')
 if not authorized(DATA):raise ValueError('Owner activation required')
 rp=OUT/'production-starts'/ID/'receipt.json'
 if rp.exists():return {'status':'already_started'}
 state={'request_id':ID,'status':'started','started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'max_new_posts':1};atomic_json(rp,state)
 try:
  from .cycle import run as cycle
  inventory=None
  if req.get('repair_slug_topic'):
   if req['repair_slug_topic']!='agri-5419edf5b44f':raise ValueError('Exact format-only repair target required')
   from .wordpress import WordPress
   from .slug_repair import repair_brief
   wp=WordPress();wp.preflight();inventory=wp.inventory()
   state['repair']=repair_brief(req['repair_slug_topic'],inventory);atomic_json(rp,state)
  result=cycle(scheduled=True,_research_inventory=inventory);state.update(status='cycle_completed',result=result,completed_at=utcnow());atomic_json(rp,state);return result
 except Exception as exc:
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state);failed('چرخه عادی متوقف شد؛ دسته خطا و پیشرفت موجود محفوظ است');return {'status':'stopped_safely','failure':state['failure']}
if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False));raise SystemExit(2 if result['status']=='stopped_safely' else 0)
