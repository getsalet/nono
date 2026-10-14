"""Native Blogfa login; discovers nonce-bearing links, never persists cookies."""
import os,sys
from urllib.parse import urlsplit
BLOG='https://afp-pipe.blogfa.com/'
PANEL='https://www.blogfa.com'
def active(page):
 if urlsplit(page.url).hostname!='www.blogfa.com' or '/desktop/' not in urlsplit(page.url).path.lower():
  raise RuntimeError('Protected Blogfa panel required')
 urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 if BLOG not in urls:raise RuntimeError('Wrong Blogfa destination; publishing blocked')
 routes={}
 for key,path in [('new','/desktop/post.aspx'),('archive','/desktop/archive.aspx'),('options','/desktop/options.aspx')]:
  candidates={u for u in urls if urlsplit(u).hostname=='www.blogfa.com' and urlsplit(u).path.lower()==path}
  if len(candidates)!=1:raise RuntimeError('Native route missing or ambiguous: '+key)
  routes[key]=candidates.pop()
 return routes
def login(page):
 username=os.getenv('BLOGFA_USERNAME');password=os.getenv('BLOGFA_PASSWORD')
 if not username or not password:raise RuntimeError('Blogfa repository secrets missing')
 page.goto(PANEL+'/Desktop/Login.aspx?ReturnUrl=%2Fdesktop%2F',wait_until='domcontentloaded',timeout=60000)
 if page.locator('input[name=usrid]').count():
  page.locator('input[name=usrid]').fill(username);page.locator('input[name=ups]').fill(password)
  for label in ('مرا به خاطر بسپار','Remember me','Keep me signed in'):
   c=page.get_by_label(label,exact=True)
   if c.count() and c.first.is_visible():c.first.check()
  with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):page.locator('input[name=btnSubmit]').click()
 page.wait_for_selector('a[href*="Post.aspx"]',timeout=30000)
 return active(page)
def main():
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(args=['--no-sandbox']);page=browser.new_page(locale='fa-IR')
  try:
   routes=login(page)
   page.goto(routes['new'],wait_until='domcontentloaded',timeout=60000)
   page.wait_for_function('()=>window.CKEDITOR&&CKEDITOR.instances.txtPostContent?.status==="ready"',timeout=60000)
   required=['#txtPostTitle','#txtPostContent','#txtPostExtended','#cmbCommentType','#btnPublish']
   if not all(page.locator(x).count()==1 for x in required):raise RuntimeError('Native editor contract incomplete')
   if page.locator('#cmbCommentType option[value="2"]').count()!=1:raise RuntimeError('Native comments-off option unavailable')
   print('Blogfa hosted login and native CKEditor contract verified; no post submitted.',flush=True)
  finally:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('Blogfa diagnostic failed: '+type(exc).__name__,file=sys.stderr);sys.exit(1)
