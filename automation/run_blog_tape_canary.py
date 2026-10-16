#!/usr/bin/env python3
"""Dispatch at most one named tape draft through the unchanged normal pipeline.
No image API key, native login or direct post submission. Durable pre-dispatch
ledger makes ambiguous dispatches non-repeatable without human reconciliation.
"""
import datetime,json,os,re,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
API='https://api.github.com/repos/getsalet/nono'
WORKFLOW='farsiblog-content.yml'
def validate(request,control,items,record,current=None):
 current=current or datetime.datetime.now(datetime.timezone.utc)
 if not re.fullmatch(r'[a-f0-9]{32}',str(request.get('request_id',''))):raise RuntimeError('Named canary request required')
 if request.get('blog')!='farsiblog'or request.get('family')!='tape20'or request.get('count')!=1 or request.get('publish')is not True:raise RuntimeError('One scoped tape article only')
 if control.get('enabled')is not True or control.get('pause_image_production')is not False or control.get('enabled_families')!=['tape20']or 'hose'not in control.get('cancelled_families',[])or 'farsiblog'not in control.get('blogs',[]):raise RuntimeError('Current tape-only scope required')
 rows=[x for x in items if x.get('key')==request.get('target')]
 if len(rows)!=1:raise RuntimeError('Unique existing target required')
 item=rows[0]
 if item.get('status')!='failed'or item.get('family')!='tape20'or item.get('failure_stage')!='image'or item.get('published'):raise RuntimeError('Only an unpublished image-stage tape failure may be retried')
 if item.get('next_retry_at'):
  due=datetime.datetime.fromisoformat(item['next_retry_at'].replace('Z','+00:00'))
  if due>current:raise RuntimeError('Target retry not yet due')
 if record.get('key')!=item['key']or record.get('family')!='tape20':raise RuntimeError('Saved record identity mismatch')
 from blog_image_draft_recovery import recover
 if recover(record)is None:raise RuntimeError('Saved image-stage draft required')
 return item

def main():
 request=json.loads((ROOT/'data/blog-tape-live-canary-request.json').read_text())
 request_id=request.get('request_id','')
 if not re.fullmatch(r'[a-f0-9]{32}',str(request_id)):raise RuntimeError('Invalid canary identity')
 path='artifacts/blog-tape-live-canary/'+request_id+'.json'
 if (ROOT/path).exists():
  print('Canary already recorded; no repeated dispatch.');return 0
 from blog_generated_image import checkpoint_asset,rollout_enabled
 report={'request_id':request_id,'blog':'farsiblog','target':request.get('target'),'family':'tape20','article_limit':1,'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'controller_run_url':'https://github.com/getsalet/nono/actions/runs/'+os.getenv('GITHUB_RUN_ID','local'),'image_api_requests_by_controller':0,'post_submissions_by_controller':0,'image_received_verified':False,'publication_verified':False,'status':'preflight'}
 def persist():checkpoint_asset(path,json.dumps(report,ensure_ascii=False,indent=2).encode(),ROOT)
 try:
  control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text())
  queue=json.loads((ROOT/'data/farsiblog/backlink-queue.json').read_text())
  slug=re.sub(r'[^A-Za-z0-9._-]+','_',str(request.get('target','')))
  record=json.loads((ROOT/'artifacts/farsiblog-backlink-queue/items'/(slug+'.json')).read_text())
  validate(request,control,queue['items'],record)
  if not rollout_enabled('farsiblog',ROOT):raise RuntimeError('Current tape acceptance required')
  from blog_image_backpressure import require_open
  require_open(ROOT)
  from check_blog_run_budget import decision
  if not decision('farsiblog',ROOT)['proceed']:raise RuntimeError('Rolling publication budget unavailable')
  token=os.getenv('GH_TOKEN','')
  if not token:raise RuntimeError('Actions dispatch credential unavailable')
  headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'}
  with urllib.request.urlopen(urllib.request.Request(API+'/actions/workflows/'+WORKFLOW+'/runs?per_page=10',headers=headers),timeout=25)as response:runs=json.load(response)['workflow_runs']
  if any(x.get('status')!='completed'for x in runs):raise RuntimeError('FarsiBlog workflow already active; no overlapping dispatch')
  report.update(status='dispatching',requested_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
  persist() # Ambiguous HTTP responses must never cause duplicate POST retries.
  payload={'ref':'main','inputs':{'count':'1','publish':'1','dry_run':'0','target':request['target']}}
  req=urllib.request.Request(API+'/actions/workflows/'+WORKFLOW+'/dispatches',data=json.dumps(payload).encode(),headers=headers)
  try:
   with urllib.request.urlopen(req,timeout=30)as response:status=response.status
  except urllib.error.HTTPError as exc:status=exc.code;exc.close()
  except Exception:status=None
  report.update(http_status=status,status='dispatch_accepted_not_generation_or_publication'if status==204 else'dispatch_uncertain_or_rejected_no_retry')
 except Exception as exc:
  from blog_image_backpressure import ImageProviderBusy
  report.update(status='deferred_provider_cooldown'if isinstance(exc,ImageProviderBusy)else'blocked_preflight',error_type=type(exc).__name__)
  if isinstance(exc,ImageProviderBusy):report['retry_at_epoch']=exc.retry_at
 finally:
  persist()
  print(json.dumps(report,ensure_ascii=False),flush=True)
  if os.getenv('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('## One tape live canary\n\nStatus: '+report['status']+'\n\nOnly one named draft requested through the normal generator, image mutex, QA, budget, native and duplicate gates. Dispatch acceptance is not generation or publication verification.\n\nReport: '+path+'\n')
 return 0 if report['status']=='dispatch_accepted_not_generation_or_publication'else 1
if __name__=='__main__':raise SystemExit(main())
