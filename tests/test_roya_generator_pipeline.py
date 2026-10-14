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
  self.assertIn('repair_prompt(item, links, obj, errors),temperature=0.1',s)
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

class ProductSemanticTests(unittest.TestCase):
 def test_hose_prompt_does_not_assign_tape_dimensions(self):
  item={'family':'hose','city_fa':'چوبر','province_fa':'گیلان','assigned_title':'لوله نخی برای سویا در چوبر؛ طراحی مسیر آب'}
  prompt=r.build_prompt(item,[])
  self.assertIn('مسیر انتقال آب',prompt);self.assertNotIn('۱۷۵',prompt)
 def test_hose_cannot_be_defined_as_tape_but_connections_are_allowed(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>لوله نخی (نوار تیپ) را بررسی کنید.</p>'))
  self.assertEqual(r.product_semantics_errors({'family':'hose'},'<p>لوله نخی آب را به شبکه نوار تیپ انتقال می‌دهد.</p>'),[])
 def test_assigned_title_is_owned_before_validation(self):
  import inspect
  s=inspect.getsource(r.main)
  self.assertLess(s.index("obj['title'] = item['assigned_title']"),s.index('errors, info = qa'))

class UnsupportedHoseClaimsTests(unittest.TestCase):
 def test_material_claim_rejected(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>جنس لوله از PE با افزودنی UV است.</p>'))
 def test_low_point_air_release_rejected(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>از نقاط کم‌ارتفاع عبور دهید تا هواگیری طبیعی انجام شود.</p>'))
 def test_unfounded_comparison_rejected(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>لوله تاشو انعطاف بیشتری دارد.</p>'))
 def test_datasheet_review_allowed(self):
  self.assertEqual(r.product_semantics_errors({'family':'hose'},'<p>جنس و فشار مجاز همان مدل را در برگه فنی بررسی کنید. تعیین نقاط هواگیری و تخلیه به بررسی مسیر نیاز دارد.</p>'),[])
 def test_corrupt_unicode_rejected(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>گرد\ufffd.</p>'))

class TransferLineEmitterRegressionTests(unittest.TestCase):
 def test_emitter_installation_on_transfer_hose_is_rejected(self):
  self.assertTrue(r.product_semantics_errors({'family':'hose'},'<p>قطره‌چکان‌گذاری لوله‌ها نیازمند محاسبه است.</p>'))
 def test_connection_to_a_separate_drip_network_is_allowed(self):
  self.assertEqual(r.product_semantics_errors({'family':'hose'},'<p>لوله نخی آب را به شبکه توزیع و نوارهای فرعی می‌رساند.</p>'),[])
