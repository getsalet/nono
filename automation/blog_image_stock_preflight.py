"""Cheap producer admission before source/text work; ready assets still flow.
The stock writer remains the atomic authority for concurrent final admission.
"""
from blog_image_stock import enabled,rows,control
WAITING={'requested','processing'}
def eligible(candidates,blog,root):
 if not candidates:return []
 if not enabled(root):return candidates
 current=rows(root);cfg=control(root)
 waiting={r['key']for r in current if r['blog']==blog and r['status']in WAITING}
 from blog_editorial_image_policy import generation_needed as required
 candidates=[x for x in candidates if not required(x,blog,root)or x['key']not in waiting]
 active=[r for r in current if r['status']in WAITING|{'ready'}]
 full=len(active)>=cfg['target']or sum(r['blog']==blog for r in active)>=cfg['per_blog_limit']
 if not full:return candidates
 ready={r['key']for r in current if r['blog']==blog and r['status']in('ready','consumed')}
 return [x for x in candidates if not required(x,blog,root)or x['key']in ready]
def waiting_keys(blog,root):
 if not enabled(root):return []
 from blog_editorial_image_policy import generation_needed as required
 return [r['key']for r in rows(root)if r['blog']==blog and r['status']in WAITING and required(r.get('item',{}),blog,root)]
