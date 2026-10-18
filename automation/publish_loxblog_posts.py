#!/usr/bin/env python3
"""One native LoxBlog submit per item; uncertainty blocks unattended retries."""
import os,re,sys,time
from urllib.parse import urlsplit,unquote,urlencode,parse_qs
import loxblog_backlink_queue as wrapper
import publish_roya_posts as state
from loxblog_native import login,launch_browser,assert_management,BLOG,NEW,ARCHIVE
from city_backlink_policy import qa,links_for,matrix_ready
from blog_post_excerpt import native_split
from content_originality import text
engine=wrapper.engine
state.QUEUE=engine.QUEUE;state.ART=engine.ART;state.PUBLISH_QUEUE=engine.ART/'publish-queue.json';state.STATE=engine.STATE;state.LOG=engine.ART/'publish-log.jsonl';state.EXPORT=engine.ART/'publish'
HOST='afp.lxb.ir'
BLOCKED={'submitting','unconfirmed','reconciled_absent'}

def public_records(rows):
 found={}
 for r in rows:
  parts=urlsplit(r['url']);match=re.match(r'^/post/(\d+)(?:[/.]|$)',parts.path)
  if parts.scheme!='https' or parts.hostname!=HOST or parts.path.rstrip('/')in ('','/posts','/rss.xml'):continue
  title=r['title'].strip()
  if not title:raise RuntimeError('Empty public post title; incomplete dedup')
  record={'pid':int(match[1])if match else None,'url':r['url']}
  if title in found and found[title]['pid']and record['pid']and found[title]['pid']!=record['pid']:raise RuntimeError('Duplicate public title')
  found[title]=record
 return found

def scan_public(page):
 pending=[BLOG,BLOG+'posts/'];seen=set();found={}
 while pending:
  url=pending.pop(0)
  if url in seen:continue
  if len(seen)>=150:raise RuntimeError('Public archive pagination incomplete')
  seen.add(url);r=page.goto(url,wait_until='domcontentloaded',timeout=60000)
  if not r or r.status>=400 or urlsplit(page.url).hostname!=HOST:raise RuntimeError('Public archive unavailable; refuse partial dedup')
  native_archive=urlsplit(page.url).path.rstrip('/')=='/posts'
  if native_archive:
   # /posts/ is LoxBlog's own archive, not the user's header/footer template.
   homes=page.locator('#content #title a[href]').evaluate_all('es=>es.map(e=>e.href)')
   credits=page.locator('#copyright a[href]').evaluate_all('es=>es.map(e=>e.href)')
   if page.locator('#content #result').count()!=1 or page.locator('#navbar').count()!=1 or not any(urlsplit(x).hostname==HOST for x in homes) or not any((urlsplit(x).hostname or '').lower()in ('loxblog.com','www.loxblog.com')for x in credits):raise RuntimeError('Native public archive fingerprint missing; refuse partial dedup')
   selectors='#result a[href]'
  else:
   if page.locator('.header,.footer').count()<2:raise RuntimeError('Public archive is not the expected native AFP template')
   selectors='article.post-card h2 a[href]' 
  rows=page.locator(selectors).evaluate_all('es=>es.map(e=>({url:e.href,title:e.textContent.trim()}))')
  for title,record in public_records(rows).items():
   if title in found and found[title]['pid']and record['pid']and found[title]['pid']!=record['pid']:raise RuntimeError('Ambiguous public title')
   found[title]=record
  for link in page.locator('#navbar a[href]' if native_archive else '.pagination a[href]').evaluate_all('es=>es.map(e=>e.href)'):
   parts=urlsplit(link)
   if parts.hostname==HOST and not parts.path.startswith('/post/') and link not in seen and link not in pending:pending.append(link)
 return found

def assert_no_native_match(page,title):
 url=ARCHIVE+'&'+urlencode({'search':title,'cat':'0','status':'','sort':'newest'})
 r=page.goto(url,wait_until='domcontentloaded',timeout=60000);assert_management(page)
 if not r or r.status>=400:raise RuntimeError('Native archive unavailable')
 page.locator('input[name=search]').wait_for(timeout=30000)
 if page.locator('input[name=search]').input_value()!=title or page.locator('select[name=status]').input_value()!='':raise RuntimeError('Native all-status search was not applied')
 table=page.locator('table')
 if table.count()!=1 or 'هیچ مطلبی با این مشخصات پیدا نشد' not in table.inner_text():raise RuntimeError('Possible published/draft/sticky match; reconcile before creation')

def find_native_record(page,title):
 # All-status native search also covers posts outside the six-card homepage.
 url=ARCHIVE+'&'+urlencode({'search':title,'cat':'0','status':'','sort':'newest'})
 r=page.goto(url,wait_until='domcontentloaded',timeout=60000);assert_management(page)
 if not r or r.status>=400:raise RuntimeError('Native lookup unavailable')
 page.locator('input[name=search]').wait_for(timeout=30000)
 if page.locator('input[name=search]').input_value()!=title or page.locator('select[name=status]').input_value()!='':raise RuntimeError('Native all-status lookup did not apply')
 table=page.locator('table')
 if table.count()!=1:raise RuntimeError('Native archive layout is ambiguous')
 if 'هیچ مطلبی با این مشخصات پیدا نشد' in table.inner_text():return None
 links=table.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)');edits={}
 for link in links:
  part=urlsplit(link);q=parse_qs(part.query);pid=q.get('editpid',[''])[0]
  if part.hostname=='loxblog.com'and part.path=='/adminnew.php'and q.get('page')==['sendpost']and pid.isdigit():edits[int(pid)]=link
 if len(edits)!=1:raise RuntimeError('Native exact-title match is not unique; manual reconciliation required')
 pid,edit=next(iter(edits.items()));aliases=[x for x in links if urlsplit(x).hostname==HOST and re.fullmatch(r'/post/'+str(pid)+r'/?',urlsplit(x).path)]
 if len(aliases)!=1:raise RuntimeError('Observed native public alias missing')
 page.goto(edit,wait_until='domcontentloaded',timeout=60000);assert_management(page);page.locator('#ptitle').wait_for(timeout=30000)
 if page.locator('#ptitle').input_value()!=title:raise RuntimeError('Native full title differs; refuse ambiguous lookup')
 if page.locator('select[name=status]').input_value()!='1':raise RuntimeError('Existing native draft/hidden post requires reconciliation; no new submit')
 return {'pid':pid,'url':aliases[0]}

def native_image_value(url):
 # Decode only UTF-8 non-ASCII escapes into an equivalent IRI. Keep encoded
 # ASCII delimiters untouched; never shorten through a third-party redirect.
 value=re.sub(r'(?:%[89a-fA-F][0-9a-fA-F])+',lambda m:unquote(m.group(),errors='strict'),url)
 if len(value)>240:raise RuntimeError('Approved image metadata URL exceeds native safe column limit')
 return value

def prepare(page,item):
 post=item['post'];short,more=native_split(post['html'])
 page.locator('#ptitle').wait_for(timeout=30000)
 page.wait_for_function('()=>window.tinymce?.get("editor1")?.initialized && window.tinymce?.get("editor2")?.initialized',timeout=60000)
 page.locator('#ptitle').fill(post['title']);page.locator('#pslug-input').fill(post['slug'])
 page.locator('input[name=pimage]').fill(''if not item.get('image_url')or(item.get('image_source')and len(item['image_url'].removeprefix('https://'))>240)else native_image_value(item['image_url']))
 page.evaluate('tags=>{const e=document.querySelector("#keywords"),t=e.__tagify;if(!t)throw new Error("Native tag control unavailable");t.removeAllTags();t.addTags(tags);}',post.get('tags',[])[:4])
 page.locator('textarea[name=meta_description]').fill(post['meta_description'])
 # Preserve the server-selected current Jalali timestamp instead of erasing it.
 native_date=page.locator('input[name=publish_at]').input_value()
 if not re.fullmatch(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',native_date):raise RuntimeError('Native current publication date unavailable')
 page.locator('input[name=is_pinned]').uncheck()
 result=page.evaluate('''data=>{
 const title=document.querySelector('#ptitle'),form=title.form;form.id=form.id||'afp-native-post';
 for(const [n,v]of Object.entries({status:'1',show_to:'1',comment_status:'0'})){
  const s=document.querySelector('select[name="'+n+'"]');s.setAttribute('form',form.id);s.value=v;s.dispatchEvent(new Event('change',{bubbles:true}));
 }
 for(const [id,body]of [['editor1',data.short],['editor2',data.more]]){
  const editor=tinymce.get(id);editor.setContent(body);editor.save();
 }
 tinymce.triggerSave();const fd=new FormData(form);
 return {title:fd.get('ptitle')===data.title,summary:fd.get('ptext')===data.short,more:fd.get('pextext')===data.more,comments:fd.get('comment_status'),status:fd.get('status'),show:fd.get('show_to'),future:fd.get('publish_at'),faqs:(String(fd.get('pextext')).match(/<details\\b/g)||[]).length};
}''',{'title':post['title'],'short':short,'more':more})
 # TinyMCE may normalize harmless markup; compare approved text and validate actual serialized FAQ.
 actual=page.evaluate('()=>({short:document.querySelector("#editor1").value,more:document.querySelector("#editor2").value})')
 if not(result['title'] and result['comments']=='0' and result['status']=='1' and result['show']=='1' and result['future']==native_date and result['faqs']==3):raise RuntimeError('Native publication controls/FAQ did not serialize correctly')
 if text(actual['short'])!=text(short) or text(actual['more'])!=text(more):raise RuntimeError('Native editor changed approved article text')
 if '<details' not in actual['more']:raise RuntimeError('Native editor removed expandable FAQs')
 print('Native form verified: real summary/continuation, three FAQs, public immediate publication, comments off.',flush=True)
 return short,more

def journal(entry,phase):
 path=engine.ART/'submission-attempts.json';j=engine.load(path,{});old=j.get(entry['key'],{})
 j[entry['key']]={**old,'phase':phase,'at':state.now()};engine.save(path,j)

def begin(entry):
 rows=engine.load(engine.ART/'submission-attempts.json',{})
 if any(r.get('phase')in BLOCKED for r in rows.values()):raise RuntimeError('Prior uncertain native submission blocks new publication; manual reconciliation required')
 journal(entry,'submitting')

def verify(public,item,record):
 url=record['url'];r=public.goto(url,wait_until='domcontentloaded',timeout=60000)
 if not r or r.status>=400 or urlsplit(public.url).hostname!=HOST:raise RuntimeError('Native public article unavailable')
 article=public.locator('article.post-card');body=article.locator('.post-content')
 if article.count()!=1 or article.locator('h1').inner_text().strip()!=item['post']['title']:raise RuntimeError('Published title not unique/exact')
 html=body.inner_html()
 if text(html)!=text(item['post']['html']):raise RuntimeError('Published full article differs from approved content')
 if body.locator('details').count()!=3:raise RuntimeError('Three native FAQs did not persist')
 hrefs={unquote(x).rstrip('/')for x in body.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)')}
 if any(unquote(x['url']).rstrip('/')not in hrefs for x in links_for(item)):raise RuntimeError('Approved contextual links did not persist')
 if body.locator('img').evaluate_all('es=>es.map(e=>e.src)')!=([item['image_url']]if item.get('image_url')else []):raise RuntimeError('Approved native image missing/duplicated or unexpected image')
 if item.get('image_source')or not item.get('image_url'):
  from blog_public_content_verify import verify_article_body as verify_text_body
  verify_text_body(item,html,links_for(item))
 if public.locator('form[action*=comment],.comment-form').count():raise RuntimeError('Public comment form still present')
 public.goto(BLOG,wait_until='domcontentloaded',timeout=60000)
 card=public.locator('article.post-card').filter(has=public.get_by_text(item['post']['title'],exact=True))
 if card.count():
  short,_=native_split(item['post']['html']);excerpt=card.locator('.post-content')
  if text(excerpt.inner_html())!=text(short):raise RuntimeError('Homepage did not render real native summary')
  if excerpt.locator('details,ul,ol').count() or len(text(excerpt.inner_html()).split())>=250:raise RuntimeError('Full article leaked into listing')
  if card.locator('a.readmore').count()!=1:raise RuntimeError('Native read-more link missing')
 return url

def main():
 from blog_image_runtime_control import publication_paused
 if publication_paused(engine.ROOT):
  print('Publication intentionally paused by user control; no queue mutation, QA API, export, login or submission.');return 0
 if not matrix_ready():raise RuntimeError('Independent title policy unavailable')
 todo=state.load(state.PUBLISH_QUEUE,{'items':[]})['items'];target=os.getenv('LOXBLOG_TARGET','')
 if target:todo=[x for x in todo if x['key']==target]
 limit=min(3,int(os.getenv('LOXBLOG_PUBLISH_LIMIT','3')),engine.remaining_publication_budget())
 if os.getenv('LOXBLOG_PUBLISH','0')!='1':
  for e in todo[:limit]:state.export_post(state.load(state.resolve_item(e),{}))
  print('LoxBlog export only; no publication.');return 0
 if not todo or not limit:print('LoxBlog idle: ready queue and rolling budget checked.');return 0
 approved=[]
 for e in todo[:limit]:
  item=state.load(state.resolve_item(e),{})
  from blog_image_gate import review
  from blog_editorial_image_policy import validate_image
  if validate_image(item,item.get('post',{}),'loxblog',engine.ROOT):
   from blog_source_image import review_for_publication
   engine.retry_transient(lambda:review_for_publication(item,'loxblog',engine.ROOT))
  errors,_=qa(item,item['post'],links_for(item),'loxblog')
  if errors or not item.get('qa',{}).get('passed'):raise RuntimeError('Native LoxBlog quality gate rejected article')
  approved.append((e,item))
 from playwright.sync_api import sync_playwright
 with sync_playwright()as pw:
  browser=launch_browser(pw);page=browser.new_page();public=browser.new_page();page.on('dialog',lambda d:d.accept())
  try:
   login(page);existing=scan_public(public)
   for e,item in approved:
    title=item['post']['title'];record=existing.get(title);native=find_native_record(page,title);recovered=bool(native)
    if native:
     if record and record['pid']and record['pid']!=native['pid']:raise RuntimeError('Native/public post IDs disagree')
     record={**native,'url':record['url']if record else native['url']}
    elif record:raise RuntimeError('Public title exists without a unique native match; no new submit')
    else:
     page.goto(NEW,wait_until='domcontentloaded',timeout=60000);assert_management(page);prepare(page,item)
     button=page.get_by_role('button',name='ارسال مطلب',exact=True)
     if button.count()!=1:raise RuntimeError('Native submit control not unique')
     begin(e)
     # One click only. A timeout or rejection leaves the durable uncertainty hold.
     try:
      with page.expect_navigation(wait_until='domcontentloaded',timeout=60000)as result:button.click()
      print('Native LoxBlog response status: '+str(result.value.status if result.value else None),flush=True)
     finally:journal(e,'unconfirmed')
     # Read only visible native validation feedback; never request payloads or tokens.
     feedback=page.locator('.alert-danger,.alert-warning,.invalid-feedback-custom').all_inner_texts()
     feedback=' | '.join(x.strip()for x in feedback if x.strip())[:600]
     # Some native database errors are unstyled and return HTTP 200.
     # Store only a category; never log the page's account details or stack trace.
     visible=page.locator('body').inner_text()
     if 'Data too long for column' in visible:feedback='Native database rejected an oversized field'
     elif 'Fatal error:' in visible:feedback='Native server fatal error'
     elif page.locator('#loginForm').count():feedback='Native session lost after submission'
     for attempt in range(12):
      existing=scan_public(public);record=existing.get(title)
      if record:break
      time.sleep(5)
     if not record:raise RuntimeError('Single native submission not confirmed; no resubmission'+('; native feedback: '+feedback if feedback else ''))
    native=find_native_record(page,title)
    if not native:raise RuntimeError('Public post lacks a unique native checkpoint identity')
    if record.get('pid')and record['pid']!=native['pid']:raise RuntimeError('Native/public identity mismatch')
    record['pid']=native['pid']
    url=verify(public,item,record)
    row={'key':e['key'],'title':title,'pid':record['pid'],'url':url,'at':state.now(),'verified':True,'recovered_existing':recovered}
    state.checkpoint(e,item,row);journal(e,'verified');existing[title]=record
    print('Verified LoxBlog publication '+str(record['pid'])+' -> '+url,flush=True)
  finally:browser.close()
 return 0
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('LoxBlog publisher stopped: '+str(exc),file=sys.stderr);sys.exit(1)
