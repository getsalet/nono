import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import build_roya_queue as build
import roya_backlink_queue as roya
class SupplementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'data/roya').mkdir(parents=True)
  self.manifest=self.root/'data/roya/approved-article-topics.json'
  self.inventory=self.root/'data/blog-site-article-targets.json'
  self.source={'key':'site-post-952','kind':'article','family':'tape20','site_title':'مراحل نصب نوار تیپ','target_url':'https://navar-abyari.ir/مراحل-نصب-نوار-تیپ/'}
  self.inventory.write_text(json.dumps({'targets':[self.source]}));self.manifest.write_text(json.dumps({'enabled':True,'source_keys':['site-post-952']}))
  self.titlepatch=patch('city_backlink_policy.title_candidates',return_value=['مراحل نصب نوار تیپ؛ تصمیم‌های طراحی آبیاری']);self.titlepatch.start();self.addCleanup(self.titlepatch.stop)
 def test_new_item_is_nonlocal_pending_and_bounded(self):
  rows=build.append_approved_articles([],{},self.root);self.assertEqual(len(rows),1);x=rows[0]
  self.assertEqual(x['status'],'pending');self.assertEqual(x['kind'],'article');self.assertEqual(x['city_fa'],'');self.assertEqual(x['target_url'],self.source['target_url']);self.assertEqual(x['attempts'],0)
 def test_existing_failed_and_published_rows_preserved_exactly(self):
  original=build.append_approved_articles([],{},self.root)[0]
  for status in ('failed','published','completed'):
   prev={**original,'status':status,'attempts':7,'published':status=='published','pid':'receipt','next_retry_at':'2099-01-01','custom_runtime':{'owner':'old'}}
   saved=copy.deepcopy(prev);rows=build.append_approved_articles([],{prev['key']:prev},self.root)
   self.assertEqual(rows,[saved]);self.assertEqual(prev,saved)
 def test_idempotent_and_source_url_deduplication(self):
  rows=build.append_approved_articles([],{},self.root);before=copy.deepcopy(rows)
  self.assertEqual(build.append_approved_articles(rows,{x['key']:x for x in rows},self.root),before)
 def test_unapproved_family_host_or_kind_fail_closed(self):
  for fields in ({'family':'hose'},{'target_url':'https://evil.test/a'},{'kind':'city'},{'target_url':'https://navar-abyari.ir/'}):
   self.inventory.write_text(json.dumps({'targets':[{**self.source,**fields}]}))
   with self.assertRaises(ValueError):build.append_approved_articles([],{},self.root)
 def test_shared_city_import_excludes_technical_supplements(self):
  import inspect,city_backlink_policy
  code=inspect.getsource(city_backlink_policy.build_queue)
  self.assertIn("if src.get('kind') == 'article':continue",code)
 def test_missing_or_disabled_manifest_is_noop(self):
  self.manifest.unlink();self.assertEqual(build.append_approved_articles([],{},self.root),[])
  self.manifest.write_text(json.dumps({'enabled':False}));self.assertEqual(build.append_approved_articles([],{},self.root),[])
 def test_fallback_never_reinterprets_article_as_city(self):
  row=build.append_approved_articles([],{},self.root)[0];queue=self.root/'queue.json';queue.write_text(json.dumps({'items':[row]}))
  with patch.object(build,'QUEUE',queue):self.assertEqual(build.targets_from_queue(),[])
 def test_article_prompt_preserves_quality_and_approved_links(self):
  x=build.append_approved_articles([],{},self.root)[0];x['assigned_title']=x['prepared_title'];p=roya.build_prompt(x,[{'title':x['site_title'],'anchor':x['site_title'],'role':'city','url':x['target_url']},{'title':'AFP','anchor':'نوار تیپ','role':'home','url':'https://navar-abyari.ir/'}])
  self.assertIn(x['assigned_title'],p);self.assertNotIn('برای شهر  در استان ',p);self.assertNotIn('لنگر باید شامل نام شهر',p);self.assertNotIn('نام شهر «»',p)
  for text in ('AFP_LINK_1','AFP_LINK_2','دقیقاً ۳ سوال','جمع‌بندی','حداقل ۳۰ کلمه','فقط HTML ساده','بدون مرجع، مقدار عددی تجویز نکن','محتوا','غیرشهری'):self.assertIn(text,p)
if __name__=='__main__':unittest.main()
