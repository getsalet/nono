"""One-shot replay of the rejected old image and three tuned editorial roles; no WordPress."""
import base64,hashlib,json,os
from .queue import DATA,OUT,ROOT,load_json,atomic_json,get_topic,utcnow,age_hours
from .healthcheck import IMAGE_MODEL
from .client import ModelClient,ImageProviderError,render_image
from .image_transport import AdmissionBlocked
from .media_policy import POLICY,image_prompt,scene_plan,generate_role,reference_images
from .image_quality import ensure_review,ImageQualityError,review_path
from .recovery import circuit_open
from automation.blog_image_queue import ImageQueueBusy
ID='aghala-image-tune-backtest-v4-reference';TOPIC='agri-af1a4b491d83'
BASELINE='artifacts/agri-v2/image-backtests/aghala-image-tune-backtest-v3/role-3.webp'
BASELINE_SHA='dd203fca78eb9f2d65b1f7476167956626f2b3cdefeb26aa3806a4d2c4a537fa'
FIRST_SHA='f37936695d3c9f27396ba8ff69c3fe55c464d666ead3a5c5488954a11ed88591'
def validate(req):
 if req!={'request_id':ID,'topic_id':TOPIC,'policy':POLICY,'model':'agnes-image-2.1-flash','roles':[3],'max_image_calls':1,'max_review_calls':3,'publication_authorized':False}:raise ValueError('Exact bounded, non-publication backtest request required')
def run():
 req=load_json(DATA/'image-backtest-request.json');validate(req);dest=OUT/'image-backtests'/ID;rp=dest/'report.json'
 if rp.exists():return {'status':'already_reserved','image_calls':0,'post_submissions':0}
 report={'request_id':ID,'policy':POLICY,'started_at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'model':IMAGE_MODEL,'image_calls':0,'review_calls':0,'max_image_calls':1,'max_review_calls':3,'post_submissions':0,'cases':[],'human_review_claimed':False,'visual_agent_review_complete':False,'sample_scope':'one dry red kidney bean harvest topic, reference-guided closed Y-filter technical role; guide generated independently, tested output must come from Agnes; not a general crop benchmark'}
 atomic_json(rp,report)
 try:
  if IMAGE_MODEL!=req['model']:raise ValueError('Requested/active model mismatch')
  if circuit_open():report['status']='provider_cooldown_honored';return report
  health=load_json(DATA/'health/latest.json')
  if age_hours(health['checked_at'])>24:raise ValueError('Health evidence expired; no automatic full audit')
  topic=get_topic('new',TOPIC);folder=OUT/'new'/TOPIC;article=load_json(folder/'article.json');first=folder/'revisions/site-style-v2/image-1.webp'
  if hashlib.sha256(first.read_bytes()).hexdigest()!=FIRST_SHA:raise ValueError('Preserved image 1 changed; stop')
  report['original_image_1_sha256']=FIRST_SHA
  baseline=(ROOT/BASELINE).read_bytes()
  if hashlib.sha256(baseline).hexdigest()!=BASELINE_SHA:raise ValueError('Rejected control bytes changed')
  client=ModelClient(health,allow_calls=True)
  # First calibrate on a real known-bad control. Never accept a reviewer outage as approval.
  control=dest/'rejected-control.webp';control.write_bytes(baseline);report['review_calls']+=1;atomic_json(rp,report)
  try:ensure_review(client,control,topic,3,article)
  except ImageQualityError:pass
  cr=load_json(review_path(control));report['control']={'image_sha256':BASELINE_SHA,'expected':'reject','review':str(review_path(control).relative_to(ROOT)),'review_status':cr['status'],'rejected':cr.get('verdict',{}).get('passed') is False}
  if cr['status']!='reviewed':report['status']='reviewer_unavailable_control';return report
  if not report['control']['rejected']:report['status']='reviewer_failed_known_bad_control';return report
  # Positive calibration is independently generated guide, NOT an Agnes output.
  good=dest/'positive-structural-control.webp';encoded=reference_images(3)[0].split(',',1)[1]
  good.write_bytes(render_image({'data':[{'b64_json':encoded}]},require_landscape=True))
  report['review_calls']+=1;atomic_json(rp,report)
  try:ensure_review(client,good,topic,3,article)
  except ImageQualityError:pass
  gr=load_json(review_path(good));report['positive_control']={'origin':'independently generated AI structural guide, not Agnes production output','expected':'pass','review_status':gr['status'],'passed':gr.get('verdict',{}).get('passed') is True,'review':str(review_path(good).relative_to(ROOT))}
  if not report['positive_control']['passed']:report['status']='reviewer_or_positive_reference_needs_inspection';return report
  atomic_json(rp,report)
  for kind in req['roles']:
   row={'role':kind,'started_at':utcnow(),'status':'reserved'};report['cases'].append(row)
   prompt=image_prompt(topic,kind,article);atomic_json(dest/f'role-{kind}-contract.json',scene_plan(topic,kind,article));(dest/f'role-{kind}-prompt.txt').write_text(prompt)
   row['prompt_sha256']=hashlib.sha256(prompt.encode()).hexdigest();report['image_calls']+=1;atomic_json(rp,report)
   try:blob=generate_role(client,topic,kind,article)
   except (ImageProviderError,AdmissionBlocked,ImageQueueBusy):raise
   except Exception as exc:
    row.update(status='generation_failed',error_type=type(exc).__name__);atomic_json(rp,report);continue
   path=dest/f'role-{kind}.webp';path.write_bytes(blob);row.update(path=str(path.relative_to(ROOT)),image_sha256=hashlib.sha256(blob).hexdigest(),status='awaiting_review')
   report['review_calls']+=1;atomic_json(rp,report)
   try:ensure_review(client,path,topic,kind,article)
   except ImageQualityError:pass
   review=load_json(review_path(path));row.update(status='reviewed' if review['status']=='reviewed' else 'review_unavailable',automated_pass=review.get('verdict',{}).get('passed',False),review=str(review_path(path).relative_to(ROOT)),finished_at=utcnow());atomic_json(rp,report)
   if review['status']!='reviewed':report['status']='stopped_reviewer_unavailable';return report
  report['status']='completed_requires_agent_visual_review'
  report['original_image_1_unchanged']=hashlib.sha256(first.read_bytes()).hexdigest()==FIRST_SHA
  return report
 except ImageProviderError as exc:
  report.update(status='stopped_provider_limit_or_failure',http_status=exc.http_status,provider_code=exc.provider_code);return report
 except (AdmissionBlocked,ImageQueueBusy):report['status']='shared_admission_deferred';return report
 except Exception as exc:report.update(status='preflight_or_transport_blocked',error_type=type(exc).__name__);return report
 finally:
  report['finished_at']=utcnow();atomic_json(rp,report)
if __name__=='__main__':
 r=run();print(json.dumps({k:r[k] for k in ('status','image_calls','post_submissions')},ensure_ascii=False))
