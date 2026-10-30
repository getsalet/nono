"""Production wiring contracts, with image/vision transports mocked; no posts."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as generated
import blog_image_gate as gate
import blog_package_labels as captions
class CaptionActivationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);(self.root/'data').mkdir()
  self.cfg=self.root/'data/blog-image-acceptance-policy.json';self.cfg.write_text(json.dumps({'mode':gate.PRACTICAL_MODE,'minimum_score':90,'require_exact_package_labels':True}))
  self.item={'key':'activation-fixture','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'آبیاری قطره ای با نوار تیپ','summary':'بررسی نصب خطوط نوار تیپ و توزیع رطوبت در خاک و پای ریشه گیاه'}}
  self.raw=(ROOT/'artifacts/blog-image-calibration/41037090356/case-3-native.webp').read_bytes()
  self.good={'english_text':captions.ENGLISH,'persian_text':captions.PERSIAN,'english_legible':True,'persian_legible':True}
 def test_preparation_really_typesets_before_local_and_public_qa(self):
  seen=[]
  def review(item,url,root=None,_candidate=None):
   if _candidate is not None:
    self.assertNotEqual(_candidate,self.raw);self.assertEqual(item['_image_caption_render']['policy'],captions.POLICY)
    self.assertEqual(item['_image_caption_render']['captions']['persian']['text'],'آبگسترفراپارسیان');seen.append(_candidate)
  with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'reconsider_candidate',return_value=None),patch.object(generated,'generate',return_value=self.raw)as gen,patch('blog_image_backpressure.require_open'),patch.object(gate,'review',side_effect=review)as qa,patch.object(generated,'checkpoint_asset',return_value='https://example.invalid/approved.webp')as checkpoint:
   generated.prepare_now(self.item,'roya',self.root,max_rounds=1)
  self.assertEqual(gen.call_count,1);self.assertEqual(qa.call_count,2);self.assertEqual(checkpoint.call_args.args[1],seen[0]);self.assertEqual(self.item['image_generation']['package_label_policy'],captions.POLICY)
 def test_ocr_uncertainty_keeps_candidate_and_does_not_regenerate(self):
  with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'reconsider_candidate',return_value=None),patch.object(generated,'generate',return_value=self.raw)as gen,patch('blog_image_backpressure.require_open'),patch.object(gate,'review',side_effect=RuntimeError('Package caption verification unresolved; candidate retained')):
   with self.assertRaisesRegex(RuntimeError,'candidate retained'):generated.prepare_now(self.item,'roya',self.root,max_rounds=2)
  self.assertEqual(gen.call_count,1);cache=self.root/'artifacts/roya-backlink-queue/generated-images'/(generated.identity(self.item,'roya')+'.webp');self.assertTrue(cache.exists())
  with patch.object(captions,'typeset',side_effect=AssertionError('do not render twice')):captions.prepare_cached(cache)
 def test_cached_primary_score_cannot_bypass_literal_caption_check(self):
  digest=hashlib.sha256(self.raw).hexdigest();folder=self.root/'artifacts/blog-image-reviews';folder.mkdir(parents=True)
  verdict={'pass':True,'score':99,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'technical_evidence_match':True,'packaging_not_used_as_hardware':True,'product_role_plausible':True,'irrigation_geometry_plausible':True,'package_soil_gap_visible':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False}
  record={'width':1200,'height':900,'policy':gate.POLICY,'review_model':__import__('os').getenv('IMAGE_REVIEW_MODEL')or gate.roya.BASE.AGNES_MODEL,'sha256':digest,'family':'tape20','topic_sha256':__import__('blog_reference_scene').topic_hash(self.item),'scene_guard_version':gate.SCENE_GUARD,'article_owner':'roya|activation-fixture','verdict':verdict}
  (folder/('tape20-'+digest+'.json')).write_text(json.dumps(record))
  wrong={**self.good,'persian_text':'آبگسترفراپاریان'}
  # This isolates cached-caption behavior, not the legacy watermark font contract.
  watermark=patch('blog_image_watermark.present',return_value=True);watermark.start();self.addCleanup(watermark.stop)
  with patch.object(captions,'inspect',return_value=wrong)as reader,patch.object(gate.roya.BASE,'fetch_json',side_effect=AssertionError('cached primary should not re-run')):
   with self.assertRaisesRegex(RuntimeError,'verification unresolved'):gate.review(copy.deepcopy(self.item),'generated://roya/fixture',self.root,_candidate=self.raw)
  self.assertEqual(reader.call_count,1)
  with patch.object(captions,'inspect',return_value=self.good)as reader:
   accepted=gate.review(copy.deepcopy(self.item),'generated://roya/fixture',self.root,_candidate=self.raw)
  self.assertEqual(reader.call_count,1);self.assertEqual(captions.record_errors(accepted),[])
 def test_no_side_effect_dispatch_is_part_of_activation_test(self):
  self.assertTrue(captions.enabled(ROOT,'tape20'));self.assertFalse(captions.enabled(ROOT,'hose'))
