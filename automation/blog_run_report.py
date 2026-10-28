#!/usr/bin/env python3
"""Observe completed generator runs. Never generate, authenticate to blogs, or retry.
Only fixed-schema, allowlisted public facts are persisted; no log bodies, step
outputs, environment values, provider responses, or credentials enter reports.
"""
import argparse,datetime as dt,json,os,re,subprocess,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO='getsalet/nono'
WORKFLOWS={'roya-backlink-queue.yml':('roya','generation'),'roya-backlink-publish.yml':('roya','publication'),'farsiblog-content.yml':('farsiblog','cycle'),'rozblog-content.yml':('rozblog','cycle'),'loxblog-content.yml':('loxblog','cycle'),'blogsky-auto.yml':('blogsky','cycle'),'parsiblog-content.yml':('parsiblog','cycle'),'niloblog-content.yml':('niloblog','cycle')}
HOSTS={'roya':'afp.royablog.ir','farsiblog':'afp.farsiblog.com','rozblog':'afp-pipe.rozblog.com','loxblog':'afp.lxb.ir','blogsky':'afp-pipe.blogsky.com','parsiblog':'afp.parsiblog.com','niloblog':'afp.niloblog.com'}
STAGES=[('checkpoint',('commit','checkpoint push','checkpoint verified')),('tests',('regression tests','test thousand','test thousand-title')),('dependencies',('install','setup-python','checkout')),('admission',('respect','preflight','budget','controls','validate','credentials','release')),('generation',('generate','generator','bounded guarded cycle')),('publication',('publish','native verification','homepage covers'))]
REASONS={'quality':'quality|preflight rejected|editorial|evidence|claim|foreign.language|text validation','login':'visual_challenge|captcha|authentication|credential|login rejected','receipt':'unconfirmed|uncertain|reconciliation','limit':'hourly|budget|rate.limit|429','image':'image'}
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def timestamp(value):
 try:
  d=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
  return d.timestamp() if d.tzinfo else None
 except (TypeError,ValueError):return None
def read(path):
 try:return json.loads(Path(path).read_text())
 except (OSError,ValueError):return None
def source_paths(blog):
 state='data/niloblog/runtime-state.json' if blog=='niloblog' else 'state/parsiblog-progress.json' if blog=='parsiblog' else f'state/{blog}-backlink-progress.json'
 gen='artifacts/niloblog/run-status.json' if blog=='niloblog' else 'artifacts/parsiblog-backlink-queue/run-report.json' if blog=='parsiblog' else f'artifacts/{blog}-backlink-queue/generation-status.json'
 return state,gen

def validate_run(run):
 path=str(run.get('path','')).split('@')[0]
 if path not in ['.github/workflows/'+x for x in WORKFLOWS] or run.get('head_branch')!='main' or (run.get('head_repository')or{}).get('full_name')!=REPO or run.get('status')!='completed':raise ValueError('Only completed allowlisted main-branch generator runs are accepted')
 if not re.fullmatch(r'\d+',str(run.get('id',''))) or not re.fullmatch(r'\d+',str(run.get('run_attempt',1))):raise ValueError('Invalid run identifier')
 return WORKFLOWS[path.rsplit('/',1)[-1]]

def build(run,jobs,state=None,generation=None,snapshot_sha=None,observed_at=None):
 from urllib.parse import urlsplit
 blog,kind=validate_run(run);rid=str(run['id']);attempt=int(run.get('run_attempt',1));start=run.get('run_started_at') or run.get('created_at');end=run.get('updated_at');lo,hi=timestamp(start),timestamp(end)
 phase='unknown';failed=[]
 for job in jobs:
  for step in job.get('steps',[]):
   if step.get('conclusion')in ('failure','timed_out'):failed.append(step)
 if failed:
  name=str(failed[0].get('name','')).lower()
  phase=next((p for p,terms in STAGES if any(t in name for t in terms)),'unknown')
 elif kind=='generation':phase='generation'
 elif run.get('conclusion')=='success':phase='completed'
 # Copy only structural cause categories, never the raw error (may contain secrets).
 category='unknown';basis='workflow';gen_status=None;retry_at=None;report= generation if isinstance(generation,dict) else {}
 at=timestamp(report.get('completed_at')or report.get('updated_at')or report.get('at'))
 matched=bool(lo is not None and hi is not None and at is not None and lo<=at<=hi+120 and (str(report.get('run_id'))==rid if report.get('run_id') else True) and (not report.get('run_attempt') or str(report['run_attempt'])==str(attempt)))
 if matched:
  gen_status=report.get('status') if report.get('status')in ('produced','partial_success','failed','idle','waiting_image','waiting_provider','published') else None
  errors=report.get('qa_errors') if isinstance(report.get('qa_errors'),list)else[]
  reason=str(report.get('reason',''))+' '+' '.join(str(x)for x in errors)
  if run.get('conclusion')=='failure':category=next((c for c,pattern in REASONS.items()if re.search(pattern,reason,re.I)),'unknown')
  if timestamp(report.get('retry_at')) is not None:retry_at=report['retry_at']
  basis='matched_producer_report'
 rows=[]
 for x in (state or {}).get('published',[]) if isinstance((state or {}).get('published',[]),list)else[]:
  if not isinstance(x,dict):continue
  try:
   u=urlsplit(str(x.get('url','')))
   if u.scheme not in ('http','https')or u.hostname!=HOSTS[blog] or u.username or u.password or u.path=='/' or u.query or u.fragment:continue
  except ValueError:continue
  at=timestamp(x.get('original_published_at')or x.get('published_at')or x.get('at'))
  if at is None or lo is None or hi is None or not(lo<=at<=hi+120)or(x.get('recovered_existing')is True and not x.get('original_published_at')):continue
  rows.append({'url':x['url'],'at':dt.datetime.fromtimestamp(at,dt.timezone.utc).isoformat()})
 receipts=list({r['url']:r for r in rows}.values())[:20]
 # Time overlap is not proof of attribution: another workflow can publish too.
 publication={'status':'receipt_observed_in_run_window' if receipts else 'not_proven','scope':'repository_snapshot_not_run_attribution','receipts':receipts}
 retry='inspect_first' if run.get('conclusion')in ('failure','timed_out','action_required') else 'not_requested'
 if category=='receipt':retry='reconcile_first'
 elif category=='limit' or gen_status in ('waiting_image','waiting_provider'):retry='wait'
 state_path,gen_path=source_paths(blog)
 return {'schema':'blog-run-report-v1','blog':blog,'run_id':rid,'run_attempt':attempt,'workflow_path':str(run['path']).split('@')[0],'run_url':f'https://github.com/{REPO}/actions/runs/{rid}/attempts/{attempt}','event':run.get('event')if run.get('event')in ('schedule','push','workflow_dispatch','workflow_run')else'other','workflow_conclusion':run.get('conclusion')if run.get('conclusion')in ('success','failure','cancelled','skipped','timed_out','action_required','neutral','stale')else'unknown','started_at':start if lo is not None else None,'completed_at':end if hi is not None else None,'observed_at':observed_at or now(),'phase':phase,'reason_code':category,'reason_basis':basis,'generation_status':gen_status,'retry':{'policy':retry,'at':retry_at,'automatic_retry_authorized':False},'publication':publication,'sources':{'snapshot_sha':snapshot_sha if re.fullmatch(r'[a-f0-9]{40}',str(snapshot_sha))else None,'state':state_path,'generation':gen_path if matched else None},'limitations':['No log bodies read; exact failure cause may be unknown.','A successful workflow is not verified publication.','Receipts are observed in a repository snapshot; time overlap does not prove this run created them.']}

def api(path,token):
 req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,headers={'Accept':'application/vnd.github+json','User-Agent':'afp-run-report','Authorization':'Bearer '+token})
 with urllib.request.urlopen(req,timeout=30)as response:return json.load(response)
def collect(run_id,token,root=ROOT):
 if not re.fullmatch(r'\d+',str(run_id)):raise ValueError('Numeric run ID required')
 run=api('actions/runs/'+str(run_id),token);blog,_=validate_run(run);jobs=[]
 for page in range(1,11):
  chunk=api(f'actions/runs/{run_id}/attempts/{int(run.get("run_attempt",1))}/jobs?per_page=100&page={page}',token).get('jobs',[]);jobs.extend(chunk)
  if len(chunk)<100:break
 else:raise RuntimeError('Incomplete job pagination; refusing partial report')
 state_path,gen_path=source_paths(blog)
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
 return build(run,jobs,read(Path(root)/state_path),read(Path(root)/gen_path),sha)

def report_order(report):return (timestamp(report.get('completed_at'))or 0,int(report.get('run_id',0)),int(report.get('run_attempt',0)))

def write_report(report,root=ROOT):
 root=Path(root);blog=report['blog'];folder=root/'artifacts/blog-run-reports'/blog;folder.mkdir(parents=True,exist_ok=True)
 archive=folder/f"{report['run_id']}-{report['run_attempt']}.json";latest=folder/'latest.json'
 content=json.dumps(report,ensure_ascii=False,indent=2)+'\n';archive.write_text(content);paths=[str(archive.relative_to(root))]
 previous=read(latest)
 if not previous or report_order(report)>=report_order(previous):latest.write_text(content);paths.append(str(latest.relative_to(root)))
 return paths

def persist(paths,root=ROOT):
 """Isolated index; no changes to generators, queues, receipts or working index."""
 from checkpoint_blogsky_native import git,tree_entries
 root=Path(root)
 if any(not re.fullmatch(r'artifacts/blog-run-reports/(roya|farsiblog|rozblog|loxblog|blogsky|parsiblog|niloblog)/(latest|[0-9]+-[0-9]+)\.json',p)or(root/p).is_symlink()for p in paths):raise ValueError('Report-only paths required')
 before=tree_entries(root,'HEAD',paths);desired={p:git(['hash-object','-w','--stdin'],root,data=(root/p).read_bytes()).stdout.decode().strip()for p in paths}
 with tempfile.TemporaryDirectory()as tmp:
  env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'),GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
  for _ in range(3):
   git(['fetch','--quiet','origin','main'],root);parent=git(['rev-parse','origin/main'],root).stdout.decode().strip();remote=tree_entries(root,parent,paths)
   for p in list(desired):
    if remote.get(p)not in (before.get(p),desired[p]) and p.endswith('/latest.json'):
     remote_report=json.loads(git(['show',parent+':'+p],root).stdout)
     if report_order(remote_report)>=report_order(read(root/p)):
      desired.pop(p);continue  # A newer report wins; still preserve this run archive.
     before[p]=remote[p]  # Desired report is strictly newer by completed run order.
   paths=list(desired)
   if any(remote.get(p)not in (before.get(p),desired[p])for p in paths):raise RuntimeError('Concurrent run archive edit; refusing overwrite')
   if all(remote.get(p)==desired[p]for p in paths):return
   git(['read-tree',parent],root,env)
   for p,blob in desired.items():git(['update-index','--add','--cacheinfo','100644,'+blob+','+p],root,env)
   tree=git(['write-tree'],root,env).stdout.decode().strip();commit=git(['commit-tree',tree,'-p',parent],root,env,b'Record observed generator run outcome [skip ci]\n').stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],root,check=False).returncode==0:return
 raise RuntimeError('Report push failed; artifact retained')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);parser.add_argument('--persist',action='store_true');args=parser.parse_args()
 report=collect(args.run_id,os.environ['GH_TOKEN']);paths=write_report(report)
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary:
  with open(summary,'a')as f:f.write('## Observed generator outcome\n\n```json\n'+json.dumps(report,ensure_ascii=False,indent=2)+'\n```\n')
 if args.persist:persist(paths)
 print('Observed run '+report['run_id']+'; report-only files written. No generator retry or publication.')
if __name__=='__main__':main()
