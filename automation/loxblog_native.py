#!/usr/bin/env python3
"""Native LoxBlog login with visual CAPTCHA; never exports sessions or secrets."""
import base64,json,os,re,sys,urllib.request
from urllib.parse import urlsplit
PANEL='https://loxblog.com'
BLOG='https://afp.lxb.ir/'
NEW=PANEL+'/adminnew.php?page=sendpost'
ARCHIVE=PANEL+'/adminnew.php?page=postslist'

def read_captcha(raw):
 import roya_backlink_queue as roya
 from agnes_json_client import parse_object
 key=roya.BASE.next_agnes_key() if hasattr(roya.BASE,'next_agnes_key') else roya.BASE.AGNES_KEY
 if not key:raise RuntimeError('Vision credential required for native visual challenge')
 payload={'model':roya.BASE.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':'Read the five decimal digits in this ordinary login verification image, left to right. Return only JSON {"digits":"12345"}. Do not infer unseen digits.'},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(raw).decode()}}]}],'temperature':0,'max_tokens':100}
 req=urllib.request.Request(roya.BASE.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=90)as r:obj=json.loads(r.read())
  value=parse_object(obj['choices'][0]['message']['content']).get('digits','')
 except Exception as exc:raise RuntimeError('Native visual challenge transcription unavailable: '+type(exc).__name__)from None
 if not re.fullmatch(r'[0-9]{5}',str(value)):raise RuntimeError('Visual challenge ambiguous; no credential submission')
 return str(value)

def launch_browser(pw):return pw.chromium.launch(headless=True)

def assert_management(page):
 if urlsplit(page.url).hostname!='loxblog.com' or urlsplit(page.url).path!='/adminnew.php':raise RuntimeError('Native management session not active')
 target=page.locator('a[href]').evaluate_all('es=>es.filter(e=>e.textContent.trim()==="afp.lxb.ir").map(e=>e.href)')
 if not any(urlsplit(x).hostname=='afp.lxb.ir' for x in target):raise RuntimeError('Native session is not managing expected AFP blog')

def login(page):
 user=os.getenv('LOXBLOG_USERNAME','');password=os.getenv('LOXBLOG_PASSWORD','')
 if not user or not password:raise RuntimeError('Missing dedicated LoxBlog repository secrets')
 page.goto(PANEL+'/login.php',wait_until='domcontentloaded',timeout=60000)
 page.locator('#usern').wait_for(timeout=30000)
 image=page.locator('#loginForm .captcha-img');image.wait_for(timeout=30000)
 page.wait_for_function('()=>document.querySelector("#loginForm .captcha-img")?.complete && document.querySelector("#loginForm .captcha-img").naturalWidth>0',timeout=30000)
 # Keep the challenge in memory only. No HAR, raw response, token or password artifacts.
 code=read_captcha(image.screenshot())
 page.locator('#usern').fill(user);page.locator('#loginPass').fill(password)
 page.locator('#loginForm input[name=captcha]').fill(code)
 for remember in ('input[autocomplete="remember-me"]','input[name="remember"]'):
  box=page.locator(remember)
  if box.count() and box.is_visible():box.check()
 with page.expect_response(lambda r:urlsplit(r.url).path=='/logininc.php' and r.request.method=='POST',timeout=60000) as result:
  page.locator('#submitlogin').click()
 try:feedback=result.value.json()
 except Exception:raise RuntimeError('Native login returned invalid response')from None
 if feedback.get('status')!='ok':
  # Don't expose native message/account data or retry credentials after a denial.
  message=str(feedback.get('message',''))
  reason='visual_challenge' if any(x in message for x in ('کپچا','تصویر','امنیتی','کد'))else'authentication'
  raise RuntimeError('Native login rejected ('+reason+'); no automatic credential retry')
 page.wait_for_url('**/adminnew.php**',timeout=60000);assert_management(page)
 print('LoxBlog native login verified for expected blog.',flush=True)
 return {'new':NEW,'archive':ARCHIVE}

def main():
 from playwright.sync_api import sync_playwright
 with sync_playwright()as pw:
  browser=launch_browser(pw)
  try:
   page=browser.new_page();login(page)
   page.goto(NEW,wait_until='domcontentloaded',timeout=60000);assert_management(page)
   page.locator('#ptitle').wait_for(timeout=30000)
   page.wait_for_function('()=>window.tinymce?.get("editor1")?.initialized && window.tinymce?.get("editor2")?.initialized',timeout=60000)
   page.goto(ARCHIVE,wait_until='domcontentloaded',timeout=60000);assert_management(page)
   page.locator('input[name=search]').wait_for(timeout=30000)
   print('Read-only diagnosis passed: expected blog, native summary/continuation editor, archive available. No publication.',flush=True)
  finally:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('LoxBlog native operation stopped: '+str(exc),file=sys.stderr);sys.exit(1)
