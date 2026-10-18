"""Native Blogfa login; discovers nonce-bearing links, never persists cookies."""
import os,sys,re,json
from urllib.parse import urlsplit,parse_qs,urljoin
BLOG='https://afp-pipe.blogfa.com/'
PANEL='https://www.blogfa.com'
def active(page):
 if urlsplit(page.url).hostname!='www.blogfa.com' or '/desktop/' not in urlsplit(page.url).path.lower():
  raise RuntimeError('Protected Blogfa panel required')
 urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)')
 if not any(urlsplit(u).scheme in ('http','https') and urlsplit(u).hostname==urlsplit(BLOG).hostname and urlsplit(u).path in ('','/') for u in urls):raise RuntimeError('Wrong Blogfa destination; publishing blocked')
 routes={}
 for key,path in [('new','/desktop/post.aspx'),('archive','/desktop/archive.aspx'),('options','/desktop/options.aspx')]:
  candidates={u for u in urls if urlsplit(u).hostname=='www.blogfa.com' and urlsplit(u).path.lower()==path and (key!='new' or parse_qs(urlsplit(u).query).get('action',[''])[0].lower()=='new')}
  if len(candidates)>1:
   labels={'new':'نوشته جدید','archive':'نوشته‌های پیشین','options':'تنظیمات و دیگر امکانات'}
   # Dashboard shortcuts can have a different per-render nonce from the sidebar.
   # Follow the actual unique sidebar link, not the ambiguous combined label set.
   nav=page.get_by_role('link',name=re.compile(r'^❯\s*'+re.escape(labels[key])+r'\s*$'))
   if nav.count()!=1:
    nav=page.get_by_role('link',name=re.compile(r'^'+re.escape(labels[key])+r'\s*$'))
   if nav.count()==1:
    chosen=urljoin(page.url,nav.get_attribute('href') or '')
    if chosen in candidates:candidates={chosen}
  if len(candidates)!=1:raise RuntimeError('Native route missing or ambiguous: '+key+' candidates='+str(len(candidates)))
  routes[key]=candidates.pop()
 return routes
def login(page,trace=None):
 raise RuntimeError('Blogfa retired by user; no login or network request')
 username=os.getenv('BLOGFA_USERNAME');password=os.getenv('BLOGFA_PASSWORD')
 if not username or not password:raise RuntimeError('Blogfa repository secrets missing')
 if trace:trace.checkpoint('before_login_navigation')
 # Let the service choose its canonical login return route, as in the native UI.
 page.goto(PANEL+'/Desktop/Home.aspx',wait_until='load',timeout=60000)
 if trace:trace.checkpoint('login_or_existing_session_loaded')
 if page.locator('input[name=usrid]').count():
  page.locator('input[name=usrid]').fill(username);page.locator('input[name=ups]').fill(password)
  for label in ('مرا به خاطر بسپار','Remember me','Keep me signed in'):
   c=page.get_by_label(label,exact=True)
   if c.count() and c.first.is_visible():c.first.check()
  with page.expect_navigation(wait_until='load',timeout=60000):page.locator('input[name=btnSubmit]').click()
 page.wait_for_selector('a[href*="Post.aspx"]',timeout=30000)
 if trace:trace.checkpoint('authenticated_native_home')
 return active(page)
def launch_browser(pw):
 # Use the actual requested engine; no custom user agent or browser impersonation.
 name=os.getenv('BLOGFA_BROWSER','chromium')
 if name=='firefox':return pw.firefox.launch()
 if name=='chromium':return pw.chromium.launch(args=['--no-sandbox'])
 raise RuntimeError('Unsupported native Blogfa browser engine')
def wait_editor_ready(page):
 # The native page starts an asynchronous session refresh on load. Document load
 # and CKEditor readiness alone do not mean that server initialization finished.
 page.wait_for_load_state('load',timeout=60000)
 page.wait_for_function('()=>window.CKEDITOR&&CKEDITOR.instances.txtPostContent?.status==="ready"',timeout=60000)
 page.wait_for_function('()=>typeof httpreq!=="undefined"&&httpreq.readyState===4&&httpreq.status===200',timeout=60000)
 print('Blogfa native editor and initial session refresh complete.',flush=True)
def wait_submit_ready(page):
 # Controlled timing comparison: keep the native form/session stable for 30s.
 # No user-agent changes, cookie copying, fabricated tokens, or submit retries.
 identity=page.url
 def validate():
  if page.url!=identity or urlsplit(page.url).hostname!='www.blogfa.com':raise RuntimeError('Native page changed before submit; not sent')
  button=page.locator('#btnPublish')
  if button.count()!=1 or not button.is_enabled():raise RuntimeError('Native submit unavailable; not sent')
  action=button.evaluate('e=>e.form.action')
  if action!=identity:raise RuntimeError('Native form action changed; not sent')
  token=parse_qs(urlsplit(action).query).get('t',[None])[0]
  cookies={c['name']:c['value']for c in page.context.cookies('https://www.blogfa.com/')}
  if not token or cookies.get('ten')!=token:raise RuntimeError('Native session/form mismatch; not sent')
 validate()
 print('Native stabilization experiment: wait 30 seconds with unchanged native form/session before the single submit.',flush=True)
 page.wait_for_timeout(30000)
 validate()
 print('Native stabilization complete; form/session still consistent.',flush=True)

def main():
 print('Blogfa retired by user; no browser, login or network request.');return 0
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=launch_browser(pw);page=browser.new_page()
  from blogfa_session_trace import SessionTrace
  trace=SessionTrace(page)
  try:
   routes=login(page,trace=trace)
   target=os.getenv('BLOGFA_TARGET','').strip();draft=None
   if target:
    from pathlib import Path
    if not all(c.isalnum() or c in '-_' for c in target):raise RuntimeError('Invalid diagnostic key')
    draft=json.loads((Path('artifacts/blogfa-backlink-queue/items')/(target+'.json')).read_text())
    if not draft.get('qa',{}).get('passed'):raise RuntimeError('Diagnostic draft must be approved')
    page.goto(routes['archive'],wait_until='domcontentloaded',timeout=60000);page.locator('#txtQuery').fill(draft['post']['title'])
    trace.checkpoint('archive_loaded')
    for option in ('0','-2','-1'):
     page.locator('#cmbMonthList').select_option(option)
     with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):page.locator('#btnSearch').click()
     trace.checkpoint('archive_search_'+option)
     print('Native reconciliation filter '+option+': empty='+str('موردی یافت نشد' in page.locator('body').inner_text()),flush=True)
    fresh=active(page);print('Fresh create route differs from initial: '+str(fresh['new']!=routes['new']),flush=True);routes=fresh
   page.goto(routes['new'],wait_until='domcontentloaded',timeout=60000)
   trace.checkpoint('native_form_received')
   wait_editor_ready(page)
   trace.checkpoint('editor_and_initial_refresh_ready')
   required=['#txtPostTitle','#txtPostContent','#txtPostExtended','#cmbCommentType','#btnPublish']
   if not all(page.locator(x).count()==1 for x in required):raise RuntimeError('Native editor contract incomplete')
   if page.locator('#cmbCommentType option[value="2"]').count()!=1:raise RuntimeError('Native comments-off option unavailable')
   if draft:
    from publish_blogfa_posts import prepare
    prepare(page,draft['post'])
    trace.checkpoint('approved_form_prepared')
   meta=page.locator('#btnPublish').evaluate('e=>({tag:e.tagName,type:e.type,name:e.name,onclick:e.getAttribute("onclick"),onsubmit:e.form.getAttribute("onsubmit"),readyState:document.readyState,formPath:new URL(e.form.action).pathname,formQueryKeys:Array.from(new URL(e.form.action).searchParams.keys()),pageQueryKeys:Array.from(new URL(location.href).searchParams.keys()),formQueryEqualsPage:new URL(e.form.action).search===location.search,fields:Array.from(new FormData(e.form)).map(([k,v])=>[k,String(v).length])})')
   print('Native editor nonsecret contract: '+str(meta),flush=True)
   print('Native script paths: '+str(page.locator('script[src]').evaluate_all('a=>a.map(x=>new URL(x.src).origin+new URL(x.src).pathname)')),flush=True)
   # Structure only: strip inline literal values, including CSRF/random/auth tokens.
   source='\n'.join(page.locator('script:not([src])').all_text_contents())
   allowed={x[0] for x in meta['fields']}|{'submit','load','click','change','DOMContentLoaded','Form1','true','false'}
   def hide(m):
    token=m[0]
    return token if token[1:-1] in allowed else '"<literal length='+str(len(token)-2)+'>"'
   sanitized=re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`",hide,source)
   sanitized=re.sub(r'/\*.*?\*/|//[^\n]*','',sanitized,flags=re.S)
   sanitized=re.sub(r'\b(?:\d{8,}|[0-9a-fA-F]{24,})\b','0',sanitized)
   print('Native inline structure (all non-control literals removed): '+json.dumps(sanitized[:16000]),flush=True)

   if draft:
    from blogfa_wire_audit import capture_without_submit
    print('READONLY native wire metadata: '+json.dumps(capture_without_submit(page),ensure_ascii=False),flush=True)
   print('Blogfa hosted login and native CKEditor contract verified; no post submitted.',flush=True)
  finally:
   print('READONLY native session lifecycle: '+json.dumps(trace.report(),ensure_ascii=False),flush=True)
   trace.close();browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('Blogfa diagnostic failed: '+(str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__),file=sys.stderr);sys.exit(1)
