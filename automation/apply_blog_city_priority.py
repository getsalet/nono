#!/usr/bin/env python3
"""CAS-reorder current queues atomically; no provider, browser or post APIs."""
import collections,copy,json,os,re,subprocess,tempfile,time
from pathlib import Path
from blog_city_priority import prioritize_queue,fresh,CONFIG,POLICY
ROOT=Path(__file__).resolve().parents[1]
BLOGS=('roya','farsiblog','rozblog','loxblog')
def git(args,raw=None,env=None,check=True):
 p=subprocess.run(['git',*args],cwd=ROOT,input=raw,capture_output=True,env=env)
 if check and p.returncode:raise RuntimeError('Priority queue repository operation failed; no state overwritten')
 return p

def unchanged_records(before,after):
 if len(before['items'])!=len(after['items']):raise RuntimeError('Row count changed')
 canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
 if collections.Counter(map(canonical,before['items']))!=collections.Counter(map(canonical,after['items'])):raise RuntimeError('Article record changed')
 for index,row in enumerate(before['items']):
  if not fresh(row)and after['items'][index]!=row:raise RuntimeError('Frozen article position changed')

def main():
 if os.getenv('GITHUB_ACTIONS')!='true':raise RuntimeError('Hosted repository checkpoint required')
 run=os.getenv('GITHUB_RUN_ID','')
 if not re.fullmatch(r'\d+',run):raise RuntimeError('Verified workflow run required')
 fd,index=tempfile.mkstemp(prefix='afp-city-priority-');os.close(fd);os.unlink(index)
 env=dict(os.environ,GIT_INDEX_FILE=index,GIT_AUTHOR_NAME='github-actions[bot]',GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',GIT_COMMITTER_NAME='github-actions[bot]',GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
 try:
  for attempt in range(5):
   git(['fetch','--quiet','origin','main']);parent=git(['rev-parse','origin/main']).stdout.decode().strip()
   remote_cfg=git(['show',parent+':'+CONFIG]).stdout
   if json.loads(remote_cfg)!=json.loads((ROOT/CONFIG).read_text()):raise RuntimeError('City priority changed; refresh required')
   control=json.loads(git(['show',parent+':data/blog-generated-image-control.json']).stdout)
   if set(control.get('blogs',[]))!=set(BLOGS)or'blogfa'not in control.get('retired_blogs',[]):raise RuntimeError('Active-blog scope changed; refusing migration')
   git(['read-tree',parent],env=env)
   report={'policy':POLICY,'workflow_run_id':run,'source_commit':parent,'provider_requests':0,'post_submissions':0,'record_fields_modified':False,'blogs':{}}
   for blog in BLOGS:
    path=f'data/{blog}/backlink-queue.json';before=json.loads(git(['show',parent+':'+path]).stdout);after=copy.deepcopy(before)
    prioritize_queue(after,ROOT);unchanged_records(before,after)
    preview=[x for x in after['items']if fresh(x)and x.get('family')in control.get('enabled_families',[])]
    report['blogs'][blog]={'rows':len(after['items']),'all_records_preserved':True,'frozen_positions_preserved':True,'future_first':[{'city':x.get('city_fa'),'key':x['key'],'title':x.get('assigned_title')or x.get('site_title')}for x in preview[:12]]}
    raw=json.dumps(after,ensure_ascii=False,indent=2).encode()+b'\n'
    blob=git(['hash-object','-w','--stdin'],raw).stdout.decode().strip();git(['update-index','--add','--cacheinfo','100644,'+blob+','+path],env=env)
   report_path='artifacts/blog-city-priority/latest.json'
   blob=git(['hash-object','-w','--stdin'],json.dumps(report,ensure_ascii=False,indent=2).encode()).stdout.decode().strip()
   git(['update-index','--add','--cacheinfo','100644,'+blob+','+report_path],env=env)
   tree=git(['write-tree'],env=env).stdout.decode().strip()
   commit=git(['commit-tree',tree,'-p',parent],b'Prioritize future city titles; preserve all article fields and frozen records\n',env).stdout.decode().strip()
   if git(['push','--quiet','origin',commit+':refs/heads/main'],check=False).returncode==0:
    print(json.dumps({'commit':commit,'blogs':list(BLOGS),'all_record_fields_preserved':True,'provider_requests':0,'post_submissions':0}))
    return 0
   time.sleep(2) # Re-read/recompute from the NEW remote parent; never replay stale rows.
  raise RuntimeError('Concurrent queue updates prevented safe reordering; no force push')
 finally:
  for path in (index,index+'.lock'):
   try:os.unlink(path)
   except FileNotFoundError:pass
if __name__=='__main__':raise SystemExit(main())
