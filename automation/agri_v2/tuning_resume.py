"""One deferred, non-publishing image tuning run; never a publication recovery reset."""
import time
from .queue import DATA,OUT,load_json,atomic_json,utcnow,age_hours
from .recovery import circuit_open
from .progress import update
REQUEST='reference-guided-resume-v1';POOL_RESUME='verified-pool-scene-resume-v1';TOPIC='agri-af1a4b491d83'
def validate(req):
 if (req.get('request_id'),req.get('backtest_request_id')) not in ((REQUEST,'reference-guided-close-and-technical-v1'),(POOL_RESUME,'verified-pool-scene-v1')) or req.get('topic_id')!=TOPIC or req.get('max_runs')!=1 or req.get('max_image_calls')!=2 or req.get('max_new_posts')!=0 or req.get('publication_authorized') is not False or not isinstance(req.get('not_before_epoch'),(int,float)):raise ValueError('Exact one-shot non-publication tuning authorization required')
def run():
 request_path=DATA/'image-tuning-resume-request.json'
 if not request_path.exists():return None
 req=load_json(request_path);validate(req);rp=OUT/'image-backtests'/req['backtest_request_id']/'report.json';sp=OUT/'image-tuning-resume'/req['request_id']/'receipt.json'
 state=load_json(sp) if sp.exists() else {'request_id':req['request_id'],'runs_started':0,'max_runs':1,'post_submissions':0}
 if rp.exists():
  report=load_json(rp);state.update(status='awaiting_agent_visual_review' if report.get('status')=='completed_requires_agent_visual_review' else 'stopped_after_one_reserved_test',backtest_status=report.get('status'),backtest_run_id=report.get('run_id'),at=utcnow());atomic_json(sp,state)
  update('آزمون تیون ثبت شد؛ تصاویر و رسیدها نیازمند بررسی مستقل هستند',75,TOPIC,status='image_tuning_review_required')
  return {'status':state['status'],'model_calls':0,'published_posts':0}
 if state['runs_started']>=1:
  update('بودجه آزمون تیون مصرف شده؛ تکرار خودکار انجام نمی‌شود',0,TOPIC,status='awaiting_review');return {'status':'image_tuning_budget_exhausted','model_calls':0,'published_posts':0}
 if time.time()<req['not_before_epoch'] or circuit_open():
  state.update(status='waiting_provider_deadline',not_before_epoch=req['not_before_epoch'],at=utcnow());atomic_json(sp,state)
  update('تیون تصویر آماده است؛ پیش از پایان مهلت صف هیچ درخواست جدیدی ارسال نمی‌شود',15,TOPIC,status='provider_cooldown')
  return {'status':'image_tuning_waiting_provider','model_calls':0,'published_posts':0}
 # Never silently replace this one-key evidence with a paid full-key audit.
 hp=DATA/'health/latest.json'
 if not hp.exists() or age_hours(load_json(hp)['checked_at'])>24:
  state.update(status='needs_fresh_health_evidence',at=utcnow());atomic_json(sp,state);return {'status':state['status'],'model_calls':0,'published_posts':0}
 state.update(runs_started=1,status='running',at=utcnow());atomic_json(sp,state)
 from .image_backtest import run as backtest
 result=backtest()
 if result.get('no_request_reserved'):state['runs_started']=0
 state.update(status=result['status'],at=utcnow());atomic_json(sp,state)
 update('آزمون محدود تیون اجرا شد؛ نتیجه نیازمند بررسی است',75,TOPIC,status='image_tuning_review_required')
 return {'status':'image_tuning_attempt_finished','result':result,'published_posts':0}
