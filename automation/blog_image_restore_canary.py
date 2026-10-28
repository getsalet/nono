#!/usr/bin/env python3
"""One real article-image canary, no post write and no production activation.
Use a verified existing Niloblog article only as context; never edit that article.
Local rollout switches are restored even if provider/image QA fails. Asset commits
use the existing separate remote-based Git index, not these local control edits.
"""
import copy,json,os
from pathlib import Path
from bs4 import BeautifulSoup
from blog_image_restore import CONFIG,EVIDENCE,POLICY
ROOT=Path(__file__).resolve().parents[1]
OUT='data/blog-image-restore-canary/latest.json'
def source(root):
 root=Path(root);state=json.loads((root/'data/niloblog/runtime-state.json').read_text())
 if state.get('intent'):raise RuntimeError('Unresolved native-write intent; canary deferred')
 rows=state.get('published',[])
 if not rows:raise RuntimeError('Verified article context unavailable')
 receipt=rows[-1];key=receipt.get('key','')
 import re
 if not re.fullmatch(r'nilo-[a-f0-9]{16}',key):raise RuntimeError('Invalid source article identity')
 saved=json.loads((root/'artifacts/niloblog/items'/f'{key}.json').read_text())
 if saved.get('key')!=key or saved.get('status')!='published' or saved.get('receipt',{}).get('public_post_verified')is not True or saved.get('receipt',{}).get('url')!=receipt.get('url'):raise RuntimeError('Verified public article receipt required')
 post=copy.deepcopy(saved['post']);soup=BeautifulSoup(post['html'],'html.parser')
 for tag in soup.find_all(['img','video','source']):tag.decompose()
 post['html']=str(soup)
 return {'key':key,'family':'tape20','site_title':post['title']},post

def main():
 import blog_generated_image as images
 from blog_image_restore import prepare,contract_errors
 from blog_image_gate import fetch
 proof=json.loads((ROOT/EVIDENCE).read_text())
 if proof.get('policy')!=POLICY or proof.get('status')!='completed' or proof.get('all_pairs_ready')is not True or proof.get('post_submissions')!=0:raise RuntimeError('All fourteen slots need real image proof before article canary')
 expected=os.getenv('PAIR_VALIDATION_RUN_ID')
 if expected and str(proof.get('workflow_run_id'))!=expected:raise RuntimeError('Canary must match the successful pair-validation run')
 item,post=source(ROOT)
 cfg=ROOT/CONFIG;control=ROOT/'data/blog-generated-image-control.json'
 originals={p:p.read_bytes()for p in (cfg,control)}
 original_pool=images.roya.BASE._key_pool;original_key=images.roya.BASE.AGNES_KEY
 report={'policy':POLICY,'status':'started','source_key':item['key'],'blog':'niloblog','workflow_run_id':os.getenv('GITHUB_RUN_ID'),'pair_validation_run_id':proof.get('workflow_run_id'),'post_submissions':0,'existing_article_edited':False,'production_activated':False}
 art=ROOT/'artifacts/blog-image-restore-canary';art.mkdir(parents=True,exist_ok=True)
 try:
  c=json.loads(originals[cfg]);c['enabled']=True;cfg.write_text(json.dumps(c))
  from agnes_key_pool import AgnesKeyPool
  images.roya.BASE._key_pool=AgnesKeyPool();images.roya.BASE.AGNES_KEY=images.roya.BASE._key_pool.next()
  c=json.loads(originals[control]);c['blogs']=list(dict.fromkeys(c['blogs']+['niloblog']));control.write_text(json.dumps(c))
  url=prepare(item,post,'niloblog',ROOT)
  import html
  post['html']='<p><img src="'+html.escape(url,quote=True)+'" alt="'+html.escape(item['image_alt'],quote=True)+'"></p>'+post['html']
  errors=contract_errors(item,post,'niloblog',ROOT)
  if errors:raise RuntimeError('Article image contract rejected')
  raw,size,fmt=fetch(url)
  if fmt!='WEBP':raise RuntimeError('Canary must use actual WebP bytes')
  (art/'article-image.webp').write_bytes(raw)
  report.update(status='passed',image_url=url,dimensions=list(size),article_title=post['title'],image_generation=item['image_generation'],image_review=item['image_review'])
  return 0
 except Exception as exc:
  report.update(status='rejected_or_deferred',failure_type=type(exc).__name__)
  raise
 finally:
  for p,raw in originals.items():p.write_bytes(raw)
  images.roya.BASE._key_pool=original_pool;images.roya.BASE.AGNES_KEY=original_key
  raw=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode();p=ROOT/OUT;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);(art/'report.json').write_bytes(raw)
  images.checkpoint_asset(OUT,raw,ROOT)
if __name__=='__main__':raise SystemExit(main())
