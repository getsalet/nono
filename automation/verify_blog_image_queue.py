#!/usr/bin/env python3
"""Real GitHub mutex probes only. No image credential or image API call exists here."""
import hashlib,json,os,re,sys,time
from pathlib import Path
from blog_image_queue import Queue,LOCK
ROOT=Path(__file__).resolve().parents[1]
def probe(worker):
 if worker not in ('A','B'):raise ValueError('Known probe identity required')
 queue=Queue(wait=480,poll=5,minimum_interval=0)
 result={'worker':worker,'workflow_run_id':os.environ['GITHUB_RUN_ID'],'image_api_requests':0,'post_submissions':0,'lock_verified':False}
 with queue.slot('queue-probe',hashlib.sha256((result['workflow_run_id']+worker).encode()).hexdigest()[:32]):
  result.update(started_at_epoch=time.time(),owner_sha256=hashlib.sha256(queue.sha.encode()).hexdigest())
  if queue.get_ref(LOCK)!=queue.sha:raise RuntimeError('Probe not sole owner')
  time.sleep(8)
  if queue.get_ref(LOCK)!=queue.sha:raise RuntimeError('Probe ownership changed while held')
  result.update(finished_at_epoch=time.time(),lock_verified=True)
 # Own refs must be gone after normal completion. Do not require global lock to
 # be absent: another legitimate runner may have acquired it in the meantime.
 if queue.get_ref(queue.ticket)is not None:raise RuntimeError('Probe ticket not released')
 path=ROOT/'artifacts/blog-image-queue-check'/('probe-'+worker+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2))
 print(json.dumps(result),flush=True)
def verify():
 run=os.environ['GITHUB_RUN_ID']
 if not re.fullmatch(r'[0-9]+',run):raise RuntimeError('Verified workflow identifier required')
 root=ROOT/'artifacts/blog-image-queue-check';rows=[json.loads((root/('probe-'+worker+'.json')).read_text())for worker in ('A','B')]
 for row in rows:
  if row.get('workflow_run_id')!=run or row.get('lock_verified')is not True or row.get('image_api_requests')!=0 or row.get('post_submissions')!=0:raise RuntimeError('Unverified or mixed probe result')
 rows.sort(key=lambda x:x['started_at_epoch'])
 if rows[0]['finished_at_epoch']>rows[1]['started_at_epoch']:raise RuntimeError('Overlapping critical sections detected')
 report={'passed':True,'workflow_run_id':run,'run_url':'https://github.com/getsalet/nono/actions/runs/'+run,'image_api_requests':0,'post_submissions':0,'cross_runner_non_overlap_verified':True,'provider_capacity_recovery_verified':False,'probes':rows}
 from blog_generated_image import checkpoint_asset
 path='artifacts/blog-image-queue-check/'+run+'.json';checkpoint_asset(path,json.dumps(report,indent=2).encode(),ROOT)
 if os.getenv('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('## Shared image queue verification\n\nTwo GitHub runners acquired the same production mutex without overlapping. No image API calls or post submissions. This does not verify image provider capacity recovery.\n\nReport: '+path+'\n')
 print(json.dumps(report),flush=True)
if __name__=='__main__':
 if len(sys.argv)==3 and sys.argv[1]=='probe':probe(sys.argv[2])
 elif len(sys.argv)==2 and sys.argv[1]=='verify':verify()
 else:raise SystemExit('Expected probe A/B or verify')
