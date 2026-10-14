#!/usr/bin/env python3
"""Single native ASP.NET submit; recover by live title, never blind retry."""
import os,re,sys,time
from pathlib import Path
from urllib.parse import urlsplit,unquote
import blogfa_backlink_queue as wrapper
import publish_roya_posts as state
from blogfa_native import login,BLOG,PANEL
from blog_post_excerpt import native_split
from city_backlink_policy import qa,links_for,matrix_ready
engine=wrapper.engine
state.QUEUE=engine.QUEUE;state.ART=engine.ART;state.PUBLISH_QUEUE=engine.ART/'publish-queue.json';state.STATE=engine.STATE;state.LOG=engine.ART/'publish-log.jsonl';state.EXPORT=engine.ART/'publish'
HOST='afp-pipe.blogfa.com'
def public_records(links):
 found={}
 for row in links:
  u=row['url'];parts=urlsplit(u)
  if parts.hostname!=HOST or not parts.path.startswith('/post/'):continue
  match=re.match(r'/post/(\d+)(?:/|$)',parts.path)
  if not match or not row['title']:raise RuntimeError('Malformed native public post record')
  record={'pid':int(match[1]),'url':u}
  title=row['title'].strip()
  if title in found and found[title]['pid']!=record['pid']:raise RuntimeError('Ambiguous live title')
  found[title]=record
 return found

def scan_public(page):
 pending=[BLOG,BLOG+'posts/'];seen=set();found={}
 while pending:
  u=pending.pop(0)
  if u in seen:continue
  if len(seen)>=100:raise RuntimeError('Public title scan incomplete; page limit')
  seen.add(u);response=page.goto(u,wait_until='domcontentloaded',timeout=60000)
  if not response or response.status>=400 or urlsplit(page.url).hostname!=HOST:raise RuntimeError('Public index unavailable; no partial dedup')
  rows=page.locator('article.post-card h2 a[href]' if urlsplit(page.url).path.rstrip('/')!='/posts' else 'a[href]').evaluate_all('a=>a.map(x=>({title:x.textContent.trim(),url:x.href}))')
  for title,record in public_records(rows).items():
   if title in found and found[title]['pid']!=record['pid']:raise RuntimeError('Duplicate live title')
   found[title]=record
  # Crawl only native pagination of the index and explicit pager controls.
  pages=page.locator('.pager a[href],.nextandprevious a[href]').evaluate_all('a=>a.map(x=>x.href)')
  pages += [x['url'] for x in rows if urlsplit(x['url']).hostname==HOST and urlsplit(x['url']).path.rstrip('/')=='/posts' and x['url'] not in seen]
  for link in pages:
   if urlsplit(link).hostname==HOST and link not in seen and link not in pending:pending.append(link)
 return found

def assert_no_native_match(page,archive,title):
 page.goto(archive,wait_until='domcontentloaded',timeout=60000)
 page.wait_for_selector('#txtQuery',timeout=30000);page.locator('#txtQuery').fill(title)
 for option in ('0','-2','-1'):
  page.locator('#cmbMonthList').select_option(option)
  with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):page.locator('#btnSearch').click()
  body=page.locator('body').inner_text()
  if 'موردی یافت نشد' not in body:raise RuntimeError('Native archive found a possible published/draft match; reconcile before creation')

def prepare(page,post):
 short,full=native_split(post['html'])
 page.wait_for_function('()=>window.CKEDITOR&&CKEDITOR.instances.txtPostContent?.status==="ready"',timeout=60000)
 toggle=page.get_by_text('[ادامه نوشته (متن تکمیلی برای نوشته های طولانی)]',exact=True)
 if toggle.count()!=1:raise RuntimeError('Native continuation toggle not found')
 toggle.click()
 page.wait_for_function('()=>CKEDITOR.instances.txtPostExtended?.status==="ready"',timeout=60000)
 page.locator('#txtPostTitle').fill(post['title'])
 page.locator('#tab3').click();page.locator('#cmbCommentType').select_option('2')
 page.locator('#chkDraft').uncheck()
 page.locator('#tab4').click();page.locator('#chkSticky').uncheck();page.locator('#chkAutomateTime').check()
 page.locator('#tab1').click()
 tags=[re.sub(r'[,+،]',' ',x).strip() for x in post.get('tags',[])[:4]]
 page.locator('#txtTags').fill('+'.join(tags))
 result=page.evaluate(r"""async data=>{
  for(const [id,body] of [['txtPostContent',data.short],['txtPostExtended',data.full]]){
   const e=CKEDITOR.instances[id];e.config.allowedContent=true;e.filter.disable();if(e.activeFilter)e.activeFilter.disable();
   await new Promise(resolve=>e.setData(body,{callback:resolve}));e.updateElement();
  }
  const form=document.querySelector('#txtPostTitle').form, fd=new FormData(form);
  return {title:fd.get('txtPostTitle')===data.title,short:String(fd.get('txtPostContent')||'').length,full:String(fd.get('txtPostExtended')||'').length,comments:fd.get('cmbCommentType'),faqs:(String(fd.get('txtPostExtended')).match(/<details\b/g)||[]).length};
 }""",{'short':short,'full':full,'title':post['title']})
 print('Blogfa native form readiness: '+str(result),flush=True)
 if not(result['title'] and result['short']>60 and result['full']>200 and result['comments']=='2' and result['faqs']==3):raise RuntimeError('Native form serialization incomplete; not submitted')
 print('Blogfa native form ready: split summary/full, 3 FAQs, comments off.',flush=True)
 return short,full

def journal(entry,phase):
 p=engine.ART/'submission-attempts.json';j=engine.load(p,{});j[entry['key']]={'phase':phase,'at':state.now()};engine.save(p,j)
def begin(entry):
 prior=engine.load(engine.ART/'submission-attempts.json',{}).get(entry['key'],{})
 if prior.get('phase')in ('submitting','unconfirmed'):raise RuntimeError('Prior uncertain native POST; manual reconciliation required')
 journal(entry,'submitting')
def verify(page,item,record):
 url=record['url']
 if urlsplit(url).hostname!=HOST:raise RuntimeError('Wrong public destination')
 resp=page.goto(url,wait_until='domcontentloaded',timeout=60000)
 if not resp or resp.status>=400:raise RuntimeError('Public article unavailable')
 article=page.locator('article.post-card').filter(has=page.get_by_text(item['post']['title'],exact=True))
 if article.count()!=1:raise RuntimeError('Expected native article not unique')
 body=article.locator('.post-content')
 hrefs={unquote(x).rstrip('/') for x in body.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')}
 if any(unquote(x['url']).rstrip('/')not in hrefs for x in links_for(item)):raise RuntimeError('Approved backlinks did not persist')
 if body.locator('details').count()!=3:raise RuntimeError('Native FAQ structure did not persist')
 imgs=body.locator('img').evaluate_all('a=>a.map(x=>x.src)')
 if imgs!=[item['image_url']]:raise RuntimeError('Approved image missing or duplicated')
 from content_originality import text
 if len(text(body.inner_html()).split())<450:raise RuntimeError('Native continuation missing')
 page.goto(BLOG,wait_until='domcontentloaded',timeout=60000)
 card=page.locator('article.post-card').filter(has=page.get_by_text(item['post']['title'],exact=True))
 if card.count():
  excerpt=card.locator('.post-content');full=native_split(item['post']['html'])[1]
  if excerpt.locator('details,h2,ul,ol').count() or len(text(excerpt.inner_html()).split())>=250:raise RuntimeError('Homepage contains full article, not native summary')
  if card.locator('a.readmore').count()!=1:raise RuntimeError('Native read-more missing')
 return url

def main():
 if not matrix_ready():raise RuntimeError('Blogfa matrix unavailable')
 todo=state.load(state.PUBLISH_QUEUE,{'items':[]})['items']
 target=os.getenv('BLOGFA_TARGET')
 if target:todo=[x for x in todo if x['key']==target]
 limit=min(3,int(os.getenv('BLOGFA_PUBLISH_LIMIT','3')),engine.remaining_publication_budget())
 if os.getenv('BLOGFA_PUBLISH','0')!='1':
  for e in todo[:limit]:state.export_post(state.load(state.resolve_item(e),{}))
  print('Blogfa export only; no remote publication.');return 0
 if not todo or not limit:print('Blogfa publication idle; queue/budget checked.');return 0
 approved=[]
 for e in todo[:limit]:
  item=state.load(state.resolve_item(e),{})
  from blog_image_gate import review
  engine.retry_transient(lambda:review(item,item['image_url']))
  errors,_=qa(item,item['post'],links_for(item),'blogfa')
  if errors:raise RuntimeError('Blogfa publication quality gate rejected')
  if not item.get('qa',{}).get('passed'):raise RuntimeError('Draft lacks successful QA')
  approved.append((e,item))
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(args=['--no-sandbox']);page=browser.new_page(locale='fa-IR');page.on('dialog',lambda d:d.accept())
  try:
   routes=login(page);existing=scan_public(page)
   for e,item in approved:
    title=item['post']['title'];record=existing.get(title);recovered=bool(record)
    if not record:
     assert_no_native_match(page,routes['archive'],title)
     page.goto(routes['new'],wait_until='domcontentloaded',timeout=60000);prepare(page,item['post']);begin(e)
     with page.expect_navigation(wait_until='domcontentloaded',timeout=60000)as response:page.locator('#btnPublish').click()
     journal(e,'unconfirmed')
     feedback={'key':e['key'],'at':state.now(),'http_status':response.value.status if response.value else None,'path':urlsplit(page.url).path,'native_message':page.locator('body').inner_text()[-2500:]}
     engine.save(engine.ART/'native-submit-feedback.json',feedback)
     print('Blogfa native submit feedback: '+str(feedback),flush=True)
     for attempt in range(12):
      existing=scan_public(page);record=existing.get(title)
      if record:break
      time.sleep(5)
     if not record:raise RuntimeError('No live confirmation after single Blogfa POST; do not retry submission')
    url=verify(page,item,record)
    row={'key':e['key'],'title':title,'pid':record['pid'],'url':url,'at':state.now(),'verified':True,'recovered_existing':recovered}
    state.checkpoint(e,item,row);journal(e,'verified');existing[title]=record
    print('Verified Blogfa article '+str(record['pid'])+' -> '+url,flush=True)
  finally:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('Blogfa publication stopped: '+str(exc),file=sys.stderr);sys.exit(1)
