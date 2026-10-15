#!/usr/bin/env python3
"""Re-evaluate release and pause controls in the executing job, without secrets."""
import json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def evaluate(release,event,repository_switch=''):
 ids=release.get('verified_post_ids',[])if isinstance(release,dict)else[]
 valid_ids=isinstance(ids,list)and all(type(x)is int and x>0 for x in ids)and len(set(ids))>=2
 approved=isinstance(release,dict)and release.get('enabled') is True and valid_ids and bool(re.fullmatch(r'https://github\.com/getsalet/nono/actions/runs/\d+',str(release.get('acceptance_run',''))))
 paused=repository_switch=='0'
 allowed=event=='workflow_dispatch'or(event=='schedule'and approved and not paused)
 return {'event':event,'versioned_approval':bool(approved),'repository_pause_active':paused,'proceed':bool(allowed)}
def main():
 try:release=json.loads((ROOT/'data/loxblog/deployment-control.json').read_text())
 except (OSError,ValueError):release={}
 report=evaluate(release,os.getenv('RELEASE_EVENT_NAME',''),os.getenv('RELEASE_REPOSITORY_SWITCH',''))
 if os.getenv('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a')as out:out.write('proceed='+('1'if report['proceed']else'0')+'\n')
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as out:out.write('### LoxBlog in-job release check\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n')
 print(json.dumps(report))
 return 0
if __name__=='__main__':raise SystemExit(main())
