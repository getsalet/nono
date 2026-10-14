import copy,inspect,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_gate as g
import farsiblog_backlink_queue as f
class GenerationRecoveryTests(unittest.TestCase):
 def test_reference_identity_uses_physical_references_not_package_words(self):
  text=g.reference_identity_instruction('hose')
  self.assertIn('Image 3',text);self.assertIn('printed words alone must not override',text)
  self.assertIn('separate true',text);self.assertNotEqual(g.POLICY,'blog-product-family-reference-vision-v1')
 def test_wrong_family_still_fails(self):
  v={'pass':True,'score':95,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False}
  self.assertIn('Image product family mismatch',g.verdict_errors(v,'hose'))
 def test_failed_draft_and_exact_errors_are_in_repair_prompt(self):
  item={'kind':'legacy','topic':'آبیاری','angle':'بررسی','family':'tape','reference_url':'https://navar-abyari.ir/'}
  obj={'html':'<p><img src="https://navar-abyari.ir/a.webp"></p><p>متن ردشده ویژه آزمون</p>','image_url':'managed-image'}
  text=f.repair_request(item,[],'مرجع',obj,['three native FAQs required'])
  self.assertIn('متن ردشده ویژه آزمون',text);self.assertIn('three native FAQs required',text);self.assertNotIn('<img',text);self.assertNotIn('managed-image',text);self.assertIn('image_url',obj)
 def test_exception_details_retain_safe_image_diagnosis(self):
  self.assertEqual(f.exception_detail(RuntimeError('Product image rejected: Image product family mismatch')),'Product image rejected: Image product family mismatch')
  self.assertEqual(f.exception_detail(RuntimeError('unknown private text should not be logged')),'RuntimeError')
 def test_title_owned_and_image_gate_preserved(self):
  source=inspect.getsource(f.main)
  self.assertIn("obj['title']=matrix_title(item,CITY_BLOG)",source)
  self.assertIn('prepare_image(item)',source);self.assertIn('remaining_publication_budget()',source)
 def test_policy_recovery_is_bounded_and_never_resets_published_rows(self):
  with tempfile.TemporaryDirectory()as d:
   art=Path(d)/'art';queue=Path(d)/'queue.json'
   failed={'key':'hose-failed','family':'hose','kind':'city','status':'failed','attempts':4,'last_error':'generation/source/validation failed: RuntimeError','next_retry_at':'2099-01-01T00:00:00Z'}
   published={**failed,'key':'published','published':True}
   tape={**failed,'key':'tape','family':'tape20'}
   with patch.object(f,'ART',art),patch.object(f,'QUEUE',queue):
    f.save(f.item_path(failed['key']),{**failed,'post':None})
    q={'items':[failed,published,tape]};f.recover_stale_image_deferrals(q)
    self.assertNotIn('next_retry_at',failed);self.assertEqual(failed['attempts'],4)
    self.assertIn('next_retry_at',published);self.assertIn('next_retry_at',tape)
    failed['next_retry_at']='2099-01-01T00:00:00Z';f.recover_stale_image_deferrals(q)
    self.assertIn('next_retry_at',failed)
