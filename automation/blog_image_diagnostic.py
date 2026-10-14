#!/usr/bin/env python3
"""One-topic image diagnosis; never generates text, queues or publishes a post."""
import json,os
from pathlib import Path
import city_backlink_policy as policy
import roya_backlink_queue as roya
ROOT=Path(__file__).resolve().parents[1]
def main():
 blog=os.getenv('BLOG_DIAGNOSTIC_BLOG','farsiblog');target=os.getenv('BLOG_DIAGNOSTIC_TARGET','').strip()
 if blog not in policy.BLOGS or not target:raise RuntimeError('An explicit supported blog and topic key are required')
 queue=json.loads((ROOT/'data'/blog/'backlink-queue.json').read_text())
 matches=[x for x in queue['items']if x['key']==target]
 if len(matches)!=1:raise RuntimeError('Topic key is missing or ambiguous')
 item=matches[0];out=ROOT/'artifacts/blog-image-diagnostic';out.mkdir(parents=True,exist_ok=True)
 roya.IMAGE_CACHE=out/'image-cache.json'
 before={'key':item['key'],'family':item['family'],'status':item.get('status')}
 policy.prepare_image(item)
 from blog_image_gate import validate_record
 errors=validate_record(item)
 if errors:raise RuntimeError('Image diagnostic rejected: '+'; '.join(errors))
 result={**before,'blog':blog,'passed':True,'publication_attempted':False,'queue_modified':False,'image_url':item['image_url'],'image_selection':item['image_selection'],'review':item['image_review']}
 (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False),flush=True)
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary:Path(summary).write_text('## Blog image diagnostic\n\n- Topic: '+target+'\n- Passed mandatory image review.\n- No text generation, queue changes or publication.\n')
if __name__=='__main__':main()
