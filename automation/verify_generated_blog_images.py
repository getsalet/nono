#!/usr/bin/env python3
"""Controlled acceptance: two product families, zero post submissions."""
import copy,json,time,sys
from pathlib import Path
from blog_generated_image import prepare,POLICY
ROOT=Path(__file__).resolve().parent.parent

def main():
 queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
 report={'policy':POLICY,'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'post_submissions':0,'families':[],'passed':False}
 for family in ['tape20','hose']:
  item=next((copy.deepcopy(x)for x in queue['items']if x.get('family')==family and x.get('kind')in('city','article')),None)
  row={'family':family,'passed':False}
  try:
   if item is None:raise ValueError('Matching real source topic missing')
   row['url']=prepare(item,'loxblog',root=ROOT);row['passed']=True;row['key']=item['key'];row['review']=item['image_review']
  except Exception as exc:
   row['error_type']=type(exc).__name__;row['stage']=item.get('_generation_stage')if item else None
   if isinstance(getattr(exc,'code',None),int):row['http_status']=exc.code
   if str(exc).startswith(('Image provider HTTP ','Asset-only repository operation failed','Image checkpoint push failed','Product image rejected:','Immutable asset commit not available')):row['reason']=str(exc)[:300]
  report['families'].append(row)
  report['passed']=len(report['families'])==2 and all(x['passed']for x in report['families'])
  path=ROOT/'data/blog-generated-image-acceptance.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps({k:v for k,v in row.items()if k!='review'},ensure_ascii=False),flush=True)
 return 0 if report['passed']else 1
if __name__=='__main__':sys.exit(main())
