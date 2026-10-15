"""Fail-closed product-family vision gate for blog image reuse.
Inspired by nono image_quality_gate and maghala2 family-aware reference rebuild.
The source website or filename alone is never treated as visual approval.
"""
import base64,hashlib,io,json,math,re,time,urllib.request
from pathlib import Path
from PIL import Image
import roya_backlink_queue as roya
POLICY='blog-product-family-reference-vision-v3-full-frame-and-product-detail'
REFERENCES={
 'tape20':'https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp',
 'hose':'https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'}
def reference_identity_instruction(expected):
 if expected == 'hose':
  return ('Authoritative hose identity references: the labeled packaged reference is the approved AFP packaged layflat coil, '
          'with folded polygonal printed panels, straps and black woven/collapsible hose layers. '
          'The labeled bare reference is its approved bare black woven flat-coil variant. Both are hose-family references, '
          'not two different product families. Shared AFP packaging may contain generic Drip Irrigation Tape '
          'lettering: printed words alone must not override physical reference identity. A separate true '
          'white-and-blue cylindrical drip-tape carton not matching these references is still a wrong product. '
          'One packaged hose or a recognizable packaged/bare pair may match the hose family; '
          'all objects must match those references and remain physically plausible.')
 return ('Authoritative tape identity: the labeled tape reference is the white-and-blue low wide cylindrical AFP drip-tape '
         'carton roll. Reject woven layflat hose, polygonal strapped hose packaging or unrelated products.')


def family(item):
 f=item.get('family')
 if f not in REFERENCES:raise RuntimeError('Unknown product family: no default-to-tape fallback')
 title=item.get('site_title','')+' '+item.get('matrix_title','')
 hose=bool(re.search(r'لوله[\s‌-]*(نخی|نخ.?دار|تاشو)',title));tape=bool(re.search(r'نوار[\s‌-]*(تیپ|آبیاری)',title))
 if f=='tape20'and hose or f=='hose'and tape:raise RuntimeError('Product title/family conflict: stop instead of guessing')
 return f

def approved_url(url):
 return isinstance(url,str)and (url.startswith('https://navar-abyari.ir/wp-content/uploads/')or bool(re.fullmatch(r'https://raw\.githubusercontent\.com/getsalet/nono/[a-f0-9]{40}/assets/blog-generated/(?:roya|farsiblog|rozblog|blogfa|loxblog)/[a-f0-9]{32}\.webp',url)))

def fetch(url):
 if not approved_url(url):raise RuntimeError('Image URL outside approved uploads')
 req=urllib.request.Request(roya.encode_url(url),headers={'User-Agent':'AFP-blog-product-image-gate/1.0'})
 with urllib.request.urlopen(req,timeout=45)as r:
  if not approved_url(r.geturl()):raise RuntimeError('Image redirected outside approved uploads')
  raw=r.read(8*1024*1024+1)
 if len(raw)>8*1024*1024:raise RuntimeError('Image download too large')
 image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw));w,h=image.size
 if min(w,h)<180 or max(w,h)>10000:raise RuntimeError('Image dimensions unacceptable')
 return raw,(w,h),image.format

def verdict_errors(v,expected):
 e=[]
 if not isinstance(v,dict):return ['Invalid vision response']
 if v.get('pass') is not True:e.append('Visual approval required')
 try:score=float(v.get('score',0))
 except (ValueError,TypeError):score=0
 if not math.isfinite(score)or score<70:e.append('Image score below 70')
 if v.get('observed_family')!=expected:e.append('Image product family mismatch')
 if v.get('expected_product_visible') is not True:e.append('Expected product not recognizable')
 for flag in ('wrong_product_present','fake_text_or_logo','implausible_geometry','people_present'):
  if v.get(flag) is not False:e.append('Vision flag not cleared: '+flag)
 return e

def visual_override_rejected(digest,root):
 path=Path(root)/'data/blog-generated-image-visual-review.json'
 if not path.exists():return False
 try:record=json.loads(path.read_text())
 except (OSError,ValueError):raise RuntimeError('Product image rejected: visual review decisions unreadable')from None
 return digest in record.get('rejected_sha256',[])

def review(item,url,root=None,_candidate=None):
 expected=family(item)
 if _candidate is None:raw,(w,h),fmt=fetch(url)
 else:
  if not url.startswith('generated://')or not isinstance(_candidate,bytes)or len(_candidate)>8*1024*1024:raise RuntimeError('Invalid local generation candidate')
  raw=_candidate;image=Image.open(io.BytesIO(raw));image.verify();image=Image.open(io.BytesIO(raw));w,h=image.size;fmt=image.format
  if min(w,h)<180 or max(w,h)>10000:raise RuntimeError('Image dimensions unacceptable')
 digest=hashlib.sha256(raw).hexdigest();root=Path(root or roya.ROOT)
 if visual_override_rejected(digest,root):raise RuntimeError('Product image rejected: direct visual inspection rejected this candidate; do not reuse cached AI approval')
 path=root/'artifacts/blog-image-reviews'/(expected+'-'+digest+'.json')
 if path.exists():record=json.loads(path.read_text())
 else:record={}
 if record.get('policy')!=POLICY or record.get('sha256')!=digest or record.get('family')!=expected:
  ref,_,ref_fmt=fetch(REFERENCES[expected]);mime={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}
  if fmt not in mime or ref_fmt not in mime:raise RuntimeError('Unsupported review image format')
  instruction=f'''{reference_identity_instruction(expected)} Strict product-family image QA. The image labeled CANDIDATE FULL FRAME is the entire candidate; any CANDIDATE PRODUCT DETAIL is a zoom of the same candidate pixels, not an additional reference or a substitute for full-frame safety review. Compare with the explicitly labeled APPROVED PRODUCT REFERENCES. An editorial two-panel image is valid: the real product photo panel establishes identity, while the other panel provides illustrative field context. Do not reject solely because it is a panel layout. Inspect both panels for unwanted products, people, fake lettering and geometry. A field background without a recognizable product in the product panel is NOT sufficient. Expected family: {expected} (tape20 = drip irrigation tape/carton roll; hose = woven yarn-reinforced collapsible layflat transfer hose). Compare recognizable identity with reference, not file name or city label. Reject wrong family, both families mixed, missing identifiable product, fabricated lettering/logos, impossible geometry, any visible person or body part. Genuine product printing matching the reference is allowed. The exact source-approved corner watermark AFP | 09134922013 is permitted; unrelated fabricated lettering or logos still fail. Do not infer crops, soil, climate, province or city identity. Ordinary background infrastructure is allowed, but a wrong commercial product is not. Return JSON only: {{"pass":true,"score":0,"observed_family":"tape20|hose|mixed|unknown","expected_product_visible":true,"wrong_product_present":false,"fake_text_or_logo":false,"implausible_geometry":false,"people_present":false,"reasons":[]}}. Pass only score>=70 and all flags cleared.'''
  def photo(label,data,format):
   return [{'type':'text','text':label},{'type':'image_url','image_url':{'url':'data:'+mime[format]+';base64,'+base64.b64encode(data).decode(),'detail':'high'}}]
  content=[{'type':'text','text':instruction}]+photo('CANDIDATE FULL FRAME: inspect every part for safety and identity.',raw,fmt)
  match=re.search(r'([a-f0-9]{32})(?:\.webp)?$',url)
  if match and (url.startswith('generated://') or '/assets/blog-generated/' in url):
   from blog_product_composite import product_panel_box
   detail=Image.open(io.BytesIO(raw)).convert('RGB').crop(product_panel_box(match[1]))
   zoom=io.BytesIO();detail.save(zoom,'PNG')
   content+=photo('CANDIDATE PRODUCT DETAIL: zoom of the same product panel in the full frame, NOT a reference. Identity must be present here AND in full frame.',zoom.getvalue(),'PNG')
  content+=photo('APPROVED PRODUCT REFERENCE: '+expected,ref,ref_fmt)
  if expected == 'hose':
   bare=Path(__file__).resolve().parent/'assets/afp-layflat-bare.jpg.b64'
   if not bare.exists():raise RuntimeError('Approved bare hose identity reference missing')
   content+=photo('APPROVED BARE HOSE REFERENCE: same hose family, not tape.',base64.b64decode(bare.read_text().strip()),'JPEG')
  payload={'model':roya.BASE.AGNES_MODEL,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}}
  key=roya.BASE.next_agnes_key()if hasattr(roya.BASE,'next_agnes_key')else roya.BASE.AGNES_KEY
  if not key:raise RuntimeError('Vision credential required; never approve by prompt or filename alone')
  for attempt in range(2):
   try:
    response=roya.BASE.fetch_json(roya.BASE.AGNES_BASE+'/chat/completions',{'Authorization':'Bearer '+key,'Content-Type':'application/json'},payload,timeout=180)
    break
   except (TimeoutError,RuntimeError)as exc:
    transient=isinstance(exc,TimeoutError)or bool(re.fullmatch(r'Agnes/provider HTTP (?:429|500|502|503|504); raw response withheld',str(exc)))or str(exc)=='Agnes/provider transport failure; private details withheld'
    if not transient or attempt==1:raise
    time.sleep(5)
    key=roya.BASE.next_agnes_key()
  value=response['choices'][0]['message']['content']
  if isinstance(value,list):value=''.join(x.get('text','')for x in value if isinstance(x,dict))
  verdict=json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip(),flags=re.I))
  record={'policy':POLICY,'sha256':digest,'family':expected,'source_url':url,'reference_url':REFERENCES[expected],'width':w,'height':h,'verdict':verdict,'reviewed_at':roya.now()}
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,ensure_ascii=False,indent=2))
 record['source_url']=url  # Identical digest/policy/family may have another immutable URL.
 errors=verdict_errors(record.get('verdict'),expected)
 if errors:raise RuntimeError('Product image rejected: '+'; '.join(errors))
 item.update(image_url=url,image_width=w,image_height=h,image_review={k:record[k]for k in ('policy','sha256','family','width','height','source_url','verdict')})
 return record

def validate_record(item):
 record=item.get('image_review',{});expected=family(item);e=[]
 if record.get('policy')!=POLICY or record.get('family')!=expected:e.append('Current family-aware image review missing')
 if record.get('source_url')!=item.get('image_url'):e.append('Image URL changed after review')
 if not re.fullmatch('[a-f0-9]{64}',str(record.get('sha256',''))):e.append('Reviewed image digest missing')
 e+=verdict_errors(record.get('verdict'),expected)
 return e

def generated_record_errors(item,blog,root=None):
 """Bind generated image to THIS blog/article; never accept another post's asset."""
 from blog_generated_image import POLICY as generation_policy,identity,rollout_enabled
 generation=item.get('image_generation',{})
 if not generation and not rollout_enabled(blog,root):return []
 errors=[];asset_id=identity(item,blog)
 if generation.get('policy')!=generation_policy:errors.append('Current generated image required for this post')
 if generation.get('blog')!=blog or generation.get('asset_id')!=asset_id:errors.append('Generated image belongs to another blog or article')
 url=item.get('image_url','')
 if not approved_url(url)or not url.endswith('/assets/blog-generated/'+blog+'/'+asset_id+'.webp')or generation.get('url')!=url:errors.append('Generated image must use this article immutable asset URL')
 from blog_product_composite import provenance
 if generation.get('product_photos')!=provenance(family(item)):errors.append('Authentic source photo provenance missing or changed')
 return errors
