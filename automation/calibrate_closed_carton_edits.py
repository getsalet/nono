#!/usr/bin/env python3
"""Two bounded reference-conditioned finish edits, never post publication."""
import base64,copy,hashlib,io,json,os,subprocess,time
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import calibrate_blog_images as base
import blog_reference_scene as scene
import blog_generated_image as generated
import blog_image_gate as gate
import blog_image_restore as restore
from blog_image_edit_reference import masked_finish_reference
ROOT=Path(__file__).resolve().parents[1]
INPUTS=(('artifacts/blog-image-calibration/41029742464/case-1-candidate-v2.webp',0),('artifacts/blog-image-calibration/41028392857/case-2-baseline.webp',1))
EDIT_PROMPT=(
 'The neutral rectangular mask in the bottom-right replaces an existing contact watermark; reconstruct matching natural soil there, with no writing or stamp. Edit the supplied photograph, do not invent another product scene. Keep the same ONE AFP carton, its authentic AFP mark, camera viewpoint, plants, black installed lines, proportions, lighting and contact shadows. '
 'Only correct the packaging finish: erase every loose white ribbon and its attached dangling tail OUTSIDE the cylindrical carton, including any black strap connecting to that ribbon. '
 'Continue the existing brown soil texture naturally where these unwanted attachments used to be. The package sidewall and round base remain intact, closed and self-contained. '
 'Do not replace the ribbon with a pipe, another ribbon, a coil or another carton. No new objects or on-image lettering. '
 'Return a single complete natural photograph. Exactly ONE closed AFP carton; its surroundings contain only the existing soil, plants and separate installed black irrigation lines.'
)

def main():
 run=os.environ['GITHUB_RUN_ID'];out=ROOT/'artifacts/blog-image-calibration'/run;out.mkdir(parents=True,exist_ok=True)
 report={'run_id':run,'round':'masked-finish-edit-v2','post_submissions':0,'article_state_changes':0,'production_activation':False,'manual_visual_approval':False,'maximum_candidates':2,'cases':[]}
 def save():
  raw=json.dumps(report,ensure_ascii=False,indent=2).encode();(out/'report.json').write_bytes(raw);generated.checkpoint_asset(str((out/'report.json').relative_to(ROOT)),raw,ROOT)
 try:
  slots=restore.evidence('roya',ROOT);items=base.load_items();save()
  for i,(path,index)in enumerate(INPUTS,1):
   item=copy.deepcopy(items[index]);item['key']='closed-carton-edit-'+run+'-'+str(i)
   for k in list(item):
    if(k.startswith('_image_')and k!='_image_article_context')or k in('image_review','image_generation','image_url'):item.pop(k,None)
   raw=(ROOT/path).read_bytes();masked=masked_finish_reference(raw);reference='data:image/png;base64,'+base64.b64encode(masked).decode()
   row={'case':i,'source_path':path,'source_sha256':hashlib.sha256(raw).hexdigest(),'prompt':EDIT_PROMPT,'reference_stamp_masked':True,'reference_sha256':hashlib.sha256(masked).hexdigest()};report['cases'].append(row);save()
   try:
    with patch.object(scene,'prompt',return_value=EDIT_PROMPT),patch.object(scene,'references',return_value=[reference]):candidate=generated.generate(item,'roya',slots=slots,max_attempts=1)
    dest=out/f'case-{i}-finish-edit.webp';dest.write_bytes(candidate);row.update(path=str(dest.relative_to(ROOT)),sha256=hashlib.sha256(candidate).hexdigest());generated.checkpoint_asset(row['path'],candidate,ROOT)
    try:
     review=gate.review(item,'generated://roya/'+item['key'],root=ROOT,_candidate=candidate);row['primary_review']=review['verdict'];row['primary_passed']=True
    except Exception as exc:
     row['primary_passed']=False;row['primary_error_type']=type(exc).__name__;row['primary_http_status']=getattr(exc,'http_status',getattr(exc,'code',None))
     p=ROOT/'artifacts/blog-image-reviews'/('tape20-'+row['sha256']+'.json')
     if p.exists():row['primary_review']=json.loads(p.read_text()).get('verdict')
    row['independent_physical_review']=gate.focused_physical_check(candidate,'WEBP',os.getenv('IMAGE_REVIEW_MODEL','agnes-3.0-flash'),generated.roya.BASE.next_agnes_key())
    row['no_strip_confirmed']=row['independent_physical_review'].get('package_has_protruding_strip')is False
    row['candidate_passed']=row['primary_passed']and row['no_strip_confirmed']
   except Exception as exc:
    row.update(error_type=type(exc).__name__,candidate_passed=False)
    if hasattr(exc,'retry_at'):row['retry_at']=exc.retry_at
   row['provider_attempts']=item.get('_image_provider_attempts',[]);save()
   if row.get('error_type'):break
 except Exception as exc:report['preflight_error_type']=type(exc).__name__
 finally:report['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
if __name__=='__main__':main()
