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
from .image_quality import REVIEW_POLICY,PREVIOUS_REVIEW_POLICY,require_all
ID='pinto-source-bound-continuation-v1';REMAINING_ID='pinto-practical85-remaining-images-v1';TOPIC='agri-a4f1fee1e3ee'
def retryable_failure(row):
 f=row.get('failure',{})
 return f.get('kind')=='image_provider' and (f.get('http_status') in (429,500,502,503,504) or f.get('category')=='network_or_timeout')

def resumable(row,req):
 return (req.get('request_id')==REMAINING_ID and row.get('status') in {'stopped_safely','provider_deferred'}
  and retryable_failure(row) and row.get('recovery_resumes',0)<req.get('max_provider_resumes',0))

class BoundedClient(ModelClient):
 def __init__(self,*a,**kw):
  self.limit=kw.pop('call_limit',3);self.review_limit=kw.pop('review_limit',self.limit)
  self.accounting_path=kw.pop('accounting_path',None);pin=kw.pop('pinned_slot',None)
  super().__init__(*a,**kw)
  old=load_json(self.accounting_path) if self.accounting_path and self.accounting_path.exists() else {}
  self.reserved={'image':old.get('image_calls_reserved',0),'text':old.get('visual_review_calls_reserved',0)}
  if any(type(v)is not int or v<0 for v in self.reserved.values()):raise CapabilityError('Invalid cumulative accounting')
  if pin:
   self.keys['image']=[pair for pair in self.keys['image'] if pair[0]==pin]
   if not self.keys['image']:raise CapabilityError('Previous image slot is unavailable; no retry rotation')
 def text(self,prompt):raise CapabilityError('This continuation permits no article generation')
 def request(self,kind,*a,**kw):
  limit=self.review_limit if kind=='text' else self.limit
  if kind not in self.reserved or self.reserved[kind]>=limit:raise CapabilityError('Explicit continuation model-call budget exhausted')
  self.reserved[kind]+=1;self.persist_counts()
  try:return super().request(kind,*a,**kw)
  finally:self.persist_counts()
 def persist_counts(self):
  if self.accounting_path:atomic_json(self.accounting_path,{'image_calls_reserved':self.reserved['image'],'visual_review_calls_reserved':self.reserved['text'],'image_call_limit':self.limit,'review_call_limit':self.review_limit,'last_image_slot':getattr(self,'last_image_slot',None),'updated_at':utcnow()})

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate(req):
 remaining=req.get('request_id')==REMAINING_ID
 expected=4 if remaining else 3
 reviews=2 if remaining else 3
 if remaining and (req.get('max_provider_resumes')!=2 or req.get('max_new_image_outputs')!=2):raise ValueError('Bounded two-role recovery required')
 if (req.get('request_id') not in {ID,REMAINING_ID} or req.get('topic_id')!=TOPIC or req.get('authorized') is not True
     or req.get('max_image_calls')!=expected or req.get('max_visual_reviews')!=reviews or req.get('max_text_generation_calls')!=0
     or req.get('max_new_posts')!=1 or req.get('preserve_existing_attempts') is not True
     or req.get('scene_policy')!=POLICY or req.get('review_policy') not in {REVIEW_POLICY,PREVIOUS_REVIEW_POLICY}):raise ValueError('Exact source-bound editorial continuation required')
 for key in ('article_sha256','brief_sha256','original_candidate_sha256','original_cycle_attempts_sha256'):
  if not isinstance(req.get(key),str) or len(req[key])!=64:raise ValueError('Exact repair evidence hashes required')
def run():
 req=load_json(DATA/'curated-continuation-request.json');validate(req)
 if not authorized(DATA):raise ValueError('Owner activation required')
 folder=OUT/'new'/TOPIC;rp=OUT/'curated-continuations'/req['request_id']/'receipt.json'
 previous_run=load_json(rp) if rp.exists() else {}
 if previous_run and not resumable(previous_run,req):return {'status':'already_reserved','model_calls':0}
 if req.get('review_policy')!=REVIEW_POLICY:raise ValueError('Historical continuation cannot consume new-policy budget')
 if circuit_open():return {'status':'provider_cooldown','model_calls':0}
 config=load_json(DATA/'config.json')
 if TOPIC in config.get('publication_holds',{}) or config.get('max_posts_per_run')!=1:raise ValueError('Publication scope changed')
 pairs={'article_sha256':folder/'article.json','brief_sha256':DATA/'briefs'/f'{TOPIC}.json','original_candidate_sha256':folder/'model-candidate.json','original_cycle_attempts_sha256':folder/'cycle-attempts.json'}
 if any(sha(path)!=req[key] for key,path in pairs.items()):raise ValueError('Curated repair source bytes changed')
 if req['request_id']==REMAINING_ID:
  from .image_quality import valid_record
  prior=OUT/'curated-continuations'/ID/'receipt.json'
  if sha(prior)!=req.get('prior_continuation_sha256') or sha(folder/'image-1.webp')!=req.get('accepted_image_1_sha256'):raise ValueError('Prior continuation or accepted image changed')
  previous=load_json(prior)
  if previous.get('status')!='stopped_safely' or previous.get('failure',{}).get('kind')!='image_quality':raise ValueError('No matching one-image quality stop')
  if not previous_run and any((folder/f'image-{n}.webp').exists() for n in (2,3)):raise ValueError('Remaining-image request only covers previously unmade roles')
  valid_record(folder/'image-1.webp',get_topic('new',TOPIC),1,load_json(folder/'article.json'))
 topic=get_topic('new',TOPIC);brief=load_json(pairs['brief_sha256']);article=load_json(pairs['article_sha256']);check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article)
 state={'request_id':req['request_id'],'topic_id':TOPIC,'status':'reserved','started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'old_attempts_preserved':load_json(folder/'cycle-attempts.json'),'max_image_calls':req['max_image_calls'],'max_visual_reviews':req['max_visual_reviews'],'max_text_generation_calls':0,'max_new_posts':1,'repair_origin':'source-bound Notion AI editorial revision; not human agronomy approval'}
 state['recovery_resumes']=previous_run.get('recovery_resumes',0)+(1 if previous_run else 0)
 pin=previous_run.get('retry_image_slot')
 if previous_run and not pin:
  routing=load_json(OUT/'image-key-routing.json')
  pin=routing.get('last_selected_slot')
 if previous_run and not pin:raise ValueError('Retry slot evidence missing')
 state['retry_image_slot']=pin
 atomic_json(rp,state)
 try:
  from .wordpress import WordPress
  wp=WordPress();wp.preflight();inventory=wp.inventory()
  with tempfile.TemporaryDirectory() as tmp:
   ip=Path(tmp)/'inventory.json';atomic_json(ip,inventory)
   draft(TOPIC,DATA/'briefs'/f'{TOPIC}.json',ip,DATA/'health/latest.json',allow_calls=True,client_factory=lambda *a,**kw:BoundedClient(*a,call_limit=req['max_image_calls'],review_limit=req['max_visual_reviews'],pinned_slot=pin,accounting_path=rp.with_name('calls.json'),**kw))
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
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow())
  counts=load_json(rp.with_name('calls.json')) if rp.with_name('calls.json').exists() else {}
  state['retry_image_slot']=counts.get('last_image_slot') or pin
  if resumable(state,req):state['status']='provider_deferred'
  atomic_json(rp,state)
  if state['status']=='provider_deferred':update('صف سرویس تصویر پر است؛ ادامه محدود پس از پایان مهلت انتظار',52,TOPIC,status='provider_cooldown')
  else:failed('ادامه مستند مقاله متوقف شد؛ دسته خطا و خروجی موجود حفظ شد')
  return {'status':state['status'],'failure':state['failure']}
if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False));raise SystemExit(2 if result['status']=='stopped_safely' else 0)
