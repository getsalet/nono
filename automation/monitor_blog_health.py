#!/usr/bin/env python3
"""Bounded, read-only AFP blog/Actions monitoring. Never submits a post or edits code."""
import datetime as dt, json, os, re, time, urllib.request, urllib.error
from pathlib import Path
from html import unescape
ROOT=Path('artifacts/blog-health-monitor');ROOT.mkdir(parents=True,exist_ok=True)
REPO=os.getenv('GITHUB_REPOSITORY','getsalet/nono')
WORKFLOWS=['roya-backlink-queue.yml','roya-backlink-publish.yml','farsiblog-content.yml','rozblog-content.yml']
BLOGS={'roya':'https://afp.royablog.ir/','farsi':'https://afp.farsiblog.com/','roz':'https://afp-pipe.rozblog.com/'}
def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def read(url,api=False):
 headers={'User-Agent':'AFP-read-only-health-monitor/1.0'}
 if api:
  headers['Accept']='application/vnd.github+json'
  token=os.getenv('GH_TOKEN','')
  if token:headers['Authorization']='Bearer '+token
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=35)as response:return response.status,response.read().decode('utf-8','replace')
def snapshot():
 row={'at':stamp(),'workflows':[],'blogs':[]}
 for name in WORKFLOWS:
  try:
   _,body=read(f'https://api.github.com/repos/{REPO}/actions/workflows/{name}/runs?per_page=1',True)
   runs=json.loads(body).get('workflow_runs',[])
   if not runs:raise RuntimeError('No workflow run returned')
   run=runs[0];item={k:run.get(k)for k in ('id','name','status','conclusion','html_url','created_at','updated_at')}
   if run.get('conclusion')=='failure':
    _,body=read(run['jobs_url'],True)
    item['failed_steps']=[{'job':j['name'],'step':s['name']}for j in json.loads(body).get('jobs',[])for s in j.get('steps',[])if s.get('conclusion')=='failure']
   row['workflows'].append(item)
  except Exception as exc:row['workflows'].append({'name':name,'unverified':type(exc).__name__})
 for name,url in BLOGS.items():
  try:
   status,body=read(url)
   # Server-rendered post-title links, not arbitrary sidebar/backlinks.
   titles=re.findall(r'<h[12][^>]*class=["\'][^"\']*post-title[^"\']*["\'][^>]*>\s*<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',body,re.S|re.I)
   posts=[{'url':unescape(u),'title':unescape(re.sub('<[^>]+>',' ',t)).strip()}for u,t in titles]
   row['blogs'].append({'name':name,'url':url,'http_status':status,'visible_posts':len(posts),'unique_post_urls':len({x['url']for x in posts}),'latest':posts[0]if posts else None,'cards_marker':('afp-roya-list-cards'in body if name=='roya'else'afp-farsi-card-layout'in body if name=='farsi'else'post-card'in body)})
  except urllib.error.HTTPError as exc:row['blogs'].append({'name':name,'url':url,'http_status':exc.code,'unverified':'Remote HTTP response; does not by itself prove the site is down'})
  except Exception as exc:row['blogs'].append({'name':name,'url':url,'unverified':type(exc).__name__})
 return row

def report(samples,start,deadline):
 last=samples[-1]if samples else {};lines=['# AFP three-blog monitoring','',f'- Started (UTC): {start.isoformat()}',f'- Planned finish (UTC): {deadline.isoformat()}',f'- Last sample (UTC): {last.get("at","none")}',f'- Samples: {len(samples)}','- Read-only: no publication, code edits, login secrets or schedule changes.','- HTTP blocks are reported as unverified, not silently treated as healthy.','- A successful job is not proof that a new post was published.','', '## Latest workflow observations','']
 for run in last.get('workflows',[]):lines.append(f'- {run.get("name")}: {run.get("status", "unverified")} / {run.get("conclusion")}; {run.get("html_url", "")} '+json.dumps(run.get('failed_steps',[]),ensure_ascii=False))
 lines+=['','## Latest public blog observations','']
 for blog in last.get('blogs',[]):lines.append('- '+json.dumps(blog,ensure_ascii=False))
 lines+=['','## Failure observations during this window','']
 observed={r['id']:r for sample in samples for r in sample['workflows']if r.get('id')and r.get('conclusion')=='failure'}
 for run in observed.values():lines.append(f'- {run["html_url"]} (created {run.get("created_at")}; may predate monitoring)')
 (ROOT/'summary.md').write_text('\n'.join(lines)+'\n')

def main():
 minutes=max(1,min(180,int(os.getenv('MONITOR_MINUTES','180'))));interval=max(60,min(300,int(os.getenv('MONITOR_INTERVAL_SECONDS','300'))))
 start=dt.datetime.now(dt.timezone.utc);deadline=start+dt.timedelta(minutes=minutes);end=time.monotonic()+minutes*60;samples=[]
 print('Read-only monitoring started:',start.isoformat(),'planned finish:',deadline.isoformat(),flush=True)
 while True:
  row=snapshot();samples.append(row)
  with (ROOT/'samples.jsonl').open('a')as out:out.write(json.dumps(row,ensure_ascii=False)+'\n')
  report(samples,start,deadline)
  print(json.dumps(row,ensure_ascii=False),flush=True)
  left=end-time.monotonic()
  if left<=0:break
  time.sleep(min(interval,left))
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary:Path(summary).write_text((ROOT/'summary.md').read_text())
 print('Read-only monitoring completed:',stamp(),flush=True)
if __name__=='__main__':main()
