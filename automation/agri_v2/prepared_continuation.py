"""Exact byte-bound continuation: no text generation, two image calls maximum."""
import hashlib,os,tempfile
from pathlib import Path
from .queue import DATA,OUT,load_json,atomic_json,utcnow,get_topic
from .pipeline import check_brief,validate_article,validate_for_publication,draft,digest
from .safe_activation import authorized
from .progress import update
from .client import ModelClient
ID='white-bean-prepared-two-images-v1';TOPIC='agri-5419edf5b44f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(req,allow_recovery=False):
 if req.get('prepared_topic')!=TOPIC or req.get('max_image_calls')!=2 or req.get('max_visual_reviews')!=2 or req.get('max_text_generation_calls')!=0:raise ValueError('Exact bounded continuation required')
 if not authorized(DATA):raise ValueError('Owner activation required')
 config=load_json(DATA/'config.json')
 if not config.get('publication_enabled') or not config.get('automatic_generation') or TOPIC in config.get('publication_holds',{}):raise ValueError('Publication not enabled')
 rp=OUT/'prepared-continuations'/ID/'receipt.json'
 prior=load_json(rp) if rp.exists() else None
 if prior:
  if prior.get('status')=='publication_verified':return None
  failure=prior.get('failure',{})
  recoverable=(allow_recovery and req.get('max_recovery_cycles')==1 and req.get('max_total_image_calls')==3 and prior.get('recovery_cycles',0)<1 and prior.get('status')=='stopped_safely' and failure.get('kind')=='image_provider' and failure.get('category') in {'provider_unavailable','network_or_timeout','rate_limited','quota_limited'} and prior.get('image_calls',0)<=1 and prior.get('visual_reviews',0)==0)
  if not recoverable:return {'status':'continuation_already_reserved'}
  from .recovery import circuit_open
  if circuit_open():return {'status':'provider_cooldown','published_posts':0,'model_calls':0}
 pp=DATA/'prepared-articles'/f'{TOPIC}.json';bp=DATA/'briefs'/f'{TOPIC}.json';folder=OUT/'new'/TOPIC;attempts=folder/'cycle-attempts.json'
 for key,path in [('prepared_article_sha256',pp),('brief_sha256',bp),('attempts_sha256',attempts)]:
  if sha(path)!=req.get(key):raise ValueError('Continuation input bytes changed')
 topic=get_topic('new',TOPIC);article=load_json(pp);brief=load_json(bp);check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article)
 if (folder/'article.json').exists() and digest(load_json(folder/'article.json'))!=digest(article):raise ValueError('Staged article changed')
 from .runtime_health import ensure_fresh
 if ensure_fresh()['status'] not in {'health_current','health_refreshed_from_actual_evidence'}:raise ValueError('Current health required')
 from .wordpress import WordPress
 wp=WordPress();wp.preflight();inventory=wp.inventory()
 state={'status':'reserved','run_id':os.environ.get('GITHUB_RUN_ID'),'started_at':utcnow(),'text_generation_calls':0,'image_calls':0,'visual_reviews':0,'prior_attempts':load_json(attempts),'old_budgets_reset':False}
 if prior:
  state.update(image_calls=prior['image_calls'],visual_reviews=prior['visual_reviews'],recovery_cycles=1,previous_receipt=prior,max_total_image_calls=3)
 atomic_json(rp,state)
 class BoundedClient(ModelClient):
  def text(self,*a,**kw):raise ValueError('No text generation authorized')
  def image(self,*a,**kw):
   if state['image_calls']>=(3 if prior else 2):raise ValueError('Image continuation budget exhausted')
   state['image_calls']+=1;atomic_json(rp,state);return super().image(*a,**kw)
  def review_image(self,*a,**kw):
   if state['visual_reviews']>=2:raise ValueError('Visual continuation budget exhausted')
   state['visual_reviews']+=1;atomic_json(rp,state);return super().review_image(*a,**kw)
 try:
  atomic_json(folder/'article.json',article)
  with tempfile.TemporaryDirectory() as d:
   ip=Path(d)/'inventory.json';atomic_json(ip,inventory)
   draft(TOPIC,bp,ip,DATA/'health/latest.json',allow_calls=True,client_factory=BoundedClient)
  update('متن و دو تصویر آماده؛ انتشار در وردپرس',80,TOPIC,topic['title'])
  result=wp.publish(folder,topic,brief,authorized=True)
  state.update(status='publication_verified',result=result,completed_at=utcnow());atomic_json(rp,state)
  update('مقاله و دو تصویر منتشر و صفحه عمومی تأیید شد',100,TOPIC,topic['title'],status='success');return result
 except Exception as exc:
  from .cycle import handle_generation_failure
  from .failure_diagnostics import failure_details
  handle_generation_failure(exc);state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state);raise

def scheduled_resume():
 req=load_json(DATA/'production-start-request.json')
 if req.get('prepared_topic')!=TOPIC:return None
 rp=OUT/'prepared-continuations'/ID/'receipt.json'
 if not rp.exists():return None
 prior=load_json(rp)
 if prior.get('status')=='publication_verified' or prior.get('recovery_cycles',0)>=1:return None
 failure=prior.get('failure',{})
 if prior.get('status')!='stopped_safely' or failure.get('kind')!='image_provider' or failure.get('category') not in {'provider_unavailable','network_or_timeout','rate_limited','quota_limited'}:return None
 return run(req,allow_recovery=True)
