"""One bounded activation-readiness check: authenticated reads and one vision review."""
import hashlib,json,os
from .queue import DATA,OUT,load_json,atomic_json,get_topic,utcnow,age_hours
from .pipeline import check_brief,validate_article,validate_for_publication
from .wordpress import WordPress
from .client import ModelClient
from .image_quality import ensure_review,valid_record,ImageQualityError
from .progress import update
REQUEST={'request_id':'one-hour-activation-health-v1','topic_id':'agri-af1a4b491d83','post_id':524163,'max_image_calls':0,'max_visual_reviews':1,'max_post_mutations':0,'publication_authorized':False}
FIRST_SHA='f37936695d3c9f27396ba8ff69c3fe55c464d666ead3a5c5488954a11ed88591'
def run():
 req=load_json(DATA/'activation-health-request.json')
 if req!=REQUEST:raise ValueError('Exact bounded read-only activation check required')
 dest=OUT/'activation-health'/req['request_id'];rp=dest/'report.json'
 if rp.exists():return {'status':'already_reserved','model_calls':0,'post_mutations':0}
 report={'request_id':req['request_id'],'run_id':os.environ.get('GITHUB_RUN_ID'),'started_at':utcnow(),'image_calls':0,'visual_review_calls':0,'post_mutations':0,'status':'reserved','human_review_claimed':False}
 atomic_json(rp,report)
 try:
  topic=get_topic('new',req['topic_id']);folder=OUT/'new'/req['topic_id'];article=load_json(folder/'article.json');brief=load_json(DATA/'briefs'/(req['topic_id']+'.json'))
  check_brief(topic,brief);validate_article(article,topic,brief);validate_for_publication(article);report['article_validation_passed']=True
  wp=WordPress();report['wordpress_connection']=wp.preflight();post,_=wp.call('posts/'+str(req['post_id'])+'?context=edit')
  marker='<!-- afp-agri-v2:'+req['topic_id']+' -->'
  if post.get('id')!=req['post_id'] or post.get('author')!=wp.user_id or marker not in post.get('content',{}).get('raw','') or post.get('status') not in ('draft','publish'):raise ValueError('Owned pilot identity/status check failed')
  report['owned_post']={'id':post['id'],'status':post['status'],'author':post['author'],'modified_gmt':post.get('modified_gmt'),'url':post.get('link')}
  first=folder/'revisions/site-style-v2/image-1.webp'
  if hashlib.sha256(first.read_bytes()).hexdigest()!=FIRST_SHA:raise ValueError('Preserved image 1 changed')
  health=load_json(DATA/'health/latest.json')
  if age_hours(health['checked_at'])>24:raise ValueError('Text capability evidence expired; no hidden audit')
  report['original_image_1_sha256']=FIRST_SHA
  try:valid_record(first,topic,1,article)
  except ImageQualityError:
   report['visual_review_calls']=1;atomic_json(rp,report)
   try:ensure_review(ModelClient(health,allow_calls=True),first,topic,1,article)
   except ImageQualityError:pass
  from .image_quality import review_path
  report['image_1_review']=load_json(review_path(first));report['image_1_current_pass']=report['image_1_review'].get('status')=='reviewed' and report['image_1_review'].get('verdict',{}).get('passed') is True
  scene=OUT/'image-backtests/verified-pool-scene-v1/report.json'
  report['scene_test_status']=load_json(scene).get('status') if scene.exists() else 'not_reserved'
  report['status']='readiness_checked_not_activation'
 except Exception as exc:report.update(status='readiness_blocked',error_type=type(exc).__name__)
 finally:
  report['finished_at']=utcnow();atomic_json(rp,report)
 return {'status':report['status'],'model_calls':report['visual_review_calls'],'post_mutations':0}
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
