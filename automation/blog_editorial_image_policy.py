"""Editorial need, not an image-quality bypass. No external calls or QA approvals.
Absent policy preserves mandatory imagery; malformed policy fails closed.
Only approved tape20 articles on the four active blogs may be image-free.
"""
import json,re
from pathlib import Path
CONFIG='data/blog-editorial-image-policy.json'
BLOGS={'roya','farsiblog','rozblog','loxblog'}
ROOT=Path(__file__).resolve().parents[1]
IMAGE_FIELDS=('image_url','image_width','image_height','image_alt','image_review','image_generation','image_selection','source_image_rejection','_image_prepared_this_run')
VISUAL_TITLE=re.compile(r'تصویری|عکس(?:\s|$)|نمودار|اینفوگرافیک|گالری|نقشه[‌ ](?:نصب|اجرا)')
VISUAL_BODY=re.compile(r'(?:تصویر|عکس|شکل|نمودار|نقشه)\s*(?:زیر|بالا|پیوست|شماره\s*[۰-۹0-9])|(?:در|مطابق|طبق)\s+(?:این\s+)?(?:تصویر|عکس|شکل|نمودار)')
def load(root=ROOT):
 p=Path(root)/CONFIG
 if not p.exists():return None
 return validate(json.loads(p.read_text()))
def validate(value):
 if not isinstance(value,dict)or value.get('policy')!='afp-editorial-image-need-v1'or value.get('mode')!='text_first' or value.get('blogs')!=['roya','farsiblog','rozblog','loxblog'] or value.get('families')!=['tape20']:raise RuntimeError('Invalid editorial image policy; no optional-image fallback')
 if 'source_image_preferred'in value and type(value['source_image_preferred'])is not bool:raise RuntimeError('Invalid source-image preference')
 if 'source_image_review_required'in value and type(value['source_image_review_required'])is not bool:raise RuntimeError('Invalid source-image review policy')
 if value.get('source_image_review_required')is False and value.get('source_image_preferred')is not True:raise RuntimeError('Trusted images require exact-source preference')
 return value
_UNSET=object()
def optional(item,blog,root=ROOT,config=_UNSET):
 value=load(root)if config is _UNSET else (validate(config)if config is not None else None)
 return bool(value and blog in value['blogs'] and item.get('family')in value['families'])
def required(item,blog,root=ROOT,post=None,config=_UNSET):
 if not optional(item,blog,root,config):return True
 flag=item.get('editorial_image_required')
 if flag is not None and type(flag)is not bool:raise RuntimeError('Editorial image requirement must be boolean')
 if flag is True:return True
 context=item.get('_image_article_context',{})
 title=(post or {}).get('title')or item.get('assigned_title')or item.get('matrix_title')or item.get('title')or context.get('title','')
 body=(post or {}).get('html') if post is not None else context.get('summary','')
 plain=re.sub('<[^>]*>',' ',body or '')
 return bool(VISUAL_TITLE.search(title or '')or VISUAL_BODY.search(plain))
def has_image(item,post):
 return bool(item.get('image_url')or item.get('image_generation')or item.get('image_review')or (post or {}).get('image_url')or re.search(r'<img\b',(post or {}).get('html',''),re.I))
def validate_image(item,post,blog,root=ROOT):
 return required(item,blog,root,post)or has_image(item,post)
def generation_needed(item,blog,root=ROOT):
 from blog_source_image import source_preferred
 return required(item,blog,root)and not source_preferred(item,blog,root)
def saved_optional(record,item,blog,root=ROOT):
 """Only an intact saved image-stage draft; full text/originality QA follows."""
 if record.get('status')!='failed'or record.get('failure_stage')!='image'or item.get('published'):return False
 post=record.get('post')
 return bool(isinstance(post,dict)and all(isinstance(post.get(k),str)and post[k].strip()for k in ('title','slug','html'))and not required(item,blog,root,post))
def prepare_article(item,post,blog,root,prepare):
 """Reuse the linked source first when authorized; no generation fallback."""
 from blog_source_image import source_preferred,prepare_source
 if source_preferred(item,blog,root):return prepare_source(item,post,blog,root)
 if required(item,blog,root,post):
  item['editorial_image_decision']='required';item['editorial_image_required']=True;return prepare()
 from blog_generated_image import identity
 from blog_image_stock import read,request_path
 asset=identity(item,blog)
 row=read(root,request_path(asset),{})
 if row.get('status')in('ready','consumed'):
  item['editorial_image_decision']='retain_approved_image';return prepare()
 # A previously attached candidate still goes through the unchanged full image
 # gate; never silently drop an invalid candidate to claim a quality pass.
 if item.get('image_url')and item.get('image_generation')and item.get('image_review'):
  raise RuntimeError('Attached image has no matching ready stock receipt; reconcile before publication')
 for field in IMAGE_FIELDS:item.pop(field,None)
 post.pop('image_url',None)
 item['editorial_image_decision']='text_only_no_visual_dependency'
 return None
