#!/usr/bin/env python3
"""Finite 3600-second observation; at most five cooldown-aware image probes.
No publisher dispatch, post submissions, image approval or release-control edits.
"""
import base64,datetime,json,os,re,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
API='https://api.github.com/repos/getsalet/nono'
DURATION=3600;SAMPLE_INTERVAL=300;PROBE_INTERVAL=600;MAX_PROBES=5
WORKFLOWS={'roya':'roya-backlink-queue.yml','farsiblog':'farsiblog-content.yml','rozblog':'rozblog-content.yml','blogfa':'blogfa-content.yml','loxblog':'loxblog-content.yml'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def api(path):
 if not path.startswith('/'):raise ValueError('Repository-relative path required')
 headers={'Accept':'application/vnd.github+json','User-Agent':'AFP-finite-monitor/1.0'}
 if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
 with urllib.request.urlopen(urllib.request.Request(API+path,headers=headers),timeout=25)as r:return json.load(r)
def content(path):return json.loads(base64.b64decode(api('/contents/'+path+'?ref=main')['content']))
def probe_allowed(elapsed,remaining,attempts,last_probe,cooldown,now,received,control):
 return(remaining>660 and attempts<MAX_PROBES and not received and cooldown<=now and elapsed-last_probe>=PROBE_INTERVAL and control.get('pause_image_production')is False and control.get('enabled_families')==['tape20'])
def snapshot():
 row={'at':utc(),'blogs':{}}
 for blog,workflow in WORKFLOWS.items():
  record={};row['blogs'][blog]=record
  try:
   runs=api('/actions/workflows/'+workflow+'/runs?per_page=2')['workflow_runs']
   record['runs']=[{k:r.get(k)for k in('id','status','conclusion','created_at','updated_at','html_url')}for r in runs]
   items=content('data/'+blog+'/backlink-queue.json').get('items',[]);counts={}
   for item in items:
    status=str(item.get('status','unknown'));counts[status]=counts.get(status,0)+1
   record['queue_status_counts']=counts;record['published_flag_count']=sum(bool(x.get('published'))for x in items)
  except Exception as exc:record['read_error_type']=type(exc).__name__
 for name,path in [('release_control','data/blog-generated-image-control.json'),('provider_cooldown','data/blog-image-provider-backpressure.json')]:
  try:row[name]=content(path)
  except Exception as exc:row[name+'_read_error_type']=type(exc).__name__
 return row

def main():
 import blog_generated_image as g
 from blog_image_backpressure import require_open,ImageProviderBusy
 run=os.getenv('GITHUB_RUN_ID','local')
 if not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise ValueError('Invalid run identifier')
 started=time.monotonic();deadline=started+DURATION
 report={'workflow_run_id':run,'run_url':'https://github.com/getsalet/nono/actions/runs/'+run,'status':'monitoring','started_at':utc(),'requested_duration_seconds':DURATION,'sample_interval_seconds':SAMPLE_INTERVAL,'minimum_probe_interval_seconds':PROBE_INTERVAL,'max_image_requests':MAX_PROBES,'post_submissions':0,'release_controls_modified':False,'production_image_approval':False,'publication_caveat':'Green runs and queue flags are not independent public-post verification.','samples':[],'probes':[]}
 path='artifacts/blog-one-hour-monitor/'+run+'.json'
 def persist():
  report['elapsed_seconds']=round(time.monotonic()-started,1)
  g.checkpoint_asset(path,json.dumps(report,ensure_ascii=False,indent=2).encode(),ROOT)
 next_sample=0;last_probe=-PROBE_INTERVAL;received=False;disabled=False
 try:
  persist()
  while time.monotonic()<deadline:
   elapsed=time.monotonic()-started
   if elapsed>=next_sample:
    current=snapshot();report['samples'].append(current);next_sample=elapsed+SAMPLE_INTERVAL;persist()
    print(json.dumps({'elapsed_minutes':round(elapsed/60,1),'samples':len(report['samples']),'probes':len(report['probes']),'image_received':received}),flush=True)
    control=current.get('release_control',{});cooldown=current.get('provider_cooldown',{}).get('retry_at_epoch')
    if isinstance(cooldown,(int,float))and not isinstance(cooldown,bool)and not disabled and probe_allowed(elapsed,deadline-time.monotonic(),len(report['probes']),last_probe,cooldown,time.time(),received,control):
     last_probe=time.monotonic()-started;probe={'number':len(report['probes'])+1,'started_at':utc(),'production_approval':False};report['probes'].append(probe)
     probe_id=run+'-probe-'+str(probe['number']);env=dict(os.environ,BLOG_IMAGE_PROBE_ID=probe_id)
     g.git(['fetch','--quiet','origin','main'],ROOT)
     files=['automation/blog_reference_scene.py','automation/blog_generated_image.py','automation/blog_image_connection.py','automation/verify_hose_full_references.py']
     if g.git(['diff','--name-only','HEAD','origin/main','--',*files],ROOT).stdout:probe['status']='skipped_code_changed';disabled=True
     else:
      try:
       require_open(ROOT)
       result=subprocess.run(['python','automation/verify_hose_full_references.py'],cwd=ROOT,env=env,capture_output=True,timeout=630)
       probe['process_exit_code']=result.returncode
       # Only safe child report; never persist stdout, stderr or API bodies.
       value=content('artifacts/blog-hose-fullrefs/'+probe_id+'.json');probe['result']=value;received=value.get('image_received')is True
       if any(x.get('http_status')in(401,402,403,429)for x in value.get('provider_attempts',[])):disabled=True
       probe['status']='candidate_saved_needs_direct_visual_review'if received else value.get('status','no_image_received')
      except ImageProviderBusy:probe['status']='skipped_shared_cooldown'
      except subprocess.TimeoutExpired:probe['status']='probe_timeout';disabled=True
      except Exception as exc:probe['status']='diagnostic_error';probe['error_type']=type(exc).__name__;disabled=True
     probe['finished_at']=utc();persist()
   time.sleep(min(30,max(0,deadline-time.monotonic())))
  report['samples'].append(snapshot());report.update(status='completed',finished_at=utc(),candidate_received=received)
 except BaseException as exc:
  report.update(status='interrupted',finished_at=utc(),error_type=type(exc).__name__);raise
 finally:
  persist()
  if os.getenv('GITHUB_STEP_SUMMARY'):
   Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('## Finite one-hour monitor\n\nStatus: '+report['status']+'; observed seconds: '+str(report['elapsed_seconds'])+'; snapshots: '+str(len(report['samples']))+'; probes: '+str(len(report['probes']))+'.\n\nNo production image approval or post submission. Candidates need direct visual inspection.\n\nReport: '+path+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
