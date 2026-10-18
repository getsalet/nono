#!/usr/bin/env python3
"""One real hour of read-only observation: FarsiBlog, RozBlog and LoxBlog only.
No dispatch, publication, image requests, credentials changes or quality bypass.
"""
import argparse,base64,concurrent.futures,datetime as dt,html,json,os,time,urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote,unquote,urljoin,urlsplit
REPO='getsalet/nono'
BLOGS={
 'farsiblog':('https://afp.farsiblog.com/','farsiblog-content.yml'),
 'rozblog':('https://afp-pipe.rozblog.com/','rozblog-content.yml'),
 'loxblog':('https://afp.lxb.ir/','loxblog-content.yml')}
ACTIVE={'queued','pending','waiting','requested','in_progress'}
def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def read(url,api=False):
 if api and urlsplit(url).netloc!='api.github.com':raise ValueError('API host not allowed')
 headers={'User-Agent':'AFP-read-only-source-backlink-watch/1.0'}
 if api:
  headers['Accept']='application/vnd.github+json'
  if os.getenv('GH_TOKEN'):headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
 with urllib.request.urlopen(urllib.request.Request(url,headers=headers,method='GET'),timeout=30)as r:
  data=r.read(4*1024*1024+1)
  if len(data)>4*1024*1024:raise ValueError('Read limit exceeded')
  return r.status,data.decode('utf-8','replace')
def api(path):return json.loads(read('https://api.github.com/repos/'+REPO+path,True)[1])
def repo_json(path,sha):
 # Fixed snapshot: do not mix state/queue versions when a publisher commits.
 obj=api('/contents/'+path+'?ref='+sha)
 if obj.get('encoding')=='base64':return json.loads(base64.b64decode(obj['content']))
 return json.loads(read('https://raw.githubusercontent.com/'+REPO+'/'+sha+'/'+path)[1])
def canonical(url):return unquote(html.unescape(url)).rstrip('/')
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='img'and attrs.get('src'):self.images.append(attrs['src'])
  if tag=='a'and attrs.get('href'):self.links.append(attrs['href'])
def verify_post(blog,item,receipt):
 url=receipt.get('url')or item.get('published_url','');host=urlsplit(BLOGS[blog][0]).hostname
 if urlsplit(url).hostname!=host or urlsplit(url).scheme!='https':return {'url':url,'unverified':'unexpected_permalink'}
 p=urlsplit(url);url=p._replace(path=quote(p.path,safe='/%')).geturl()
 status,body=read(url);tags=Tags();tags.feed(body)
 source=item.get('image_source')or{};image=item.get('image_url');target=item.get('target_url')
 return {'url':url,'http_status':status,'original_source_image_tag_present':bool(image and source and any(canonical(urljoin(url,x))==canonical(image)for x in tags.images)),
  'source_backlink_present':bool(target and any(canonical(urljoin(url,x))==canonical(target)for x in tags.links)),
  'source_image_attached':bool(source and image),'image_policy':source.get('policy'),'visual_review_performed':source.get('visual_review_performed'),
  'editorial_image_decision':item.get('editorial_image_decision'),'any_image_tag_present':bool(tags.images)}
def inspect(blog,sha,baseline=None):
 url,workflow=BLOGS[blog];out={'blog':blog,'at':stamp(),'workflow':workflow}
 try:
  runs=api('/actions/workflows/'+workflow+'/runs?per_page=12')['workflow_runs']
  out['runs']=[{k:r.get(k)for k in ('id','event','status','conclusion','html_url','created_at')}for r in runs]
  out['active_run_ids']=[r['id']for r in runs if r.get('status')in ACTIVE]
  failures=[r for r in runs if r.get('conclusion')=='failure'];out['failure_observations']=[]
  for run in failures[:2]:
   jobs=api('/actions/runs/'+str(run['id'])+'/jobs?per_page=100').get('jobs',[])
   out['failure_observations'].append({'id':run['id'],'url':run['html_url'],'created_at':run['created_at'],'failed_steps':[{'job':j['name'],'step':s['name']}for j in jobs for s in j.get('steps',[])if s.get('conclusion')=='failure']})
  state=repo_json('state/'+blog+'-backlink-progress.json',sha);queue=repo_json('data/'+blog+'/backlink-queue.json',sha)
  receipts=state.get('published',[]);items=queue.get('items',[])
  # A verified publisher receipt is the publication evidence, never green Actions alone.
  valid=[x for x in receipts if x.get('url')and x.get('key')and x.get('at')]
  out['receipt_ids']=[x['url']for x in valid];out['verified_receipt_total']=len(valid)
  out['last_verified_receipt']=max(valid,key=lambda x:x['at'],default=None)
  out['queue_status']=dict(Counter(x.get('status','unknown')for x in items));out['failure_stages']=dict(Counter(x.get('failure_stage','unspecified')for x in items if x.get('status')=='failed'))
  recent=[];now=dt.datetime.now(dt.timezone.utc)
  for row in valid:
   at=dt.datetime.fromisoformat(row['at'].replace('Z','+00:00'))
   if at.tzinfo is None:raise ValueError('Ambiguous receipt timestamp')
   if dt.timedelta(0)<=now-at<=dt.timedelta(hours=1):recent.append(row)
  # Read the actual existing budget function, not a guessed threshold.
  from farsiblog_backlink_queue import remaining_publication_budget
  import tempfile
  with tempfile.TemporaryDirectory()as temp:
   path=Path(temp)/'state.json';path.write_text(json.dumps(state));out['remaining_publication_budget']=remaining_publication_budget(path,now)
  out['receipts_last_60_minutes']=len(recent)
  new=[x for x in valid if baseline is not None and x['url']not in baseline];out['new_verified_receipts']=new
  bykey={x.get('key'):x for x in items};out['new_post_checks']=[]
  # Also verify the latest existing publication at baseline; later only newly observed posts.
  check=new if baseline is not None else ([out['last_verified_receipt']]if out['last_verified_receipt']else[])
  for receipt in check[:12]:
   try:out['new_post_checks'].append(verify_post(blog,bykey.get(receipt['key'],{}),receipt))
   except Exception as exc:out['new_post_checks'].append({'url':receipt['url'],'unverified':type(exc).__name__})
 except Exception as exc:out['unverified']=type(exc).__name__
 try:out['public_home_http_status']=read(url)[0]
 except Exception as exc:out['public_home_unverified']=type(exc).__name__
 return out
def snapshot(baselines):
 sha=api('/commits/main')['sha']
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
  rows=list(pool.map(lambda b:inspect(b,sha,baselines.get(b)),BLOGS))
 return {'at':stamp(),'repository_ref':sha,'blogs':rows}
def write_report(root,samples,start,elapsed,completed):
 last=samples[-1];lines=['# One-hour source-backlink generator watch','',f'Started UTC: {start}',f'Last observation UTC: {last["at"]}',f'Observed elapsed seconds: {elapsed:.1f}',f'One-hour window completed: {completed}',f'Samples: {len(samples)}','',
 'Scope: FarsiBlog, RozBlog and LoxBlog only. Read-only; no native submissions, workflow recovery, image generation/review or production changes.',
 'A successful monitor or generator job does not prove publication. Counts use publisher receipts; HTML checks verify the saved original-image URL and target backlink, not visual quality or downloaded image pixels.',
 'Pre-existing failures are retained with creation timestamps. HTTP/transport blocks remain unverified, not diagnosed as downtime. No new receipts alone does not prove a failure; normal publication budgets remain authoritative.','']
 for row in last['blogs']:
  b=row['blog'];new={r['url']:r for s in samples for v in s['blogs']if v['blog']==b for r in v.get('new_verified_receipts',[])}
  lines+=['## '+b,'','Unique new verified publication receipts observed: '+str(len(new)),'',json.dumps({k:v for k,v in row.items()if k!='receipt_ids'},ensure_ascii=False,indent=2),'']
  checks={c['url']:c for s in samples for v in s['blogs']if v['blog']==b for c in v.get('new_post_checks',[])if c.get('url')in new}
  lines+=['New publication HTML evidence:',json.dumps(list(checks.values()),ensure_ascii=False,indent=2),'']
 (root/'summary.md').write_text('\n'.join(lines)+'\n')
 (root/'status.json').write_text(json.dumps({'started_at':start,'last_observed_at':last['at'],'elapsed_seconds':elapsed,'one_hour_completed':completed,'samples':len(samples)},indent=2))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');parser.add_argument('--output',default='artifacts/source-backlink-three-blog-watch');args=parser.parse_args()
 root=Path(args.output);root.mkdir(parents=True,exist_ok=True);start=stamp();clock=time.monotonic();end=clock+3600;baselines={};samples=[]
 print(json.dumps({'started_at':start,'duration_seconds':3600,'blogs':list(BLOGS),'read_only':True}),flush=True)
 while True:
  row=snapshot(baselines);samples.append(row)
  for b in row['blogs']:
   if b['blog']not in baselines and 'receipt_ids'in b:baselines[b['blog']]=set(b['receipt_ids'])
  with (root/'samples.jsonl').open('a')as out:out.write(json.dumps(row,ensure_ascii=False)+'\n')
  elapsed=time.monotonic()-clock;complete=elapsed>=3600
  write_report(root,samples,start,elapsed,complete)
  print(json.dumps({'at':row['at'],'elapsed_seconds':round(elapsed),'blogs':[{k:v.get(k)for k in ('blog','active_run_ids','verified_receipt_total','remaining_publication_budget','unverified')}for v in row['blogs']]}),flush=True)
  if complete or args.once:break
  # Samples at approximately 0,5,...,60 minutes, not interval+request duration.
  next_at=min(end,clock+len(samples)*300);time.sleep(max(0,next_at-time.monotonic()))
 if os.getenv('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text((root/'summary.md').read_text())
 return 0
if __name__=='__main__':raise SystemExit(main())
