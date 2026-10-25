"""One explicit content-only repair of our published post, with a restorable backup."""
import json,hashlib,os
from .queue import DATA,OUT,load_json,atomic_json,utcnow,get_topic
from .safe_activation import authorized
from .wordpress import WordPress,WPError
from .internal_links import LINK_POLICY,augment,selected_links,validate_targets,verify_links,external_links
from .progress import update,failed
from .failure_diagnostics import failure_details
ID='pinto-internal-link-repair-v1';TOPIC='agri-a4f1fee1e3ee';POST=524170
def validate(req):
 if (req.get('request_id')!=ID or req.get('topic_id')!=TOPIC or req.get('post_id')!=POST or req.get('authorized') is not True or req.get('policy')!=LINK_POLICY
  or req.get('max_existing_posts')!=1 or req.get('max_new_posts')!=0 or req.get('max_model_calls')!=0 or not req.get('expected_modified_gmt')):raise ValueError('Exact one-post internal-link repair required')
def run():
 req=load_json(DATA/'internal-link-repair-request.json');validate(req);rp=OUT/'internal-link-repairs'/ID/'receipt.json'
 if rp.exists():return {'status':'already_reserved','model_calls':0}
 if not authorized(DATA):raise ValueError('Owner activation required')
 wp=WordPress();wp.preflight();topic=get_topic('new',TOPIC);marker='<!-- afp-agri-v2:'+TOPIC+' -->'
 post,_=wp.call('posts/'+str(POST)+'?context=edit');before=post.get('content',{}).get('raw','')
 if post.get('id')!=POST or post.get('author')!=wp.user_id or post.get('status')!='publish' or marker not in before:raise WPError('Published post ownership/marker changed')
 if post.get('modified_gmt')!=req['expected_modified_gmt']:raise WPError('Post changed since link audit; preserve newer content')
 targets=selected_links(topic,post['link']);validate_targets(targets);after=augment(before,topic,post['link'])
 if after==before:return {'status':'links_already_present','model_calls':0}
 state={'request_id':ID,'post_id':POST,'status':'reserved','at':utcnow(),'run_id':os.environ.get('GITHUB_RUN_ID'),'model_calls':0,'new_posts':0,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'external_citations_preserved':True};atomic_json(rp,state)
 atomic_json(rp.with_name('before.json'),{'post_id':POST,'modified_gmt':post['modified_gmt'],'content_raw':before,'featured_media':post['featured_media'],'title':post['title'],'url':post['link'],'status':'publish'})
 try:
  current,_=wp.call('posts/'+str(POST)+'?context=edit')
  if current.get('modified_gmt')!=post['modified_gmt'] or current.get('content',{}).get('raw')!=before:raise WPError('Post changed during link verification')
  wp.call('posts/'+str(POST),'POST',{'content':after})
  saved,_=wp.call('posts/'+str(POST)+'?context=edit');body=saved['content']['raw']
  if saved['featured_media']!=post['featured_media'] or saved['status']!='publish' or saved['link']!=post['link'] or saved['title']!=post['title']:raise WPError('Non-content post properties changed')
  if external_links(body)!=external_links(before):raise WPError('Scientific citations changed')
  verify_links(body,targets)
  receipt=OUT/'new'/TOPIC/'wordpress-receipt.json';r=load_json(receipt);r['internal_links_policy']=LINK_POLICY;atomic_json(receipt,r)
  result=wp.verify(POST,topic,receipt)
  public,_=wp.call('posts/'+str(POST));verify_links(public['content']['rendered'],targets)
  state.update(status='public_links_verified',completed_at=utcnow(),result=result,links=[{'anchor':t['anchor'],'url':t['url']} for t in targets],after_sha256=hashlib.sha256(body.encode()).hexdigest());atomic_json(rp,state)
  update('لینک‌های داخلی مقاله، دو کلمه کلیدی اصلی و صفحه عمومی تأیید شد',100,TOPIC,topic['title'],status='success')
  return {'status':'public_links_verified','url':post['link'],'model_calls':0,'links':state['links']}
 except Exception as exc:
  state.update(status='stopped_safely',failure=failure_details(exc),completed_at=utcnow());atomic_json(rp,state);failed('اصلاح لینک داخلی متوقف شد؛ نسخه پشتیبان حفظ شده است');return {'status':'stopped_safely','failure':state['failure']}
if __name__=='__main__':
 result=run();print(json.dumps(result,ensure_ascii=False));raise SystemExit(2 if result['status']=='stopped_safely' else 0)
