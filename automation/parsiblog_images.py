"""Scoped real AFP product-photo review; generated farm-scene rules stay unchanged."""
import base64,datetime as dt,hashlib,json,math,os,re
from pathlib import Path
import blog_image_gate as shared
import roya_backlink_queue as common
from blog_generated_image import family_enabled
POLICY='parsiblog-real-product-photo-v1'
SCOPE='real-product-photo'
ROOT=Path(__file__).resolve().parents[1]
TRUE_FLAGS=('expected_product_visible','reference_identity_match','afp_brand_recognizable')
FALSE_FLAGS=('wrong_product_present','fake_text_or_logo','implausible_geometry','people_present','unrelated_brand_present')
def controls(item,root):
 try:c=json.loads((Path(root)/'data/blog-generated-image-control.json').read_text())
 except (OSError,ValueError):return ['Image preflight rejected: image controls unreadable']
 if c.get('pause_image_production')is not False:return ['Image preflight rejected: global image stop']
 if not family_enabled(item,root):return ['Image preflight rejected: product family held or cancelled']
 return []
def verdict_errors(value,expected):
 if not isinstance(value,dict):return ['Image preflight rejected: invalid real-photo verdict']
 e=[];score=value.get('score')
 if type(score)not in(int,float)or not math.isfinite(score)or not 90<=score<=100:e.append('Image preflight rejected: real-photo score must be 90-100')
 if value.get('pass')is not True:e.append('Image preflight rejected: real-photo approval missing')
 if value.get('observed_family')!=expected:e.append('Image preflight rejected: real-photo family mismatch')
 for name in TRUE_FLAGS:
  if value.get(name)is not True:e.append('Image preflight rejected: real-photo condition '+name)
 for name in FALSE_FLAGS:
  if value.get(name)is not False:e.append('Image preflight rejected: real-photo defect '+name)
 return e
def record_path(root,family,digest):return Path(root)/'artifacts/parsiblog-backlink-queue/real-product-reviews'/(family+'-'+digest+'.json')
def vision(raw,fmt,expected):
 mime={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}
 if fmt not in mime:raise RuntimeError('Image preflight rejected: unsupported real-photo format')
 instruction=(shared.reference_identity_instruction(expected)+' Inspect the attached actual product photograph from the official AFP website. '
  'This is a REAL PRODUCT PACKSHOT, not an AI-generated agricultural field scene. It is an identity illustration, not evidence of a local farm, crop, installation, technical specification or city. '
  'No installed irrigation, soil, crop, scene integration, exact product count, phone watermark or ground clearance is required in this real-photo scope. '
  'Judge the visible product itself: correct recognizable physical family, authentic legible main AFP branding, no clearly invented logo/text, unrelated brand, mixed/wrong product, people or gross impossible geometry. '
  'Fine print need not be fully readable at this original resolution; do not invent lettering. A transparent/white background and ordinary photographic crop are acceptable if the product remains recognizable. '
  'Approve only overall score at least 90/100 and every identity/safety condition passes. Do not treat the source URL or filename as proof; inspect actual pixels. '
  'Return JSON only with pass (boolean), score (number 0-100), observed_family (exactly tape20, hose, mixed or unknown), expected_product_visible, reference_identity_match, afp_brand_recognizable (booleans), wrong_product_present, fake_text_or_logo, implausible_geometry, people_present, unrelated_brand_present (booleans), reasons (array of short visual observations).')
 content=[{'type':'text','text':instruction},{'type':'image_url','image_url':{'url':'data:'+mime[fmt]+';base64,'+base64.b64encode(raw).decode(),'detail':'high'}}]
 model=os.getenv('IMAGE_REVIEW_MODEL')or common.BASE.AGNES_MODEL
 payload={'model':model,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}}
 key=common.BASE.next_agnes_key()
 result=common.BASE.fetch_json(common.BASE.AGNES_BASE+'/chat/completions',{'Authorization':'Bearer '+key,'Content-Type':'application/json'},payload,timeout=180)
 value=result['choices'][0]['message']['content']
 if isinstance(value,list):value=''.join(x.get('text','')for x in value if isinstance(x,dict))
 return json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip(),flags=re.I)),model
def prepare_image(item,root=ROOT):
 root=Path(root);expected=shared.family(item);errors=controls(item,root)
 if errors:raise RuntimeError('; '.join(errors))
 url=shared.REFERENCES[expected];raw,size,fmt=shared.fetch(url);digest=hashlib.sha256(raw).hexdigest()
 if shared.visual_override_rejected(digest,root):raise RuntimeError('Image preflight rejected: direct visual rejection')
 path=record_path(root,expected,digest);model=os.getenv('IMAGE_REVIEW_MODEL')or common.BASE.AGNES_MODEL
 record=json.loads(path.read_text())if path.exists()else{}
 if record.get('policy')!=POLICY or record.get('scope')!=SCOPE or record.get('sha256')!=digest or record.get('src')!=url or record.get('family')!=expected or record.get('review_model')!=model:
  verdict,model=vision(raw,fmt,expected)
  record={'policy':POLICY,'scope':SCOPE,'family':expected,'src':url,'sha256':digest,'dimensions':list(size),'review_model':model,'reviewed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'verdict':verdict,'not_local_farm_evidence':True}
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 errors=verdict_errors(record.get('verdict'),expected)
 if errors:raise RuntimeError('; '.join(errors))
 item['image_review']=record;item['image_selection']=SCOPE+'-vision-approved'
 return url
def validate_record(item,root=ROOT):
 from blog_image_restore import enabled as restored
 if restored('parsiblog',root):return controls(item,root)+shared.validate_record(item)+shared.generated_record_errors(item,'parsiblog',root)
 root=Path(root);errors=controls(item,root)
 try:expected=shared.family(item)
 except RuntimeError:return errors+['Image preflight rejected: unknown/conflicting product family']
 r=item.get('image_review',{});digest=r.get('sha256','')
 if r.get('policy')!=POLICY or r.get('scope')!=SCOPE or r.get('family')!=expected or r.get('src')!=item.get('image_url')or r.get('src')!=shared.REFERENCES[expected]or not re.fullmatch('[a-f0-9]{64}',digest):return errors+['Image preflight rejected: current scoped real-photo record missing']
 p=record_path(root,expected,digest)
 try:stored=json.loads(p.read_text())
 except (OSError,ValueError):return errors+['Image preflight rejected: persisted real-photo verdict missing']
 if stored!=r:errors.append('Image preflight rejected: persisted real-photo verdict changed')
 if shared.visual_override_rejected(digest,root):errors.append('Image preflight rejected: direct visual rejection')
 if not errors:
  try:raw,_,_=shared.fetch(r['src'])
  except Exception:return ['Image preflight rejected: cannot verify current product-photo bytes']
  if hashlib.sha256(raw).hexdigest()!=digest:errors.append('Image preflight rejected: product-photo bytes changed')
 return errors+verdict_errors(r.get('verdict'),expected)
