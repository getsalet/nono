"""The no-ribbon condition is opt-in, fail-closed and independent of score."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_gate as g
class ClosedPackageTests(unittest.TestCase):
 def record(self):
  v={'pass':True,'score':99,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_count_match':True,'technical_evidence_match':True,'packaging_not_used_as_hardware':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False}
  return {'scene_guard_version':g.SCENE_GUARD,'acceptance_mode':g.PRACTICAL_MODE,'verdict':v,'closed_package_required':True,'package_finish_policy':g.PACKAGE_FINISH_POLICY,'focused_physical_review':{'package_has_protruding_strip':False}}
 def test_strip_rejected_even_with_score_99(self):
  for flag in (True,None,0,'false'):
   r=self.record();r['focused_physical_review']['package_has_protruding_strip']=flag
   with self.subTest(flag=flag):self.assertTrue(g.generated_scene_errors(r,'tape20'))
 def test_missing_or_old_independent_evidence_rejected(self):
  for field in ('package_finish_policy','focused_physical_review'):
   r=self.record();r.pop(field);self.assertTrue(g.generated_scene_errors(r,'tape20'))
 def test_clean_carton_and_other_advisory_details_allowed(self):
  r=self.record();r['focused_physical_review'].update(clear_soil_gap=False,line_touches_or_crosses_package=True)
  self.assertEqual(g.generated_scene_errors(r,'tape20'),[])
 def test_wrong_product_and_other_core_defects_remain_blocked(self):
  for field in ('fake_text_or_logo','people_present','wrong_product_present'):
   r=self.record();r['verdict'][field]=True;self.assertTrue(g.generated_scene_errors(r,'tape20'))
 def test_configuration_is_explicit_and_tape_only(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/g.ACCEPTANCE_CONFIG;p.parent.mkdir(parents=True);p.write_text(json.dumps({'forbid_protruding_package_strip':True}))
   self.assertTrue(g.closed_package_required(d,'tape20'));self.assertFalse(g.closed_package_required(d,'hose'))
   p.write_text(json.dumps({'forbid_protruding_package_strip':'true'}))
   with self.assertRaises(RuntimeError):g.closed_package_required(d,'tape20')
class ClosedPackageReviewIntegrationTests(unittest.TestCase):
 def setUp(self):
  from test_blog_practical_score90 import PracticalScore90Tests
  self.f=PracticalScore90Tests();self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.f.cfg['forbid_protruding_package_strip']=True;self.f.write_config()
 def review(self,strip):
  from unittest.mock import patch
  self.f.save_record()
  with patch.object(g.roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(g.roya.BASE,'fetch_json',side_effect=AssertionError('Original primary review must be retained')),patch.object(g,'focused_physical_check',return_value={'package_has_protruding_strip':strip})as focus:
   record=g.review(self.f.item,'generated://rozblog/'+'a'*32,self.f.root,_candidate=self.f.raw)
  self.assertEqual(focus.call_count,1)
  return record
 def test_clean_cached_candidate_gets_fresh_independent_check_and_binding(self):
  r=self.review(False)
  self.assertTrue(r['closed_package_required']);self.assertEqual(r['package_finish_policy'],g.PACKAGE_FINISH_POLICY)
  self.assertTrue(self.f.item['image_review']['closed_package_required'])
  self.assertEqual(r['verdict']['score'],95)
 def test_ribbon_is_rejected_even_if_primary_cached_score_is_95(self):
  with self.assertRaisesRegex(RuntimeError,'protruding strip'):
   self.review(True)
 def test_missing_result_is_not_approval(self):
  with self.assertRaisesRegex(RuntimeError,'protruding strip'):
   self.review(None)
if __name__=='__main__':unittest.main()
