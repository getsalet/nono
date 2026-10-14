#!/usr/bin/env python3
"""Cheap rolling-budget preflight; no API, generation, login or publication."""
import datetime as dt,json,os,sys
from pathlib import Path
from farsiblog_backlink_queue import remaining_publication_budget
ROOT=Path(__file__).resolve().parents[1]
def decision(blog,root=ROOT,current=None,force=False):
 if blog not in ('farsiblog','rozblog'):raise ValueError('Unsupported blog')
 current=current or dt.datetime.now(dt.timezone.utc);state=Path(root)/'state'/(blog+'-backlink-progress.json')
 remaining=remaining_publication_budget(state,current)
 recent=[]
 if state.exists():
  for row in json.loads(state.read_text()).get('published',[]):
   at=dt.datetime.fromisoformat(row['at'].replace('Z','+00:00'))
   if at>=current-dt.timedelta(hours=1):recent.append(at)
 return {'proceed':force or remaining>0,'remaining':remaining,'next_eligible_at':(min(recent)+dt.timedelta(hours=1)).isoformat() if remaining==0 and recent else None}
def main():
 blog=sys.argv[1];prefix='FARSIBLOG'if blog=='farsiblog'else'ROZBLOG'
 force=os.getenv(prefix+'_DRY_RUN')=='1' or os.getenv('ROZBLOG_LOGIN_DIAGNOSTIC')=='1'
 d=decision(blog,force=force);print(json.dumps(d),flush=True)
 output=os.getenv('GITHUB_OUTPUT')
 if output:
  with open(output,'a')as f:f.write('proceed='+('1'if d['proceed']else'0')+'\n')
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary and not d['proceed']:
  with open(summary,'a')as f:f.write('## Normal budget idle\n\nRolling 60-minute publication budget is exhausted. No AI generation, browser installation or publication attempted. Next eligibility: '+str(d['next_eligible_at'])+'. The scheduled queue check remains enabled.\n')
if __name__=='__main__':main()
