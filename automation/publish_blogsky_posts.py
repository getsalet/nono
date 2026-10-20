#!/usr/bin/env python3
"""Explicit one-post native publisher. Generation/export and publication are separate.
Default is read-only diagnosis. Explicit automatic control enables one approved post.
An uncertain submission journal blocks all retries.
"""
import datetime,hashlib,json,os,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY=re.compile(r'city-[0-9a-f]{16}')
def read(path,default=None):return json.loads(path.read_text()) if path.exists() else default
def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def gate(root=ROOT):
 from check_blog_pipeline_control import decision
 c=read(root/'data/blogsky/native-publication-control.json',{})
 from blogsky_auto_control import MANUAL,AUTOMATIC
 if c not in (MANUAL,AUTOMATIC):raise RuntimeError('Native publication is not explicitly enabled for single-post operation')
 if not decision('blogsky',root)['proceed']:raise RuntimeError('Global Blogsky stop gate is active')
def pending(root=ROOT):
 for p in (root/'artifacts/blogsky-backlink-queue/native-publications').glob('*.json'):
  if read(p,{}).get('phase')!='verified':raise RuntimeError('Unconfirmed native submission exists; reconcile before any further publication')
def prepare(key,root=ROOT):
 from export_blogsky_posts import export
 from city_backlink_policy import qa,links_for
 from blog_generated_image import family_enabled
 from farsiblog_backlink_queue import remaining_publication_budget
 if not KEY.fullmatch(key):raise RuntimeError('Exact city key required')
 q=read(root/'data/blogsky/backlink-queue.json',{'items':[]});rows=[x for x in q['items'] if x['key']==key]
 if len(rows)!=1:raise RuntimeError('Unique queue target required')
 item=rows[0]
 if item.get('published'):return None
 pending(root)
 if remaining_publication_budget(root/'state/blogsky-backlink-progress.json')<1:raise RuntimeError('Hourly publication budget exhausted')
 from blogsky_auto_control import configuration,AUTOMATIC,hour_open
 if configuration(root)==AUTOMATIC and not hour_open(root):raise RuntimeError('Automatic one-post hourly budget exhausted')
 if not family_enabled(item,root):raise RuntimeError('Product family is held')
 manifest=export(root);entries=[x for x in manifest['items'] if x['key']==key]
 if len(entries)!=1:raise RuntimeError('Target has no currently approved export')
 entry=entries[0];record=read(root/f'artifacts/blogsky-backlink-queue/items/{key}.json',{});post=record['post'];item={**record,**item}
 errors,_=qa(item,post,links_for(item),'blogsky',root)
 if errors:raise RuntimeError('Raw article failed current QA')
 body=(root/entry['body_file']).read_text()
 if hashlib.sha256(body.encode()).hexdigest()!=entry['body_sha256']:raise RuntimeError('Export digest mismatch')
 return q,item,post,entry,body

def checkpoint(root,q,item,post,result,journal):
 from export_blogsky_posts import export
 key=item['key'];stamp=now();item.update(status='published',published=True,published_url=result['url'],published_at=stamp,native_publication_verified=True,title=post['title'],slug=post['slug'])
 record=read(root/f'artifacts/blogsky-backlink-queue/items/{key}.json');record.update(item);record['post']=post
 save(root/f'artifacts/blogsky-backlink-queue/items/{key}.json',record)
 q['items']=[{k:v for k,v in item.items() if k not in ('post','blog','qa')} if x['key']==key else x for x in q['items']];save(root/'data/blogsky/backlink-queue.json',q)
 state=read(root/'state/blogsky-backlink-progress.json',{});state.setdefault('failed',{}).pop(key,None);state['updated_at']=stamp;state['completed_keys']=list(dict.fromkeys(state.get('completed_keys',[])+[key]));state.setdefault('published',[]).append({'key':key,'url':result['url'],'at':stamp});save(root/'state/blogsky-backlink-progress.json',state)
 digest=hashlib.sha256(result['url'].encode()).hexdigest();save(root/f'artifacts/content-originality/blogsky/{digest}.json',{'key':key,'url':result['url'],'source':'actual public native DOM readback','html':result['html']})
 journal.update(phase='verified',publicUrl=result['url'],verifiedAt=stamp,native_publication_verified=True,publicArticleSha256=hashlib.sha256(result['html'].encode()).hexdigest(),verification={k:v for k,v in result.items() if k!='html'})
 save(root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json',journal)
 export(root)
 save(root/'artifacts/blogsky-backlink-queue/publish-queue.json',{'generated_at':stamp,'blog':'https://afp-pipe.blogsky.com','count':0,'items':[]})

def durable_automatic_intent(root,receipt,journal):
 """Push only the write-ahead intent BEFORE any automated irreversible click.
 A runner loss or failed public verification therefore blocks subsequent runs.
 No credential, browser storage, cookie or raw form response is checkpointed.
 """
 if os.getenv('GITHUB_ACTIONS')!='true':raise RuntimeError('Automatic publication requires a durable GitHub runner checkpoint')
 save(receipt,journal)
 relative=str(receipt.relative_to(root))
 commands=[['config','user.name','github-actions[bot]'],['config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],['add','--',relative],['commit','-m','Checkpoint Blogsky automatic submit intent [skip ci]','--',relative],['push','origin','HEAD:main']]
 for args in commands:
  result=subprocess.run(['git',*args],cwd=root,capture_output=True,timeout=90)
  if result.returncode:raise RuntimeError('Durable automatic intent checkpoint failed; no native submit allowed')

def run(page,context,root=ROOT):
 import blogsky_native as native
 from city_backlink_policy import links_for,qa
 from content_originality import PublishedBody
 gate(root);mode=os.getenv('BLOGSKY_NATIVE_MODE','diagnose')
 if mode not in ('diagnose','publish-one','auto-one'):raise RuntimeError('Unsupported native operation')
 ready=None
 if mode=='auto-one':
  from blogsky_auto_control import select_target
  key=select_target(root)
  if key is None:print('No approved automatic target or hourly idle; no login or submission.');return 0
  ready=prepare(key,root)
 if mode=='publish-one':
  ready=prepare(os.getenv('BLOGSKY_TARGET',''),root)
  if ready is None:print('Already verified published; no native submission.');return 0
 if mode=='auto-one' and ready is None:print('Already published; automatic submission skipped.');return 0
 native.login(page)
 if mode=='diagnose':
  page.goto(native.ARCHIVE,wait_until='domcontentloaded',timeout=60000)
  if page.url!=native.ARCHIVE:raise RuntimeError('Native archive unavailable')
  print('Native Blogsky login, expected blog, editor and archive verified. No publication.');return 0
 q,item,post,entry,body=ready;key=item['key']
 # Inspect native archive before any submit. Existing matching title/slug requires
 # explicit reconciliation, never a speculative retry or duplicate publication.
 archive=context.new_page()
 try:
  archive.goto(native.ARCHIVE,wait_until='domcontentloaded',timeout=60000)
  if archive.url!=native.ARCHIVE:raise RuntimeError('Native archive not available')
  matches=archive.locator('a').evaluate_all('(aa,x)=>aa.some(a=>a.textContent.trim()===x.title || a.href.includes("/"+x.slug))',post)
  if matches:raise RuntimeError('Matching native post exists; reconcile instead of submitting')
 finally:archive.close()
 serialized=native.fill(page,post,body)
 parser=PublishedBody('afp-article-body');parser.feed(serialized)
 if not parser.done:raise RuntimeError('Native serialization lost article boundary')
 serialized_post={**post,'html':''.join(parser.parts)};errors,_=qa(item,serialized_post,links_for(item),'blogsky',root)
 if errors:raise RuntimeError('Native editor serialization failed current QA')
 # Recheck controls immediately before the irreversible click, then durable WAL.
 gate(root);pending(root)
 receipt=root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json'
 journal={'key':key,'title':post['title'],'phase':'submitting','submittedAt':now(),'bodySha256':hashlib.sha256(serialized.encode()).hexdigest(),'schedule':mode=='auto-one'};save(receipt,journal)
 if mode=='auto-one':
  durable_automatic_intent(root,receipt,journal)
  gate(root)
  from blogsky_auto_control import configuration,AUTOMATIC,hour_open
  if configuration(root)!=AUTOMATIC or not hour_open(root):raise RuntimeError('Automatic admission changed before submit; reconcile saved intent')
 page.locator('#publish').click();page.wait_for_timeout(2000)
 observed=page.get_by_role('link',name='مشاهده یادداشت',exact=True).get_attribute('href',timeout=30000)
 if not native.public_url(observed):raise RuntimeError('Submission not confirmed; reconcile journal, do not retry')
 journal.update(phase='submitted_unverified',publicUrl=observed);save(receipt,journal)
 public=context.new_page()
 try:
  public.goto(observed,wait_until='domcontentloaded',timeout=60000);result=native.public_readback(public);native.verify(result,post,links_for(item),item.get('image_url'))
 finally:public.close()
 checkpoint(root,q,item,post,result,journal);print('One native Blogsky publication publicly verified: '+result['url']);return 0

def main():
 gate(ROOT)  # Before importing/installing any browser or reading credentials.
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  try:
   context=browser.new_context();return run(context.new_page(),context)
  finally:browser.close()
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as exc:
  # Never print browser exceptions/raw form responses that might include secrets.
  print('Blogsky native operation stopped: '+(str(exc) if type(exc) is RuntimeError else type(exc).__name__)+'. Review controls/checkpoints; no automatic retry.',file=sys.stderr);raise SystemExit(1)
