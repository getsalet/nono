"""One reserved reference-guided replay; controls are NOT Agnes production outputs."""
import hashlib,json,os
from .queue import DATA,OUT,ROOT,load_json,atomic_json,get_topic,utcnow,age_hours
from .healthcheck import IMAGE_MODEL
from .client import ModelClient,ImageProviderError,render_image
from .image_transport import AdmissionBlocked
from .media_policy import POLICY,image_prompt,scene_plan,generate_role,reference_images
from .image_quality import ensure_review,ImageQualityError,review_path
from .recovery import circuit_open
from .pilot_resume import defer_provider
from automation.blog_image_queue import ImageQueueBusy
ID='reference-guided-close-and-technical-v1';TOPIC='agri-af1a4b491d83'
POOL_ID='verified-pool-scene-v1'
POOL_REQUEST={'request_id': 'verified-pool-scene-v1', 'topic_id': 'agri-af1a4b491d83', 'policy': 'agri-topic-scene-aghala-v5-role-guides', 'model': 'agnes-image-2.1-flash', 'roles': [2, 3], 'max_image_calls': 2, 'max_review_calls': 5, 'publication_authorized': False, 'source_audit_sha256': '92dc2db5af6914b4da446c1b5353794cf831833a87e10514eadb4535e88bfe84', 'source_audit_run_id': '40155321751', 'required_image_slots': ['AGNES_API_KEY', 'AGNES_API_KEY2', 'AGNES_API_KEY3']}
FIRST_SHA='f37936695d3c9f27396ba8ff69c3fe55c464d666ead3a5c5488954a11ed88591'
NEGATIVES={2:('artifacts/agri-v2/model-switch/image-model-switch-21-v1/agnes-image-2.1-flash.webp','37e3543b9ecdae528c90f7a31bb7e14668cf666e07f00474bab85e3326e1d169'),3:('artifacts/agri-v2/image-backtests/aghala-image-tune-backtest-v3/role-3.webp','dd203fca78eb9f2d65b1f7476167956626f2b3cdefeb26aa3806a4d2c4a537fa')}
def validate(req):
 if req!=POOL_REQUEST and req!={'request_id':ID,'topic_id':TOPIC,'policy':'agri-topic-scene-aghala-v5-role-guides','model':'agnes-image-2.1-flash','roles':[2,3],'max_image_calls':2,'max_review_calls':5,'publication_authorized':False}:raise ValueError('Exact bounded, non-publication role-guided replay required')
def verify_pool_evidence(req,health):
 if req['request_id']!=POOL_ID:return
 source=OUT/'image-key-audit/unique-image-capability-v1/report.json'
 if hashlib.sha256(source.read_bytes()).hexdigest()!=req['source_audit_sha256']:raise ValueError('Image pool audit changed')
 audit=load_json(source)
 if audit.get('run_id')!=req['source_audit_run_id'] or audit.get('model')!=req['model']:raise ValueError('Image pool evidence mismatch')
 if not set(req['required_image_slots']).issubset(health.get('eligible_image_slots',[])):raise ValueError('Verified image slots unavailable')
 for slot in ('AGNES_API_KEY2','AGNES_API_KEY3'):
  row=next((r for r in audit['cases'] if r['slot']==slot and r['state']=='healthy'),None)
  if not row or hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Verified diagnostic image changed')
def inspect(client,path,topic,role,article):
 try:ensure_review(client,path,topic,role,article)
 except ImageQualityError:pass
 return load_json(review_path(path))
def record_provider_failure(exc,report):
 deadline=defer_provider(exc)
 report.update(status='stopped_provider_limit_or_failure',http_status=exc.http_status,provider_code=exc.provider_code,retry_after_seconds=exc.retry_after_seconds,retry_at_epoch=deadline)
 if report['cases'] and report['cases'][-1]['status']=='reserved':report['cases'][-1].update(status='provider_rejected',http_status=exc.http_status,provider_code=exc.provider_code)
def run():
 req=load_json(DATA/'image-backtest-request.json');validate(req);dest=OUT/'image-backtests'/req['request_id'];rp=dest/'report.json'
 if rp.exists():return {'status':'already_reserved','image_calls':0,'post_submissions':0}
 # A cooldown is not an attempted test and must not consume its unique reservation.
 if circuit_open():return {'status':'provider_cooldown_honored','image_calls':0,'post_submissions':0,'no_request_reserved':True}
 if req['policy']!=POLICY:return {'status':'historical_recipe_changed_no_replay','image_calls':0,'post_submissions':0}
 report={'request_id':req['request_id'],'policy':POLICY,'started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'model':IMAGE_MODEL,'image_calls':0,'review_calls':0,'max_image_calls':2,'max_review_calls':5,'post_submissions':0,'cases':[],'negative_controls':[],'human_review_claimed':False,'visual_agent_review_complete':False,'sample_scope':'red kidney bean dry-harvest detail and neutral technical role only; independently authored references are not counted as Agnes outputs'}
 atomic_json(rp,report)
 try:
  if IMAGE_MODEL!=req['model']:raise ValueError('Requested/active model mismatch')
  health=load_json(DATA/'health/latest.json')
  if age_hours(health['checked_at'])>24:raise ValueError('Health evidence expired; no automatic full audit')
  verify_pool_evidence(req,health)
  if req['request_id']==POOL_ID:report['pool_evidence']={k:req[k] for k in ('source_audit_sha256','source_audit_run_id','required_image_slots')}
  topic=get_topic('new',TOPIC);folder=OUT/'new'/TOPIC;article=load_json(folder/'article.json');first=folder/'revisions/site-style-v2/image-1.webp'
  if hashlib.sha256(first.read_bytes()).hexdigest()!=FIRST_SHA:raise ValueError('Preserved image 1 changed; stop')
  report['original_image_1_sha256']=FIRST_SHA;client=ModelClient(health,allow_calls=True)
  for role,(source,sha) in NEGATIVES.items():
   raw=(ROOT/source).read_bytes()
   if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Negative control bytes changed')
   path=dest/f'negative-role-{role}.webp';path.write_bytes(raw);report['review_calls']+=1;atomic_json(rp,report);review=inspect(client,path,topic,role,article)
   row={'role':role,'image_sha256':sha,'expected':'reject','review_status':review['status'],'rejected':review.get('verdict',{}).get('passed') is False,'review':str(review_path(path).relative_to(ROOT))};report['negative_controls'].append(row);atomic_json(rp,report)
   if review['status']!='reviewed':report['status']='reviewer_unavailable_control';return report
   if not row['rejected']:report['status']='reviewer_failed_known_bad_control';return report
  # Only the inspected technical guide is a positive control. The botanical
  # layout is intentionally composed INPUT, never asserted to be a final photo.
  good=dest/'positive-structural-control.webp';encoded=reference_images(3)[0].split(',',1)[1]
  good.write_bytes(render_image({'data':[{'b64_json':encoded}]},require_landscape=True));report['review_calls']+=1;atomic_json(rp,report)
  review=inspect(client,good,topic,3,article);report['positive_control']={'origin':'independently generated AI structural guide, not Agnes output','role':3,'expected':'pass','review_status':review['status'],'passed':review.get('verdict',{}).get('passed') is True,'review':str(review_path(good).relative_to(ROOT))}
  if not report['positive_control']['passed']:report['status']='reviewer_or_positive_reference_needs_inspection';return report
  for role in req['roles']:
   row={'role':role,'started_at':utcnow(),'status':'reserved'};report['cases'].append(row);prompt=image_prompt(topic,role,article)
   atomic_json(dest/f'role-{role}-contract.json',scene_plan(topic,role,article));(dest/f'role-{role}-prompt.txt').write_text(prompt);row['prompt_sha256']=hashlib.sha256(prompt.encode()).hexdigest();report['image_calls']+=1;atomic_json(rp,report)
   try:blob=generate_role(client,topic,role,article)
   except (ImageProviderError,AdmissionBlocked,ImageQueueBusy):raise
   except Exception as exc:
    row.update(status='generation_failed',error_type=type(exc).__name__);report['status']='stopped_generation_uncertain';atomic_json(rp,report);return report
   finally:row['generation_slot']=getattr(client,'last_image_slot',None);atomic_json(rp,report)
   path=dest/f'role-{role}.webp';path.write_bytes(blob);row.update(path=str(path.relative_to(ROOT)),image_sha256=hashlib.sha256(blob).hexdigest(),status='awaiting_review');report['review_calls']+=1;atomic_json(rp,report)
   review=inspect(client,path,topic,role,article);row.update(status='reviewed' if review['status']=='reviewed' else 'review_unavailable',automated_pass=review.get('verdict',{}).get('passed',False),review=str(review_path(path).relative_to(ROOT)),finished_at=utcnow());atomic_json(rp,report)
   if review['status']!='reviewed':report['status']='stopped_reviewer_unavailable';return report
  report.update(status='completed_requires_agent_visual_review',original_image_1_unchanged=hashlib.sha256(first.read_bytes()).hexdigest()==FIRST_SHA);return report
 except ImageProviderError as exc:record_provider_failure(exc,report);return report
 except (AdmissionBlocked,ImageQueueBusy):report['status']='shared_admission_deferred';return report
 except Exception as exc:report.update(status='preflight_or_transport_blocked',error_type=type(exc).__name__);return report
 finally:report['finished_at']=utcnow();atomic_json(rp,report)
if __name__=='__main__':
 r=run();print(json.dumps({k:r[k] for k in ('status','image_calls','post_submissions')},ensure_ascii=False))
