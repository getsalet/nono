"""Read only failed-job log diagnostics; no generation or dispatch."""
import os,json,re,urllib.request,urllib.error,urllib.parse,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUNS=[39993329355,39993835755]
class LogRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  host=urllib.parse.urlsplit(newurl).hostname or ''
  if not (host.endswith('.blob.core.windows.net')or host.endswith('.githubusercontent.com')or host.endswith('.github.com')):raise RuntimeError('Refuse untrusted log redirect')
  nxt=super().redirect_request(req,fp,code,msg,headers,newurl)
  if nxt:nxt.remove_header('Authorization')
  return nxt
def api(path,raw=False):
 req=urllib.request.Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+path,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
 with urllib.request.build_opener(LogRedirect()).open(req,timeout=60)as r:return r.read().decode('utf-8','replace')if raw else json.load(r)
def clean(line):
 line=line.replace(os.environ['GH_TOKEN'],'[redacted]')
 return re.sub(r'(?i)(Bearer\s+\S+|sk-[A-Za-z0-9_-]{12,})','[redacted]',line)[:700]
def main():
 out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'read_only':True,'runs':[]}
 for run in RUNS:
  row={'id':run,'failed_jobs':[],'active_jobs':[]}
  try:
   for j in api('/actions/runs/'+str(run)+'/jobs?per_page=100')['jobs']:
    if j['status']!='completed':row['active_jobs'].append({'name':j['name'],'status':j['status'],'started_at':j['started_at'],'active_steps':[{'name':x['name'],'started_at':x.get('started_at')}for x in j.get('steps',[])if x.get('status')=='in_progress']})
    if j['conclusion']!='failure':continue
    text=api('/actions/jobs/'+str(j['id'])+'/logs',True);lines=text.splitlines();selected=[]
    for i,line in enumerate(lines):
     if re.search(r'FAIL: |ERROR: |AssertionError:|RuntimeError:|PipelineStop:|::error::|##\[error\]|fatal:|Unexpected tracked changes|CONFLICT |cannot rebase|error: cannot|error: could not',line):
      selected.extend(clean(x)for x in lines[max(0,i-5):min(len(lines),i+7)]if not re.search(r'(?:AGNES_API_KEY|PASSWORD|USERNAME|GH_TOKEN|ACCESS_TOKEN):',x))
    row['failed_jobs'].append({'name':j['name'],'failed_steps':[s['name']for s in j.get('steps',[])if s.get('conclusion')=='failure'],'diagnostics':list(dict.fromkeys(selected))[:110]})
  except urllib.error.HTTPError as e:
   row['read_error']='HTTPError';row['http_status']=e.code
   try:row['api_message']=json.loads(e.read()).get('message','')[:250]
   except Exception:pass
  except Exception as e:row['read_error']=type(e).__name__
  out['runs'].append(row)
 p=ROOT/'artifacts/generator-recovery-diagnostics.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
