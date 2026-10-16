"""Reuse an image-stage draft, never a QA verdict or another article's asset."""
import copy,re

def recover(record):
 if record.get('status')!='failed'or record.get('failure_stage')!='image':return None
 post=record.get('post')
 if not isinstance(post,dict)or not all(isinstance(post.get(k),str)and post[k].strip()for k in ['title','slug','html']):return None
 post=copy.deepcopy(post)
 post['html']=re.sub(r'<p>\s*<img\b[^>]*>\s*</p>','',post['html'],flags=re.I)
 post['html']=re.sub(r'<img\b[^>]*>','',post['html'],flags=re.I)
 post.pop('image_url',None)
 return post
