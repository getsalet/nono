"""One source/hash-bound continuation after offline article repair. Never reset old attempts."""
import hashlib,json,tempfile,os
from pathlib import Path
from .queue import DATA,OUT,load_json,atomic_json,utcnow,get_topic
from .pipeline import draft,validate_article,validate_for_publication,check_brief
from .client import ModelClient,CapabilityError
from .failure_diagnostics import failure_details
from .safe_activation import authorized
from .recovery import circuit_open
from .progress import update,failed
from .media_policy import POLICY
from .image_quality import REVIEW_POLICY,require_all
ID='pinto-source-bound-continuation-v1';TOPIC='agri-a4f1fee1e3ee'
class BoundedClient(ModelClient):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.reserved={'image':0,'text':0}
 def text(self,prompt):raise CapabilityError('This continuation permits no article generation')
 def request(self,kind,*a,**kw):
  if kind not in self.reserved or self.reserved[kind]>=3:raise CapabilityError('Explicit continuation model-call budget exhausted')
  self.reserved[kind]+=1
  return super().request(kind,*a,**kw)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate(req):
 if (req.get('request_id')!=ID or req.get('topic_id')!=TOPIC or req.get('authorized') is not True
     or req.get('max_image_calls')!=3 or req.get('max_visual_reviews')!=3 or req.get('max_text_generation_calls')!=0
     or req.get('max_new_posts')!=1 or req.get('preserve_existing_attempts') is not True
     or req.get('scene_policy')!=POLICY or req.get('review_policy')!=REVIEW_POLICY):raise ValueError('Exact source-bound editorial continuation required')
 for key in ('article_sha256','brief_sha256','original_candidate_sha256','original_cycle_attempts_sha256'):
  if not isinstance(req.get(key),str) or len(req[key])!=64:raise ValueError('Exact repair evidence hashes required')
def run():
 req=load_json(DATA/'curated-continuation-request.json');validate(req)
 if not authorized(DATA):raise ValueError('Owner activation required')
 folder=OUT/'new'/TOPIC;rp=OUT/'curated-continuations'/ID/'receipt.json'
 if rp.exists():return {'status':'already_reserved','model_calls':0}
 if circuit_open():return {'status':'provider_cooldown','model_calls':0}
 config=load_json(DATA/'config.json')
 if TOPIC in config.get('publication_holds',{}) or config.get('max_posts_per_run')!=1:raise ValueError('Publication scope changed')
 pairs={'article_sha256':folder/'article.json','brief_sha256':DATA/'briefs'/f'{TOPIC}.json','original_candidate_sha256':folder/'model-candidate.json','original_cycle_attempts_sha256':folder/'cycle-attempts.json'}
 if any(sha(path)!=req[key] for key,path in pairs.items()):raise ValueError('Curated repair source bytes changed')
 topic=get_topic('new',TOPIC);brief=load_json(pairs['brief_sha256']);article=load_json(pairs['article_sha256']);check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article)
 state={'request_id':ID,'topic_id':TOPIC,'status':'reserved','started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'old_attempts_preserved':load_json(folder/'cycle-attempts.json'),'max_image_calls':3,'max_visual_reviews':3,'max_text_generation_calls':0,'max_new_posts':1,'repair_origin':'source-bound Notion AI editorial revision; not human agronomy approval'};atomic_json(rp,state)
 try:
  from .wordpress import WordPress
  wp=WordPress();wp.preflight();inventory=wp.inventory()
  with tempfile.TemporaryDirectory() as tmp:
   ip=Path(tmp)/'inventory.json';atomic_json(ip,inventory)
   draft(TOPIC,DATA/'briefs'/f'{TOPIC}.json',ip,DATA/'health/latest.json',allow_calls=True,client_factory=BoundedClient)
  if sha(folder/'cycle-attempts.json')!=req['original_cycle_attempts_sha256']:raise ValueError('Original production attempt receipt changed')
  require_all(folder,topic,article)
  state.update(status='publishing_after_three_current_quality_passes',at=utcnow());atomic_json(rp,state)
  result=wp.publish(folder,topic,brief,authorized=True)
  state.update(status='publication_verified',result=result,completed_at=utcnow());atomic_json(rp,state)
  update('سه تصویر و انتشار صفحه عمومی تأیید شد',100,TOPIC,topic['title'],status='success')
  return {'status':state['status'],'result':result}
 except Exception as exc:
  from .cycle import handle_generation_failure
  handle_generation_failure(exc)
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state)
  failed('ادامه مستند مقاله متوقف شد؛ دسته خطا و خروجی موجود حفظ شد')
  return {'status':state['status'],'failure':state['failure']}
if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False));raise SystemExit(2 if result['status']=='stopped_safely' else 0)
