#!/usr/bin/env python3
"""Diagnostic exact-token language repair. Never saves a ready post or native state."""
import argparse,copy,json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(target,root=ROOT,model=None):
 if not re.fullmatch(r'pb-[0-9a-f]{20}',target):raise ValueError('One approved Parsiblog key required')
 from parsiblog_text import language_patch_prompt,apply_language_patch,post_language_errors,language_patch_rejection,language_feedback
 from parsiblog_policy import qa
 if model is None:
  from roya_backlink_queue import agnes
  model=lambda request:agnes(request,temperature=0)
 rejected=json.loads((root/'artifacts/parsiblog-backlink-queue/rejected'/f'{target}.json').read_text())
 if rejected.get('key')!=target or rejected.get('passed')is not False or rejected.get('errors')!=['Unexpected foreign-language text in Persian article']:raise ValueError('Diagnostic requires a saved language-only QA rejection')
 post=copy.deepcopy(rejected['post']);before=language_feedback(post)
 matrix=json.loads((root/'data/parsiblog/title-matrix.json').read_text());item=next((r for r in matrix['items']if r['key']==target),None)
 if item is None:raise ValueError('Target not in approved matrix')
 result={'target':target,'run_id':os.getenv('GITHUB_RUN_ID'),'mode':'language_diagnostic_only','native_write_attempted':False,'ready_post_saved':False,'state_changed':False,'publication_authorized':False,'full_source_and_editorial_review_still_required':True,'invalid_tokens_before':before}
 payload=model(language_patch_prompt(post))
 try:fixed,audit=apply_language_patch(post,payload)
 except ValueError as e:return dict(result,status='rejected',patch_rejection=language_patch_rejection(e,payload))
 errors,_=qa(item,fixed,root,require_image=False,originality=False)
 return dict(result,status='validated_language_not_published'if not errors else'rejected',language_repairs=audit,invalid_tokens_after=language_feedback(fixed),qa_errors=errors)
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 result=validate(a.target);out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Language diagnostic:',result['status'],'no ready post, native write or state change')
 return 0 if result['status']=='validated_language_not_published'else 1
if __name__=='__main__':sys.exit(main())
