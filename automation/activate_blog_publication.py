#!/usr/bin/env python3
"""Dispatch one scoped canary per blog; never publish directly or log tokens."""
import json,os,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS={'roya':'roya-backlink-queue.yml','farsiblog':'farsiblog-content.yml','rozblog':'rozblog-content.yml','loxblog':'loxblog-content.yml'}
def plan(control):
 if control.get('enabled')is not True or control.get('pause_image_production')is not False:return []
 scope=control.get('enabled_families',[])
 if not scope or not set(scope)<={'tape20','hose'}:raise RuntimeError('Explicit approved family scope required')
 result=[]
 for blog in control.get('blogs',[]):
  if blog not in WORKFLOWS:raise RuntimeError('Unknown blog')
  inputs={'count':'1','dry_run':'0','target':''}
  if blog!='roya':inputs['publish']='1'
  result.append({'blog':blog,'workflow':WORKFLOWS[blog],'inputs':inputs})
 return result
def main():
 control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text());jobs=plan(control)
 if not jobs:print('Activation not requested or control paused; no workflow dispatched.');return 0
 from blog_generated_image import rollout_enabled
 for job in jobs:
  if not rollout_enabled(job['blog'],ROOT):raise RuntimeError('Approved scoped image rollout required')
 if control.get('activation_dispatch_mode')=='sequential_by_hour_monitor':
  print('Approved tape-only activation delegated to finite sequential hour monitor.');return 0
 token=os.getenv('GH_TOKEN','')
 if not token:raise RuntimeError('Scoped Actions token unavailable')
 report=[]
 for job in jobs:
  url='https://api.github.com/repos/getsalet/nono/actions/workflows/'+job['workflow']+'/dispatches'
  req=urllib.request.Request(url,data=json.dumps({'ref':'main','inputs':job['inputs']}).encode(),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'})
  try:
   with urllib.request.urlopen(req,timeout=30)as response:status=response.status
  except urllib.error.HTTPError as exc:status=exc.code;exc.close()
  except Exception:status=None
  report.append({'blog':job['blog'],'workflow_dispatch_accepted':status==204,'http_status':status})
  print(json.dumps(report[-1]),flush=True)
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as out:
   out.write('## Scoped publication activation\n\nEnabled families: '+', '.join(control['enabled_families'])+'. Other families remain held.\n\n')
   out.write('Dispatch acceptance is NOT a verified published post. Each pipeline retains article/image/native/duplicate and rolling-budget checks. One initial article requested per blog.\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n')
 return 0 if all(x['workflow_dispatch_accepted']for x in report)else 1
if __name__=='__main__':raise SystemExit(main())
