#!/usr/bin/env python3
"""One bounded hose-only image probe. Never change release controls or publish posts."""
import copy,hashlib,json,os,re,subprocess
from pathlib import Path
import blog_reference_scene as scene
import blog_generated_image as generated
ROOT=Path(__file__).resolve().parents[1]
OUT='artifacts/blog-hose-fullrefs'
def main():
 run=os.getenv('GITHUB_RUN_ID','local')
 if not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise RuntimeError('Invalid diagnostic run identifier')
 report={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'workflow_run_id':run,'post_submissions':0,'production_approval':False,'direct_visual_approval':False,'generation_attempt_limit':1,'family':'hose','image_received':False}
 try:
  queue=json.loads((ROOT/'data/loxblog/backlink-queue.json').read_text())
  item=next(copy.deepcopy(x)for x in queue['items']if x.get('family')=='hose'and x.get('published')and x.get('kind')in('city','article'))
  post_path=ROOT/'artifacts/loxblog-backlink-queue/items'/(re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])+'.json')
  item['_image_article_context']=scene.context_from_post(json.loads(post_path.read_text())['post'])
  refs=scene.references(item)
  report.update(article_key=item['key'],article_context=item['_image_article_context'],scene_plan=scene.scene_plan(item,'loxblog'),family_recipe=scene.recipe_for(item),reference_count=len(refs),reference_sha256=[hashlib.sha256(x.encode()).hexdigest()for x in refs],prompt_sha256=hashlib.sha256(scene.prompt(item,'loxblog').encode()).hexdigest())
  # generate() only: no prepare(), no publish(), no release bypass and no QA approval.
  # A held family may produce a diagnostic candidate, never a production asset.
  raw=generated.generate(item,'loxblog',max_attempts=1)
  path=OUT+'/'+run+'.webp'
  url=generated.checkpoint_asset(path,raw,ROOT)
  report.update(image_received=True,candidate_path=path,candidate_url=url,sha256=hashlib.sha256(raw).hexdigest(),render=item.get('_image_render'))
 except Exception as exc:
  report['error_type']=type(exc).__name__
  if re.fullmatch(r'Image provider HTTP \d+; raw response withheld',str(exc)):report['safe_error']=str(exc)
 finally:
  report['provider_attempts']=locals().get('item',{}).get('_image_provider_attempts',[])
  raw=json.dumps(report,ensure_ascii=False,indent=2).encode()
  generated.checkpoint_asset(OUT+'/'+run+'.json',raw,ROOT)
  print(json.dumps({'image_received':report['image_received'],'production_approval':False,'post_submissions':0,'safe_error':report.get('safe_error')}),flush=True)
 return 0 if report['image_received']else 1
if __name__=='__main__':raise SystemExit(main())
