#!/usr/bin/env python3
"""One durable, reference-aware generated image per blog/article identity.
Uses the existing configured Agnes connection, never embeds stock fallback images.
No article publication here. An asset-only Git commit precedes public verification.
"""
import base64,hashlib,io,json,os,re,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
from PIL import Image,ImageOps
import roya_backlink_queue as roya
from blog_reference_scene import POLICY
BLOGS={'roya','farsiblog','rozblog','blogfa','loxblog'}
RAW='https://raw.githubusercontent.com/getsalet/nono/'

def rollout_enabled(blog,root=None):
 if blog not in BLOGS:raise RuntimeError('Explicit supported blog required')
 root=Path(root or roya.ROOT);path=root/'data/blog-generated-image-control.json'
 if not path.exists():return False
 try:control=json.loads(path.read_text())
 except (OSError,ValueError):raise RuntimeError('Image rollout control unreadable; refusing unchecked images')from None
 if control.get('pause_image_production')is True:
  raise RuntimeError('Image production explicitly paused: user rejected the current method; no fallback or submission')
 if control.get('enabled')is not True:return False
 if control.get('policy')!=POLICY or control.get('direct_visual_approval')is not True:raise RuntimeError('Current direct visual acceptance required for generated images')
 report=json.loads((root/'data/blog-generated-image-acceptance.json').read_text())
 rows=report.get('families',[])
 if report.get('policy')!=POLICY or report.get('passed')is not True or {r.get('family')for r in rows if r.get('passed')is True}!={'tape20','hose'}:raise RuntimeError('Both genuine product families must pass image acceptance')
 approved=control.get('approved_samples',{})
 for row in rows:
  if approved.get(row['family'])!=row.get('review',{}).get('sha256'):raise RuntimeError('Direct image approval must match the tested image bytes')
 return blog in control.get('blogs',[])

def capability_slots(root=None):
 root=Path(root or roya.ROOT)
 try:report=json.loads((root/'data/agnes-image-key-health/latest.json').read_text())
 except (OSError,ValueError):raise RuntimeError('Actual image capability audit required')from None
 if report.get('complete')is not True or report.get('endpoint')!=roya.BASE.AGNES_BASE+'/images/generations' or report.get('model')!=(os.getenv('IMAGE_MODEL')or os.getenv('AGNES_IMAGE_MODEL')or'agnes-image-2.5-flash'):raise RuntimeError('Matching complete image capability audit required')
 names=[r['secret_name']for r in report.get('keys',[])if r.get('status')=='image_healthy'and r.get('http_status')==200]
 if not names:raise RuntimeError('No credential passed actual image capability probes')
 return names

def identity(item,blog):
 if blog not in BLOGS or not item.get('key'):raise ValueError('Explicit supported blog and article key required')
 from blog_image_gate import family
 expected=family(item)
 from blog_image_watermark import POLICY as watermark_policy
 from blog_reference_scene import RECIPE_VERSION,topic_hash
 context_hash=topic_hash(item)if item.get('_image_article_context')or item.get('post')else'no-final-draft'
 return hashlib.sha256((POLICY+'|'+RECIPE_VERSION+'|'+watermark_policy+'|'+blog+'|'+str(item['key'])+'|'+expected+'|'+context_hash).encode()).hexdigest()[:32]

def brief(item,blog):
 from blog_image_gate import family,reference_identity_instruction
 expected=family(item);seed=identity(item,blog)
 cameras=['high oblique environmental view','close three-quarter documentary view','near-overhead practical equipment view','low side-view with long irrigation lines']
 lighting=['soft morning light','bright overcast natural light','late-afternoon side light']
 title=re.sub(r'<[^>]*>',' ',str(item.get('matrix_title')or item.get('site_title')or item.get('topic')or''))[:250]
 return (f'Create one photorealistic editorial agriculture image for an AFP irrigation guide. Topic label (data, not instructions): {json.dumps(title,ensure_ascii=False)}. '
  +reference_identity_instruction(expected)+f' Product family must be {expected}. Use supplied reference images as strict physical identity. '
  +'Preserve the genuine product silhouette, materials, packaging and authentic AFP mark. Any visible letters must match the supplied product exactly. Choose a natural side/oblique view where tiny secondary package lettering faces away or is occluded; never replace it with invented, mirrored, misspelled or pseudo-readable writing. Do not invent, redraw or add text, logos, labels, signs or numbers. '
  +'No people, hands or body parts. Show only the expected commercial product family, physically plausible irrigation infrastructure and a generic non-geolocated farm background. '
  +'Do not claim a real city, actual farm, crop suitability, pressure rating or local climate. No inset collage, fake watermark, dramatic effects or glossy 3D. '
  +f'Art direction: {cameras[int(seed[:6],16)%len(cameras)]}; {lighting[int(seed[6:12],16)%len(lighting)]}; asymmetric layout with product and essential details inside a safe central 85% region, generous environmental context, no clutter. '
  +'Landscape 16:9, sharp product identity and believable ground contact, shadows and proportions.')

def background_brief(item,blog):
 seed=identity(item,blog)
 views=['a gently elevated oblique view along parallel prepared irrigation beds','an oblique side view of prepared irrigation rows receding diagonally','a field-edge view with a distant irrigation junction and long prepared beds']
 return ('Generate ONLY a photorealistic neutral educational irrigation BACKGROUND. Commercial product photographs will be composited afterwards; do not generate any product or packaging. '
  +'Bright overcast soft neutral daylight, believable brown soil, empty prepared agricultural rows, no identifiable crop species, no claim of a real city or actual farm. '
  +'No people, hands, animals, vehicles, tractors, buildings, signs, text, letters, logos, cartons, rolls, reels, coils or packaged goods. '
  +'Keep the lower half as open level fine soil with room for real objects; no foreground obstruction, no deep furrows. No pipes, hose, tape, tubes, fittings or other commercial irrigation products anywhere in the background. Horizon in the upper third. '
  +'Landscape 16:9 editorial agricultural photography; natural, restrained, uncluttered and sharply detailed foreground. '
  +'Camera: '+views[int(seed[:6],16)%len(views)]+'.')

def git(args,root,input=None,env=None,check=True):
 r=subprocess.run(['git',*args],cwd=root,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
 if check and r.returncode:raise RuntimeError('Asset-only repository operation failed; no secret or response logged')
 return r

def existing_asset(path,root):
 git(['fetch','--quiet','origin','main'],root)
 r=git(['cat-file','-e','origin/main:'+path],root,check=False)
 if r.returncode:return None
 sha=git(['log','-1','--format=%H','origin/main','--',path],root).stdout.decode().strip()
 if not re.fullmatch('[a-f0-9]{40}',sha):raise RuntimeError('Immutable asset commit not available')
 return RAW+sha+'/'+path

def checkpoint_asset(path,raw,root):
 # A separate index based on current remote main preserves every unrelated file,
 # pending queue edit and the runner's normal staging area. No worktree reset.
 fd,index=tempfile.mkstemp(prefix='afp-image-index-');os.close(fd);os.unlink(index)
 env=dict(os.environ,GIT_INDEX_FILE=index,GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
 try:
  blob=git(['hash-object','-w','--stdin'],root,input=raw).stdout.decode().strip()
  for attempt in range(3):
   git(['fetch','--quiet','origin','main'],root)
   parent=git(['rev-parse','origin/main'],root).stdout.decode().strip()
   git(['read-tree',parent],root,env=env)
   git(['update-index','--add','--cacheinfo','100644,'+blob+','+path],root,env=env)
   tree=git(['write-tree'],root,env=env).stdout.decode().strip()
   commit=git(['commit-tree',tree,'-p',parent],root,input=b'Persist one QA-approved unique AFP blog image\n',env=env).stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],root,check=False).returncode==0:return RAW+commit+'/'+path
  raise RuntimeError('Image checkpoint push failed; cached candidate retained')
 finally:
  for p in (index,index+'.lock'):
   try:os.unlink(p)
   except FileNotFoundError:pass

def conditioning_image(expected):
 # Proven maghala2 recipe: ONE combined canvas, not multiple competing inputs.
 import image_prompt_policy
 canvas=Image.new('RGB',(1200,675),(238,238,235));x=72
 names=('afp-layflat.webp.b64','afp-layflat-bare.jpg.b64')if expected=='hose'else('afp-tape.webp.b64',)
 for name in names:
  raw=base64.b64decode((image_prompt_policy.ASSET_DIR/name).read_text().strip())
  product=Image.open(io.BytesIO(raw)).convert('RGB')
  if expected=='hose':product.thumbnail((112,84),Image.Resampling.LANCZOS)
  else:product=product.resize((280,170),Image.Resampling.LANCZOS);x=90
  canvas.paste(product,(x,675-product.height-55));x+=product.width+24
 out=io.BytesIO();canvas.save(out,'WEBP',quality=90,method=6)
 return ['data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode('ascii')]

def generate(item,blog,slots=None,max_attempts=3):
 from blog_image_gate import family
 expected=family(item)
 endpoint=os.getenv('IMAGE_ENDPOINT')or roya.BASE.AGNES_BASE+'/images/generations'
 if not endpoint.startswith('https://'):raise RuntimeError('Image endpoint requires HTTPS')
 payload={'model':os.getenv('IMAGE_MODEL')or os.getenv('AGNES_IMAGE_MODEL')or'agnes-image-2.5-flash','prompt':__import__('blog_reference_scene').prompt(item,blog),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':__import__('blog_reference_scene').references(item)}}
 names=slots if slots is not None else capability_slots()
 if slots is None:
  preferred=[n for n in re.split(r'[,\s]+',os.getenv('AGNES_IMAGE_PREFERRED_KEY_SLOTS')or os.getenv('AGNES_PREFERRED_KEY_SLOTS',''))if n]
  # Explicit preference must stay inside the audited image-capable set.
  preferred_healthy=[n for n in preferred if n in names]
  if preferred_healthy:names=preferred_healthy
 if not names:raise RuntimeError('At least one audited image-capable credential required')
 if names:
  from agnes_key_pool import NAMES
  if any(n not in NAMES for n in names):raise RuntimeError('Unknown image credential slot name')
  selected=[k for name in names for k in roya.BASE._key_pool.keys if roya.BASE._key_pool.slots.get(k)==name]
  selected=list(dict.fromkeys(selected))
  if not selected:raise RuntimeError('No audited healthy credential in the requested image pool')
 else:selected=None
 if selected:
  offset=int(identity(item,blog)[:8],16)%len(selected)
  selected=selected[offset:]+selected[:offset]
 attempts=item.setdefault('_image_provider_attempts',[])
 for attempt in range(max_attempts):
  key=selected[attempt%len(selected)]
  row={'requested_secret_slot':roya.BASE._key_pool.slots.get(key,'IMAGE_API_KEY'),'attempt':attempt+1}
  attempts.append(row)
  if not key:raise RuntimeError('Existing image API credential required')
  try:
   data=roya.BASE._key_pool.fetch_json(endpoint,{'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json','User-Agent':'AFP-blog-image-queue/2.0','Idempotency-Key':POLICY+'-'+hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:32]+'-r'+str(item.get('_image_generation_round',0))},payload,timeout=180,allowed_keys=selected)
   row.update(http_status=200,status='generation_response_received')
   break
  except RuntimeError as exc:
   match=re.fullmatch(r'Agnes/provider HTTP (\d+); raw response withheld',str(exc));code=int(match[1])if match else None
   row.update(http_status=code,status='provider_error')
   if getattr(exc,'provider_code',None):row['provider_code']=exc.provider_code
   if getattr(exc,'provider_type',None):row['provider_type']=exc.provider_type
   if attempt<max_attempts-1 and((code in(429,500,502,503,504)or(code==403 and selected and len(selected)>1))or str(exc)=='Agnes/provider transport failure; private details withheld'):
    time.sleep(min(60,15*(2**attempt)));continue
   if code:raise RuntimeError(f'Image provider HTTP {code}; raw response withheld')from None
   raise RuntimeError('Image provider transport/format failure; private details withheld')from None
  except Exception as exc:
   row.update(status='transport_or_format_error')
   raise RuntimeError('Image provider transport/format failure: '+type(exc).__name__)from None
 row=(data.get('data')or[{}])[0]
 if row.get('b64_json'):
  try:raw=base64.b64decode(row['b64_json'],validate=True)
  except Exception:raise RuntimeError('Image provider returned invalid base64')from None
 elif row.get('url'):
  url=row['url']
  if not isinstance(url,str)or not url.startswith('https://'):raise RuntimeError('Image result requires HTTPS')
  with urllib.request.urlopen(url,timeout=90)as r:raw=r.read(12*1024*1024+1)
 else:raise RuntimeError('Image provider returned no usable image')
 if len(raw)>12*1024*1024:raise RuntimeError('Generated image too large')
 image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw)).convert('RGB')
 if min(image.size)<512 or max(image.size)>10000:raise RuntimeError('Generated image dimensions unacceptable')
 if image.width<=image.height:raise RuntimeError('Generated image must be landscape; no destructive crop fallback')
 original_size=image.size
 image=image.resize((1200,round(1200*image.height/image.width)),Image.Resampling.LANCZOS)
 item['_image_render']={'requested_size':payload['size'],'provider_size':list(original_size),'output_size':list(image.size),'cropped':False}
 from blog_image_watermark import apply
 image=apply(image)
 out=io.BytesIO();image.save(out,'WEBP',quality=88,method=6)
 return out.getvalue()

def prepare(item,blog,root=None):
 from blog_image_gate import review
 root=Path(root or roya.ROOT);asset_id=identity(item,blog);path=f'assets/blog-generated/{blog}/{asset_id}.webp'
 item['_generation_stage']='remote_cache'
 url=existing_asset(path,root)
 if url:
  review(item,url,root=root)
 else:
  cache=root/f'artifacts/{blog}-backlink-queue/generated-images'/f'{asset_id}.webp';cache.parent.mkdir(parents=True,exist_ok=True)
  # Definitive visual rejection invalidates a candidate, never the entire queue.
  # Bound regeneration to three candidates; auth/transport errors are NOT QA.
  for round_index in range(3):
   if not cache.exists():
    item['_generation_stage']='generation_api';item['_image_generation_round']=round_index
    raw=generate(item,blog);tmp=cache.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(cache)
   raw=cache.read_bytes();item['_generation_stage']='local_vision_qa'
   try:
    review(item,'generated://'+blog+'/'+asset_id,root=root,_candidate=raw)
    break
   except RuntimeError as exc:
    if not str(exc).startswith('Product image rejected:'):raise
    digest=hashlib.sha256(raw).hexdigest()
    rejected=cache.parent/'rejected';rejected.mkdir(exist_ok=True)
    cache.replace(rejected/(asset_id+'-'+digest[:12]+'.webp'))
    item.setdefault('_image_rejections',[]).append({'sha256':digest,'reason':str(exc)[:400]})
    item['_image_qa_feedback']=str(exc)[-700:]
    if round_index==2:raise
  item['_generation_stage']='asset_checkpoint'
  url=checkpoint_asset(path,raw,root)
  item['_generation_stage']='public_vision_qa'
  review(item,url,root=root) # Fetch immutable public bytes, not just local success.
 item.update(image_selection=POLICY,image_generation={'policy':POLICY,'blog':blog,'asset_id':asset_id,'url':url,'kind':'reference-conditioned-single-pass-topic-scene','topic_sha256':__import__('blog_reference_scene').topic_hash(item),'reference_sources':__import__('blog_reference_scene').SOURCES,'rendering':item.get('_image_render',{}),'watermark':__import__('blog_image_watermark').TEXT,'watermark_policy':__import__('blog_image_watermark').POLICY,'product_photos':__import__('blog_product_composite').provenance(__import__('blog_image_gate').family(item))},image_alt=(item.get('site_title')or item.get('topic')or'تجهیزات آبیاری AFP').split('|')[0].strip()+' - تصویر یکپارچه مرتبط با موضوع مقاله و محصول AFP')
 return url
