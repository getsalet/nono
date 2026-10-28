"""One policy-bound repair of proven pre-write text failures, never resubmission."""
import copy,inspect,json,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import roya_backlink_queue as r
import build_roya_queue as build
class PreflightRecoveryTests(unittest.TestCase):
 def setUp(self):
  self.item={'key':'city/test','province':'test','family':'tape20','status':'failed','failure_stage':'text_validation','generated_at':'2026-10-23T17:00:00Z'}
  self.record={**self.item,'qa':{'passed':False,'errors':['Exactly three complete native details/summary/p FAQs required']},'post':{'title':'نگهداری نوار تیپ','slug':'tape-maintenance','html':'<p>مقاله واقعی نیازمند اصلاح</p>'}}
 def test_matching_text_failure_is_unapproved_input_only(self):
  old=copy.deepcopy(self.record);post=r.preflight_repair_draft(self.record,self.item,{})
  self.assertEqual(post,self.record['post']);self.assertEqual(self.record,old);self.assertIsNot(post,self.record['post'])
 def test_once_only_and_rebuild_preserves_marker(self):
  for location in ('item','record'):
   a=copy.deepcopy(self.item);b=copy.deepcopy(self.record);(a if location=='item' else b)['preflight_recovery']={'policy':r.PREFLIGHT_RECOVERY_POLICY}
   self.assertIsNone(r.preflight_repair_draft(b,a,{}))
  self.assertIn('preflight_recovery',build.RUNTIME_FIELDS)
 def test_published_identity_stale_and_nontext_failures_never_recover(self):
  for fields in ({'published':True},{'pid':7},{'native_id':'7'},{'published_url':'https://example.test/post'},{'intent':{'key':'x'}},{'generated_at':'old'},{'key':'other'},{'failure_stage':'image'},{'status':'completed'},{'qa':{'passed':True,'errors':['x']}},{'qa':{'passed':False,'errors':[]}}):
   with self.subTest(fields=fields):self.assertIsNone(r.preflight_repair_draft({**self.record,**fields},self.item,{}))
  self.assertIsNone(r.preflight_repair_draft(self.record,self.item,{'published':[{'key':self.item['key']}]}))
 def test_unknown_or_future_timer_stays_held(self):
  for timer in ('2099-01-01T00:00:00Z','bad',True,'2026-01-01T00:00:00'):
   self.assertIsNone(r.preflight_repair_draft(self.record,{**self.item,'next_retry_at':timer},{}))
 def test_pick_works_without_broad_retry_flag_and_preserves_hose_hold(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);r.save_json(root/'city_test.json',self.record)
   with patch.multiple(r,ROOT=root,ITEMS=root,RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=True):
    self.assertEqual(r.pick({'items':[self.item]},{},1),[self.item])
   with patch.multiple(r,ROOT=root,ITEMS=root,RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=False):
    self.assertEqual(r.pick({'items':[self.item]},{},1),[])
 def test_publisher_installs_its_html_parser(self):
  workflow=(ROOT/'.github/workflows/roya-backlink-publish.yml').read_text()
  self.assertIn('pip install --quiet Pillow beautifulsoup4',workflow)
 def test_prompt_and_full_quality_gates_remain(self):
  source=inspect.getsource(r.build_prompt);self.assertIn('<summary>پرسش</summary><p>پاسخ</p></details>',source)
  self.assertNotIn('\ufffd',source)
  body=inspect.getsource(r.main);self.assertIn("ART / 'preflight-recovery-history'",body);self.assertIn('errors, info = qa(item, obj, links)',body)
  self.assertLess(body.index("item['preflight_recovery'] ="),body.index("item['status'] = 'processing'"))
