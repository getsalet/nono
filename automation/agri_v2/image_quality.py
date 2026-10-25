"""Fail-closed vision gate bound to exact image, topic, role, recipe and reference bytes."""
import hashlib,json
from pathlib import Path
from .queue import atomic_json,load_json,utcnow
from .media_policy import POLICY,contract_hash,reference_images
from .healthcheck import TEXT_MODEL
REVIEW_POLICY='agri-vision-qa-v4-hardware-identity'
CHECKS=('hardware_identity_match','crop_stage_match','role_camera_match','topic_evidence_match','product_identity_match','single_product','product_scale_match','product_fully_in_frame','package_separate_from_plumbing','physical_geometry_plausible','packaging_closed_no_protruding_material','no_people','no_added_text','phone_label_correct')
class ImageQualityError(ValueError):pass
def verdict(value):
 if not isinstance(value,dict):raise ImageQualityError('Vision verdict must be an object')
 checks=value.get('checks');score=value.get('score');reasons=value.get('reasons')
 if not isinstance(checks,dict) or any(type(checks.get(k))is not bool for k in CHECKS):raise ImageQualityError('Missing, unknown or non-boolean vision check')
 if type(score)is not int or not 0<=score<=100:raise ImageQualityError('Invalid vision score')
 if not isinstance(reasons,list) or not reasons or any(not isinstance(x,str) or not x.strip() for x in reasons):raise ImageQualityError('Vision review reasons required')
 return {'passed':all(checks[k] for k in CHECKS) and score>=85,'checks':{k:checks[k] for k in CHECKS},'score':score,'reasons':[x[:500] for x in reasons[:12]]}
def binding(path,topic,kind,article=None):
 return {'image_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'contract_sha256':contract_hash(topic,kind,article),'reference_sha256':hashlib.sha256(reference_images()[0].encode()).hexdigest(),'policy':POLICY,'role':kind,'topic_id':topic.get('id'),'review_model':TEXT_MODEL,'review_policy':REVIEW_POLICY}
def review_path(path):return Path(path).with_suffix('.quality.json')
def valid_record(path,topic,kind,article=None):
 rp=review_path(path)
 if not rp.exists():raise ImageQualityError('Image has no current visual review')
 row=load_json(rp);expected=binding(path,topic,kind,article)
 if any(row.get(k)!=v for k,v in expected.items()):raise ImageQualityError('Image/contract/reference review binding changed')
 if row.get('status')!='reviewed' or row.get('verdict',{}).get('passed') is not True or not verdict(row.get('verdict'))['passed']:raise ImageQualityError('Image rejected or visual review unavailable; no upload')
 return row

def ensure_review(client,path,topic,kind,article=None):
 path=Path(path);rp=review_path(path);expected=binding(path,topic,kind,article)
 if rp.exists():
  row=load_json(rp)
  if all(row.get(k)==v for k,v in expected.items()):return valid_record(path,topic,kind,article)
 row={**expected,'checked_at':utcnow(),'reviewer':'automated_multimodal_model','human_review_claimed':False,'status':'review_started','no_auto_regeneration':True}
 atomic_json(rp,row) # reserve before call: crash or unavailable review never becomes pass
 try:
  result=verdict(client.review_image(path.read_bytes(),topic,kind,article));row.update(status='reviewed',verdict=result)
 except Exception as exc:
  row.update(status='review_unavailable',error_type=type(exc).__name__)
  atomic_json(rp,row);raise ImageQualityError('Visual review unavailable or malformed; no upload') from None
 atomic_json(rp,row)
 if not result['passed']:raise ImageQualityError('Image rejected by visual QA; preserve bytes, no upload or automatic regeneration')
 return row

def require_all(folder,topic,article=None):
 for kind in (1,2,3):valid_record(Path(folder)/f'image-{kind}.webp',topic,kind,article)
