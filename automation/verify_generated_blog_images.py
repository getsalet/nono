#!/usr/bin/env python3
"""Controlled acceptance: two product families, zero post submissions."""
import copy,json,time,sys,re,shutil,hashlib,os,subprocess
from pathlib import Path
from blog_generated_image import prepare,POLICY,capability_slots,identity
from blog_reference_scene import RECIPE_VERSION
from blog_image_connection import settings
# Snapshot-only diagnostics never constitute acceptance or production approval.
# Preserve native provider aspect; acceptance is still separate from production approval.
import roya_backlink_queue as roya
ROOT=Path(__file__).resolve().parent.parent

def main(initialize_only=False):
 path=ROOT/'data/blog-generated-image-acceptance.json';path.parent.mkdir(parents=True,exist_ok=True)
 def save_report():
  tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2));tmp.replace(path)
 try:source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
 except Exception:source_commit=None
 report={'recipe_version':RECIPE_VERSION,'connection':None,'source_commit':source_commit,'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'active_secret_slots':[],'policy':POLICY,'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'post_submissions':0,'families':[],'passed':False}
 save_report() # Invalidate stale success before configuration, audit or queue loading can fail.
 if initialize_only:return 0
 try:
  report['connection']=settings(roya.BASE.AGNES_BASE)
  pool=roya.BASE._key_pool
  dedicated=bool(os.getenv('IMAGE_API_KEY','').strip())
  audited=set()if dedicated else set(capability_slots())
  report['active_secret_slots']=['IMAGE_API_KEY']if dedicated else[pool.slots[k]for k in pool.keys if pool.slots[k]in audited]
  report['capability_evidence']='actual_image_response_plus_visual_gate'if dedicated else'endpoint_specific_legacy_image_audit'
  queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
 except Exception as exc:
  report['preflight_error']={'type':type(exc).__name__};save_report();print('Image acceptance preflight failed safely: '+type(exc).__name__,flush=True);return 1
 save_report()
 for family in ['tape20','hose']:
  item=next((copy.deepcopy(x)for x in queue['items']if x.get('family')==family and x.get('published')and x.get('kind')in('city','article')),None)
  row={'family':family,'passed':False}
  if item is not None:
   from blog_reference_scene import context_from_post
   post_path=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json')
   if post_path.exists():item['_image_article_context']=context_from_post(json.loads(post_path.read_text()).get('post')or{})
  try:
   if item is None:raise ValueError('Matching real source topic missing')
   if os.getenv('BLOG_IMAGE_CACHE_SNAPSHOT_ONLY')=='1':raise RuntimeError('Cached candidates snapshot only; no generation or publication')
   from blog_reference_scene import scene_plan,prompt,references
   row['scene_plan']=scene_plan(item,'loxblog')
   actual_prompt=prompt(item,'loxblog');actual_refs=references(item)
   row['request_contract']={'recipe_version':RECIPE_VERSION,'prompt_sha256':hashlib.sha256(actual_prompt.encode()).hexdigest(),'prompt_characters':len(actual_prompt),'reference_count':len(actual_refs),'reference_sha256':[hashlib.sha256(ref.encode()).hexdigest()for ref in actual_refs],'scene_intent':row['scene_plan'].get('intent'),'crop':row['scene_plan'].get('crop'),'post_title':item['_image_article_context']['title']}
   save_report()
   row['requested_size']='1024x768'
   row['url']=prepare(item,'loxblog',root=ROOT);row['passed']=True;row['key']=item['key'];row['review']=item['image_review'];row['generation']=item.get('image_generation',{})
  except Exception as exc:
   row['error_type']=type(exc).__name__;row['stage']=item.get('_generation_stage')if item else None
   if isinstance(getattr(exc,'code',None),int):row['http_status']=exc.code
   if str(exc).startswith(('Image provider HTTP ','Asset-only repository operation failed','Image checkpoint push failed','Product image rejected:','Immutable asset commit not available','Cached candidates snapshot only')):row['reason']=str(exc)[:300]
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
  save_report()
  print(json.dumps({k:v for k,v in row.items()if k!='review'},ensure_ascii=False),flush=True)
 return 0 if report['passed']or os.getenv('BLOG_IMAGE_CACHE_SNAPSHOT_ONLY')=='1'else 1
if __name__=='__main__':sys.exit(main(initialize_only='--initialize-only'in sys.argv))
