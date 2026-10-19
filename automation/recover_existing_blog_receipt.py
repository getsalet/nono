#!/usr/bin/env python3
"""Named existing-post reconciliation only. This module has no submit path."""
import importlib,json,os,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGETS={'farsiblog':'article-1e888a405d8d8fd3','loxblog':'city-52b5c7a0e0d4a0f3'}
def recover(blog):
 if blog not in TARGETS:raise ValueError('Unsupported receipt recovery blog')
 from blog_image_runtime_control import publication_paused
 if publication_paused(ROOT):raise RuntimeError('Publication intentionally paused; recovery deferred')
 key=TARGETS[blog];art=ROOT/'artifacts'/(blog+'-backlink-queue')
 report={'blog':blog,'key':key,'mode':'existing_post_only','new_submissions':0,'passed':False}
 try:
  state=json.loads((ROOT/'state'/(blog+'-backlink-progress.json')).read_text())
  if any(r['key']==key for r in state.get('published',[])):
   report.update(passed=True,result='already_checkpointed');return report
  publisher=importlib.import_module('publish_'+blog+'_posts')
  native=publisher.native if blog=='farsiblog' else publisher.state
  engine=publisher.generator if blog=='farsiblog' else publisher.engine
  entry={'key':key,'item_file':key+'.json'};item=native.load(native.resolve_item(entry),{})
  if item.get('key')!=key or not item.get('qa',{}).get('passed') or not item.get('post',{}).get('html'):raise RuntimeError('Approved saved article missing')
  from playwright.sync_api import sync_playwright
  with sync_playwright()as pw:
   browser=pw.chromium.launch(headless=True)
   try:
    page=browser.new_page();public=browser.new_page();publisher.login(page)
    if blog=='farsiblog':
     pid=publisher.scan(page).get(item['post']['title'].strip())
     if not pid:raise RuntimeError('Existing exact native title not found; no new submission allowed')
     url=publisher.verify(public,item,pid)
    else:
     record=publisher.find_native_record(page,item['post']['title'])
     if not record:raise RuntimeError('Existing unique native record not found; no new submission allowed')
     pid=record['pid'];url=publisher.verify(public,item,record)
    row={'key':key,'title':item['post']['title'],'pid':pid,'url':url,'at':native.now(),'verified':True,'recovered_existing':True}
    native.checkpoint(entry,item,row)
    if blog=='loxblog':publisher.journal(entry,'verified')
    report.update(passed=True,result='verified_existing',pid=pid,url=url)
   finally:browser.close()
 except Exception as exc:
  report['error_class']=type(exc).__name__
  # Only application-authored RuntimeError messages; never Playwright call logs,
  # page HTML, credentials, screenshots, sessions, or native form data.
  report['reason']=str(exc)[:350] if type(exc)is RuntimeError else 'Hosted verification failed; inspect error location'
  report['error_location']=[{'file':Path(f.filename).name,'line':f.lineno} for f in traceback.extract_tb(exc.__traceback__) if str(ROOT/'automation')in f.filename][-4:]
 finally:
  art.mkdir(parents=True,exist_ok=True);(art/'existing-receipt-recovery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return report
if __name__=='__main__':
 report=recover(sys.argv[1]);print(json.dumps(report,ensure_ascii=False));sys.exit(0 if report['passed'] else 1)
