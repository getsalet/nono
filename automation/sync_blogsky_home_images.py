#!/usr/bin/env python3
"""Refresh only homepage card-cover CSS from the actual latest public articles.
No article generation/submission, invented imagery, settings changes, or client JS.
The existing server-rendered recent widget remains the source of titles/links.
"""
import hashlib,json,re,sys,os
from pathlib import Path
from urllib.parse import urlsplit,urljoin,quote
ROOT=Path(__file__).resolve().parents[1]
BLOG='https://afp-pipe.blogsky.com'
EDIT='https://www.blogsky.com/afp-pipe/page/edit/8352807900'
RECENT='.sidebar>.menu:has(>.head>a[href="/posts"])>ul'
START='/* AFP_LIVE_CARD_IMAGES_START */'
END='/* AFP_LIVE_CARD_IMAGES_END */'
FOLDER='artifacts/blogsky-backlink-queue/home-card-images'

def valid_image(url):
 p=urlsplit(url or '')
 return p.scheme=='https' and p.netloc=='navar-abyari.ir' and p.path.startswith('/wp-content/uploads/') and not p.query and not p.fragment

def cover_css(rows):
 from blogsky_native import public_url
 lines=[START]
 seen=set()
 for row in rows:
  if not public_url(row.get('url')) or not valid_image(row.get('image')) or row['url'] in seen:raise RuntimeError('Invalid or duplicate exact article image mapping')
  seen.add(row['url']);path=quote(urlsplit(row['url']).path,safe='/%-._~');image=quote(row['image'],safe=':/%-._~')
  lines.append('body:has(#afp-home) '+RECENT+'>li>a[href="'+path+'"]::before{background-image:url("'+image+'");background-size:cover;background-position:center}')
 lines.append(END)
 if not rows:raise RuntimeError('No verified article images available; homepage unchanged')
 return '\n'.join(lines)

def without_mapping(body):
 if START not in body and END not in body:return body
 if body.count(START)!=1 or body.count(END)!=1:raise RuntimeError('Ambiguous homepage image mapping boundary')
 return re.sub(re.escape(START)+r'.*?'+re.escape(END),'',body,flags=re.S)

def preserved_body(body):
 # HTMLArea wraps style text in CDATA comments on each serialize round-trip.
 # Ignore only these editor-added CSS no-ops; keep all other HTML/text exact.
 def normalize(match):
  content=without_mapping(match.group(2))
  content=re.sub(r'/\*<!\[CDATA\[\*/\s*|\s*/\*\]\]>\*/','',content)
  return match.group(1)+content.strip()+match.group(3)
 return re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',normalize,body,flags=re.S|re.I)

def patch_body(body,css):
 if len(re.findall(r'<div\b[^>]*\bid=["\']afp-home["\']',body,re.I))!=1:raise RuntimeError('Expected homepage root unavailable')
 style=re.search(r'(<style\b[^>]*\bid=["\']afp-page-style["\'][^>]*>)(.*?)(</style>)',body,re.S|re.I)
 if not style:raise RuntimeError('Expected homepage stylesheet unavailable')
 old=style.group(2)
 if START in old:
  without_mapping(old)
  new=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:css,old,flags=re.S)
 else:new=old+css
 return body[:style.start(2)]+new+body[style.end(2):]

def collect(context):
 from blogsky_native import public_url
 page=context.new_page();rows=[]
 try:
  page.goto(BLOG+'/',wait_until='domcontentloaded',timeout=60000)
  if page.url.rstrip('/')!=BLOG or page.locator('#afp-home').count()!=1:raise RuntimeError('Unexpected public homepage')
  anchors=page.locator(RECENT+'>li>a[href]').evaluate_all('(aa)=>aa.slice(0,6).map(a=>({url:a.href,title:a.textContent.trim()}))')
  if not anchors or len({a['url'] for a in anchors})!=len(anchors):raise RuntimeError('Native recent-post widget missing or duplicated')
  for anchor in anchors:
   if not public_url(anchor['url']):raise RuntimeError('Unexpected recent article URL')
   page.goto(anchor['url'],wait_until='domcontentloaded',timeout=60000)
   data=page.evaluate('''()=>({url:location.href,title:document.querySelector('.post-title')?.textContent.trim(),images:[...document.querySelectorAll('.afp-article-body img')].map(i=>({src:i.src,alt:i.alt}))})''')
   if data['url']!=anchor['url'] or data['title']!=anchor['title'] or len(data['images'])!=1 or not valid_image(data['images'][0]['src']):raise RuntimeError('Actual public article source image not uniquely verified')
   image=data['images'][0]['src']
   loaded=page.evaluate('''src=>new Promise(resolve=>{const im=new Image();let done=false;const end=v=>{if(!done){done=true;resolve(v)}};im.onload=()=>end(im.naturalWidth>32&&im.naturalHeight>32);im.onerror=()=>end(false);im.src=src;setTimeout(()=>end(false),20000)})''',image)
   if not loaded:raise RuntimeError('Article source image could not be decoded; no placeholder substituted')
   rows.append({'url':anchor['url'],'title':anchor['title'],'image':image,'alt':data['images'][0]['alt']})
 finally:page.close()
 return rows

def verify_live(context,rows,root=ROOT):
 page=context.new_page()
 try:
  for width,label in [(1440,'desktop'),(390,'mobile')]:
   page.set_viewport_size({'width':width,'height':1000});page.goto(BLOG+'/',wait_until='networkidle',timeout=60000)
   observed=page.locator(RECENT+'>li>a[href]').evaluate_all('''aa=>aa.slice(0,6).map(a=>({url:a.href,image:getComputedStyle(a,'::before').backgroundImage,backgroundSize:getComputedStyle(a,'::before').backgroundSize}))''')
   by_url={a['url']:a for a in observed}
   for row in rows:
    if row['url'] not in by_url or row['image'] not in by_url[row['url']]['image'] or by_url[row['url']]['backgroundSize']!='cover':raise RuntimeError('Live card image CSS not confirmed')
   if page.evaluate('()=>document.documentElement.scrollWidth>innerWidth+1'):raise RuntimeError('Homepage horizontal overflow after card image sync')
   page.locator(RECENT).screenshot(path=str(root/FOLDER/(label+'.png')),timeout=60000)
 finally:page.close()

def sync(context,root=ROOT):
 from publish_blogsky_posts import gate,save,now
 import blogsky_native as native
 gate(root);report={'phase':'checking','updated_at':now(),'run_id':os.getenv('GITHUB_RUN_ID','local'),'article_submissions':0,'page_save_attempts':0}
 folder=root/FOLDER;folder.mkdir(parents=True,exist_ok=True)
 try:
  rows=collect(context);css=cover_css(rows);report.update(cards=rows,css_sha256=hashlib.sha256(css.encode()).hexdigest(),phase='editing_existing_homepage')
  page=context.new_page()
  try:
   native.login(page);page.goto(EDIT,wait_until='domcontentloaded',timeout=60000)
   if page.url!=EDIT or page.locator('#page-form').count()!=1 or page.locator('#post-address').input_value()!='afp-home':raise RuntimeError('Exact existing homepage editor unavailable')
   page.wait_for_function('()=>window.HTMLArea && document.querySelector("#page-form").onsubmit',timeout=30000)
   page.evaluate('''()=>{clearInterval(window.interval);const old=HTMLArea.prototype.getHTML;try{HTMLArea.prototype.getHTML=function(){window.afpHomeEditor=this;return this._textArea?.value||''};document.querySelector('#page-form').onsubmit()}finally{HTMLArea.prototype.getHTML=old}}''')
   page.wait_for_function('()=>window.afpHomeEditor && afpHomeEditor._doc?.body',timeout=30000)
   before=page.evaluate('()=>afpHomeEditor.getHTML()');after=patch_body(before,css)
   (folder/'before.html').write_text(before)
   if before!=after:
    serialized=page.evaluate('''body=>{afpHomeEditor.setHTML(body);const html=afpHomeEditor.getHTML();document.querySelector('#post-content').value=html;return html}''',after)
    (folder/'candidate.html').write_text(serialized)
    if preserved_body(serialized)!=preserved_body(before):raise RuntimeError('Homepage changed outside card image mapping; save refused')
    valid=page.evaluate('''()=>{const f=document.querySelector('#page-form');return f.checkValidity()&&(!window.jQuery||!jQuery.fn.valid||jQuery(f).valid())}''')
    if not valid:raise RuntimeError('Homepage form invalid; no save attempted')
    gate(root);report['page_save_attempts']=1;save(folder/'status.json',report)
    page.locator('#publish').click();page.wait_for_timeout(2000)
   report['phase']='verifying_public_homepage'
  finally:page.close()
  verify_live(context,rows,root)
  template=root/'templates/blogsky/afp-home.html';template.write_text(patch_body(template.read_text(),css))
  report.update(phase='verified',verified_at=now(),count=len(rows));save(folder/'status.json',report)
  print('Verified public homepage article-image cards: '+str(len(rows))+'; article submissions: 0')
  return report
 except Exception as exc:
  report.update(phase='failed',error_type=type(exc).__name__,error_category=str(exc) if type(exc) is RuntimeError else 'Native browser operation failed; no article retry')
  save(folder/'status.json',report);raise RuntimeError(report['error_category']) from None

def main():
 from publish_blogsky_posts import gate
 gate(ROOT)
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  try:sync(browser.new_context())
  finally:browser.close()
if __name__=='__main__':
 try:main()
 except Exception as exc:print('Homepage image sync stopped: '+(str(exc) if type(exc) is RuntimeError else type(exc).__name__),file=sys.stderr);raise SystemExit(1)
