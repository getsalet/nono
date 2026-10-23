"""One explicitly selected existing-post correction; no generation or post creation."""
import copy, datetime as dt, hashlib, html, json, re, subprocess, time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'data/rozblog-editorial-repair-plan.json'
ART=ROOT/'artifacts/rozblog-editorial-repair'

def digest(body):
 from content_originality import text
 return hashlib.sha256(text(body).encode()).hexdigest()

def structure(body):
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(body,'html.parser')
 return {'links':[(unquote(a.get('href','')).rstrip('/'),a.get_text())for a in soup.select('a[href]')],
         'images':[(unquote(x.get('src','')),x.get('alt',''))for x in soup.select('img')],
         'faqs':len(soup.select('details')),'summaries':len(soup.select('details > summary'))}

def corrected(bodies,plan):
 if plan.get('policy')!='same-post-exact-editorial-repair-v1' or plan.get('post_creations_allowed')!=0:raise RuntimeError('Explicit no-creation policy required')
 if set(bodies)!={'mtex','mtex2'}:raise RuntimeError('Both native editors required')
 result=dict(bodies)
 for row in plan['replacements']:
  old,new=row['old'],row['new']
  if not old or not new or any(c in new for c in '<>'):raise RuntimeError('Plain-text replacement required')
  if sum(v.count(old)for v in result.values())!=1:raise RuntimeError('Expected source text must occur exactly once; no partial edit')
  result={k:v.replace(old,new,1)for k,v in result.items()}
 combined=''.join(result.values())
 if structure(combined)!=structure(''.join(bodies.values())):raise RuntimeError('Links, image or FAQs changed')
 if re.search(r'[\u0400-\u052f\u3400-\u9fff]',html.unescape(combined)):raise RuntimeError('Foreign-script corruption remains')
 from bs4 import BeautifulSoup
 words=len(BeautifulSoup(combined,'html.parser').get_text(' ',strip=True).split())
 if not 500<=words<=1000:raise RuntimeError('Corrected article outside existing length contract')
 return result

def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def checkpoint(paths):
 for p in paths:
  if (ROOT/p).exists():subprocess.run(['git','add','-f',p],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==0:return
 subprocess.run(['git','-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Checkpoint same-post RozBlog editorial repair [skip ci]'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 for attempt in range(3):
  subprocess.run(['git','pull','--rebase','origin','main'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  if subprocess.run(['git','push','origin','HEAD:main'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:return
  time.sleep(3)
 raise RuntimeError('Checkpoint not pushed; no blind edit retry')

def verify_body(actual,expected):
 if digest(actual)!=digest(expected) or structure(actual)!=structure(expected):raise RuntimeError('Existing article text, links, image or FAQs differ')

def main():
 from check_blog_pipeline_control import decision
 if not decision('rozblog')['proceed']:raise RuntimeError('Existing user stop blocks repair')
 import publish_rozblog_posts as native
 from repair_rozblog_images import find_edit,public_content
 from playwright.sync_api import sync_playwright
 plan=json.loads(PLAN.read_text());key=plan['key'];pid=plan['pid'];title=plan['title'];url=plan['url']
 if key!='city-af176e874da31363' or pid!=187 or urlsplit(url).hostname!='afp-pipe.rozblog.com':raise RuntimeError('Unapproved repair target')
 ART.mkdir(parents=True,exist_ok=True);journal_path=ART/'journal.json'
 journal=json.loads(journal_path.read_text())if journal_path.exists()else{}
 paths=['artifacts/rozblog-editorial-repair']
 with sync_playwright()as pw:
  browser=pw.chromium.launch(args=['--no-sandbox']);context=browser.new_context(locale='fa-IR');page=context.new_page();public=context.new_page()
  try:
   # Verify the saved item and live article before opening any editor.
   item_path=ROOT/'artifacts/rozblog-backlink-queue/items'/(key+'.json');item=json.loads(item_path.read_text())
   if item['post']['title']!=title:raise RuntimeError('Saved title mismatch')
   source_backup=ART/'backup.json'
   original=json.loads(source_backup.read_text())['post']['html']if source_backup.exists()else item['post']['html']
   expected=corrected({'mtex':original,'mtex2':''},plan)
   expected_html=''.join(expected.values());live=public_content(public,url,title)
   # A persisted submission journal permits read-only reconciliation, never another POST.
   pending=journal.get('phase')in('submitting','unconfirmed','verified')
   if pending and (journal.get('expected_sha256')!=digest(expected_html) or journal.get('pid')!=pid):raise RuntimeError('Pending journal/plan mismatch; no write')
   if not pending:verify_body(live,item['post']['html'])
   posts,_=native.login(page);existing=native.scan(page,posts);record=existing.get(title,{})
   if record.get('pid')!=pid or unquote(record.get('url','')).rstrip('/')!=unquote(url).rstrip('/'):raise RuntimeError('Native post identity mismatch')
   edit=find_edit(page,posts,pid);page.goto(edit,wait_until='domcontentloaded',timeout=60000)
   if parse_qs(urlsplit(page.url).query).get('id')!=[str(pid)]:raise RuntimeError('Observed same-post edit route required')
   page.wait_for_selector('#mtitle',timeout=30000)
   if page.locator('#mtitle').input_value()!=title:raise RuntimeError('Native title mismatch')
   page.wait_for_function('()=>window.tinymce&&["mtex","mtex2"].every(id=>tinymce.get(id)?.initialized)',timeout=60000)
   read_editors=lambda:page.evaluate('()=>({mtex:tinymce.get("mtex").getContent(),mtex2:tinymce.get("mtex2").getContent()})')
   before=read_editors()
   if not pending:
    verify_body(''.join(before.values()),item['post']['html'])
    # The provider serializes punctuation/entities differently. The complete
    # native text and link/image/FAQ structure were verified against the saved
    # original above. Use the already-reviewed corrected source, not fuzzy edits.
    if digest(before['mtex2'])!=digest('') or structure(before['mtex2'])!=structure(''):raise RuntimeError('Unexpected nonempty continuation; no editor repartition allowed')
    after={'mtex':expected_html,'mtex2':before['mtex2']}
    verify_body(''.join(after.values()),expected_html)
    save(ART/'backup.json',{'pid':pid,'title':title,'url':url,'bodies':before,'post':item['post']})
    save(ART/'candidate.json',{'pid':pid,'title':title,'url':url,'bodies':after,'expected_sha256':digest(expected_html)})
    # Set only the two existing text editors; leave title/slug/status/category/date untouched.
    page.evaluate('b=>{for(const id of ["mtex","mtex2"]){tinymce.get(id).setContent(b[id]);tinymce.get(id).save()}}',after)
    verify_body(''.join(read_editors().values()),expected_html)
    button=page.get_by_role('button',name='ارسال مطلب و بازسازی سایت',exact=False)
    if button.count()!=1:raise RuntimeError('Unique observed native edit-save required')
    journal={'key':key,'pid':pid,'url':url,'title':title,'phase':'submitting','post_creations':0,'before_sha256':digest(''.join(before.values())),'expected_sha256':digest(expected_html),'at':dt.datetime.now(dt.timezone.utc).isoformat()}
    save(journal_path,journal);checkpoint(paths) # persist uncertainty BEFORE the single native edit
    try:
     with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):button.click()
    finally:
     journal['phase']='unconfirmed';save(journal_path,journal)
   # No POST is ever retried. Reload the existing form to prove persistence.
   page.goto(edit,wait_until='domcontentloaded',timeout=60000)
   page.wait_for_function('()=>window.tinymce&&["mtex","mtex2"].every(id=>tinymce.get(id)?.initialized)',timeout=60000)
   if page.locator('#mtitle').input_value()!=title:raise RuntimeError('Title changed after save')
   verify_body(''.join(read_editors().values()),expected_html)
   confirmed=False
   for attempt in range(3):
    try:verify_body(public_content(public,url,title),expected_html);confirmed=True;break
    except Exception:
     if attempt==2:raise
     time.sleep(5)
   if not confirmed:raise RuntimeError('Public text unconfirmed; retain journal, do not resubmit')
   if native.scan(page,posts).get(title,{}).get('pid')!=pid:raise RuntimeError('Post ID changed')
   # Persist corrected saved body only after the independent remote checks.
   item['post']['html']=expected_html
   item['editorial_correction']={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'same_post_id':pid,'plan_policy':plan['policy'],'native_reopen_verified':True,'public_body_verified':True,'post_creations':0}
   save(item_path,item);paths.append(str(item_path.relative_to(ROOT)))
   journal.update(phase='verified',verified_at=dt.datetime.now(dt.timezone.utc).isoformat(),native_reopen_verified=True,public_body_verified=True,links_image_faqs_preserved=True)
   save(journal_path,journal);checkpoint(paths)
   print('Verified existing RozBlog post 187 corrected; no post created.')
  finally:
   if journal:save(journal_path,journal)
   checkpoint(paths);browser.close()
if __name__=='__main__':main()
