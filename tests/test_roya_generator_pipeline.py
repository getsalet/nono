import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import roya_backlink_queue as r
class RoyaGenerationTests(unittest.TestCase):
 def setUp(self):
  self.links=[{'url':'https://navar-abyari.ir/city/%d8%ae-looleh/','title':'خرید لوله در خوی','anchor':'لوله خوی','role':'city'},{'url':'https://navar-abyari.ir/province/','anchor':'استان','role':'province'}]
  self.item={'city_fa':'خوی','province_fa':'آذربایجان غربی','family':'hose','assigned_title':'لوله نخی برای بامیه در خوی؛ تناسب با مزرعه'}
 def test_prompt_uses_tokens_not_long_urls_or_blog_address(self):
  p=r.build_prompt(self.item,self.links)
  self.assertIn('href="AFP_LINK_1"',p);self.assertIn('href="AFP_LINK_2"',p)
  self.assertNotIn(self.links[0]['url'],p);self.assertNotIn(r.BLOG,p)
  self.assertIn('گارانتی',p);self.assertIn('حتی در جمله منفی',p)
 def test_only_exact_href_tokens_resolve(self):
  obj={'html':'<p>AFP_LINK_1</p><a href="AFP_LINK_1">خوی</a><a href="AFP_LINK_99">بد</a><a href="https://wrong.example/">بد</a>','links_used':['AFP_LINK_1','AFP_LINK_99']}
  got=r.resolve_link_tokens(obj,self.links)
  self.assertIn('href="'+self.links[0]['url']+'"',got['html'])
  self.assertIn('<p>AFP_LINK_1</p>',got['html']);self.assertIn('href="AFP_LINK_99"',got['html']);self.assertIn('https://wrong.example/',got['html'])
  self.assertEqual(got['links_used'],[self.links[0]['url'],'AFP_LINK_99'])
 def test_repair_includes_failed_draft_and_errors_without_managed_image(self):
  draft={'title':'عنوان قبلی','html':'<img src="https://example/image.jpg"><p>متن قبلی</p><a href="'+self.links[0]['url']+'">خوی</a>'}
  original=copy.deepcopy(draft);p=r.repair_prompt(self.item,self.links,draft,['unexpected latin words: soils'])
  self.assertIn('متن قبلی',p);self.assertIn('unexpected latin words: soils',p)
  self.assertNotIn('<img',p);self.assertNotIn(self.links[0]['url'],p);self.assertEqual(original,draft)
 def test_generation_resolves_tokens_before_quality_gate(self):
  import inspect
  s=inspect.getsource(r.main)
  self.assertLess(s.index('resolve_link_tokens(obj, links)'),s.index('errors, info = qa'))
  self.assertIn('repair_prompt(item, links, obj, errors)',s)
if __name__=='__main__':unittest.main()

class CheckpointRegressionTests(unittest.TestCase):
 def test_both_roya_writers_checkout_current_main_inside_shared_lock(self):
  for name in ('roya-backlink-queue.yml','roya-backlink-publish.yml'):
   s=(ROOT/'.github/workflows'/name).read_text()
   self.assertIn('group: roya-backlink-pipeline',s);self.assertIn('ref: main',s)
 def test_generation_preserves_recovery_before_commit(self):
  s=(ROOT/'.github/workflows/roya-backlink-queue.yml').read_text()
  self.assertLess(s.index('actions/upload-artifact@v4'),s.index('- name: Commit queue'))
  self.assertIn('no overwrite',s)
