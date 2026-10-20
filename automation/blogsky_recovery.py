"""Explicit, single-use recovery after fresh authenticated and public absence checks.
Normal automatic admission never ignores an unresolved journal. No deletion, no
implicit retry: only the exact prior intent authorized in the control may pass.
"""
import datetime,hashlib,json,os
from dataclasses import dataclass

def fingerprint(value):
 return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@dataclass(frozen=True)
class AbsencePermit:
 key:str
 prior_digest:str
 run_id:str
 checked_at:str
 evidence:dict
 def allows(self,path,journal):
  try:
   age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(self.checked_at)).total_seconds()
   return (os.getenv('GITHUB_ACTIONS')=='true' and self.run_id==os.getenv('GITHUB_RUN_ID') and bool(self.run_id)
    and 0<=age<300 and path.stem==self.key and journal.get('key')==self.key and fingerprint(journal)==self.prior_digest)
  except (ValueError,TypeError):return False

def authorize(context,key,root):
 import blogsky_native as native
 from publish_blogsky_posts import read,KEY,gate
 gate(root)
 control=read(root/'data/blogsky/native-recovery-control.json',{})
 journal=read(root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json',{})
 if (not KEY.fullmatch(key) or control.get('enabled') is not True or control.get('key')!=key
     or control.get('prior_journal_sha256')!=fingerprint(journal)
     or journal.get('phase')!='submitting' or os.getenv('GITHUB_ACTIONS')!='true'
     or not os.getenv('GITHUB_RUN_ID') or os.getenv('GITHUB_RUN_ATTEMPT')!='1'):
  raise RuntimeError('Exact unconsumed recovery authorization required')
 post=read(root/f'artifacts/blogsky-backlink-queue/items/{key}.json',{})['post']
 if post.get('title')!=journal.get('title'):raise RuntimeError('Recovery article binding mismatch')
 page=context.new_page()
 try:
  page.goto(native.ARCHIVE,wait_until='domcontentloaded',timeout=60000)
  if page.url!=native.ARCHIVE:raise RuntimeError('Recovery requires authenticated native archive')
  inspection=page.locator('a[href]').evaluate_all('''(aa,p)=>({matches:aa.filter(a=>a.textContent.trim()===p.title||a.href.includes(p.slug)).length,editorLinks:[...new Set(aa.filter(a=>a.href.includes('/afp-pipe/post/edit/')).map(a=>a.href))]})''',post)
  expected=set(control.get('expected_native_editor_urls',[]))
  if inspection['matches'] or len(expected)!=2 or set(inspection['editorLinks'])!=expected:
   raise RuntimeError('Native absence is not established; reconcile without resubmission')
  page.goto(native.BLOG+'/posts',wait_until='domcontentloaded',timeout=60000)
  if page.url.rstrip('/')!=native.BLOG+'/posts':raise RuntimeError('Unexpected recovery public archive')
  public=page.locator('a[href]').evaluate_all('''(aa,p)=>({matches:aa.filter(a=>a.textContent.trim()===p.title||a.href.includes(p.slug)).length,urls:[...new Set(aa.filter(a=>/\\/post-[0-9]+\\//.test(a.href)).map(a=>a.href))]})''',post)
  expected_public=set(control.get('expected_public_urls',[]))
  if public['matches'] or len(expected_public)!=2 or set(public['urls'])!=expected_public:
   raise RuntimeError('Public absence is not established; no resubmission')
 finally:page.close()
 at=datetime.datetime.now(datetime.timezone.utc).isoformat()
 return AbsencePermit(key,fingerprint(journal),os.environ['GITHUB_RUN_ID'],at,{'native_matches':0,'public_matches':0,'native_archive_count':2,'public_archive_count':2,'checkedAt':at})
