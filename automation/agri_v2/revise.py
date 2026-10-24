"""Explicit one-post formatting/media revision, not a mass publisher or new-article generator."""
import hashlib,json,re
from .queue import DATA,OUT,load_json,atomic_json,get_topic,utcnow,age_hours
from .pipeline import check_brief,validate_article,validate_for_publication
from .client import ModelClient
from .media_policy import image_prompt
from .article_format import DISCLOSURE,faq_html
from .wordpress import WordPress,WPError,illustrated_content

def run():
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
 if state['attempts']>=2:raise ValueError('Revision retry budget exhausted')
 wp=WordPress();wp.preflight();pid=req['post_id'];marker='<!-- afp-agri-v2:'+ident+' -->'
 post,_=wp.call('posts/'+str(pid)+'?context=edit')
 if post['author']!=wp.user_id or marker not in post['content']['raw'] or post['status']!='publish':raise WPError('Revision ownership/status mismatch: status='+str(post.get('status'))+'; own_author='+str(post.get('author')==wp.user_id)+'; marker='+str(marker in post.get('content',{}).get('raw','')))
 hp=load_json(DATA/'health/latest.json')
 if age_hours(hp['checked_at'])>24:raise ValueError('Health report expired')
 state['attempts']+=1;atomic_json(status_path,state)
 client=ModelClient(hp,allow_calls=True)
 for i in range(1,4):
  path=work/f'image-{i}.webp'
  if not path.exists():
   print('Stage: reference-conditioned AFP product image '+str(i),flush=True)
   blob=client.image(image_prompt(topic,i));tmp=path.with_suffix('.tmp');tmp.write_bytes(blob);tmp.replace(path)
  if any(x['index']==i for x in state['media']):continue
  name=ident+'-'+rev+'-image-'+str(i);found,_=wp.call('media?slug='+name+'&context=edit')
  if len(found)>1:raise WPError('Ambiguous revision media')
  if found:
   m=found[0]
   if m.get('author')!=wp.user_id or m.get('post') not in (0,pid):raise WPError('Revision media ownership mismatch')
  else:m,_=wp.call('media','POST',blob=path.read_bytes(),headers={'Content-Type':'image/webp','Content-Disposition':'attachment; filename="'+name+'.webp"'})
  m,_=wp.call('media/'+str(m['id']),'POST',{'post':pid,'title':topic['title']+' — نوار تیپ AFP','alt_text':topic['crop']+' و نوار تیپ AFP در محیط کشاورزی','caption':''})
  state['media'].append({'index':i,'id':m['id'],'url':m['source_url'],'revision_path':str(path.relative_to(OUT.parent.parent))});atomic_json(status_path,state)
 media=sorted(state['media'],key=lambda x:x['index'])
 body=marker+'\n'+illustrated_content(article['content_html'],media,topic['crop'])+DISCLOSURE+faq_html(article['faq'])
 current,_=wp.call('posts/'+str(pid)+'?context=edit')
 if current['modified_gmt']!=post['modified_gmt'] or current['author']!=wp.user_id:raise WPError('Post changed during generation; stop for review')
 wp.call('posts/'+str(pid),'POST',{'content':body,'excerpt':article['excerpt'],'featured_media':media[0]['id']})
 receipt.setdefault('media_history',[]).append({'revision':'before-'+rev,'media':receipt['media']});receipt.update(media=media,style_revision=rev);atomic_json(rp,receipt)
 wp.verify(pid,topic,rp)
 for m in receipt['media_history'][-1]['media']:
  old,_=wp.call('media/'+str(m['id'])+'?context=edit')
  if old['author']==wp.user_id and old['post']==pid:wp.call('media/'+str(m['id']),'POST',{'caption':''})
 state.update(verified=True,completed_at=utcnow(),content_sha256=hashlib.sha256(body.encode()).hexdigest());atomic_json(status_path,state)
 prov=load_json(folder/'provenance.json');prov.update(image_revision=rev,images='AI reference-conditioned AFP tape product, bottom-right phone label; illustrations, not agronomic evidence',format={'table':True,'faq_count':3,'faq_markup':'faq-section details/summary','visible_image_caption':False});atomic_json(folder/'provenance.json',prov)
 return {'status':'revised','post_id':pid,'url':receipt['url'],'images':3,'faq_count':3,'table':True}

def main():
 try:print(json.dumps(run(),ensure_ascii=False));return 0
 except Exception as e:
  print('Revision stopped safely: '+(str(e)[:160] if isinstance(e,(ValueError,WPError)) else type(e).__name__));return 2
if __name__=='__main__':raise SystemExit(main())
