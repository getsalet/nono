"""Explicit seven-blog generated-image contract. Staged, never auto-activates.
Secret names only. Pair routing never borrows another blog's or text credentials.
Legacy policies stay unchanged until a tested rollout is deliberately enabled.
"""
import datetime,json,os,re,time
from pathlib import Path
POLICY='afp-blog-generated-images-restore-v1'
CONFIG='data/blog-image-restore.json'
EVIDENCE='data/blog-image-pair-validation/latest.json'
BLOGS=('roya','farsiblog','rozblog','loxblog','blogsky','parsiblog','niloblog')
ROOT=Path(__file__).resolve().parents[1]
def load(root=ROOT):
 p=Path(root)/CONFIG
 if not p.exists():return None
 c=json.loads(p.read_text())
 from agnes_key_pool import NAMES
 if not isinstance(c,dict)or c.get('policy')!=POLICY or type(c.get('enabled'))is not bool:raise RuntimeError('Invalid image restore policy')
 if c.get('model')!='agnes-image-2.5-flash' or any(type(c.get(k))is not int for k in ('minimum_images_per_post','maximum_images_per_post','default_images_per_post')) or (c['minimum_images_per_post'],c['maximum_images_per_post'],c['default_images_per_post'])!=(1,2,1):raise RuntimeError('One to two generated images required; default one')
 pairs=c.get('key_pairs',{})
 if not isinstance(pairs,dict)or set(pairs)!=set(BLOGS):raise RuntimeError('Exactly seven active blog image pairs required')
 names=[]
 for b,pair in pairs.items():
  if not isinstance(pair,list)or len(pair)!=2 or any(n not in NAMES or n=='AGNES_API_KEY8' for n in pair):raise RuntimeError('Invalid image key pair')
  names+=pair
 if len(set(names))!=14 or set(names)&set(c.get('text_preferred_slots',[])):raise RuntimeError('Image pairs must be disjoint and separate from preferred text slots')
 if c.get('families')!=['tape20']or c.get('retired_blogs')!=['blogfa']or c.get('preserve_held_families')is not True or c.get('fallback_to_text_only')is not False:raise RuntimeError('Retirement, family holds and mandatory images must be preserved')
 return c

def enabled(blog,root=ROOT):
 c=load(root)
 return bool(c and c['enabled'] and blog in c['key_pairs'])

def assigned(blog,root=ROOT):
 c=load(root)
 if not c or blog not in BLOGS:raise RuntimeError('No active-blog image key assignment')
 return c['key_pairs'][blog][:]

def reserved(root=ROOT):
 c=load(root)
 return {n for pair in c['key_pairs'].values()for n in pair}if c and c['enabled']else set()

def pool(root=ROOT,environ=None):
 """No text-health filter or fallback. Capability evidence is checked separately."""
 from agnes_key_pool import AgnesKeyPool
 env=os.environ if environ is None else environ
 names={n for pair in load(root)['key_pairs'].values()for n in pair}
 safe={n:env.get(n,'')for n in names}
 safe['AGNES_IMAGE_PAIR_POOL']='1'
 safe['AGNES_API_BASE']=env.get('AGNES_API_BASE','https://apihub.agnes-ai.com/v1')
 return AgnesKeyPool(safe,report_path='/nonexistent-image-pair-text-audit')

def evidence(blog,root=ROOT,current=None):
 from blog_image_connection import settings
 c=load(root);v=json.loads((Path(root)/EVIDENCE).read_text())
 if not c or v.get('policy')!=POLICY or v.get('status')!='completed' or v.get('connection')!=settings('https://apihub.agnes-ai.com/v1')or v.get('post_submissions')!=0 or v.get('key_pairs')!=c['key_pairs']:raise RuntimeError('Matching completed image-pair validation required')
 try:stamp=datetime.datetime.fromisoformat(v['finished_at'].replace('Z','+00:00')).timestamp()
 except (KeyError,TypeError,ValueError):raise RuntimeError('Image pair validation timestamp invalid')from None
 clock=time.time()if current is None else current
 if clock<stamp:raise RuntimeError('Image pair validation timestamp is in the future')
 fresh=clock-stamp<=72*3600;recent=set()
 if not fresh:
  # Ongoing successful image requests are fresher capability proof than a
  # periodic paid probe. A never-used/stale backup is not silently re-admitted.
  from blog_image_key_router import state
  for name,row in state(root)['keys'].items():
   when=row.get('last_success_at_epoch')
   if type(when)in(int,float)and 0<=clock-when<=72*3600:recent.add(name)
 rows=v.get('keys',[])
 if not isinstance(rows,list)or any(not isinstance(x,dict)for x in rows)or len({x.get('secret_name')for x in rows})!=len(rows):raise RuntimeError('Invalid image pair evidence')
 byname={x.get('secret_name'):x for x in rows};result=[]
 for name in assigned(blog,root):
  row=byname.get(name,{});image=row.get('image',{})
  if ((fresh or name in recent) and not row.get('duplicate_of') and image.get('status')=='image_healthy' and image.get('http_status')==200 and type(image.get('width'))is int and type(image.get('height'))is int and 512<=image['height']<image['width']<=10000 and re.fullmatch('[a-f0-9]{64}',str(image.get('image_sha256','')))):result.append(name)
 if not result:raise RuntimeError('No image-proven credential in this blog pair; no outside fallback')
 return result

def prepare(item,post,blog,root=ROOT):
 from blog_generated_image import rollout_enabled,prepare_now
 from blog_reference_scene import context_from_post
 if not enabled(blog,root)or not rollout_enabled(blog,root):raise RuntimeError('Generated image rollout not enabled for this blog')
 if item.get('family')not in load(root)['families']:raise RuntimeError('Image family remains held')
 item['_image_article_context']=context_from_post(post)
 item['editorial_image_decision']='mandatory_generated_1_to_2'
 # Exactly one image is the economical default within the owner's 1..2 range.
 # One corrective candidate is allowed ONLY after a definitive local visual
 # rejection. Existing prepare_now never retries transport/auth/quota as QA.
 # Full candidate, product, topic, watermark and immutable public-byte QA apply.
 url=prepare_now(item,blog,root,max_rounds=2)
 item['image_url']=url
 # Do not retain incompatible trusted-source provenance on an unpublished draft.
 item.pop('image_source',None);item.pop('source_image_review',None)
 return url

def contract_errors(item,post,blog,root=ROOT):
 if not enabled(blog,root)and not item.get('image_generation'):return []
 from bs4 import BeautifulSoup
 from blog_image_gate import validate_record,generated_record_errors
 imgs=BeautifulSoup(post.get('html',''),'html.parser').find_all('img')
 e=[]
 if not 1<=len(imgs)<=2:e.append('Every post requires one to two approved generated images')
 # Current adapter produces one; a second cannot be inserted without its own QA.
 if len(imgs)!=1 or any(x.get('src')!=item.get('image_url')for x in imgs):e.append('Image count/URL does not match reviewed generated asset')
 return e+validate_record(item)+generated_record_errors(item,blog,root)


def failure_details(item,exc,root=ROOT):
 """Fixed diagnostic codes and saved review flags only; never remote exception text."""
 stage=item.get('_generation_stage')
 if stage not in ('remote_cache','generation_api','local_vision_qa','asset_checkpoint','public_vision_qa'):stage='unknown'
 text=str(exc)
 code='image_pipeline_failed'
 if text=='Hosted image queue not configured; no provider request':code='image_queue_not_configured'
 elif text.startswith('Product image rejected:'):code='image_quality_rejected'
 elif text.startswith('Image provider HTTP '):code='image_provider_failed'
 elif stage=='asset_checkpoint':code='image_checkpoint_failed'
 elif stage=='public_vision_qa':code='public_image_verification_failed'
 result={'code':code,'stage':stage,'exception_type':type(exc).__name__}
 rejections=item.get('_image_rejections',[])
 if rejections:
  digest=rejections[-1].get('sha256')
  if re.fullmatch('[a-f0-9]{64}',str(digest)):
   result['rejected_sha256']=digest
   try:row=json.loads((Path(root)/'artifacts/blog-image-reviews'/('tape20-'+digest+'.json')).read_text())
   except (OSError,ValueError):row={}
   verdict=row.get('verdict',{})if row.get('sha256')==digest else{}
   flags=('topic_match','technical_evidence_match','packaging_not_used_as_hardware','product_role_plausible','package_soil_gap_visible','irrigation_geometry_plausible','product_count_match','product_fully_in_frame')
   result['failed_review_flags']=[k for k in flags if verdict.get(k)is False]
   if type(verdict.get('score'))in (int,float):result['review_score']=verdict['score']
 return result
