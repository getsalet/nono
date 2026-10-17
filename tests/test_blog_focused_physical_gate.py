"""Two separate vision checks, one actual candidate; never generate or publish."""
import copy,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_gate as gate
import blog_generated_image as generated
import blog_image_watermark as watermark
import roya_backlink_queue as roya
import blog_reference_scene as scene
class FocusedPhysicalGateTests(unittest.TestCase):
 def setUp(self):
  self.item={'key':'two-stage','family':'tape20','_image_article_context':{'title':'نوار تیپ سیب زمینی؛ نکات نگهداری','summary':'بازرسی خط آبیاری نوار تیپ و بررسی رطوبت خاک کنار ریشه در ردیف های گیاه سیب زمینی انجام می شود.'}}
  self.primary={'pass':True,'score':99,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'technical_evidence_match':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False,**{k:True for k in gate.SCENE_FLAGS}}
  self.focused={'clear_soil_gap':True,'line_touches_or_crosses_package':False,'extra_loose_product_coil':False,'package_has_protruding_strip':False,'reason':'Independent fixture evidence'}
  b=io.BytesIO();watermark.apply(Image.new('RGB',(1200,900),'brown')).save(b,'WEBP');self.raw=b.getvalue()
 def reply(self,value):return {'choices':[{'message':{'content':json.dumps(value)}}]}
 def execute(self,root,focused=None,primary=None):
  replies=[self.reply(primary or self.primary),self.reply(self.focused if focused is None else focused)]
  with patch.object(generated,'family_enabled',return_value=True),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',side_effect=replies)as api,patch.object(generated,'generate')as gen:
   try:result=gate.review(self.item,'generated://roya/'+'a'*32,root,_candidate=self.raw)
   finally:self.calls=api.call_args_list;gen.assert_not_called()
  return result
 def test_primary_and_focused_both_must_pass(self):
  with tempfile.TemporaryDirectory()as d:result=self.execute(Path(d))
  self.assertEqual(len(self.calls),2);self.assertEqual(result['focused_physical_review'],self.focused)
  self.assertEqual(self.item['image_review']['focused_physical_review'],self.focused)
  text=self.calls[1].args[2]['messages'][0]['content'][0]['text']
  self.assertIn('independent safety check',text);self.assertIn('no previous verdict',text)
  self.assertNotIn(self.item['_image_article_context']['title'],text)
 def test_high_primary_score_cannot_override_line_touch(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);focused={**self.focused,'line_touches_or_crosses_package':True}
   with self.assertRaisesRegex(RuntimeError,'Independent physical condition'):self.execute(root,focused)
   record=json.loads(next((root/'artifacts/blog-image-reviews').glob('*.json')).read_text())
  self.assertEqual(len(self.calls),2);self.assertFalse(record['verdict']['pass']);self.assertFalse(record['verdict']['package_soil_gap_visible'])
  self.assertNotIn('image_review',self.item)
 def test_extra_loose_coil_is_not_a_single_product_pass(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(RuntimeError):self.execute(Path(d),{**self.focused,'extra_loose_product_coil':True})
 def test_required_carton_is_not_counted_as_an_extra_coil(self):
  with tempfile.TemporaryDirectory()as d:self.execute(Path(d))
  text=self.calls[1].args[2]['messages'][0]['content'][0]['text']
  self.assertIn('required AFP package itself is NEVER an extra_loose_product_coil',text)
  self.assertIn('DISTINCT ADDITIONAL',text)
  self.assertIn('A protruding tail is NOT a second product',text)
 def test_protruding_strip_rejects_even_with_one_package_and_clear_soil(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)
   with self.assertRaisesRegex(RuntimeError,'package_has_protruding_strip'):
    self.execute(root,{**self.focused,'package_has_protruding_strip':True})
   record=json.loads(next((root/'artifacts/blog-image-reviews').glob('*.json')).read_text())
  self.assertFalse(record['verdict']['pass']);self.assertFalse(record['verdict']['product_role_plausible'])
  self.assertTrue(record['verdict']['product_count_match']);self.assertTrue(record['verdict']['package_soil_gap_visible'])
 def test_missing_protruding_strip_check_cannot_reuse_legacy_approval(self):
  old={k:v for k,v in self.focused.items()if k!='package_has_protruding_strip'}
  self.assertTrue(gate.focused_separation_errors(old))
 def test_already_rejected_candidate_does_not_pay_for_second_review(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(RuntimeError):self.execute(Path(d),primary={**self.primary,'technical_evidence_match':False,'pass':False})
  self.assertEqual(len(self.calls),1)
 def test_missing_or_nonboolean_focused_results_fail_closed(self):
  for value in (None,{},[],{**self.focused,'clear_soil_gap':'true'},{**self.focused,'line_touches_or_crosses_package':0}):
   self.assertTrue(gate.focused_separation_errors(value))
 def test_structured_publication_requires_independent_evidence(self):
  record={'scene_guard_version':gate.SCENE_GUARD,'verdict':self.primary}
  self.assertIn('Independent package separation review required',gate.generated_scene_errors(record,'tape20'))
  record['focused_physical_review']=self.focused;self.assertEqual(gate.generated_scene_errors(record,'tape20'),[])
 def test_monitoring_prompt_separates_dry_package_patch_from_wet_roots(self):
  text=scene.prompt(self.item,'roya');self.assertIn('dark moist soil',text)
  self.assertIn('Only the separate carton island is dry',text);self.assertIn('No loose coil',text)
if __name__=='__main__':unittest.main()
