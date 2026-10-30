#!/usr/bin/env python3
"""Three-stage bilingual-label backtest; zero new image generations, zero posts."""
import base64,copy,hashlib,io,json,os,time
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import calibrate_blog_images as base
import blog_reference_scene as scene
import blog_generated_image as generated
import blog_image_gate as gate
import blog_image_restore as restore
import blog_package_labels as labels
ROOT=Path(__file__).resolve().parents[1]
CASES=(('existing',1),('existing-angle',1),('existing-holdout',2))
def clear(item):
 item=copy.deepcopy(item)
 for k in list(item):
  if(k.startswith('_image_')and k!='_image_article_context')or k in('image_review','image_generation','image_url'):item.pop(k,None)
 return item

def prompt(item):
 from blog_image_art_direction import closed_package_prompt
 text=closed_package_prompt(scene.article(item),scene.scene_plan(item,'roya'))
 text=text.replace('about one fifth of frame width','about one third of frame width').replace('Elevated three-quarter close view','Near-frontal three-quarter close view').replace('Angle tiny secondary print away from the camera rather than inventing lettering.','Keep the main front label nearly frontal, sharp and large enough for BOTH small captions to be readable.')
 return text+' OWNER-APPROVED BRAND PRINT: directly BELOW the AFP letters, print exactly "Drip Irrigation Tape" in English. Directly BELOW the blue water-drop symbol, print exactly "آبگسترفراپاریان" in correctly joined Persian, right-to-left. These captions belong ON THE PACKAGE, not the scene or contact watermark. No pseudo-letters or substitute wording; preserve the blue lower band and the authentic AFP symbol and wordmark.'

def main():
 run=os.environ['GITHUB_RUN_ID'];out=ROOT/'artifacts/blog-image-calibration'/run;out.mkdir(parents=True,exist_ok=True)
 report={'run_id':run,'round':'exact-bilingual-labels','post_submissions':0,'article_state_changes':0,'production_activation':False,'maximum_new_images':0,'expected_english':labels.ENGLISH,'expected_persian':labels.PERSIAN,'cases':[]}
 def save():
  raw=json.dumps(report,ensure_ascii=False,indent=2).encode();(out/'report.json').write_bytes(raw);generated.checkpoint_asset(str((out/'report.json').relative_to(ROOT)),raw,ROOT)
 def asset(name,raw):
  p=out/name;p.write_bytes(raw);generated.checkpoint_asset(str(p.relative_to(ROOT)),raw,ROOT);return str(p.relative_to(ROOT))
 try:
  items=base.load_items();slots=restore.evidence('roya',ROOT);save()
  for i,(kind,index)in enumerate(CASES,1):
   item=clear(items[index]);item['key']='caption-calibration-'+run+'-'+str(i);row={'case':i,'kind':kind,'source_key':items[index]['key'],'accepted':False};report['cases'].append(row);save()
   try:
    if kind.startswith('existing'):
     source={'existing':'artifacts/blog-image-calibration/41029742464/case-2-candidate-v2.webp','existing-angle':'artifacts/blog-image-calibration/41031355848/case-2-finish-edit.webp','existing-holdout':'artifacts/blog-image-calibration/41037090356/case-3-native.webp'}[kind];raw=(ROOT/source).read_bytes();row['source_path']=source
    else:
     if json.loads((ROOT/'data/blog-generated-image-control.json').read_text()).get('pause_image_production')is not False:raise RuntimeError('Existing production hold remains active')
     text=prompt(item);row['generation_prompt']=text
     ref=base64.b64decode((scene.reference.ASSET_DIR/'afp-tape.webp.b64').read_text().strip());refs=['data:image/webp;base64,'+base64.b64encode(ref).decode()]
     with patch.object(scene,'prompt',return_value=text),patch.object(scene,'references',return_value=refs):raw=generated.generate(item,'roya',slots=slots,max_attempts=1)
     row['native_path']=asset(f'case-{i}-native.webp',raw)
    row['source_sha256']=hashlib.sha256(raw).hexdigest();row['stage']='local-caption-geometry';save()
    locations=labels.detect_geometry(raw);row['local_geometry']=locations
    image,proof=labels.typeset(raw,locations);buf=io.BytesIO();image.save(buf,'WEBP',quality=95,method=6);raw=buf.getvalue();row['typesetting']=proof
    row['candidate_path']=asset(f'case-{i}-exact-labels.webp',raw);row['stage']='independent-readback';save();reading=labels.inspect(raw)
    row['final_blind_read']=reading;row['caption_errors']=labels.exact_errors(reading)
    if not row['caption_errors']:
     row['stage']='full-image-qa';save();record=gate.review(item,'generated://roya/'+item['key'],root=ROOT,_candidate=raw);row.update(primary_review=record['verdict'],focused_physical_review=record.get('focused_physical_review'),accepted=True)
    row['stage']='complete'
   except Exception as exc:
    row.update(error_type=type(exc).__name__,http_status=getattr(exc,'http_status',getattr(exc,'code',None)))
    if isinstance(exc,RuntimeError)and not row.get('http_status'):row['local_error']=str(exc)[:180]if str(exc).startswith(('Caption','New caption','Clean sleeve','Joined Persian','Verified caption','Product image rejected:'))else'Error details withheld'
    if hasattr(exc,'retry_at'):row['retry_at']=exc.retry_at
   row['provider_attempts']=item.get('_image_provider_attempts',[]);save()
   if row.get('retry_at')or row.get('http_status'):report['stopped_for_service_error']=True;break
 except Exception as exc:report['preflight_error_type']=type(exc).__name__
 finally:report['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
if __name__=='__main__':main()
