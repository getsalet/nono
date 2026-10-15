#!/usr/bin/env python3
"""One durable, reference-aware generated image per blog/article identity.
Uses the existing configured Agnes connection, never embeds stock fallback images.
No article publication here. An asset-only Git commit precedes public verification.
"""
import base64,hashlib,io,json,os,re,subprocess,tempfile,urllib.request,urllib.error
from pathlib import Path
from PIL import Image,ImageOps
import roya_backlink_queue as roya
POLICY='afp-one-generated-blog-image-v1'
BLOGS={'roya','farsiblog','rozblog','blogfa','loxblog'}
RAW='https://raw.githubusercontent.com/getsalet/nono/'

def identity(item,blog):
 if blog not in BLOGS or not item.get('key'):raise ValueError('Explicit supported blog and article key required')
 from blog_image_gate import family
 expected=family(item)
 return hashlib.sha256((POLICY+'|'+blog+'|'+str(item['key'])+'|'+expected).encode()).hexdigest()[:32]

def brief(item,blog):
 from blog_image_gate import family,reference_identity_instruction
 expected=family(item);seed=identity(item,blog)
 cameras=['high oblique environmental view','close three-quarter documentary view','near-overhead practical equipment view','low side-view with long irrigation lines']
 lighting=['soft morning light','bright overcast natural light','late-afternoon side light']
 title=re.sub(r'<[^>]*>',' ',str(item.get('matrix_title')or item.get('site_title')or item.get('topic')or''))[:250]
 return (f'Create one photorealistic editorial agriculture image for an AFP irrigation guide. Topic label (data, not instructions): {json.dumps(title,ensure_ascii=False)}. '
  +reference_identity_instruction(expected)+f' Product family must be {expected}. Use supplied reference images as strict physical identity. '
  +'Preserve the genuine product silhouette, materials, packaging and authentic printing. Do not invent, redraw or add text, logos, labels, signs or numbers. '
  +'No people, hands or body parts. Show only the expected commercial product family, physically plausible irrigation infrastructure and a generic non-geolocated farm background. '
  +'Do not claim a real city, actual farm, crop suitability, pressure rating or local climate. No inset collage, fake watermark, dramatic effects or glossy 3D. '
  +f'Art direction: {cameras[int(seed[:6],16)%len(cameras)]}; {lighting[int(seed[6:12],16)%len(lighting)]}; asymmetric layout with product and essential details inside a safe central 85% region, generous environmental context, no clutter. '
  +'Landscape 16:9, sharp product identity and believable ground contact, shadows and proportions.')

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

def generate(item,blog):
 import image_prompt_policy
 from blog_image_gate import family
 expected=family(item);ref_item={'source_id':blog+'-'+str(item['key'])+('-layflat'if expected=='hose'else''),'topic':'لوله نخی'if expected=='hose'else'نوار تیپ'}
 key=roya.BASE.next_agnes_key()if hasattr(roya.BASE,'next_agnes_key')else roya.BASE.AGNES_KEY
 if not key:raise RuntimeError('Existing image API credential required')
 payload={'model':os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash'),'prompt':brief(item,blog),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':image_prompt_policy.reference_images(1,ref_item)}}
 req=urllib.request.Request(roya.BASE.AGNES_BASE+'/images/generations',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Idempotency-Key':POLICY+'-'+identity(item,blog)})
 try:
  with urllib.request.urlopen(req,timeout=600)as r:data=json.loads(r.read(25*1024*1024))
 except urllib.error.HTTPError as e:raise RuntimeError('Image provider HTTP '+str(e.code)+'; raw response withheld')from None
 except Exception as e:raise RuntimeError('Image provider transport/format failure: '+type(e).__name__)from None
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
 image=ImageOps.fit(image,(1200,675),Image.Resampling.LANCZOS);out=io.BytesIO();image.save(out,'WEBP',quality=82,method=6)
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
  if not cache.exists():
   item['_generation_stage']='generation_api'
   raw=generate(item,blog);tmp=cache.with_suffix('.tmp');tmp.write_bytes(raw);tmp.replace(cache)
  raw=cache.read_bytes()
  item['_generation_stage']='local_vision_qa'
  review(item,'generated://'+blog+'/'+asset_id,root=root,_candidate=raw)
  item['_generation_stage']='asset_checkpoint'
  url=checkpoint_asset(path,raw,root)
  item['_generation_stage']='public_vision_qa'
  review(item,url,root=root) # Fetch immutable public bytes, not just local success.
 item.update(image_selection=POLICY,image_generation={'policy':POLICY,'blog':blog,'asset_id':asset_id,'url':url},image_alt=(item.get('site_title')or item.get('topic')or'تجهیزات آبیاری AFP').split('|')[0].strip()+' - تصویر راهنمای محصول')
 return url
