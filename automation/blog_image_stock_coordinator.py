"""Bounded read-only scheduler + explicit Actions dispatch, never an image/native API.
Keeps the existing one-image-request worker and all its admission/QA gates intact.
"""
import datetime as dt,json,math,os,subprocess,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG='data/blog-image-coordinator-control.json'
WORKFLOW='blog-image-stock.yml'
ACTIVE={'queued','in_progress','waiting','pending','requested'}
BLOGS={'roya','farsiblog','rozblog','loxblog'}
SLOTS={'AGNES_API_KEY10','AGNES_API_KEY7','AGNES_API_KEY11','AGNES_API_KEY3'}

def stamp(value):
 if isinstance(value,bool)or not isinstance(value,(int,float))or not math.isfinite(value)or not 0<=value<4102444800:raise ValueError('Invalid coordinator timestamp')
 return value

def validate_config(cfg):
 if not isinstance(cfg,dict)or cfg.get('policy')!='bounded-image-stock-coordinator-v1'or type(cfg.get('enabled'))is not bool:raise ValueError('Invalid coordinator control')
 # Bounds are deliberate and cannot be raised by environment variables.
 expected={'session_minutes':55,'poll_seconds':60,'minimum_worker_interval_seconds':300,'max_worker_runs_per_hour':12,'max_dispatches_per_session':12}
 if any(type(cfg.get(k))is not int or cfg[k]!=v for k,v in expected.items()):raise ValueError('Invalid coordinator bounds')
 return cfg

def instant(value):
 if not isinstance(value,str):raise ValueError('Missing run timestamp')
 x=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 if x.tzinfo is None:raise ValueError('Ambiguous run timestamp')
 return x.timestamp()

def plan(cfg,control,key_config,provider,pool,stock,audit,runs,now,last_dispatch=0,dispatches=0):
 validate_config(cfg);now=stamp(now);stamp(last_dispatch)
 def wait(reason,until=None,stop=False):return {'dispatch':False,'reason':reason,'retry_at':until,'stop':stop}
 if not cfg['enabled']:return wait('coordinator_disabled',stop=True)
 if not isinstance(audit,dict)or audit.get('complete_text')is not True or audit.get('complete_image')is not True:raise ValueError('Image capability audit unavailable')
 connection=audit.get('connection',{})
 if connection.get('endpoint')!='https://apihub.agnes-ai.com/v1/images/generations'or connection.get('model')!='agnes-image-2.5-flash':raise ValueError('Image capability audit connection mismatch')
 if not 0<=now-instant(audit.get('finished_at'))<=72*3600:return wait('image_capability_audit_expired',stop=True)
 if not isinstance(control,dict)or type(control.get('pause_image_production'))is not bool or type(control.get('enabled'))is not bool:raise ValueError('Production control unavailable')
 if control['pause_image_production']or not control['enabled']:return wait('production_paused',stop=True)
 blogs=control.get('blogs');retired=control.get('retired_blogs');families=control.get('enabled_families')
 if not isinstance(blogs,list)or not set(blogs)<=BLOGS or not isinstance(retired,list)or 'blogfa'not in retired or families!=['tape20']:raise ValueError('Active production scope changed; explicit review required')
 if not isinstance(key_config,dict)or key_config.get('policy')!='audited-image-key-pool-v1'or key_config.get('enabled')is not True:raise ValueError('Audited routing unavailable')
 slots=key_config.get('slots')
 if not isinstance(slots,list)or not slots or len(slots)!=len(set(slots))or not set(slots)<=SLOTS:raise ValueError('Unaudited image slot; no dispatch')
 if not isinstance(pool,dict)or pool.get('policy')!='audited-image-key-pool-v1'or not isinstance(pool.get('keys'),dict):raise ValueError('Routing state unavailable')
 if pool.get('shared_block'):return wait('account_limit_requires_review',stop=True)
 shared=max(stamp(provider.get('retry_at_epoch')),stamp(pool.get('shared_retry_at_epoch',0)))
 eligible=[]
 for slot in slots:
  row=pool['keys'].get(slot,{})
  if not isinstance(row,dict):raise ValueError('Invalid image slot state')
  if row.get('status')in('authentication_rejected','image_scope_denied','billing_required'):continue
  eligible.append(stamp(row.get('retry_at_epoch',0)))
 if not eligible:return wait('all_audited_routes_disabled',stop=True)
 provider_at=max(shared,min(eligible))
 if provider_at>now:return wait('provider_cooldown',provider_at)
 if not isinstance(runs,list):raise ValueError('Incomplete rolling workflow history; no dispatch')
 if any(r.get('status')in ACTIVE for r in runs):return wait('worker_already_active')
 starts=[]
 for run in runs:
  when=instant(run.get('created_at'))
  if when>now+60:raise ValueError('Future workflow timestamp')
  starts.append(when)
 if len(runs)>=100 and min(starts)>now-3600:raise ValueError('Incomplete rolling workflow history; no dispatch')
 latest_completed=max((r for r in runs if r.get('status')=='completed'and r.get('conclusion')!='cancelled'),key=lambda r:r['created_at'],default={})
 if latest_completed.get('conclusion')in('failure','timed_out','action_required','startup_failure'):return wait('worker_failure_requires_review',stop=True)
 if last_dispatch and not any(t>=last_dispatch-2 for t in starts):
  return wait('worker_dispatch_not_observed',last_dispatch+300,stop=now-last_dispatch>=300)
 recent=[t for t in starts if now-3600<t<=now]
 if len(recent)>=cfg['max_worker_runs_per_hour']:return wait('rolling_worker_run_budget',min(recent)+3600)
 if dispatches>=cfg['max_dispatches_per_session']:return wait('session_dispatch_budget',stop=True)
 last=max(starts+[last_dispatch])
 if last+cfg['minimum_worker_interval_seconds']>now:return wait('minimum_dispatch_spacing',last+cfg['minimum_worker_interval_seconds'])
 pending=[]
 for row in stock:
  if not isinstance(row,dict):raise ValueError('Invalid stock snapshot')
  if row.get('blog')not in blogs or row.get('blog')in retired or row.get('status')not in('requested','processing'):continue
  if row.get('item',{}).get('family')!='tape20':continue
  pending.append(stamp(row.get('retry_at',0)))
 if not pending:return wait('no_pending_production_images')
 if min(pending)>now:return wait('article_retry_cooldown',min(pending))
 return {'dispatch':True,'reason':'due_article_owned_image','retry_at':None,'stop':False,'worker_runs_last_hour':len(recent)}

class Github:
 def __init__(self):
  if os.getenv('GITHUB_REPOSITORY')!='getsalet/nono':raise RuntimeError('Coordinator repository mismatch')
  token=os.getenv('GH_TOKEN')
  if not token:raise RuntimeError('Actions token required')
  self.headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'AFP-bounded-image-coordinator'}
 def request(self,path,payload=None):
  data=None if payload is None else json.dumps(payload).encode();headers=dict(self.headers)
  if data is not None:headers['Content-Type']='application/json'
  req=urllib.request.Request('https://api.github.com/repos/getsalet/nono'+path,headers=headers,data=data)
  try:
   with urllib.request.urlopen(req,timeout=35)as r:
    raw=r.read();return json.loads(raw)if raw else {'http_status':r.status}
  except urllib.error.HTTPError as exc:raise RuntimeError('Coordinator GitHub HTTP '+str(exc.code)+'; private response withheld')from None
 def runs(self):
  value=self.request('/actions/workflows/'+WORKFLOW+'/runs?per_page=100')
  rows=value.get('workflow_runs')
  if not isinstance(rows,list):raise RuntimeError('Workflow history unavailable')
  return rows
 def dispatch(self):return self.request('/actions/workflows/'+WORKFLOW+'/dispatches',{'ref':'main'})

def snapshot(root):
 subprocess.run(['git','fetch','--quiet','--depth=1','origin','main'],cwd=root,check=True,capture_output=True)
 ref=subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=root).decode().strip()
 def read(path):return json.loads(subprocess.check_output(['git','show',ref+':'+path],cwd=root,stderr=subprocess.DEVNULL))
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',ref,'data/blog-image-stock/requests'],cwd=root).decode().splitlines()
 rows=[read(p)for p in paths]
 return {'cfg':read(CONFIG),'control':read('data/blog-generated-image-control.json'),'key_config':read('data/blog-image-key-pool.json'),'provider':read('data/blog-image-provider-backpressure.json'),'pool':read('data/blog-image-key-pool-state.json'),'stock':rows,'audit':read('data/agnes-usable-key-audit/latest.json'),'ref':ref}

def run(root=ROOT,clock=time.time,sleep=time.sleep,client=None,loader=snapshot):
 root=Path(root);initial=loader(root);cfg=validate_config(initial['cfg']);client=client or Github()
 deadline=time.monotonic()+cfg['session_minutes']*60;dispatches=0;last_dispatch=0;events=[];previous=None
 folder=root/'artifacts/blog-image-coordinator';folder.mkdir(parents=True,exist_ok=True)
 while True:
  if time.monotonic()>=deadline:break
  now=clock()
  try:
   snap=loader(root);ref=snap.pop('ref');decision=plan(**snap,runs=client.runs(),now=now,last_dispatch=last_dispatch,dispatches=dispatches)
  except Exception as exc:
   # Read/API uncertainty cannot authorize a dispatch.
   decision={'dispatch':False,'reason':'observation_unavailable','error_type':type(exc).__name__,'stop':False};ref=None
  event={'at':dt.datetime.fromtimestamp(now,dt.timezone.utc).isoformat(),'ref':ref,**decision,'publication_attempted':False,'image_api_requests':0}
  if decision['dispatch']:
   # Reserve local spacing BEFORE dispatch. If acceptance is uncertain, STOP;
   # never blindly repeat an Actions request that may already have succeeded.
   last_dispatch=now;dispatches+=1
   try:
    response=client.dispatch()
    if response.get('http_status')!=204:raise RuntimeError('Dispatch acknowledgement unavailable')
    event['reason']='worker_dispatch_accepted';event['worker_run_not_yet_observed']=True
   except Exception as exc:
    event.update(reason='dispatch_outcome_unverified',error_type=type(exc).__name__,stop=True)
  events.append(event);report={'policy':cfg['policy'],'dispatches':dispatches,'events':events,'target_not_asserted':True,'publication_attempted':False}
  (folder/'latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  if event['reason']!=previous:print(json.dumps(event),flush=True);previous=event['reason']
  if event.get('stop')or time.monotonic()>=deadline:break
  sleep(min(cfg['poll_seconds'],max(0,deadline-time.monotonic())))
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as s:s.write('\n## Bounded image coordinator\n\nWorker dispatch requests: '+str(dispatches)+'. No image API or native publication calls. Dispatch acceptance is not image or publication success.\n')
 return 0
if __name__=='__main__':raise SystemExit(run())
