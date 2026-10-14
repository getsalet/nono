"""Read-only native form wire comparison: intercepted publication is never sent."""
import hashlib,json,re
from urllib.parse import urlsplit,parse_qs
APP_FIELDS=('hasextended','ismobile','txtPostTitle','txtPostContent','txtPostExtended','btnPublish','txtTags','cmbCommentType','chkDraft','chkSticky','chkAutomateTime')
def url_shape(url):
 p=urlsplit(url);q=parse_qs(p.query,keep_blank_values=True)
 return {'origin':p.scheme+'://'+p.netloc if p.netloc else '', 'path':p.path,'query':{k:[{'length':len(x),'ascii_digits':bool(re.fullmatch(r'[0-9]+',x))}for x in v]for k,v in q.items()}}
def cookie_names(raw):return [x.partition('=')[0].strip()for x in raw.split(';')if x.strip()]
def app_fingerprint(fields):
 x={k:fields[k]for k in APP_FIELDS if k in fields}
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def capture_without_submit(page):
 expected=page.locator('#btnPublish').evaluate('e=>e.form.action')
 cookies=[{k:c[k]for k in ('name','domain','path','secure','httpOnly','sameSite')}for c in page.context.cookies() if c['domain'].lstrip('.')in ('www.blogfa.com','blogfa.com')]
 cookie_values={c['name']:c['value']for c in page.context.cookies('https://www.blogfa.com/')}
 query=parse_qs(urlsplit(expected).query)
 relations={'ten_matches_form_t':cookie_values.get('ten')==query.get('t',[None])[0],'ten_length':len(cookie_values.get('ten','')),'ph_length':len(cookie_values.get('ph','')),'window_name_length':page.evaluate('window.name.length'),'character_set':page.evaluate('document.characterSet'),'accept_charset':page.locator('#btnPublish').evaluate('e=>e.form.acceptCharset'),'browser_clock_delta_seconds':round(page.evaluate('Date.now()')/1000-__import__('time').time(),1)}
 result=[]
 def block(route):
  req=route.request
  if req.method=='POST'and urlsplit(req.url).hostname=='www.blogfa.com'and urlsplit(req.url).path.lower()=='/desktop/post.aspx':
   h=req.all_headers();fields=parse_qs(req.post_data or '',keep_blank_values=True)
   result.append({'sent_to_server':False,'session_relations':relations,'method':req.method,'url':url_shape(req.url),'request_url_equals_form_action':req.url==expected,'origin':h.get('origin'),'referer':url_shape(h.get('referer','')),'content_type':h.get('content-type'),'accept_language':h.get('accept-language'),'user_agent':h.get('user-agent'),'sec_fetch_site':h.get('sec-fetch-site'),'cookie_names':cookie_names(h.get('cookie','')),'browser_cookie_metadata':cookies,'field_lengths':{k:[len(x)for x in v]for k,v in fields.items()},'application_fingerprint':app_fingerprint(fields),'body_bytes':len(req.post_data_buffer or b'')})
   route.abort('aborted');return
  if req.method=='POST':route.abort('aborted');return
  route.continue_()
 page.route('**/*',block)
 try:
  try:page.locator('#btnPublish').click(no_wait_after=True,timeout=15000)
  except Exception:
   if not result:raise RuntimeError('Read-only interception did not capture a native form')from None
  page.wait_for_timeout(500)
  if len(result)!=1:raise RuntimeError('Expected exactly one intercepted native form')
  return result[0]
 finally:page.unroute('**/*',block)
