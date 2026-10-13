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
BLOG=engine.BLOG;PANEL='https://www.rozblog.com';EXPECTED_HOST='afp-pipe.rozblog.com';DO_PUBLISH=os.getenv('ROZBLOG_PUBLISH','0')=='1'
def active(page):
 # Native change_accont returns a blank document, not the authenticated panel.
 # This guard must run only on the reloaded protected usercp page.
 if urlsplit(page.url).hostname!='www.rozblog.com' or urlsplit(page.url).path!='/usercp.php':
  raise RuntimeError('Protected RozBlog panel required before destination verification')
 urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 if EXPECTED_HOST not in {urlsplit(u).hostname for u in urls}:
  raise RuntimeError('Wrong active RozBlog; never publish to spadan1 or drip-irrigation')
 routes={}
 for name in ('admin_post','new_post'):
  matches={u for u in urls if urlsplit(u).scheme=='https' and urlsplit(u).hostname=='www.rozblog.com' and re.fullmatch(r'/panel\d+/'+name,urlsplit(u).path)}
  if len(matches)!=1:raise RuntimeError('Missing or ambiguous native publication route: '+name)
  routes[name]=matches.pop()
 if urlsplit(routes['admin_post']).path.rsplit('/',1)[0]!=urlsplit(routes['new_post']).path.rsplit('/',1)[0]:
  raise RuntimeError('Native publication routes belong to different panels')
 return routes['admin_post'],routes['new_post']
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
 # Wait for the one native selection request, then reopen the protected panel.
 # Never treat its empty response as proof of the selected site's identity.
 with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):
  manage.click()
 page.goto(PANEL+'/usercp.php',wait_until='domcontentloaded',timeout=60000)
 if '/login.php' in page.url:raise RuntimeError('Session expired after native blog selection')
 page.wait_for_selector('a[href*="/new_post"]',state='attached',timeout=30000)
 return active(page)

def post_records(rows):
 found={}
 for row in rows:
  match=re.fullmatch(r'tr_(\d+)',row.get('row_id',''))
  if not match or int(match[1])<1 or row.get('checkbox_id')!=match[1]:
   raise RuntimeError('Native post row identity incomplete; refuse partial dedup')
  title=row.get('title','').strip();url=row.get('url','');parts=urlsplit(url)
  if not title or parts.hostname!=EXPECTED_HOST or parts.scheme not in ('http','https') or parts.path in ('','/'):
   raise RuntimeError('Native post title/public destination incomplete')
  record={'pid':int(match[1]),'url':url}
  if title in found and found[title]!=record:raise RuntimeError('Ambiguous duplicate title in live panel')
  found[title]=record
 return found

def scan(page,posts):
 found={};pending=[posts];seen=set()
 while pending:
  url=pending.pop(0)
  if url in seen:continue
  seen.add(url);page.goto(url,wait_until='domcontentloaded',timeout=60000)
  if '/login.php'in page.url:raise RuntimeError('Session expired before title scan')
  page.wait_for_selector('table.tb_new',state='attached',timeout=30000)
  headers=page.locator('table.tb_new th').all_text_contents()
  if not any('عنوان' in h for h in headers):raise RuntimeError('Native post table identity missing')
  # RozBlog supports custom public URL formats. Read the native row ID and
  # public title link; never infer an ID from a /post/ URL that may not exist.
  rows=page.locator('table.tb_new tr[id^="tr_"]').evaluate_all(r"""rows=>rows.map(r=>({row_id:r.id,checkbox_id:r.querySelector('input[name="deleted_items[]"]')?.value,title:r.querySelector('a.post-title-link')?.textContent.trim(),url:r.querySelector('a.post-title-link')?.href}))""")
  for title,record in post_records(rows).items():
   if title in found and found[title]!=record:raise RuntimeError('Ambiguous duplicate title in live panel')
   found[title]=record
  links=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
  for link in links:
   if link.startswith(posts+'?')and re.search(r'[?&](page|p)=\d+',link)and link not in seen:pending.append(link)
  if len(seen)>100:raise RuntimeError('Title scan page limit exceeded; no partial dedup')
 return found

def confirm_post(page,posts,title):
 # Read-only retries for eventual consistency; never a second form submission.
 for attempt in range(3):
  found=scan(page,posts);record=found.get(title)
  if record:return found,record
  if attempt<2:time.sleep(2)
 raise RuntimeError('No panel confirmation after one submit; reconcile before retry')

def verify(page,item,pid,public_url):
 url=public_url
 if urlsplit(url).hostname!=EXPECTED_HOST:raise RuntimeError('Native public URL belongs to another blog')
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
    item=state.load(state.resolve_item(entry),{});post=item['post'];record=existing.get(post['title']);pid=record['pid']if record else None;recovered=bool(record)
    if not pid:
     page.goto(add,wait_until='domcontentloaded',timeout=60000);page.wait_for_selector('#mtitle');page.wait_for_function('()=>window.tinymce&&tinymce.get("mtex")&&tinymce.get("mtex").getBody()')
     page.locator('#mtitle').fill(post['title']);page.locator('#input_url_seo').fill(post['slug']);page.locator('input[name=pimg]').fill('')
     page.locator('select[name=status]').select_option('1');page.locator('select[name=member]').select_option('0');page.locator('select[name=pcm]').select_option('7')
     page.evaluate('post=>{tinymce.get("mtex").setContent(post.html);if(tinymce.get("mtex2"))tinymce.get("mtex2").setContent("");document.querySelector("#ptags").value=(post.tags||[]).join(",");tinymce.triggerSave()}',post)
     # Arm navigation BEFORE the only native POST. A load-state check after
     # click can return while the old document is still loaded; navigating to
     # the list then aborts the in-flight save.
     with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):
      page.get_by_role('button',name='ارسال مطلب و بازسازی سایت',exact=False).click()
     existing,record=confirm_post(page,posts,post['title']);pid=record['pid']
    url=verify(page,item,pid,record['url']);row={'key':entry['key'],'title':post['title'],'pid':pid,'url':url,'at':state.now(),'verified':True,'recovered_existing':recovered};state.checkpoint(entry,item,row)
    print('Verified RozBlog post '+str(pid)+' -> '+url,flush=True);time.sleep(10)
  finally:
   page.close()
   if not attached:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('RozBlog publication stopped: '+str(exc),file=sys.stderr);sys.exit(1)
