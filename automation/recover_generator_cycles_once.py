"""Explicit one-shot standard dispatch, not a recurring scheduler or publisher.
No provider/site credentials. Never retry a POST with uncertain delivery.
"""
import datetime,json,os,pathlib,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
REQUESTS=[
 ('farsiblog-content.yml',{'count':'1','publish':'1','dry_run':'0'}),
 ('rozblog-content.yml',{'count':'1','publish':'1','dry_run':'0'}),
 ('loxblog-content.yml',{'count':'1','publish':'1','dry_run':'0'}),
 ('blogsky-auto.yml',{}),
 ('parsiblog-content.yml',{'mode':'publish','retry_pre_submit':'false'}),
 ('roya-backlink-queue.yml',{'count':'1','dry_run':'0'})]
def main():
 if os.getenv('GITHUB_REF')!='refs/heads/main' or os.getenv('GITHUB_EVENT_NAME')!='push':
  raise RuntimeError('Only explicit main-branch recovery marker push is permitted')
 report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_id':os.environ['GITHUB_RUN_ID'],'dispatches':[],'publication_verified':False}
 for workflow,inputs in REQUESTS:
  payload=json.dumps({'ref':'main','inputs':inputs}).encode()
  req=urllib.request.Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/actions/workflows/'+workflow+'/dispatches',data=payload,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'},method='POST')
  row={'workflow':workflow,'inputs':inputs,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(req,timeout=45)as response:row.update(http_status=response.status,dispatch_accepted=response.status==204)
  except urllib.error.HTTPError as e:row.update(http_status=e.code,dispatch_accepted=False)
  except Exception as e:row.update(dispatch_accepted=False,delivery_uncertain=True,error_type=type(e).__name__)
  report['dispatches'].append(row)
  print(json.dumps(row),flush=True)
  # Receipt is local until upload; no POST retries, including network ambiguity.
  path=ROOT/'artifacts/generator-recovery-dispatch.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2))
 if not all(x.get('dispatch_accepted')for x in report['dispatches']):raise RuntimeError('At least one dispatch not confirmed; no automatic retry')
if __name__=='__main__':main()
