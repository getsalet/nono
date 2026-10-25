"""Finalize one unchanged two-image article from real existing visual evidence, zero model calls."""
import os,json
from .queue import DATA,OUT,load_json,atomic_json,utcnow,get_topic
from .curated_continuation import sha
from .safe_activation import authorized
from .image_quality import REVIEW_POLICY,SCORE_POLICY,matching_evidence,binding,verdict,valid_record,require_all,ImageQualityError
from .pipeline import check_brief,validate_article,validate_for_publication
from .progress import update,failed
from .failure_diagnostics import failure_details
ID='pinto-critical-check-finalize-v1';TOPIC='agri-a4f1fee1e3ee'
def validate(req):
 if (req.get('request_id')!=ID or req.get('topic_id')!=TOPIC or req.get('authorized') is not True
  or any(req.get(k)!=0 for k in ('max_image_calls','max_visual_reviews','max_text_generation_calls'))
  or req.get('max_new_posts')!=1 or req.get('review_policy')!=REVIEW_POLICY or req.get('score_policy')!=SCORE_POLICY):raise ValueError('Exact zero-call finalization required')
def run():
 req=load_json(DATA/'practical-finalize-request.json');validate(req);rp=OUT/'practical-finalizations'/ID/'receipt.json'
 if rp.exists():return None if load_json(rp).get('status')=='publication_verified' else {'status':'finalization_already_reserved','model_calls':0}
 if not authorized(DATA):raise ValueError('Owner activation required')
 config=load_json(DATA/'config.json')
 if TOPIC in config.get('publication_holds',{}) or config.get('max_posts_per_run')!=1:raise ValueError('Publication scope changed')
 folder=OUT/'new'/TOPIC;bp=DATA/'briefs'/f'{TOPIC}.json';quality=folder/'image-2.quality.json'
 fresh=OUT/'practical-rechecks/pinto-illustration-recheck-v1/fresh-image-2.quality.json'
 paths={'article_sha256':folder/'article.json','brief_sha256':bp,'image_1_sha256':folder/'image-1.webp','image_2_sha256':folder/'image-2.webp','prior_quality_sha256':quality,'fresh_quality_sha256':fresh,'attempts_sha256':folder/'cycle-attempts.json'}
 if any(sha(path)!=req.get(k) for k,path in paths.items()):raise ValueError('Source-bound finalization bytes changed')
 topic=get_topic('new',TOPIC);article=load_json(folder/'article.json');brief=load_json(bp)
 check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article);valid_record(folder/'image-1.webp',topic,1,article)
 review=load_json(fresh)
 if review.get('status')!='reviewed' or not matching_evidence(review,binding(folder/'image-2.webp',topic,2,article)) or not verdict(review.get('verdict'))['passed']:raise ImageQualityError('Existing evidence must pass every critical check')
 state={'request_id':ID,'status':'reserved','run_id':os.environ.get('GITHUB_RUN_ID'),'started_at':utcnow(),'model_calls':0,'image_calls':0,'visual_review_calls':0,'score_retained':review['verdict']['score'],'score_policy':SCORE_POLICY,'new_visual_review_claimed':False,'old_budgets_reset':False};atomic_json(rp,state)
 try:
  from .wordpress import WordPress
  wp=WordPress();wp.preflight()
  rp.with_name('prior-image-2.quality.json').write_bytes(quality.read_bytes())
  # Preserve exact real v11 evidence, including score72 and its historic passed=false.
  # valid_record deterministically evaluates critical booleans under the new owner policy.
  quality.write_bytes(fresh.read_bytes());require_all(folder,topic,article)
  atomic_json(folder/'wordpress-draft-payload.json',{'title':topic['title'],'slug':brief['slug'],'content':article['content_html'],'excerpt':article['excerpt'],'status':'draft'})
  update('کنترل‌های اصلی دو تصویر پذیرفته شد؛ ثبت همان مقاله بدون فراخوانی مدل',85,TOPIC,topic['title'])
  result=wp.publish(folder,topic,brief,authorized=True)
  state.update(status='publication_verified',result=result,completed_at=utcnow());atomic_json(rp,state)
  update('مقاله با یک تصویر شاخص و یک تصویر داخل متن منتشر و تأیید شد',100,TOPIC,topic['title'],status='success')
  return {'status':'publication_verified','result':result,'model_calls':0}
 except Exception as exc:
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state);failed('تکمیل انتشار متوقف شد؛ هیچ فراخوانی مدل انجام نشد')
  return {'status':'stopped_safely','failure':state['failure'],'model_calls':0}
