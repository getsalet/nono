#!/usr/bin/env python3
"""Finite 3600-second tape-only observation with no synthetic image probes.
Sequential normal-pipeline activation; no direct native submissions or image approval.
"""
import base64,datetime,json,os,re,subprocess,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
API='https://api.github.com/repos/getsalet/nono'
DURATION=3600;SAMPLE_INTERVAL=300;PROBE_INTERVAL=600;MAX_PROBES=5
PUBLIC_BLOGS={'roya':'https://afp.royablog.ir/','farsiblog':'https://afp.farsiblog.com/','rozblog':'https://afp-pipe.rozblog.com/','blogfa':'https://afp-pipe.blogfa.com/','loxblog':'https://afp.lxb.ir/'}
WORKFLOWS={'roya':'roya-backlink-queue.yml','farsiblog':'farsiblog-content.yml','rozblog':'rozblog-content.yml','blogfa':'blogfa-content.yml','loxblog':'loxblog-content.yml'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def api(path):
 if not path.startswith('/'):raise ValueError('Repository-relative path required')
 headers={'Accept':'application/vnd.github+json','User-Agent':'AFP-finite-monitor/1.0'}
 if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
 with urllib.request.urlopen(urllib.request.Request(API+path,headers=headers),timeout=25)as r:return json.load(r)
def content(path):
 value=api('/contents/'+path+'?ref=main')
 # Contents omits bodies above 1 MB: use the exact returned Git blob SHA.
 if not value.get('content'):
  sha=value.get('sha','')
  if not re.fullmatch(r'[a-f0-9]{40}',sha):raise RuntimeError('Missing verified JSON blob identifier')
  value=api('/git/blobs/'+sha)
 if value.get('encoding')!='base64'or not value.get('content'):raise RuntimeError('JSON blob content unavailable')
 return json.loads(base64.b64decode(value['content']))
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
   published=[x for x in items if x.get('published')]
   record['published_keys']=[str(x.get('key',''))for x in published]
   try:record['generation_status']=content('artifacts/'+blog+'-backlink-queue/generation-status.json')
   except Exception as exc:record['generation_status_read_error_type']=type(exc).__name__
   try:
    if runs:
     jobs=api('/actions/runs/'+str(runs[0]['id'])+'/jobs?per_page=100').get('jobs',[])
     record['latest_jobs']=[{'name':j.get('name'),'status':j.get('status'),'conclusion':j.get('conclusion'),'failed_steps':[s.get('name')for s in j.get('steps',[])if s.get('conclusion')=='failure']}for j in jobs]
   except Exception as exc:record['jobs_read_error_type']=type(exc).__name__
   record['public_home']=public_check(PUBLIC_BLOGS[blog])
  except Exception as exc:record['read_error_type']=type(exc).__name__
 for name,path in [('release_control','data/blog-generated-image-control.json'),('provider_cooldown','data/blog-image-provider-backpressure.json')]:
  try:row[name]=content(path)
  except Exception as exc:row[name+'_read_error_type']=type(exc).__name__
 try:
  row['image_stock_control']=content('data/blog-image-stock-control.json')
  stock_runs=api('/actions/workflows/blog-image-stock.yml/runs?per_page=2')['workflow_runs']
  row['image_stock_runs']=[{k:r.get(k)for k in('id','status','conclusion','created_at','html_url')}for r in stock_runs]
  listing=api('/contents/data/blog-image-stock/requests?ref=main')
  if not isinstance(listing,list)or len(listing)>=1000:raise RuntimeError('Stock directory incomplete')
  requests=[]
  for entry in listing:
   if not re.fullmatch(r'data/blog-image-stock/requests/[a-f0-9]{32}\.json',str(entry.get('path',''))):raise RuntimeError('Invalid stock path')
   value=content(entry['path'])
   requests.append({k:value.get(k)for k in('asset_id','blog','status','attempts','last_error','retry_at','ready_at','consumed_at','url')})
  row['image_stock_requests']=requests
 except Exception as exc:row['image_stock_read_error_type']=type(exc).__name__
 return row

def public_check(url):
 # Availability observation only: a homepage 200 is not a verified new post.
 request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 AFP-read-only-hour-monitor'})
 try:
  with urllib.request.urlopen(request,timeout=12)as response:
   body=response.read(2*1024*1024)
   return {'http_status':response.status,'bytes_read':len(body),'new_post_verified':False}
 except urllib.error.HTTPError as exc:
  code=exc.code;exc.close();return {'http_status':code,'new_post_verified':False}
 except Exception as exc:return {'read_error_type':type(exc).__name__,'new_post_verified':False}

def dispatch_next(current,dispatches):
 """At most one single-item normal workflow per blog, no cooldown bypass."""
 control=current.get('release_control',{})
 if current.get('image_stock_control',{}).get('enabled')is True:return None  # Observe existing schedules; no extra image/prose pressure.
 if control.get('activation_dispatch_mode')!='sequential_by_hour_monitor':return None
 if control.get('enabled')is not True or control.get('pause_image_production')is not False or control.get('enabled_families')!=['tape20'] or 'hose'not in control.get('cancelled_families',[]):return None
 cooldown=current.get('provider_cooldown',{}).get('retry_at_epoch')
 if not isinstance(cooldown,(int,float))or isinstance(cooldown,bool)or cooldown>time.time():return None
 records=current.get('blogs',{})
 if set(records)!=set(WORKFLOWS)or any('read_error_type'in r or not r.get('runs')for r in records.values()):return None
 if any(run.get('status')!='completed'for r in records.values()for run in r['runs']):return None
 # A dispatch may not appear in Actions immediately. Stop rather than overlap.
 if dispatches:
  last=dispatches[-1]
  if last.get('http_status')!=204:return None
  if not any(datetime.datetime.fromisoformat(x['created_at'].replace('Z','+00:00'))>=datetime.datetime.fromisoformat(last['requested_at'].replace('Z','+00:00'))for x in records[last['blog']]['runs']):return None
 blog=next((b for b in WORKFLOWS if b in control.get('blogs',[])and b not in {d['blog']for d in dispatches}),None)
 if blog is None:return None
 from blog_generated_image import rollout_enabled
 if not rollout_enabled(blog,ROOT):raise RuntimeError('Current tape acceptance required before dispatch')
 from activate_blog_publication import plan
 job=next(x for x in plan(control)if x['blog']==blog)
 stamp=utc();headers={'Accept':'application/vnd.github+json','Content-Type':'application/json','Authorization':'Bearer '+os.environ['GH_TOKEN']}
 request=urllib.request.Request(API+'/actions/workflows/'+job['workflow']+'/dispatches',data=json.dumps({'ref':'main','inputs':job['inputs']}).encode(),headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=30)as response:status=response.status
 except urllib.error.HTTPError as exc:status=exc.code;exc.close()
 except Exception:status=None
 return {'blog':blog,'workflow':job['workflow'],'requested_at':stamp,'http_status':status,'count':1,'native_publication_verified':False}

def main():
 import blog_generated_image as g
 from blog_image_backpressure import require_open,ImageProviderBusy
 run=os.getenv('GITHUB_RUN_ID','local')
 if not re.fullmatch(r'[A-Za-z0-9_-]+',run):raise ValueError('Invalid run identifier')
 started=time.monotonic();deadline=started+DURATION
 report={'workflow_run_id':run,'run_url':'https://github.com/getsalet/nono/actions/runs/'+run,'status':'monitoring','started_at':utc(),'requested_duration_seconds':DURATION,'sample_interval_seconds':SAMPLE_INTERVAL,'minimum_probe_interval_seconds':PROBE_INTERVAL,'max_image_requests':0,'post_submissions':0,'release_controls_modified':False,'production_image_approval':False,'publication_caveat':'Green runs and queue flags are not independent public-post verification.','samples':[],'probes':[],'dispatches':[],'image_probe_policy':'disabled; only normal tape20 pipelines generate images','activation_mode':'observe existing schedules when independent stock is enabled; otherwise legacy guarded dispatch'}
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
    control=current.get('release_control',{})
    decision=dispatch_next(current,report['dispatches'])
    if decision:
     report['dispatches'].append(decision);persist()
   time.sleep(min(30,max(0,deadline-time.monotonic())))
  report['samples'].append(snapshot());report.update(status='completed',finished_at=utc(),candidate_received=received)
  first=report['samples'][0];last=report['samples'][-1]
  report['stock_status_counts']={name:sum(x.get('status')==name for x in last.get('image_stock_requests',[]))for name in('requested','processing','ready','consumed','rejected','cancelled','superseded')}
  report['new_published_flags']={blog:len(set(last.get('blogs',{}).get(blog,{}).get('published_keys',[]))-set(first.get('blogs',{}).get(blog,{}).get('published_keys',[])))for blog in WORKFLOWS}
  report['independently_verified_new_posts']=0  # Requires a separate exact-post inspection, not a homepage 200.
 except BaseException as exc:
  report.update(status='interrupted',finished_at=utc(),error_type=type(exc).__name__);raise
 finally:
  persist()
  if os.getenv('GITHUB_STEP_SUMMARY'):
   Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('## Finite one-hour monitor\n\nStatus: '+report['status']+'; observed seconds: '+str(report['elapsed_seconds'])+'; snapshots: '+str(len(report['samples']))+'; probes: '+str(len(report['probes']))+'.\n\nNo direct post submission or image approval. Dispatch acceptance is not verified publication.\n\nReport: '+path+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
