#!/usr/bin/env python3
"""Native RozBlog publisher: active-blog guard, QA, title dedup and live checkpoints.
Unattended login requires ROZBLOG_USERNAME / ROZBLOG_PASSWORD. Email OTP login is
interactive only; no cookies, passwords or one-time codes are stored in git.
"""
import os,re,sys,time
from urllib.parse import urlsplit,unquote
from pathlib import Path
import rozblog_backlink_queue as wrapper
import publish_roya_posts as state
from city_backlink_policy import matrix_ready,qa,links_for
engine=wrapper.engine
state.QUEUE=engine.QUEUE;state.ART=engine.ART;state.PUBLISH_QUEUE=engine.ART/'publish-queue.json';state.STATE=engine.STATE;state.LOG=engine.ART/'publish-log.jsonl';state.EXPORT=engine.ART/'publish'
BLOG=engine.BLOG;PANEL='https://www.rozblog.com';DO_PUBLISH=os.getenv('ROZBLOG_PUBLISH','0')=='1'
def active(page):
 urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 if 'afp-pipe.rozblog.com'not in {urlsplit(u).hostname for u in urls}:raise RuntimeError('Wrong active RozBlog; never publish to spadan1 or drip-irrigation')
def login(page):
 page.goto(PANEL+'/usercp.php',wait_until='domcontentloaded',timeout=60000)
 if '/login.php'in page.url:
  username=os.getenv('ROZBLOG_USERNAME','');password=os.getenv('ROZBLOG_PASSWORD','')
  if not username or not password:raise RuntimeError('Repository RozBlog login secrets required; OTP cannot run unattended')
  page.locator('#tab-username').click();page.locator('#username').fill(username);page.locator('#password').fill(password)
  for label in ('مرا به خاطر بسپار','Remember me','Keep me signed in'):
   c=page.get_by_label(label,exact=True)
   if c.count()and c.first.is_visible():c.first.check()
  page.locator('#login_roz input[type=submit]').click()
  page.wait_for_url('**/usercp.php',timeout=60000)
 links=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 site=next((u for u in links if u.endswith('/list_site')),None)
 if not site:raise RuntimeError('Authenticated site-list link missing')
 page.goto(site,wait_until='domcontentloaded');choice=page.locator('.site-item').filter(has=page.locator('a[href*="afp-pipe."]'))
 if choice.count()!=1:raise RuntimeError('Cannot uniquely locate intended blog')
 manage=choice.get_by_role('link',name='مدیریت',exact=True)
 if manage.count()!=1:raise RuntimeError('Verified native blog selection missing')
 manage.click();page.wait_for_load_state('domcontentloaded');active(page)
 urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 posts=next((u for u in urls if u.endswith('/admin_post')),None);add=next((u for u in urls if u.endswith('/new_post')),None)
 if not posts or not add:raise RuntimeError('Native publication routes missing')
 return posts,add

def scan(page,posts):
 found={};pending=[posts];seen=set()
 while pending:
  url=pending.pop(0)
  if url in seen:continue
  seen.add(url);page.goto(url,wait_until='domcontentloaded',timeout=60000)
  if '/login.php'in page.url:raise RuntimeError('Session expired before title scan')
  rows=page.locator('a[href]').evaluate_all('a=>a.map(x=>({text:x.textContent.trim(),url:x.href}))')
  for r in rows:
   m=re.search(r'/post/(\d+)(?:[/.]|$)',r['url'])
   if m and urlsplit(r['url']).hostname=='afp-pipe.rozblog.com'and r['text']:
    if r['text']in found and found[r['text']]!=int(m[1]):raise RuntimeError('Ambiguous duplicate title in live panel')
    found[r['text']]=int(m[1])
   if r['url'].startswith(posts+'?')and re.search(r'[?&](page|p)=\d+',r['url'])and r['url']not in seen:pending.append(r['url'])
  if len(seen)>100:raise RuntimeError('Title scan page limit exceeded; no partial dedup')
 return found

def verify(page,item,pid):
 url=BLOG+'/post/'+str(pid)
 response=page.goto(url,wait_until='domcontentloaded',timeout=60000)
 if not response or response.status>=400 or urlsplit(page.url).hostname!='afp-pipe.rozblog.com':raise RuntimeError('Public post inaccessible; stop and reconcile, no second submit')
 article=page.locator('article.post-card').filter(has=page.get_by_text(item['post']['title'],exact=True)).first
 if not article.count():raise RuntimeError('Published AFP article/title missing')
 content=article.locator('.post-content');hrefs={unquote(u).rstrip('/')for u in content.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')}
 if any(unquote(x['url']).rstrip('/')not in hrefs for x in links_for(item)):raise RuntimeError('Contextual city/province/home backlink did not persist')
 if content.locator('details').count()!=3:raise RuntimeError('FAQ did not persist')
 images=article.locator('img[src]').evaluate_all('a=>a.map(x=>x.src)')
 if item['image_url']not in images:raise RuntimeError('Approved city image did not persist')
 return page.url

def main():
 if not matrix_ready():print('RozBlog publication paused pending title matrix.');return 0
 q=state.load(state.PUBLISH_QUEUE,{'items':[]});todo=q['items'];limit=min(3,int(os.getenv('ROZBLOG_PUBLISH_LIMIT','3')),engine.remaining_publication_budget())
 if not DO_PUBLISH:
  for entry in todo[:limit]:state.export_post(state.load(state.resolve_item(entry),{}))
  print('Export only; no remote mutation');return 0
 if not os.getenv('AGENT_BROWSER_CDP')and not(os.getenv('ROZBLOG_USERNAME')and os.getenv('ROZBLOG_PASSWORD')):raise RuntimeError('Set ROZBLOG_USERNAME and ROZBLOG_PASSWORD secrets')
 if not todo or limit==0:print('No approved article or hourly publication capacity.');return 0
 approved=[]
 for entry in todo[:9]:
  if len(approved)>=limit:break
  item=state.load(state.resolve_item(entry),{})
  try:
   from blog_image_gate import review
   engine.retry_transient(lambda:review(item,item['image_url']))
   errors,_=qa(item,item['post'],links_for(item),'rozblog')
   if errors:raise RuntimeError('Publication QA rejected')
  except Exception as exc:
   item['status']='failed';item['last_error']='publication preflight rejected: '+type(exc).__name__
   item['attempts']=item.get('attempts',0)+1;engine.defer_item(item)
   queue=engine.load(engine.QUEUE,{'items':[]})
   for row in queue['items']:
    if row['key']==entry['key']:
     row.update(status='failed',last_error=item['last_error'],attempts=item['attempts'],next_retry_at=item['next_retry_at'])
   engine.save(state.resolve_item(entry),item);engine.save(engine.QUEUE,queue);engine.refresh_ready(queue)
   print(entry['key']+': preflight deferred; continuing to next approved draft',flush=True)
   continue
  approved.append(entry)
 todo=approved
 if not todo:print('All current drafts deferred; queue preserved for next scheduled run.');return 0
 from playwright.sync_api import sync_playwright
 attached=bool(os.getenv('AGENT_BROWSER_CDP'))
 with sync_playwright()as pw:
  browser=pw.chromium.connect_over_cdp(os.environ['AGENT_BROWSER_CDP'])if attached else pw.chromium.launch(args=['--no-sandbox'])
  context=browser.contexts[0]if attached else browser.new_context(locale='fa-IR');page=context.new_page()
  try:
   posts,add=login(page);existing=scan(page,posts)
   for entry in todo[:limit]:
    item=state.load(state.resolve_item(entry),{});post=item['post'];pid=existing.get(post['title']);recovered=bool(pid)
    if not pid:
     page.goto(add,wait_until='domcontentloaded',timeout=60000);page.wait_for_selector('#mtitle');page.wait_for_function('()=>window.tinymce&&tinymce.get("mtex")&&tinymce.get("mtex").getBody()')
     page.locator('#mtitle').fill(post['title']);page.locator('#input_url_seo').fill(post['slug']);page.locator('input[name=pimg]').fill('')
     page.locator('select[name=status]').select_option('1');page.locator('select[name=member]').select_option('0');page.locator('select[name=pcm]').select_option('7')
     page.evaluate('post=>{tinymce.get("mtex").setContent(post.html);if(tinymce.get("mtex2"))tinymce.get("mtex2").setContent("");document.querySelector("#ptags").value=(post.tags||[]).join(",");tinymce.triggerSave()}',post)
     page.get_by_role('button',name='ارسال مطلب و بازسازی سایت',exact=False).click();page.wait_for_load_state('domcontentloaded');existing=scan(page,posts);pid=existing.get(post['title'])
     if not pid:raise RuntimeError('No panel confirmation after one submit; reconcile before retry')
    url=verify(page,item,pid);row={'key':entry['key'],'title':post['title'],'pid':pid,'url':url,'at':state.now(),'verified':True,'recovered_existing':recovered};state.checkpoint(entry,item,row)
    print('Verified RozBlog post '+str(pid)+' -> '+url,flush=True);time.sleep(10)
  finally:
   page.close()
   if not attached:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('RozBlog publication stopped: '+str(exc),file=sys.stderr);sys.exit(1)
