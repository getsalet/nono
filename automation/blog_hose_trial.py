"""Conservative three-request diagnostic budget; never changes production scope."""
import json,os,re,subprocess,time
from pathlib import Path
CONFIG='data/blog-hose-trial-control.json'
DIRECTORY='artifacts/blog-hose-fullrefs'
def decision(cfg,reports,now):
 if cfg.get('enabled')is not True:return 'disabled'
 if (cfg.get('maximum_requests')!=3 or cfg.get('minimum_interval_seconds')!=1200
     or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',str(cfg.get('trial_id','')))):
  raise RuntimeError('Invalid bounded hose trial control')
 for key in ('expires_at_epoch','baseline_last_attempt_epoch'):
  if isinstance(cfg.get(key),bool)or not isinstance(cfg.get(key),(int,float)):raise RuntimeError('Invalid trial timestamp')
 if now>=cfg['expires_at_epoch']:return 'expired'
 baseline=cfg.get('baseline_runs')
 if not isinstance(baseline,list)or baseline!=['39086561494']:raise RuntimeError('Explicit real baseline required')
 selected=[r for r in reports if str(r.get('workflow_run_id'))in baseline or r.get('trial_id')==cfg['trial_id']]
 if not any(str(r.get('workflow_run_id'))in baseline for r in selected):raise RuntimeError('Baseline provider evidence missing')
 if any(r.get('image_received')is True for r in selected):return 'candidate_received'
 for r in selected:
  for a in r.get('provider_attempts',[]):
   if a.get('http_status')in(401,402,403,429)or a.get('provider_code')=='insufficient_quota':return 'provider_limit_requires_review'
 used=sum(max(1 if r.get('provider_request_reserved')is True else 0,len(r.get('provider_attempts',[])))for r in selected)
 if used>=cfg['maximum_requests']:return 'request_budget_exhausted'
 last=max([cfg['baseline_last_attempt_epoch']]+[r.get('trial_attempt_at_epoch',0)for r in selected])
 if now<last+cfg['minimum_interval_seconds']:return 'trial_spacing'
 return 'allowed'

def admission(root):
 root=Path(root);hosted=os.getenv('GITHUB_ACTIONS')=='true'
 def read(path):
  if not hosted:return json.loads((root/path).read_text())
  p=subprocess.run(['git','show','origin/main:'+path],cwd=root,capture_output=True,check=True)
  return json.loads(p.stdout)
 if hosted:
  subprocess.run(['git','fetch','--quiet','origin','main'],cwd=root,check=True,capture_output=True)
  p=subprocess.run(['git','ls-tree','-r','--name-only','origin/main','--',DIRECTORY],cwd=root,capture_output=True,check=True)
  paths=p.stdout.decode().splitlines()
 else:paths=[str(p.relative_to(root))for p in(root/DIRECTORY).glob('*.json')]
 if len(paths)>500:raise RuntimeError('Trial report listing too large')
 reports=[]
 for path in paths:
  if not path.endswith('.json'):continue
  if not re.fullmatch(DIRECTORY+r'/[A-Za-z0-9_-]+\.json',path):raise RuntimeError('Invalid trial report path')
  reports.append(read(path))
 cfg=read(CONFIG)
 return decision(cfg,reports,time.time()),cfg

if __name__=='__main__':
 status,_=admission(Path(__file__).resolve().parents[1])
 print(json.dumps({'trial_status':status,'provider_requests':0,'post_submissions':0}))
 output=os.getenv('GITHUB_OUTPUT')
 if output:
  with open(output,'a')as f:f.write('allowed='+('1'if status=='allowed'else'0')+'\n')
