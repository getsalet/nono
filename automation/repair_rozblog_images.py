#!/usr/bin/env python3
"""Replace images of explicitly selected existing native posts; never create posts."""
import copy,hashlib,html,json,re,subprocess,time
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,unquote
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'artifacts/rozblog-image-repair'
def replace_image(body,old,new):
 matches=list(re.finditer(r'<img\b[^>]*>',body,re.I))
 if len(matches)!=1:raise RuntimeError('Exactly one old body image required')
 tag=matches[0];src=re.search(r'\bsrc\s*=\s*(["\'])(.*?)\1',tag[0],re.I|re.S)
 if not src or unquote(html.unescape(src[2]))!=unquote(old):raise RuntimeError('Native image does not match approved repair selection')
 newtag=tag[0][:src.start(2)]+html.escape(new,quote=True)+tag[0][src.end(2):]
 return body[:tag.start()]+newtag+body[tag.end():]
def invariant(body):
 from content_originality import text
 links=re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']',body,re.I)
 return {'text_sha256':hashlib.sha256(text(body).encode()).hexdigest(),'links':[unquote(html.unescape(u)).rstrip('/')for u in links],'images':len(re.findall(r'<img\b',body,re.I))}
def persist():
 paths=['artifacts/rozblog-image-repair','data/rozblog/backlink-queue.json','artifacts/rozblog-backlink-queue/items','artifacts/blog-image-reviews']
 for p in paths:
  if (ROOT/p).exists():subprocess.run(['git','add','-f',p],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==0:return
 subprocess.run(['git','-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Checkpoint existing RozBlog image-only repair; preserve post identity'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 for attempt in range(3):
  subprocess.run(['git','pull','--rebase','origin','main'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  if subprocess.run(['git','push','origin','main'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:return
  time.sleep(3)
 raise RuntimeError('Image repair checkpoint not pushed; no blind resubmission')
def find_edit(page,posts,pid):
 from inspect_rozblog_image_editor import observed_edit_url
 pending=[posts];seen=set()
 while pending:
  url=pending.pop(0)
  if url in seen:continue
  seen.add(url);page.goto(url,wait_until='domcontentloaded',timeout=60000);row=page.locator('#tr_'+str(pid))
  if row.count():
   links=row.locator('a[href]').evaluate_all("a=>a.map(x=>({href:x.href,label:(x.innerText+' '+(x.title||'')).trim()}))")
   return observed_edit_url(links,posts,pid)
  for link in page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href)'):
   if link.startswith(posts+'?')and re.search(r'[?&](page|p)=\d+',link)and link not in seen:pending.append(link)
  if len(seen)>100:break
 raise RuntimeError('Observed existing native edit route not found')
def public_content(page,url,title):
 response=page.goto(url,wait_until='domcontentloaded',timeout=60000)
 if not response or response.status>=400 or urlsplit(page.url).hostname!='afp-pipe.rozblog.com':raise RuntimeError('Existing public article inaccessible')
 article=page.locator('article.post-card').filter(has=page.get_by_text(title,exact=True))
 if article.count()!=1:raise RuntimeError('Public article title is not unique')
 return article.locator('.post-content').inner_html()
def main():
 import publish_rozblog_posts as native
 from blog_generated_image import prepare
 from blog_image_gate import validate_record,generated_record_errors
 from playwright.sync_api import sync_playwright
 plan=json.loads((ROOT/'data/rozblog-image-repair-plan.json').read_text())
 if plan.get('mode')!='repair':print('Repair disabled: inspection mode, no native writes');return 0
 ART.mkdir(parents=True,exist_ok=True);journal_path=ART/'repair-journal.json';journal=json.loads(journal_path.read_text())if journal_path.exists()else{}
 queue=json.loads((ROOT/'data/rozblog/backlink-queue.json').read_text());rows={r['key']:r for r in queue['items']};limit=max(1,min(6,int(plan.get('limit',1))));done=0
 def savejournal():journal_path.write_text(json.dumps(journal,ensure_ascii=False,indent=2))
 with sync_playwright()as pw:
  browser=pw.chromium.launch(args=['--no-sandbox']);context=browser.new_context(locale='fa-IR');page=context.new_page();public=context.new_page()
  try:
   posts,_=native.login(page);existing=native.scan(page,posts)
   for selected in plan['items']:
    key=selected['key'];pid=selected['pid'];title=selected['title'];old_url=selected['old_image_url'];phase=journal.get(key,{}).get('phase')
    if phase=='verified':continue
    if phase in('submitting','unconfirmed'):raise RuntimeError('Uncertain existing-post edit requires read-only reconciliation before another write')
    if done>=limit:break
    row=rows[key]
    if not row.get('published')or existing.get(title,{}).get('pid')!=pid or unquote(existing[title]['url']).rstrip('/')!=unquote(selected['url']).rstrip('/'):raise RuntimeError('Existing native post identity does not match explicit repair selection')
    safe=re.sub(r'[^A-Za-z0-9._-]+','_',key);item_path=ROOT/'artifacts/rozblog-backlink-queue/items'/(safe+'.json');item=json.loads(item_path.read_text());before_live=public_content(public,selected['url'],title)
    edit=find_edit(page,posts,pid);page.goto(edit,wait_until='domcontentloaded',timeout=60000);page.wait_for_selector('#mtitle')
    if parse_qs(urlsplit(page.url).query).get('id')!=[str(pid)]or page.locator('#mtitle').input_value()!=title:raise RuntimeError('Edit route/title mismatch; never use a new-post form')
    page.wait_for_function('()=>window.tinymce&&typeof tinymce.get==="function"&&["mtex","mtex2"].every(id=>tinymce.get(id)?.initialized)',timeout=60000)
    bodies=page.evaluate('()=>({mtex:tinymce.get("mtex").getContent(),mtex2:tinymce.get("mtex2").getContent()})')
    combined=bodies['mtex']+bodies['mtex2'];before=invariant(combined)
    if before['images']!=1:raise RuntimeError('Existing body must contain exactly one replaceable image')
    (ART/(safe+'-before.json')).write_text(json.dumps({'pid':pid,'url':selected['url'],'title':title,'bodies':bodies,'invariant':before,'live_invariant':invariant(before_live)},ensure_ascii=False,indent=2))
    candidate=copy.deepcopy(item);candidate['key']=key;new_url=prepare(candidate,'rozblog')
    if validate_record(candidate)or generated_record_errors(candidate,'rozblog'):raise RuntimeError('New per-article watermarked image failed QA')
    target='mtex'if re.search(r'<img\b',bodies['mtex'],re.I)else'mtex2';updated=dict(bodies);updated[target]=replace_image(bodies[target],old_url,new_url)
    if invariant(updated['mtex']+updated['mtex2'])!=before:raise RuntimeError('Image-only transform changed text, link destinations or image count')
    result=page.evaluate('''b=>{for(const id of ["mtex","mtex2"]){tinymce.get(id).setContent(b[id]);tinymce.get(id).save()}return {mtex:tinymce.get("mtex").getContent(),mtex2:tinymce.get("mtex2").getContent()}}''',updated)
    if invariant(result['mtex']+result['mtex2'])!=before:raise RuntimeError('Native editor serialization changed content; no write')
    journal[key]={'pid':pid,'url':selected['url'],'old_image_url':old_url,'new_image_url':new_url,'phase':'submitting','before':before,'post_creations':0};savejournal();persist()
    button=page.get_by_role('button',name='ارسال مطلب و بازسازی سایت',exact=False)
    if button.count()!=1:raise RuntimeError('Unique observed native edit-save button required')
    with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):button.click()
    journal[key]['phase']='unconfirmed';savejournal()
    # Read-only confirmation only: never issue a second POST after uncertainty.
    confirmed=None
    for attempt in range(3):
     try:
      after_live=public_content(public,selected['url'],title)
      if new_url in html.unescape(after_live)and invariant(after_live)==invariant(before_live):confirmed=after_live;break
     except Exception:
      if attempt==2:raise
     time.sleep(4)
    if confirmed is None:raise RuntimeError('Image edit unconfirmed; stop and reconcile without resubmitting')
    rescanned=native.scan(page,posts)
    if rescanned.get(title,{}).get('pid')!=pid:raise RuntimeError('Native post ID changed after image edit')
    for field in ('image_url','image_width','image_height','image_review','image_generation','image_selection','image_alt'):
     if field in candidate:item[field]=candidate[field];row[field]=candidate[field]
    item['post']['html']=replace_image(item['post']['html'],old_url,new_url);item['post']['image_url']=new_url
    item_path.write_text(json.dumps(item,ensure_ascii=False,indent=2));(ROOT/'data/rozblog/backlink-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2))
    journal[key].update(phase='verified',text_and_links_unchanged=True,post_id_unchanged=True,phone='09134922013');savejournal();persist();done+=1
    print('Verified image-only replacement of existing RozBlog pid='+str(pid),flush=True)
  finally:
   savejournal();persist();browser.close()
 return 0
if __name__=='__main__':raise SystemExit(main())
