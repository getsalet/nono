#!/usr/bin/env python3
"""Blogsky native form adapter. No schedules, credential artifacts or hidden approvals."""
import os,re
from urllib.parse import urlsplit
PANEL='https://www.blogsky.com'
BLOG='https://afp-pipe.blogsky.com'
NEW=PANEL+'/afp-pipe/post/new'
ARCHIVE=PANEL+'/afp-pipe/post/index'
def public_url(value):
 p=urlsplit(value or '')
 return (p.scheme=='https' and p.netloc=='afp-pipe.blogsky.com' and not p.query and not p.fragment
         and bool(re.fullmatch(r'/(?:\d{4}/\d{2}/\d{2}/post-[1-9]\d*/[^/]+|post/[1-9]\d*/[^/]+/?)',p.path)))
def assert_editor(page):
 if page.url!=NEW or page.locator('#post-form').count()!=1:raise RuntimeError('Expected Blogsky new-post form unavailable')
 if page.locator('a[href="https://afp-pipe.blogsky.com"]').count()+page.locator('a[href="https://afp-pipe.blogsky.com/"]').count()<1:raise RuntimeError('Unexpected Blogsky account/blog')
def login(page):
 user=os.environ.get('BLOGSKY_USERNAME','');password=os.environ.get('BLOGSKY_PASSWORD','')
 if not user or not password:raise RuntimeError('Dedicated Blogsky repository secrets required')
 page.goto(PANEL+'/login',wait_until='domcontentloaded',timeout=60000)
 page.locator('#UserName').fill(user);page.locator('#Password').fill(password)
 remember=page.locator('input[type=checkbox]')
 for i in range(remember.count()):
  box=remember.nth(i)
  if box.is_visible() and re.search('remember|keep|stay',str(box.get_attribute('name')),re.I):box.check()
 page.locator('form:has(#UserName) button[type=submit]').click()
 page.wait_for_timeout(2000)
 if urlsplit(page.url).path=='/login':raise RuntimeError('Native Blogsky authentication rejected; no credential retry')
 page.goto(NEW,wait_until='domcontentloaded',timeout=60000);assert_editor(page)
 page.wait_for_function('()=>window.HTMLArea && document.querySelector("#post-form").onsubmit && document.querySelector(".htmlarea iframe")?.contentDocument?.body',timeout=30000)
 page.evaluate('()=>clearInterval(window.interval)')
def fill(page,post,body):
 assert_editor(page)
 page.evaluate('''()=>{clearInterval(window.interval);const old=HTMLArea.prototype.getHTML;try{HTMLArea.prototype.getHTML=function(){window.afpNativeEditor=this;return this._textArea?.value||''};document.querySelector('#post-form').onsubmit()}finally{HTMLArea.prototype.getHTML=old}if(!window.afpNativeEditor)throw Error('Native editor unavailable')}''')
 page.wait_for_function('()=>window.afpNativeEditor && ((afpNativeEditor._editMode==="wysiwyg" && afpNativeEditor._doc?.body) || (afpNativeEditor._editMode==="textmode" && afpNativeEditor._textArea))',timeout=30000)
 page.locator('#post-title').fill(post['title'])
 page.evaluate('''({body,tags,slug})=>{afpNativeEditor.setHTML(body);document.querySelector('#post-content').value=body;document.querySelector('#post-address').value=slug;$('#post-tag').tokenfield('setTokens',tags);document.querySelector('#Post_CommentStatus').value='2'}''',{'body':body,'tags':post['tags'],'slug':post['slug']})
 return page.evaluate('()=>{const h=afpNativeEditor.getHTML();document.querySelector("#post-content").value=h;return h}')
def public_readback(page):
 if not public_url(page.url):raise RuntimeError('Unrecognized native public URL')
 return page.evaluate('''()=>{const a=document.querySelector('.afp-article-body');return {url:location.href,title:document.querySelector('.post-title')?.textContent.trim(),html:a?.innerHTML,details:a?.querySelectorAll('details').length,summaries:a?.querySelectorAll('summary').length,links:a?[...a.querySelectorAll('a')].map(x=>({url:x.getAttribute('href'),anchor:x.textContent})):[],images:a?[...a.querySelectorAll('img')].map(x=>({src:x.getAttribute('src'),alt:x.alt})):[],layout:!!document.querySelector('#afp-post'),footer:!!document.querySelector('.afp-rich-footer'),mobileCall:!!document.querySelector('.afp-mobile-call[href="tel:+989134922013"]')}}''')
def verify(result,post,links,image_url):
 from content_originality import text
 if not public_url(result.get('url')):raise RuntimeError('Invalid public verification URL')
 if result.get('title')!=post['title'] or text(result.get('html',''))!=text(post['html']):raise RuntimeError('Public article content mismatch')
 if result.get('details')!=3 or result.get('summaries')!=3:raise RuntimeError('Public FAQ mismatch')
 if not all(result.get(k) for k in ('layout','footer','mobileCall')):raise RuntimeError('Public single-post layout missing')
 actual=sorted((x['url'],x['anchor']) for x in result.get('links',[]));expected=sorted((x['url'],x['anchor']) for x in links)
 if actual!=expected:raise RuntimeError('Public contextual backlinks mismatch')
 images=result.get('images',[])
 if image_url:
  if len(images)!=1 or images[0].get('src')!=image_url or not images[0].get('alt'):raise RuntimeError('Public source image mismatch')
 elif images:raise RuntimeError('Unexpected public image')
 return True


def discover_public_post(page,post):
 """Find one exact title+slug in the public archive, never submit or retry POST."""
 page.goto(BLOG+'/posts',wait_until='domcontentloaded',timeout=60000)
 if page.url.rstrip('/')!=BLOG+'/posts':raise RuntimeError('Unexpected public archive URL')
 matches=page.locator('a[href]').evaluate_all('(aa,p)=>aa.filter(a=>a.textContent.trim()===p.title && new URL(a.href).pathname.endsWith("/"+p.slug)).map(a=>a.href)',post)
 urls={url for url in matches if public_url(url)}
 if len(urls)!=1:raise RuntimeError('Published post not uniquely confirmed in public archive; reconcile journal, never resubmit')
 return next(iter(urls))


def form_validation(page):
 """Read only native validity; never submit or expose field values/tokens."""
 return page.evaluate('''()=>{const f=document.querySelector('#post-form');if(!f)return {valid:false,errorFields:['missing-form']};let valid=f.checkValidity(),errorFields=[];if(window.jQuery&&jQuery.fn.valid){valid=jQuery(f).valid()&&valid;errorFields=(jQuery(f).validate().errorList||[]).map(e=>e.element.id)}return {valid,errorFields}}''')

def validate_form(page):
 result=form_validation(page)
 if not result.get('valid'):raise RuntimeError('Native form validation failed before submission intent; no publication')
 return result
