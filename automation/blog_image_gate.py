"""Fail-closed product-family vision gate for blog image reuse.
Inspired by nono image_quality_gate and maghala2 family-aware reference rebuild.
The source website or filename alone is never treated as visual approval.
"""
import base64,hashlib,io,json,re,urllib.request
from pathlib import Path
from PIL import Image
import roya_backlink_queue as roya
POLICY='blog-product-family-reference-vision-v2-physical-identity'
REFERENCES={
 'tape20':'https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp',
 'hose':'https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'}
def reference_identity_instruction(expected):
 if expected == 'hose':
  return ('Authoritative hose identity references: image 2 is the approved AFP packaged layflat coil, '
          'with folded polygonal printed panels, straps and black woven/collapsible hose layers. '
          'Image 3 is its approved bare black woven flat-coil variant. Both are hose-family references, '
          'not two different product families. Shared AFP packaging may contain generic Drip Irrigation Tape '
          'lettering: printed words alone must not override physical reference identity. A separate true '
          'white-and-blue cylindrical drip-tape carton not matching these references is still a wrong product. '
          'One packaged hose or a recognizable packaged/bare pair may match the hose family; '
          'all objects must match those references and remain physically plausible.')
 return ('Authoritative tape identity: image 2 is the white-and-blue low wide cylindrical AFP drip-tape '
         'carton roll. Reject woven layflat hose, polygonal strapped hose packaging or unrelated products.')


def family(item):
 f=item.get('family')
 if f not in REFERENCES:raise RuntimeError('Unknown product family: no default-to-tape fallback')
 title=item.get('site_title','')+' '+item.get('matrix_title','')
 hose=bool(re.search(r'لوله[\s‌-]*(نخی|نخ.?دار|تاشو)',title));tape=bool(re.search(r'نوار[\s‌-]*(تیپ|آبیاری)',title))
 if f=='tape20'and hose or f=='hose'and tape:raise RuntimeError('Product title/family conflict: stop instead of guessing')
 return f

def fetch(url):
 if not url.startswith('https://navar-abyari.ir/wp-content/uploads/'):raise RuntimeError('Image URL outside approved uploads')
 req=urllib.request.Request(roya.encode_url(url),headers={'User-Agent':'AFP-blog-product-image-gate/1.0'})
 with urllib.request.urlopen(req,timeout=45)as r:
  if not r.geturl().startswith('https://navar-abyari.ir/wp-content/uploads/'):raise RuntimeError('Image redirected outside approved uploads')
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
 if score<70:e.append('Image score below 70')
 if v.get('observed_family')!=expected:e.append('Image product family mismatch')
 if v.get('expected_product_visible') is not True:e.append('Expected product not recognizable')
 for flag in ('wrong_product_present','fake_text_or_logo','implausible_geometry','people_present'):
  if v.get(flag) is not False:e.append('Vision flag not cleared: '+flag)
 return e

def review(item,url,root=None):
 expected=family(item);raw,(w,h),fmt=fetch(url);digest=hashlib.sha256(raw).hexdigest();root=Path(root or roya.ROOT)
 path=root/'artifacts/blog-image-reviews'/(expected+'-'+digest+'.json')
 if path.exists():record=json.loads(path.read_text())
 else:record={}
 if record.get('policy')!=POLICY or record.get('sha256')!=digest or record.get('family')!=expected:
  ref,_,ref_fmt=fetch(REFERENCES[expected]);mime={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}
  if fmt not in mime or ref_fmt not in mime:raise RuntimeError('Unsupported review image format')
  instruction=f'''{reference_identity_instruction(expected)} Strict product-family image QA. Image 1 is the candidate; image 2 is the approved {expected} product reference. Expected family: {expected} (tape20 = drip irrigation tape/carton roll; hose = woven yarn-reinforced collapsible layflat transfer hose). Compare recognizable identity with reference, not file name or city label. Reject wrong family, both families mixed, missing identifiable product, fabricated lettering/logos, impossible geometry, any visible person or body part. Genuine product printing matching the reference is allowed. The exact source-approved corner watermark AFP | 09134922013 is permitted; unrelated fabricated lettering or logos still fail. Do not infer crops, soil, climate, province or city identity. Ordinary background infrastructure is allowed, but a wrong commercial product is not. Return JSON only: {{"pass":true,"score":0,"observed_family":"tape20|hose|mixed|unknown","expected_product_visible":true,"wrong_product_present":false,"fake_text_or_logo":false,"implausible_geometry":false,"people_present":false,"reasons":[]}}. Pass only score>=70 and all flags cleared.'''
  content=[{'type':'text','text':instruction}]+[{'type':'image_url','image_url':{'url':'data:'+mime[f]+';base64,'+base64.b64encode(b).decode()}}for b,f in ((raw,fmt),(ref,ref_fmt))]
  if expected == 'hose':
   bare=Path(__file__).resolve().parent/'assets/afp-layflat-bare.jpg.b64'
   if not bare.exists():raise RuntimeError('Approved bare hose identity reference missing')
   content.append({'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+bare.read_text().strip()}})
  payload={'model':roya.BASE.AGNES_MODEL,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}}
  key=roya.BASE.next_agnes_key()if hasattr(roya.BASE,'next_agnes_key')else roya.BASE.AGNES_KEY
  if not key:raise RuntimeError('Vision credential required; never approve by prompt or filename alone')
  req=urllib.request.Request(roya.BASE.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=90)as r:response=json.loads(r.read())
  value=response['choices'][0]['message']['content']
  if isinstance(value,list):value=''.join(x.get('text','')for x in value if isinstance(x,dict))
  verdict=json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip(),flags=re.I))
  record={'policy':POLICY,'sha256':digest,'family':expected,'source_url':url,'reference_url':REFERENCES[expected],'width':w,'height':h,'verdict':verdict,'reviewed_at':roya.now()}
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,ensure_ascii=False,indent=2))
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
