#!/usr/bin/env python3
"""Cheap rolling-budget preflight; no API, generation, login or publication."""
import datetime as dt,json,os,sys
from pathlib import Path
from farsiblog_backlink_queue import remaining_publication_budget
ROOT=Path(__file__).resolve().parents[1]
def decision(blog,root=ROOT,current=None,force=False,target=""):
 if blog not in ('farsiblog','rozblog','blogfa','loxblog'):raise ValueError('Unsupported blog')
 current=current or dt.datetime.now(dt.timezone.utc);state=Path(root)/'state'/(blog+'-backlink-progress.json')
 remaining=remaining_publication_budget(state,current)
 recent=[]
 if state.exists():
  for row in json.loads(state.read_text()).get('published',[]):
   at=dt.datetime.fromisoformat(row['at'].replace('Z','+00:00'))
   if at>=current-dt.timedelta(hours=1):recent.append(at)
 result={'proceed':force or remaining>0,'remaining':remaining,'next_eligible_at':(min(recent)+dt.timedelta(hours=1)).isoformat() if remaining==0 and recent else None}
 if blog in ('blogfa','loxblog'):
  journal=Path(root)/('artifacts/'+blog+'-backlink-queue/submission-attempts.json')
  rows=json.loads(journal.read_text())if journal.exists()else{}
  blocked=[key for key,row in rows.items()if row.get('phase')in ('submitting','unconfirmed','reconciled_absent')]
  # Reconciliation permits only a named controlled test, not automatic release.
  # A named manual recovery can still discover an already-public article, but
  # the publisher journal guard remains authoritative before ANY new POST.
  if blocked and not force and not target:
   result.update(proceed=False,reason='native_reconciliation_required',blocked_keys=blocked)
 return result
def main():
 blog=sys.argv[1];prefix=blog.upper()
 force=os.getenv(prefix+'_DRY_RUN')=='1' or os.getenv(prefix+'_LOGIN_DIAGNOSTIC')=='1'
 d=decision(blog,force=force,target=os.getenv(prefix+'_TARGET',''));print(json.dumps(d),flush=True)
 output=os.getenv('GITHUB_OUTPUT')
 if output:
  with open(output,'a')as f:f.write('proceed='+('1'if d['proceed']else'0')+'\n')
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary and not d['proceed']:
  with open(summary,'a')as f:
   if d.get('reason')=='native_reconciliation_required':
    f.write('## Native publication blocked — manual reconciliation required\n\n'+blog+' returned no verified publication for a prior native POST. This is NOT healthy publication or normal hourly budget idle. Approved drafts and the original journal remain intact; no AI generation, browser installation or native resubmission was attempted. A named manual recovery retains the publisher duplicate guard.\n')
   else:f.write('## Normal budget idle\n\nRolling 60-minute publication budget is exhausted. No AI generation, browser installation or publication attempted. Next eligibility: '+str(d['next_eligible_at'])+'. The scheduled queue check remains enabled.\n')
if __name__=='__main__':main()
