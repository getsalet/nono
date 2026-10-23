"""Finite read-only seven-generator audit. No credentials except repository token.
Only report checkpoints are written; no workflow dispatch, login or provider call.
"""
import base64,collections,concurrent.futures,datetime,json,os,pathlib,re,subprocess,time,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
BLOGS={
 'roya':('https://afp.royablog.ir/',['roya-backlink-queue.yml','roya-backlink-publish.yml']),
 'farsiblog':('https://afp.farsiblog.com/',['farsiblog-content.yml']),
 'rozblog':('https://afp-pipe.rozblog.com/',['rozblog-content.yml']),
 'loxblog':('https://afp.lxb.ir/',['loxblog-content.yml']),
 'blogsky':('https://afp-pipe.blogsky.com/',['blogsky-auto.yml']),
 'parsiblog':('http://afp.parsiblog.com/',['parsiblog-content.yml']),
 'niloblog':('https://afp.niloblog.com/',['niloblog-content.yml'])}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def api(path):
 req=urllib.request.Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+path,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'AFP-readonly-generator-audit'})
 with urllib.request.urlopen(req,timeout=35)as r:return json.load(r)
def file_json(path,ref):
 value=api('/contents/'+path+'?ref='+ref)
 if not value.get('content'):value=api('/git/blobs/'+value['sha'])
 return json.loads(base64.b64decode(value['content']))
def state_path(blog):
 return 'data/niloblog/runtime-state.json'if blog=='niloblog'else 'state/parsiblog-progress.json'if blog=='parsiblog'else 'state/'+blog+'-backlink-progress.json'
def inspect_blog(blog,ref):
 url,workflows=BLOGS[blog];out={'workflows':{}}
 for workflow in workflows:
  try:
   definition=api('/actions/workflows/'+workflow);runs=api('/actions/workflows/'+workflow+'/runs?per_page=5').get('workflow_runs',[])
   row={'state':definition.get('state'),'runs':[{k:r.get(k)for k in ['id','status','conclusion','event','created_at','updated_at','head_sha','html_url']}for r in runs]}
   if runs:
    jobs=api('/actions/runs/'+str(runs[0]['id'])+'/jobs?per_page=100').get('jobs',[])
    row['latest_jobs']=[{'name':j.get('name'),'conclusion':j.get('conclusion'),'status':j.get('status'),'started_at':j.get('started_at'),'completed_at':j.get('completed_at'),'steps':[{'name':s.get('name'),'conclusion':s.get('conclusion'),'started_at':s.get('started_at'),'completed_at':s.get('completed_at')}for s in j.get('steps',[])]}for j in jobs]
   out['workflows'][workflow]=row
  except Exception as e:out['workflows'][workflow]={'read_error':type(e).__name__}
 try:
  d=file_json(state_path(blog),ref);published=d.get('published',[]);published=list(published.values())if isinstance(published,dict)else published
  out['state']={'published_count':len(published),'published_keys':[x.get('key',x.get('id',x.get('url')))for x in published],'latest_publications':published[-3:],'updated_at':d.get('updated_at'),'intent_pending':bool(d.get('intent')),'in_progress':bool(d.get('in_progress'))}
 except Exception as e:out['state']={'read_error':type(e).__name__}
 if blog in ('roya','farsiblog','rozblog','loxblog','blogsky'):
  try:
   rows=file_json('data/'+blog+'/backlink-queue.json',ref)['items'];out['queue']={'items':len(rows),'statuses':dict(collections.Counter(x.get('status','unknown')for x in rows)),'ready_unpublished':sum(x.get('status')in('completed','ready')and not x.get('published')for x in rows),'failure_reasons':dict(collections.Counter(str(x.get('last_error','unknown'))[:250]for x in rows if x.get('status')=='failed'))}
  except Exception as e:out['queue']={'read_error':type(e).__name__}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'AFP-readonly-generator-audit'})
  with urllib.request.urlopen(req,timeout=35)as r:out['public_home']={'status':r.status,'final_url':r.url,'bytes':len(r.read())}
 except Exception as e:out['public_home']={'read_error':type(e).__name__}
 return blog,out

def persist(report):
 run=os.environ['GITHUB_RUN_ID'];path=pathlib.Path('artifacts/generator-hour-audit')/(run+'.json');dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,ensure_ascii=False,indent=2))
 subprocess.run(['git','config','user.name','github-actions[bot]'],check=True);subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],check=True)
 subprocess.run(['git','add','-f',str(path)],check=True)
 if subprocess.run(['git','diff','--cached','--quiet']).returncode==0:return
 subprocess.run(['git','commit','-m','Checkpoint read-only generator audit [skip ci]'],check=True,stdout=subprocess.DEVNULL)
 for attempt in range(3):
  subprocess.run(['git','pull','--rebase','origin','main'],check=True,stdout=subprocess.DEVNULL)
  if subprocess.run(['git','push','origin','HEAD:main'],stdout=subprocess.DEVNULL).returncode==0:return
  time.sleep(3*(attempt+1))
 raise RuntimeError('Report checkpoint push failed')
def main():
 start=time.monotonic();report={'started_at':utc(),'requested_seconds':3600,'interval_seconds':300,'status':'monitoring','scope':list(BLOGS),'retired_blogfa_excluded':True,'read_only':True,'provider_requests':0,'native_submissions':0,'workflow_dispatches':0,'samples':[]}
 for index in range(13):
  wait=start+index*300-time.monotonic()
  if wait>0:time.sleep(wait)
  sample={'at':utc(),'elapsed_seconds':round(time.monotonic()-start,1),'blogs':{}}
  try:
   ref=api('/commits/main')['sha'];sample['repository_ref']=ref
   with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
    for blog,row in pool.map(lambda b:inspect_blog(b,ref),BLOGS):sample['blogs'][blog]=row
  except Exception as e:sample['read_error']=type(e).__name__
  report['samples'].append(sample);report['elapsed_seconds']=round(time.monotonic()-start,1)
  if index==12:report.update(status='completed',finished_at=utc())
  persist(report);print(json.dumps({'sample':index,'elapsed_seconds':report['elapsed_seconds'],'status':report['status']}),flush=True)
 if os.getenv('GITHUB_STEP_SUMMARY'):pathlib.Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('One-hour read-only audit completed. No publication, provider request or production-control change. Evidence: artifacts/generator-hour-audit/'+os.environ['GITHUB_RUN_ID']+'.json')
if __name__=='__main__':main()
