#!/usr/bin/env python3
"""Controlled acceptance: two product families, zero post submissions."""
import copy,json,time,sys,re,shutil,hashlib
from pathlib import Path
from blog_generated_image import prepare,POLICY,capability_slots,identity
import roya_backlink_queue as roya
ROOT=Path(__file__).resolve().parent.parent

def main():
 queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
 pool=roya.BASE._key_pool
 audited=set(capability_slots())
 active_slots=[pool.slots[k]for k in pool.keys if pool.slots[k]in audited]
 report={'active_secret_slots':active_slots,'healthy_only':True,'policy':POLICY,'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'post_submissions':0,'families':[],'passed':False}
 for family in ['tape20','hose']:
  item=next((copy.deepcopy(x)for x in queue['items']if x.get('family')==family and x.get('published')and x.get('kind')in('city','article')),None)
  row={'family':family,'passed':False}
  if item is not None:
   from blog_reference_scene import context_from_post
   path=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json')
   if path.exists():item['_image_article_context']=context_from_post(json.loads(path.read_text()).get('post')or{})
  try:
   if item is None:raise ValueError('Matching real source topic missing')
   row['url']=prepare(item,'loxblog',root=ROOT);row['passed']=True;row['key']=item['key'];row['review']=item['image_review']
  except Exception as exc:
   row['error_type']=type(exc).__name__;row['stage']=item.get('_generation_stage')if item else None
   if isinstance(getattr(exc,'code',None),int):row['http_status']=exc.code
   if str(exc).startswith(('Image provider HTTP ','Asset-only repository operation failed','Image checkpoint push failed','Product image rejected:','Immutable asset commit not available')):row['reason']=str(exc)[:300]
  if item is not None:
   row['article_context']=item.get('_image_article_context',{})
   row['rejections']=item.get('_image_rejections',[])
   asset_id=identity(item,'loxblog');cache=ROOT/'artifacts/loxblog-backlink-queue/generated-images'
   candidates=list(cache.glob(asset_id+'.webp'))+list((cache/'rejected').glob(asset_id+'-*.webp'))
   destination=ROOT/'artifacts/blog-image-acceptance'/POLICY;destination.mkdir(parents=True,exist_ok=True)
   row['candidate_paths']=[]
   for candidate in candidates:
    raw=candidate.read_bytes();name=family+'-'+hashlib.sha256(raw).hexdigest()[:20]+'.webp'
    target=destination/name;target.write_bytes(raw);row['candidate_paths'].append(str(target.relative_to(ROOT)))
  row['provider_attempts']=item.get('_image_provider_attempts',[])if item else []
  report['families'].append(row)
  report['passed']=len(report['families'])==2 and all(x['passed']for x in report['families'])
  path=ROOT/'data/blog-generated-image-acceptance.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print(json.dumps({k:v for k,v in row.items()if k!='review'},ensure_ascii=False),flush=True)
 return 0 if report['passed']else 1
if __name__=='__main__':sys.exit(main())
