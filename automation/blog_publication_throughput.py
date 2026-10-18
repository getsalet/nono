"""Read-only rolling target check from native publisher checkpoints, never Actions status.
No publication, dispatch, credentials or website requests. The publisher remains
responsible for native/public verification; this report does not repeat it.
"""
import datetime as dt,json,os
from pathlib import Path
from urllib.parse import urlsplit
BLOGS={'roya':'afp.royablog.ir','farsiblog':'afp.farsiblog.com','rozblog':'afp-pipe.rozblog.com','loxblog':'afp.lxb.ir'}
WINDOW_MINUTES=30
MINIMUM_POSTS=3

def instant(value):
 if not isinstance(value,str):raise ValueError('Missing publication timestamp')
 stamp=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 if stamp.tzinfo is None:raise ValueError('Ambiguous publication timestamp')
 return stamp.astimezone(dt.timezone.utc)

def evaluate(states,now):
 if now.tzinfo is None:raise ValueError('Timezone-aware current time required')
 now=now.astimezone(dt.timezone.utc);lower=now-dt.timedelta(minutes=WINDOW_MINUTES)
 publications=[];issues=[];by_blog={b:0 for b in BLOGS}
 for blog,host in BLOGS.items():
  state=states.get(blog)
  if not isinstance(state,dict)or not isinstance(state.get('published'),list):
   issues.append({'blog':blog,'reason':'publisher_checkpoint_unavailable'});continue
  parsed=[]
  for row in state['published']:
   try:
    if not isinstance(row,dict):raise ValueError()
    at=instant(row.get('at'))
    if at>now:raise ValueError('Future timestamp')
    if not isinstance(row.get('key'),str)or not row['key']or type(row.get('pid'))is not int or row['pid']<=0:raise ValueError()
    parts=urlsplit(row.get('url',''))
    if parts.scheme!='https'or parts.hostname!=host or parts.path in ('','/'):raise ValueError()
    parsed.append((at,row))
   except (TypeError,ValueError,AttributeError):issues.append({'blog':blog,'reason':'invalid_publisher_checkpoint'})
  # Earliest native checkpoint wins. A duplicate entry or later editorial
  # correction of an old post must never inflate this window's publication count.
  keys=set();ids=set();urls=set()
  for at,row in sorted(parsed,key=lambda pair:pair[0]):
   if row['key']in keys or row['pid']in ids or row['url']in urls:continue
   keys.add(row['key']);ids.add(row['pid']);urls.add(row['url'])
   if lower<at<=now:
    publications.append({'blog':blog,'key':row['key'],'pid':row['pid'],'url':row['url'],'at':at.isoformat()});by_blog[blog]+=1
 count=len(publications)
 return {'policy':'native-publication-target-3-per-30m-v1','observed_at':now.isoformat(),'window_start_exclusive':lower.isoformat(),'window_minutes':WINDOW_MINUTES,'minimum_posts':MINIMUM_POSTS,'count':count,'by_blog':by_blog,'shortfall':max(0,MINIMUM_POSTS-count),'status':'unverified'if issues else('target_met'if count>=MINIMUM_POSTS else'target_shortfall'),'evidence':'persisted native publisher verification checkpoints, not freshly reverified public pages','publications':publications,'issues':issues,'publication_attempted':False}

def main(root=None):
 from blog_image_stock import read,refresh
 root=Path(root or Path(__file__).resolve().parents[1]);now=dt.datetime.now(dt.timezone.utc)
 try:
  refresh(root);states={b:read(root,'state/'+b+'-backlink-progress.json')for b in BLOGS};result=evaluate(states,now)
 except Exception as exc:
  result={'status':'unverified','observed_at':now.isoformat(),'reason':type(exc).__name__,'publication_attempted':False}
 out=root/'artifacts/blog-throughput';out.mkdir(parents=True,exist_ok=True)
 (out/'latest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 message=('Verified publisher checkpoints in rolling 30 minutes: '+str(result['count'])+' / '+str(MINIMUM_POSTS)+'; '+result['status'])if 'count'in result else'Publication throughput observation unavailable; not a success finding'
 print(message)
 if result['status']!='target_met':print('::warning::'+message)
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a')as stream:stream.write('\n## Actual publication target\n\n'+message+'\n\nNo native post submitted. A successful worker run is not proof that this target was met.\n')
 # This observation must not prevent a ready-image handoff during a shortfall.
 return 0
if __name__=='__main__':raise SystemExit(main())
