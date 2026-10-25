"""One final half-open technical-role canary inside the owner's one-hour window."""
import hashlib,json,os,time
from .queue import DATA,OUT,ROOT,load_json,atomic_json,get_topic,utcnow,age_hours
from .client import ModelClient,ImageProviderError
from .media_policy import generate_role,POLICY
from .image_quality import binding,valid_record,ensure_review,review_path,ImageQualityError,verdict
from .image_transport import AdmissionBlocked
from .recovery import circuit_open
from .pilot_resume import defer_provider
from .progress import update
from automation.blog_image_queue import ImageQueueBusy
ID='one-hour-final-technical-canary-v1';TOPIC='agri-af1a4b491d83'
def validate(req):
 if req.get('request_id')!=ID or req.get('topic_id')!=TOPIC or req.get('role')!=3 or req.get('max_image_calls')!=1 or req.get('max_visual_reviews')!=1 or req.get('max_post_mutations')!=0 or req.get('publication_authorized') is not False or req.get('source_run_id')!='40157593032' or not isinstance(req.get('not_before_epoch'),(int,float)) or not isinstance(req.get('window_end_epoch'),(int,float)):raise ValueError('Exact one-window one-image canary required')
def check_controls(req,topic,article):
 folder=OUT/'image-backtests/verified-pool-scene-v1';source=folder/'report.json'
 if hashlib.sha256(source.read_bytes()).hexdigest()!=req['source_report_sha256']:raise ValueError('Parent replay report changed')
 report=load_json(source)
 if report.get('run_id')!=req['source_run_id'] or report.get('policy')!=POLICY or report.get('image_calls')!=1 or report.get('status')!='stopped_provider_limit_or_failure':raise ValueError('Unexpected supervised replay state')
 for role in (2,3):
  image=folder/f'negative-role-{role}.webp';row=load_json(review_path(image));expected=binding(image,topic,role,article)
  if any(row.get(k)!=v for k,v in expected.items()) or row.get('status')!='reviewed' or verdict(row.get('verdict'))['passed'] is not False:raise ValueError('Current negative calibration missing')
 valid_record(folder/'positive-structural-control.webp',topic,3,article)
def run():
 req=load_json(DATA/'health-canary-request.json');validate(req);dest=OUT/'health-canary'/ID;rp=dest/'report.json'
 if rp.exists():return {'status':'already_reserved','model_calls':0}
 report={'request_id':ID,'run_id':os.environ.get('GITHUB_RUN_ID'),'started_at':utcnow(),'status':'waiting_provider_deadline','image_calls':0,'visual_review_calls':0,'post_mutations':0,'max_image_calls':1,'max_visual_reviews':1,'publication_authorized':False,'role':3,'human_review_claimed':False,'agent_visual_review_complete':False}
 atomic_json(rp,report)
 try:
  update('آزمون نهایی محدود سلامت منتظر پایان مهلت سرویس است',15,TOPIC,status='provider_cooldown')
  while time.time()<req['window_end_epoch']:
   state=load_json(OUT/'provider-circuit.json');deadline=max(req['not_before_epoch'],state.get('retry_at_epoch',0) if state.get('open') else 0)
   if time.time()>=deadline and not circuit_open():break
   time.sleep(min(30,max(1,req['window_end_epoch']-time.time())))
  else:report['status']='window_ended_before_admission';return report
  topic=get_topic('new',TOPIC);article=load_json(OUT/'new'/TOPIC/'article.json');health=load_json(DATA/'health/latest.json')
  if age_hours(health['checked_at'])>24:raise ValueError('Text health evidence expired')
  check_controls(req,topic,article);report['cached_calibration_verified']=True;report['source_report_sha256']=req['source_report_sha256'];client=ModelClient(health,allow_calls=True)
  report.update(image_calls=1,status='generating_one_technical_scene');atomic_json(rp,report);update('یک آزمون نهاییِ صحنه فنی؛ بدون انتشار یا تکرار خودکار',35,TOPIC,status='image_canary_running')
  try:blob=generate_role(client,topic,3,article)
  finally:report['generation_slot']=getattr(client,'last_image_slot',None)
  path=dest/'role-3.webp';path.write_bytes(blob);report.update(image_sha256=hashlib.sha256(blob).hexdigest(),path=str(path.relative_to(ROOT)),valid_image_bytes=True)
  # A real image response demonstrates transport recovery, not article approval.
  atomic_json(OUT/'provider-circuit.json',{'open':False,'at':utcnow(),'reason':'verified_image_bytes_from_final_canary','request_id':ID,'publication_visual_approval':False})
  report['visual_review_calls']=1;atomic_json(rp,report)
  try:ensure_review(client,path,topic,3,article)
  except ImageQualityError:pass
  row=load_json(review_path(path));report.update(status='candidate_requires_agent_visual_review',automated_pass=row.get('status')=='reviewed' and row.get('verdict',{}).get('passed') is True,quality_review=str(review_path(path).relative_to(ROOT)));return report
 except ImageProviderError as exc:
  report.update(status='provider_still_blocked',http_status=exc.http_status,provider_code=exc.provider_code,retry_after_seconds=exc.retry_after_seconds,retry_at_epoch=defer_provider(exc));return report
 except (AdmissionBlocked,ImageQueueBusy):report.update(status='shared_admission_blocked',image_calls=0);return report
 except Exception as exc:report.update(status='canary_blocked',error_type=type(exc).__name__);return report
 finally:
  report['finished_at']=utcnow();atomic_json(rp,report)
  update('آزمون نهایی سلامت ثبت شد؛ انتشار فقط با تأیید کامل مجاز است',40,TOPIC,status='image_canary_review_required' if report.get('valid_image_bytes') else 'provider_blocked')
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
