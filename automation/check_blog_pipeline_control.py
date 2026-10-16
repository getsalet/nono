#!/usr/bin/env python3
"""Stdlib-only stop gate before queue changes, dependencies, credentials or APIs."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLOGS=('roya','farsiblog','rozblog','blogfa','loxblog')
def decision(blog,root=ROOT):
 if blog not in BLOGS:raise ValueError('Unsupported blog')
 path=Path(root)/'data/blog-generated-image-control.json'
 try:
  value=json.loads(path.read_text())
  if not isinstance(value,dict)or type(value.get('pause_image_production'))is not bool:raise ValueError('Invalid control')
 except (OSError,ValueError,TypeError):return {'blog':blog,'proceed':False,'reason':'control_unavailable','publication_attempted':False}
 paused=value['pause_image_production']
 return {'blog':blog,'proceed':not paused,'reason':'user_pause'if paused else'other_gates_still_required','publication_attempted':False}
def main():
 report=decision(sys.argv[1]);print(json.dumps(report))
 if os.getenv('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a')as out:out.write('proceed='+('1'if report['proceed']else'0')+'\n')
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as out:
   out.write('## '+report['blog']+' pipeline: '+('preflight allowed'if report['proceed']else'BLOCKED — '+report['reason'])+'\n\n')
   out.write('This is a control decision, NOT successful generation or publication. ')
   out.write('No queue rebuild, credential validation, dependency/browser installation or article submission is allowed while blocked. Other release, budget, image and duplicate-prevention gates remain mandatory.\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
