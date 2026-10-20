#!/usr/bin/env python3
"""Bounded reconciliation of two known posts. Never creates a new article."""
import copy,json,os,re,sys,time,traceback
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
TARGETS={'farsiblog':'city-3e7ef4ae8bebb305','loxblog':'city-fbb8d21e0c46bc3f'}

def matches(item,body,links):
 from blog_public_content_verify import verify_article_body
 try:verify_article_body(item,body,links);return True
 except RuntimeError:return False

def entry_and_item(state,blog):
 key=TARGETS[blog];path=state.ART/'items'/(key+'.json')
 item=state.load(path,{})
 if item.get('key')!=key or not item.get('post') or not item.get('qa',{}).get('passed'):raise RuntimeError('Exact QA-approved recovery draft unavailable')
 return {'key':key,'item_file':str(path)},item

def farsi():
 import publish_farsiblog_posts as publisher
 from farsiblog_pressure_wording import normalize
 from blog_public_content_verify import verify_article_body
 state=publisher.native;generator=publisher.generator
 entry,item=entry_and_item(state,'farsiblog');links=generator.links_for(item)
 corrected=copy.deepcopy(item);corrected['post']=normalize(item['post'])
 errors,info=generator.qa(corrected,corrected['post'],links)
 if errors:raise RuntimeError('Full corrected-draft QA rejected: '+str(errors))
 corrected['qa']={'passed':True,'errors':[],**info}
 from playwright.sync_api import sync_playwright
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  try:
   page=browser.new_page();publisher.login(page)
   # Exhaustive native scan; refuse duplicate titles and keep observed edit URL.
   pending=[state.POSTS_URL];seen=set();records=[]
   while pending:
    url=pending.pop(0)
    if url in seen:continue
    if len(seen)>=100:raise RuntimeError('Native archive scan incomplete')
    seen.add(url);page.goto(url,wait_until='domcontentloaded',timeout=60000);publisher.active_blog(page)
    page.locator('table.poststable').wait_for(timeout=30000)
    records+=page.locator('table.poststable tbody tr').evaluate_all('es=>es.map(e=>({title:e.querySelector(".tdtitle")?.innerText.trim(),edit:e.querySelector("a.actionedit")?.href}))')
    pending += [u for u in page.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)')if urlsplit(u).netloc==urlsplit(state.PANEL).netloc and urlsplit(u).path.rstrip('/')=='/User/Posts' and u not in seen and u not in pending]
   found=[r for r in records if r['title']==item['post']['title']]
   edits={r['edit']for r in found}
   if len(edits)!=1:raise RuntimeError('Native title is absent or ambiguous; no new POST allowed')
   edit=edits.pop()
   if not re.fullmatch(re.escape(state.PANEL)+r'/User/EditPosts/146/?',edit):raise RuntimeError('Unexpected native identity; stop')
   pid=146
   public=browser.new_page()
   try:
    try:
     verified_url=publisher.verify(public,corrected,pid)
    except RuntimeError:
     actual=public.locator('article.post-card .post-content').inner_html()
     censored=copy.deepcopy(item);censored['post']['html']=re.sub(r'نرمال([\u200c ])کننده فشار',r'ن********\1کننده فشار',item['post']['html'])
     if not matches(censored,actual,links):raise RuntimeError('Public mismatch is not the diagnosed wording-only change; no edit')
     page.goto(edit,wait_until='domcontentloaded',timeout=60000);publisher.active_blog(page)
     if page.locator('#ptitle').input_value().strip()!=item['post']['title']:raise RuntimeError('Edit title identity mismatch')
     slug=page.locator('#plink').input_value()
     if slug!=item['post']['slug'][:60].strip('-'):raise RuntimeError('Edit slug identity mismatch')
     page.wait_for_function("()=>['pshort','pfull'].every(id=>window.tinymce?.get(id)?.initialized)",timeout=45000)
     native=page.evaluate("()=>tinymce.get('pshort').getContent()+tinymce.get('pfull').getContent()")
     if not any(matches(x,native,links)for x in (item,censored,corrected)):raise RuntimeError('Native body does not match known draft; no edit')
     form=page.locator('#ptitle').evaluate('e=>({action:e.form?.action,cls:e.form?.className,method:e.form?.method})')
     if form['method'].lower()!='post' or not form['action'].rstrip('/').endswith('/User/EditPosts/146'):raise RuntimeError('Native edit form action not confirmed: '+str(form))
     if page.locator('input[name=postid]').input_value()!='146':raise RuntimeError('Hidden existing post identity mismatch; no edit')
     page.evaluate("body=>{tinymce.get('pshort').setContent(body);tinymce.get('pfull').setContent('');tinymce.triggerSave();}",corrected['post']['html'])
     serialized=page.evaluate("()=>tinymce.get('pshort').getContent()+tinymce.get('pfull').getContent()")
     verify_article_body(corrected,serialized,links)
     # Submit the existing edit form once, preserving all server-loaded metadata.
     # The native edit can save via AJAX without a document navigation.
     # Observe the confirmed native /Op/ AJAX handler once, then verify content;
     # never treat a navigation timeout as permission to submit again.
     from playwright.sync_api import TimeoutError as BrowserTimeout
     try:
      with page.expect_response(lambda r:r.request.method=='POST' and urlsplit(r.url).hostname==urlsplit(state.PANEL).hostname and urlsplit(r.url).path.rstrip('/')=='/Op',timeout=90000)as saved:
       page.locator('#ptitle').evaluate("e=>window.jQuery?window.jQuery(e.form).submit():e.form.submit()")
      if saved.value.status>=400:raise RuntimeError('Native existing edit HTTP '+str(saved.value.status)+'; no repeat submission')
      feedback=saved.value.text().strip()
      if not feedback.startswith('success:'):
       if feedback.startswith('error:'):
        reason=re.sub(r'<[^>]*>',' ',feedback)[:300]
        for value in (os.getenv('FARSIBLOG_USERNAME'),os.getenv('FARSIBLOG_PASSWORD')):
         if value:reason=reason.replace(value,'[redacted]')
        raise RuntimeError('Native existing edit rejected: '+reason)
       raise RuntimeError('Native existing edit did not acknowledge success; no repeat submission')
     except BrowserTimeout:
      print('Edit response uncertain; checking public article without another POST.',flush=True)
     verified_url=None
     for attempt in range(3):
      try:verified_url=publisher.verify(public,corrected,pid);break
      except RuntimeError:
       if attempt==2:raise
       time.sleep(3)
    row={'key':entry['key'],'title':corrected['post']['title'],'pid':pid,'url':verified_url,'at':state.now(),'verified':True,'recovered_existing':True,'repair':'standard-pressure-regulator-wording-v1'}
    state.checkpoint(entry,corrected,row)
    print('FarsiBlog existing post146 strictly verified and checkpointed; no new article.',flush=True)
   finally:public.close()
  finally:browser.close()

def lox():
 import publish_loxblog_posts as publisher
 entry,item=entry_and_item(publisher.state,'loxblog')
 links=publisher.links_for(item)
 errors,_=publisher.qa(item,item['post'],links,'loxblog',ROOT)
 if errors:raise RuntimeError('Full existing-draft QA rejected: '+str(errors))
 from playwright.sync_api import sync_playwright
 from blog_public_content_verify import verify_article_body
 with sync_playwright()as pw:
  browser=publisher.launch_browser(pw)
  try:
   page=browser.new_page();public=browser.new_page();publisher.login(page)
   record=publisher.find_native_record(page,item['post']['title'])
   if not record:raise RuntimeError('Existing all-status native match absent; no new POST allowed')
   url=publisher.verify(public,item,record)
   public.goto(url,wait_until='domcontentloaded',timeout=60000)
   verify_article_body(item,public.locator('article.post-card .post-content').inner_html(),links)
   row={'key':entry['key'],'title':item['post']['title'],'pid':record['pid'],'url':url,'at':publisher.state.now(),'verified':True,'recovered_existing':True}
   publisher.state.checkpoint(entry,item,row);publisher.journal(entry,'verified')
   print('LoxBlog existing native post',record['pid'],'strictly verified; uncertainty cleared without any article submit.',flush=True)
  finally:browser.close()

def main():
 blog=sys.argv[1]
 if blog not in TARGETS:raise RuntimeError('Unsupported recovery target')
 from check_blog_pipeline_control import decision
 from city_backlink_policy import matrix_ready
 if not decision(blog,ROOT)['proceed'] or not matrix_ready():raise RuntimeError('Recovery stopped by publication control')
 if blog=='loxblog':
  from check_loxblog_release import evaluate
  release=json.loads((ROOT/'data/loxblog/deployment-control.json').read_text())
  if not evaluate(release,'schedule',os.getenv('REPOSITORY_SWITCH',''))['proceed']:raise RuntimeError('LoxBlog release not approved')
 {'farsiblog':farsi,'loxblog':lox}[blog]()
def run_report():
 blog=sys.argv[1]
 if blog not in TARGETS:raise RuntimeError('Unsupported recovery target')
 report={'blog':blog,'key':TARGETS[blog],'passed':False,'new_articles':0}
 try:
  main();report['passed']=True
 except Exception as exc:
  report['error_class']=type(exc).__name__
  report['reason']=str(exc)[:350]if type(exc)is RuntimeError else 'Hosted operation failed; inspect sanitized location'
  report['locations']=[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(exc.__traceback__)if str(ROOT/'automation')in f.filename][-6:]
  raise
 finally:
  path=ROOT/'artifacts'/(blog+'-backlink-queue')/'known-post-recovery.json'
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':run_report()
