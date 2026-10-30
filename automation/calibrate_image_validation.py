#!/usr/bin/env python3
"""Final bounded QA of two EXISTING no-tail candidates; zero image generations."""
import copy,hashlib,json,os,time
from pathlib import Path
import calibrate_blog_images as base
import blog_image_gate as gate
import blog_generated_image as generated
ROOT=Path(__file__).resolve().parents[1]
CASES=(('artifacts/blog-image-calibration/41029742464/case-2-candidate-v2.webp',1),('artifacts/blog-image-calibration/41031355848/case-2-finish-edit.webp',1))
def main():
 run=os.environ['GITHUB_RUN_ID'];out=ROOT/'artifacts/blog-image-calibration'/run;out.mkdir(parents=True,exist_ok=True)
 report={'run_id':run,'round':'existing-image-validation','post_submissions':0,'article_state_changes':0,'image_generations':0,'production_activation':False,'cases':[]}
 def save():
  raw=json.dumps(report,ensure_ascii=False,indent=2).encode();(out/'report.json').write_bytes(raw);generated.checkpoint_asset(str((out/'report.json').relative_to(ROOT)),raw,ROOT)
 items=base.load_items()
 for i,(path,index)in enumerate(CASES,1):
  item=copy.deepcopy(items[index]);item['key']='image-validation-'+run+'-'+str(i)
  for k in list(item):
   if(k.startswith('_image_')and k!='_image_article_context')or k in('image_review','image_generation','image_url'):item.pop(k,None)
  raw=(ROOT/path).read_bytes();row={'case':i,'source_path':path,'sha256':hashlib.sha256(raw).hexdigest(),'accepted':False};report['cases'].append(row);save()
  try:
   record=gate.review(item,'generated://roya/'+item['key'],root=ROOT,_candidate=raw)
   row.update(accepted=True,verdict=record['verdict'],focused_physical_review=record.get('focused_physical_review'),closed_package_required=record.get('closed_package_required'),package_finish_policy=record.get('package_finish_policy'))
  except Exception as exc:
   row.update(error_type=type(exc).__name__,http_status=getattr(exc,'http_status',getattr(exc,'code',None)),error_category='quality_rejection'if str(exc).startswith('Product image rejected:')else'validation_failure')
   saved=ROOT/'artifacts/blog-image-reviews'/('tape20-'+row['sha256']+'.json')
   if saved.exists():
    evidence=json.loads(saved.read_text());row.update(verdict=evidence.get('verdict'),focused_physical_review=evidence.get('focused_physical_review'))
  save()
 report['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
if __name__=='__main__':main()
