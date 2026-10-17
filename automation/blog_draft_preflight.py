"""Validate real final prose before image work; never creates a publishable QA pass.
Final publisher QA still defaults to require_image=True and is unchanged.
"""
import copy,re
from pathlib import Path

def active(root):
 from blog_image_stock import enabled,control
 return enabled(root)and control(root).get('text_preflight_required')is True

class DraftUnavailable(RuntimeError):pass

def clean(post):
 post=copy.deepcopy(post)
 post['html']=re.sub(r'<p>\s*<img\b[^>]*>\s*</p>','',post.get('html',''),flags=re.I)
 post['html']=re.sub(r'<img\b[^>]*>','',post['html'],flags=re.I)
 post.pop('image_url',None)
 return post

def subject_errors(item,post,root):
 from blog_reference_scene import _lexical_text
 from city_backlink_policy import read
 title=_lexical_text(post.get('title',''));plain=_lexical_text(re.sub('<[^>]*>',' ',post.get('html','')))
 errors=[]
 for crop in read(Path(root)/'data/blog-city-title-matrix.json',{}).get('row_crops',[]):
  crop=_lexical_text(crop)
  if crop and re.search(r'(?<!\w)'+re.escape(crop)+r'(?!\w)',title)and not re.search(r'(?<!\w)'+re.escape(crop)+r'(?!\w)',plain):
   errors.append('Assigned title crop missing from real body: '+crop)
 topic_words=('اتصال','فشار','فیلتر','گرفتگی','تخلیه','فاصله','پایش','نگهداری')
 expected=[word for word in topic_words if word in title]
 if expected and not any(word in plain[:450]for word in expected):
  errors.append('Article introduction must address the assigned technical topic, not a reused generic price/sales article')
 return errors

def check(item,post,blog,root,links=None):
 if not isinstance(post,dict)or not all(isinstance(post.get(k),str)and post[k].strip()for k in('title','slug','html')):
  return ['Actual final article title, slug and body required before image request']
 post=clean(post)
 if blog=='roya':
  import roya_backlink_queue as r
  if links is None:
   from blog_image_stock import read
   links=r.approved_links(item,read(root,'data/roya/link-library.json',{}))
  post=r.resolve_link_tokens(post,links)
  errors,_=r.qa(item,post,links,root=root,require_image=False)
 else:
  from city_backlink_policy import qa,links_for,resolve_editorial_link_tokens
  links=links if links is not None else links_for(item)
  resolve_editorial_link_tokens(post,links)
  errors,_=qa(item,post,links,blog,root=root,require_image=False)
 return list(dict.fromkeys(errors+subject_errors(item,post,root)))

def check_saved(request,source,root):
 from blog_image_stock import read
 path='artifacts/'+request['blog']+'-backlink-queue/items/'+re.sub(r'[^A-Za-z0-9._-]+','_',source['key'])+'.json'
 record=read(root,path)
 if not isinstance(record,dict)or not isinstance(record.get('post'),dict):raise DraftUnavailable('Saved draft not yet available; no image API')
 post=clean(record['post'])
 from blog_reference_scene import context_from_post
 if context_from_post(post)!=request['item'].get('_image_article_context'):
  return ['Saved draft changed after image request; rebuild request from current validated text']
 return check(source,post,request['blog'],root)
