"""Bounded four-blog health window with guarded workflow recovery, no native POSTs."""
import base64,datetime as dt,json,os,re,time,urllib.request,urllib.error
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urlsplit,urlunsplit,unquote
from content_originality import PublishedBody,text
REPO=os.getenv('GITHUB_REPOSITORY','getsalet/nono');API='https://api.github.com/repos/'+REPO
BLOGS={
 'roya':{'url':'https://afp.royablog.ir/','workflows':['roya-backlink-queue.yml','roya-backlink-publish.yml'],'optin':None},
 'farsiblog':{'url':'https://afp.farsiblog.com/','workflows':['farsiblog-content.yml'],'optin':'FARSIBLOG_AUTOMATION_ENABLED'},
 'rozblog':{'url':'https://afp-pipe.rozblog.com/','workflows':['rozblog-content.yml'],'optin':'ROZBLOG_AUTOMATION_ENABLED'},
 'blogfa':{'url':'https://afp-pipe.blogfa.com/','workflows':['blogfa-content.yml'],'optin':'BLOGFA_AUTOMATION_ENABLED'}}
ACTIVE={'in_progress','queued','waiting','pending','requested'}
def stamp():return dt.datetime.now(dt.timezone.utc)
def iso(d):return d.isoformat()
def instant(s):
 if not s:return None
 d=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
 if d.tzinfo is None:raise ValueError('Ambiguous checkpoint timestamp')
 return d.astimezone(dt.timezone.utc)
def request(url,api=False,payload=None):
 headers={'User-Agent':'Mozilla/5.0 (compatible; AFP-HealthMonitor/1.0)'}
 if api:
  if urlsplit(url).hostname!='api.github.com':raise ValueError('Refuse token on non-GitHub API host')
  headers['Accept']='application/vnd.github+json';headers['Authorization']='Bearer '+os.environ['GH_TOKEN']
 if payload is not None:headers['Content-Type']='application/json'
 req=urllib.request.Request(url,headers=headers,data=json.dumps(payload).encode()if payload is not None else None)
 with urllib.request.urlopen(req,timeout=35)as r:return r.status,r.read().decode('utf-8','replace')
def api(path,payload=None):
 status,body=request(API+path,True,payload);return json.loads(body)if body else {'http_status':status}
def repo_json(path,ref):
 obj=api('/contents/'+path+'?ref='+ref)
 if obj.get('encoding')=='base64':return json.loads(base64.b64decode(obj['content']))
 url=obj.get('download_url')
 if urlsplit(url or '').hostname!='raw.githubusercontent.com':raise RuntimeError('Repository snapshot unavailable')
 return json.loads(request(url)[1])
def recent_budget(blog,rows,now):
 dates=[instant(x.get('at'))for x in rows]
 if any(d is None for d in dates):raise ValueError('Incomplete publication history')
 last=max(dates,default=None);recent=[d for d in dates if d>=now-dt.timedelta(hours=1)]
 return {'last_verified_at':iso(last)if last else None,'publication_age_minutes':(now-last).total_seconds()/60 if last else None,
  'remaining_hourly_budget':None if blog=='roya'else max(0,3-len(recent)),
  'next_eligible_at':iso(min(recent)+dt.timedelta(hours=1))if blog!='roya'and len(recent)>=3 else None}
class Titles(HTMLParser):
 def __init__(self):super().__init__();self.card=0;self.card_title=False;self.heading=False;self.anchor=None;self.parts=[];self.posts=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='article'and 'post-card'in a.get('class','').split():self.card+=1;self.card_title=False
  if t in ('h1','h2')and ('post-title'in a.get('class','').split()or self.card and not self.card_title):self.heading=True
  if t=='a'and self.heading:self.anchor=a.get('href');self.parts=[]
 def handle_data(self,s):
  if self.anchor:self.parts.append(s)
 def handle_endtag(self,t):
  if t=='a'and self.anchor:
   title=' '.join(''.join(self.parts).split())
   if title:self.posts.append({'url':self.anchor,'title':title});self.card_title=True
   self.anchor=None
  if t in ('h1','h2'):self.heading=False
  if t=='article'and self.card:self.card-=1

def public_snapshot(url):
 status,body=request(url);p=Titles();p.feed(body);host=urlsplit(url).hostname
 posts=[x for x in p.posts if urlsplit(x['url']).hostname in (host,None) and '/post/'in x['url']]
 head=re.search(r'<head\b[^>]*>(.*?)</head>',body,re.I|re.S)
 tags=re.findall(r'<meta\b[^>]*name=["\']google-site-verification["\'][^>]*>',head[1]if head else '',re.I)
 return {'http_status':status,'server_post_titles':len(posts),'duplicate_post_urls':len(posts)-len({x['url']for x in posts}),
  'verification_token_present':len(tags)==1 and '-BhLoljNdO2asCo1OjpTRZDWkhzl0RbWJCgrz-lCDqc'in tags[0],
  'latest':posts[0]if posts else None,'parser_unverified':not bool(posts)}
def latest_article(url,host):
 parts=urlsplit(url)
 if parts.hostname!=host or not parts.path.startswith('/post/'):raise ValueError('Wrong latest article destination')
 secure=urlunsplit(('https',parts.netloc,parts.path,parts.query,''));status,body=request(secure)
 parser=PublishedBody();parser.feed(body);fragment=''.join(parser.parts)
 return {'url':secure,'http_status':status,'body_extracted':parser.done,'body_words':len(text(fragment).split()),
  'images':len(re.findall(r'<img\b',fragment,re.I)),'faqs':len(re.findall(r'<details\b',fragment,re.I))}
def recovery_plan(blog,row,now,last_recovery,enabled):
 if not enabled:return None,'scheduled opt-in is off'
 if row.get('unverified') or row.get('public',{}).get('unverified'):return None,'observations incomplete; do not guess'
 runs=row.get('workflows',[])
 if any(x.get('status')in ACTIVE for x in runs):return None,'workflow already running or queued'
 if any(x.get('failed_steps')and any(s.get('job')=='tests' for s in x['failed_steps'])for x in runs):return None,'test failure needs code repair, not blind rerun'
 if row.get('remaining_hourly_budget')==0:return None,'normal hourly budget idle'
 previous=last_recovery.get(blog)
 if previous and (now-instant(previous['at'])).total_seconds()<3600:return None,'recovery cooldown'
 if previous and previous.get('count',0)>=2:return None,'two-hour recovery limit reached'
 if row.get('public',{}).get('http_status')!=200:return None,'public site not independently verified'
 failed=any(x.get('conclusion')=='failure'for x in runs)
 age=row.get('publication_age_minutes')
 if not failed and (age is None or age<60):return None,'publication current or baseline not established'
 # Only dispatch documented pipelines. Their QA, limits, dedup and POST journals remain authoritative.
 ready=row.get('ready_count',0)
 if blog=='roya':
  workflow='roya-backlink-publish.yml'if ready else'roya-backlink-queue.yml'
  inputs={'publish':'1','limit':'3'}if ready else{'count':'1','dry_run':'0','target':''}
 else:workflow=BLOGS[blog]['workflows'][0];inputs={'count':'0'if ready else'1','publish':'1','dry_run':'0','target':''}
 return {'workflow':workflow,'inputs':inputs},'recover failed/stalled pipeline within normal safeguards'

def snapshot(last_recovery,article_cache,allow_recovery):
 now=stamp();ref=api('/commits/main')['sha'];variables={x['name']:x['value']for x in api('/actions/variables?per_page=100').get('variables',[])if x['name'].endswith('_AUTOMATION_ENABLED')}
 out={'at':iso(now),'repository_ref':ref,'blogs':[]}
 for blog,cfg in BLOGS.items():
  row={'blog':blog,'url':cfg['url'],'workflows':[],'recoveries':[]}
  try:
   for name in cfg['workflows']:
    runs=api('/actions/workflows/'+name+'/runs?per_page=8').get('workflow_runs',[])
    run=next((r for r in runs if r.get('event')!='push'),None)
    if not run:raise RuntimeError('No content workflow run')
    w={k:run.get(k)for k in ('id','status','conclusion','event','html_url','created_at')};w['workflow']=name
    if w['conclusion']=='failure':
     jobs=api('/actions/runs/'+str(w['id'])+'/jobs?per_page=100').get('jobs',[])
     w['failed_steps']=[{'job':j['name'],'step':s['name']}for j in jobs for s in j.get('steps',[])if s.get('conclusion')=='failure']
    row['workflows'].append(w)
   q=repo_json('data/'+blog+'/backlink-queue.json',ref);state=repo_json('state/'+blog+'-backlink-progress.json',ref)
   counts=Counter(x.get('status','unknown')for x in q.get('items',[]));row['queue_status']=dict(counts)
   row['ready_count']=sum(x.get('status')in ('completed','ready')and not x.get('published')for x in q.get('items',[]))
   row.update(recent_budget(blog,state.get('published',[]),now))
   row['scheduled_enabled']=not cfg['optin'] or variables.get(cfg['optin'])=='1'
   try:
    row['public']=public_snapshot(cfg['url']);latest=row['public'].get('latest')
    if latest:
     u=latest['url']
     if u not in article_cache:article_cache[u]=latest_article(u,urlsplit(cfg['url']).hostname)
     row['latest_article']=article_cache[u]
   except urllib.error.HTTPError as exc:row['public']={'http_status':exc.code,'unverified':'remote HTTP response; not proof of outage'}
   except Exception as exc:row['public']={'unverified':type(exc).__name__}
   plan,reason=recovery_plan(blog,row,now,last_recovery,row['scheduled_enabled']);row['recovery_reason']=reason
   if plan and allow_recovery:
    result=api('/actions/workflows/'+plan['workflow']+'/dispatches',{'ref':'main','inputs':plan['inputs']})
    previous=last_recovery.get(blog,{});last_recovery[blog]={'at':iso(now),'count':previous.get('count',0)+1}
    row['recoveries'].append({**plan,'at':iso(now),'response_status':result.get('http_status')})
  except Exception as exc:row['unverified']=type(exc).__name__
  out['blogs'].append(row)
 return out

def report(root,samples,start,deadline):
 last=samples[-1];lines=['# AFP four-blog two-hour monitoring','',f'Started UTC: {iso(start)}',f'Planned finish UTC: {iso(deadline)}',f'Last observation UTC: {last["at"]}',f'Samples: {len(samples)}','',
 'Native posts are never submitted by this monitor. Bounded workflow recovery only: no quality bypass, no secret changes, no resubmission outside publisher dedup/journals. Normal hourly idle is not a failure. HTTP/observation blocks are unverified, not declared healthy or down.','']
 for row in last['blogs']:
  lines+=['## '+row['blog'],'',json.dumps(row,ensure_ascii=False,indent=2),'']
 changes=[{'at':s['at'],'blog':r['blog'],'recovery':a}for s in samples for r in s['blogs']for a in r.get('recoveries',[])]
 lines+=['## Guarded recovery history','',json.dumps(changes,ensure_ascii=False,indent=2)]
 (root/'summary.md').write_text('\n'.join(lines)+'\n')
def main():
 minutes=max(1,min(180,int(os.getenv('MONITOR_MINUTES','120'))));interval=max(60,min(300,int(os.getenv('MONITOR_INTERVAL_SECONDS','300'))));allow=os.getenv('MONITOR_RECOVER','0')=='1'
 root=Path('artifacts/four-blog-health-monitor');root.mkdir(parents=True,exist_ok=True);start=stamp();deadline=start+dt.timedelta(minutes=minutes);end=time.monotonic()+minutes*60;samples=[];recoveries={};cache={}
 print('Monitoring started UTC '+iso(start)+'; planned finish UTC '+iso(deadline)+'; guarded recovery '+str(allow),flush=True)
 while True:
  try:row=snapshot(recoveries,cache,allow)
  except Exception as exc:row={'at':iso(stamp()),'blogs':[],'unverified':type(exc).__name__}
  samples.append(row)
  with (root/'samples.jsonl').open('a')as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
  report(root,samples,start,deadline)
  print(json.dumps({'at':row['at'],'unverified':row.get('unverified'),'blogs':[{'blog':r['blog'],'remaining':r.get('remaining_hourly_budget'),'last_verified':r.get('last_verified_at'),'unverified':r.get('unverified')or r.get('public',{}).get('unverified'),'recovery':r.get('recovery_reason'),'dispatches':len(r.get('recoveries',[]))}for r in row['blogs']]},ensure_ascii=False),flush=True)
  left=end-time.monotonic()
  if left<=0:break
  time.sleep(min(interval,left))
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary:Path(summary).write_text((root/'summary.md').read_text())
 print('Monitoring completed UTC '+iso(stamp()),flush=True)
if __name__=='__main__':main()
