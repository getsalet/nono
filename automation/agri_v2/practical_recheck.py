"""One owner-authorized review of existing bytes; no image/article generation."""
import json,os
from .queue import DATA,OUT,load_json,atomic_json,utcnow,get_topic
from .curated_continuation import sha,BoundedClient
from .safe_activation import authorized
from .image_quality import REVIEW_POLICY,binding,verdict,valid_record,require_all,reject_known,ImageQualityError
from .pipeline import check_brief,validate_article,validate_for_publication
from .failure_diagnostics import failure_details
from .progress import update,failed
ID='pinto-illustration-recheck-v1';TOPIC='agri-a4f1fee1e3ee'
def validate(req):
 if (req.get('request_id')!=ID or req.get('topic_id')!=TOPIC or req.get('authorized') is not True
  or req.get('max_image_calls')!=0 or req.get('max_visual_reviews')!=1 or req.get('max_text_generation_calls')!=0
  or req.get('max_new_posts')!=1 or req.get('review_policy') not in {REVIEW_POLICY,'agri-vision-qa-v11-illustrative85'}):raise ValueError('Exact existing-image review authorization required')
 for k in ('article_sha256','brief_sha256','image_1_sha256','image_2_sha256','prior_quality_sha256','attempts_sha256'):
  if not isinstance(req.get(k),str) or len(req[k])!=64:raise ValueError('Exact existing artifact hashes required')
def run():
 if (DATA/'practical-finalize-request.json').exists():
  from .practical_finalize import run as finalize
  return finalize()
 req=load_json(DATA/'practical-recheck-request.json');validate(req)
 rp=OUT/'practical-rechecks'/ID/'receipt.json'
 if rp.exists():
  old=load_json(rp)
  return None if old.get('status')=='publication_verified' else {'status':'existing_review_already_reserved','model_calls':0}
 if not authorized(DATA):raise ValueError('Owner activation required')
 config=load_json(DATA/'config.json')
 if TOPIC in config.get('publication_holds',{}) or config.get('max_posts_per_run')!=1:raise ValueError('Publication scope changed')
 folder=OUT/'new'/TOPIC;bp=DATA/'briefs'/f'{TOPIC}.json';quality=folder/'image-2.quality.json'
 paths={'article_sha256':folder/'article.json','brief_sha256':bp,'image_1_sha256':folder/'image-1.webp','image_2_sha256':folder/'image-2.webp','prior_quality_sha256':quality,'attempts_sha256':folder/'cycle-attempts.json'}
 if any(sha(path)!=req[k] for k,path in paths.items()):raise ValueError('Existing artifact bytes changed')
 topic=get_topic('new',TOPIC);article=load_json(folder/'article.json');brief=load_json(bp)
 check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article)
 valid_record(folder/'image-1.webp',topic,1,article);reject_known(folder/'image-2.webp')
 state={'request_id':ID,'status':'review_reserved','run_id':os.environ.get('GITHUB_RUN_ID'),'started_at':utcnow(),'max_visual_reviews':1,'max_image_calls':0,'new_image_generation':False,'old_budgets_reset':False};atomic_json(rp,state)
 try:
  from .wordpress import WordPress
  wp=WordPress();wp.preflight()
  # Save exact rejected receipt before a new, explicitly authorized visual call.
  archive=rp.with_name('prior-image-2.quality.json');archive.write_bytes(quality.read_bytes())
  client=BoundedClient(load_json(DATA/'health/latest.json'),allow_calls=True,call_limit=0,review_limit=1,accounting_path=rp.with_name('calls.json'))
  update('بازبینی همان تصویر موجود با معیار تصویرسازی کاربردی؛ بدون تولید مجدد',70,TOPIC,topic['title'])
  review={**binding(folder/'image-2.webp',topic,2,article),'status':'reviewed','checked_at':utcnow(),'reviewer':'automated_multimodal_model','human_review_claimed':False,'prior_quality_sha256':req['prior_quality_sha256'],'explicit_owner_recheck':True,'verdict':verdict(client.review_image((folder/'image-2.webp').read_bytes(),topic,2,article))}
  atomic_json(rp.with_name('fresh-image-2.quality.json'),review)
  if not review['verdict']['passed']:raise ImageQualityError('Existing image still rejected under practical illustration review')
  if any(sha(path)!=req[k] for k,path in paths.items()):raise ValueError('Existing bytes changed during review')
  atomic_json(quality,review);require_all(folder,topic,article)
  atomic_json(folder/'wordpress-draft-payload.json',{'title':topic['title'],'slug':brief['slug'],'content':article['content_html'],'excerpt':article['excerpt'],'status':'draft'})
  state.update(status='publishing_after_two_quality_passes');atomic_json(rp,state)
  result=wp.publish(folder,topic,brief,authorized=True)
  state.update(status='publication_verified',result=result,completed_at=utcnow());atomic_json(rp,state)
  update('دو تصویر موجود پذیرفته شد و انتشار صفحه عمومی تأیید شد',100,TOPIC,topic['title'],status='success')
  return {'status':'publication_verified','result':result}
 except Exception as exc:
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state)
  failed('بازبینی کاربردی متوقف شد؛ تصاویر و ارزیابی‌های قبلی محفوظ است')
  return {'status':'stopped_safely','failure':state['failure']}
if __name__=='__main__':
 result=run() or {'status':'already_verified'};print(json.dumps(result,ensure_ascii=False));raise SystemExit(2 if result['status']=='stopped_safely' else 0)
