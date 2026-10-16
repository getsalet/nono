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


def capacity_retry_due(item,current=None):
 """Only transient image-capacity failures; never visual/text/auth failures."""
 import datetime
 if item.get('status')!='failed' or item.get('published') or item.get('failure_stage')!='image':return False
 reason=str(item.get('last_error')or'')
 if not any(marker in reason for marker in ('ImageProviderBusy','ImageQueueBusy','Image provider queue full; generation deferred until','Shared image queue occupied;')):return False
 stamp=item.get('next_retry_at')
 if not stamp:return True  # Legacy capacity failures had no per-item timer.
 try:
  at=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))
  if at.tzinfo is None:return False
  return at<=(current or datetime.datetime.now(datetime.timezone.utc))
 except (ValueError,TypeError,AttributeError):return False
