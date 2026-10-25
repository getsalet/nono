"""Explicit one-post formatting/media revision, not a mass publisher or new-article generator."""
import hashlib,json,re
from urllib.parse import quote
from .queue import DATA,OUT,load_json,atomic_json,get_topic,utcnow,age_hours
from .pipeline import check_brief,validate_article,validate_for_publication
from .client import ModelClient,CapabilityError
from .progress import update,failed
from .media_policy import image_prompt,generate_role
from .image_quality import ensure_review,require_all
from .article_format import DISCLOSURE,faq_html
from .wordpress import WordPress,WPError,illustrated_content

def restore_owned_post(wp,post,req,marker,slug):
 if post.get('id')!=req['post_id'] or post.get('author')!=wp.user_id or marker not in post.get('content',{}).get('raw',''):raise WPError('Restore ownership/marker mismatch')
 if post['status']=='publish':return post
 if req.get('restore_same_post_authorized') is not True or post['status'] not in ('trash','draft'):raise WPError('Restoration requires explicit owner permission')
 if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Reviewed canonical slug required')
 conflicts,_=wp.call('posts?slug='+quote(slug))
 if any(x['id']!=post['id'] for x in conflicts):raise WPError('Canonical slug belongs to another post')
 if post['status']=='trash':
  print('Stage: restore the explicitly authorized same post as draft',flush=True)
  post,_=wp.call('posts/'+str(post['id']),'POST',{'status':'draft','slug':slug})
  if post.get('status')!='draft' or post.get('author')!=wp.user_id or marker not in post.get('content',{}).get('raw',''):raise WPError('Restore verification failed')
 return post

def run(recovery_extension=None):
 req=load_json(DATA/'style-revision-request.json')
 if req.get('publish_revision_authorized') is not True or req.get('max_posts')!=1 or req.get('rebuild_images')!=3:raise ValueError('Explicit single-post revision required')
 ident=req['topic_id'];rev=req['request_id']
 if not re.fullmatch(r'[a-z0-9-]{3,50}',rev):raise ValueError('Invalid revision identifier')
 topic=get_topic('new',ident);brief=load_json(DATA/'briefs'/f'{ident}.json');check_brief(topic,brief)
 folder=OUT/'new'/ident;article=load_json(folder/'article.json');validate_article(article,topic,brief);validate_for_publication(article)
 rp=folder/'wordpress-receipt.json';receipt=load_json(rp)
 if receipt['post_id']!=req['post_id']:raise ValueError('Post/receipt mismatch')
 work=folder/'revisions'/rev;status_path=work/'receipt.json';state=load_json(status_path) if status_path.exists() else {'revision':rev,'post_id':req['post_id'],'media':[],'attempts':0}
 if state.get('verified') is True:return {'status':'already_revised','model_calls':0}
 retry_review=req.get('inspected_transient_retry',{})
 max_attempts=3 if retry_review.get('failed_run_id')==40086065181 and retry_review.get('reason')=='provider_unavailable' and retry_review.get('max_additional_cycles')==1 else 2
 recovery_request=load_json(DATA/'research-request.json') if (DATA/'research-request.json').exists() else {}
 recovery=recovery_request.get('pilot_recovery',{})
 if recovery.get('authorized') is True and recovery.get('topic_id')==ident and recovery.get('max_additional_cycles')==1 and recovery_request.get('request_id')=='research-feeder-rollout-v1':max_attempts=4
 if recovery_extension is not None:
  from .pilot_resume import validate_request
  validate_request(recovery_extension);max_attempts=6
 if state['attempts']>=max_attempts:raise ValueError('Revision retry budget exhausted')
 update('اعتبارسنجی اصلاح همان مقاله',5,ident,topic['title'])
 wp=WordPress();wp.preflight();update('اتصال وردپرس تأیید شد',10);pid=req['post_id'];marker='<!-- afp-agri-v2:'+ident+' -->'
 post,_=wp.call('posts/'+str(pid)+'?context=edit')
 before_status=post['status']
 post=restore_owned_post(wp,post,req,marker,brief['slug']);update('بازگردانی مجاز و مالکیت همان مقاله تأیید شد',20)
 if before_status=='trash':
  atomic_json(work/'restore-audit.json',{'post_id':pid,'from_status':'trash','to_status':'draft','canonical_slug':brief['slug'],'owner_authorized':True,'at':utcnow()})
  receipt.update(status='draft_restored_for_revision',public_verified=False);atomic_json(rp,receipt)
 hp=load_json(DATA/'health/latest.json')
 if age_hours(hp['checked_at'])>24:raise ValueError('Health report expired')
 state['attempts']+=1;atomic_json(status_path,state)
 client=ModelClient(hp,allow_calls=True)
 for i in range(1,4):
  path=work/f'image-{i}.webp'
  if not path.exists():
   update('ساخت تصویر محصول‌دار '+str(i),20+(i-1)*20)
   print('Stage: reference-conditioned AFP product image '+str(i),flush=True)
   blob=generate_role(client,topic,i,article);tmp=path.with_suffix('.tmp');tmp.write_bytes(blob);tmp.replace(path)
  ensure_review(client,path,topic,i,article)
 require_all(work,topic,article)
 # All three images must pass before any new media upload or post mutation.
 for i in range(1,4):
  path=work/f'image-{i}.webp'
  if any(x['index']==i for x in state['media']):continue
  name=ident+'-'+rev+'-image-'+str(i);found,_=wp.call('media?slug='+name+'&context=edit')
  if len(found)>1:raise WPError('Ambiguous revision media')
  if found:
   m=found[0]
   if m.get('author')!=wp.user_id or m.get('post') not in (0,pid):raise WPError('Revision media ownership mismatch')
  else:m,_=wp.call('media','POST',blob=path.read_bytes(),headers={'Content-Type':'image/webp','Content-Disposition':'attachment; filename="'+name+'.webp"'})
  m,_=wp.call('media/'+str(m['id']),'POST',{'post':pid,'title':topic['title']+' — نوار تیپ AFP','alt_text':topic['crop']+' و نوار تیپ AFP در محیط کشاورزی','caption':''})
  state['media'].append({'index':i,'id':m['id'],'url':m['source_url'],'revision_path':str(path.relative_to(OUT.parent.parent))});atomic_json(status_path,state);update('تصویر '+str(i)+' ساخته، برچسب‌گذاری و بارگذاری شد',20+i*20)
 media=sorted(state['media'],key=lambda x:x['index'])
 body=marker+'\n'+illustrated_content(article['content_html'],media,topic['crop'])+DISCLOSURE+faq_html(article['faq'])
 current,_=wp.call('posts/'+str(pid)+'?context=edit')
 if current['modified_gmt']!=post['modified_gmt'] or current['author']!=wp.user_id or current['status'] not in ('draft','publish') or marker not in current['content']['raw']:raise WPError('Post changed during generation; stop for review')
 update('ثبت جدول، سه FAQ و انتشار همان مقاله',90)
 wp.call('posts/'+str(pid),'POST',{'content':body,'excerpt':article['excerpt'],'featured_media':media[0]['id'],'status':'publish','slug':brief['slug']})
 receipt.setdefault('media_history',[]).append({'revision':'before-'+rev,'media':receipt['media']});receipt.update(media=media,style_revision=rev,status='published');atomic_json(rp,receipt)
 wp.verify(pid,topic,rp)
 for m in receipt['media_history'][-1]['media']:
  old,_=wp.call('media/'+str(m['id'])+'?context=edit')
  if old['author']==wp.user_id and old['post']==pid:wp.call('media/'+str(m['id']),'POST',{'caption':''})
 state.update(verified=True,completed_at=utcnow(),content_sha256=hashlib.sha256(body.encode()).hexdigest());atomic_json(status_path,state)
 prov=load_json(folder/'provenance.json');prov.update(image_revision=rev,images='AI reference-conditioned AFP tape product, bottom-right phone label; illustrations, not agronomic evidence',format={'table':True,'faq_count':3,'faq_markup':'faq-section details/summary','visible_image_caption':False});atomic_json(folder/'provenance.json',prov)
 update('اصلاح مقاله و صفحه عمومی تأیید شد',100,status='success')
 return {'status':'revised','post_id':pid,'url':receipt['url'],'images':3,'faq_count':3,'table':True}

def main():
 try:print(json.dumps(run(),ensure_ascii=False));return 0
 except Exception as e:
  failed('سرویس تصویر موقتاً در دسترس نیست؛ تصویر ساخته‌شده محفوظ است' if isinstance(e,CapabilityError) and 'provider_unavailable' in str(e) else 'متوقف؛ گزارش اجرای GitHub را بررسی کنید')
  print('Revision stopped safely: '+(str(e)[:160] if isinstance(e,(ValueError,WPError,CapabilityError)) else type(e).__name__));return 2
if __name__=='__main__':raise SystemExit(main())
