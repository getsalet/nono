import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
from niloblog_editorial_patch import blocks,apply_patch,patch_prompt
class EditorialPatchTests(unittest.TestCase):
 def setUp(self):
  self.post={'title':'عنوان ثابت','meta_description':'شرح ثابت','tags':['آموزش'],'html':'<h2>نگهداری</h2><p>دستور مستند <a href="https://a.example/">لینک اول</a></p><p>علت بی شاهد</p><h2>حمل</h2><p>بند سالم <a href="https://b.example/">لینک دوم</a></p>'}
 def test_exact_block_patch_keeps_unaffected_bytes_and_metadata(self):
  before=copy.deepcopy(self.post);out,audit=apply_patch(self.post,{'edits':[{'block_id':'b1','html':'<p>دستور بدون علت فرضی</p>'}]})
  self.assertEqual(out['html'],self.post['html'].replace('<p>علت بی شاهد</p>','<p>دستور بدون علت فرضی</p>'));self.assertEqual(self.post,before)
  for k in ['title','meta_description','tags']:self.assertEqual(out[k],before[k])
  self.assertEqual(audit['changed_blocks'],['b1']);self.assertNotEqual(audit['before_sha256'],audit['after_sha256'])
 def test_no_global_rewrite_title_change_or_unknown_block(self):
  for payload in [{'html':'replacement'},{'edits':[]},{'edits':[{'block_id':'b99','html':'<p>متن</p>'}]},{'edits':[],'title':'تازه'},{'edits':[{'block_id':'b1','html':'<p>متن</p>'}]*2}]:
   with self.assertRaises(ValueError):apply_patch(self.post,payload)
 def test_link_deletion_retarget_and_anchor_change_are_rejected(self):
  for html in ['', '<p>بدون لینک</p>','<p><a href="https://evil.example/">لینک اول</a></p>','<p><a href="https://a.example/">تغییر متن</a></p>']:
   with self.assertRaises(ValueError):apply_patch(self.post,{'edits':[{'block_id':'b0','html':html}]})
 def test_insertion_outside_named_block_is_rejected(self):
  for html in ['<p>اصلاح</p><p>متن اضافه</p>','<h2>تغییر ساختار</h2>','<p>متن</p>خارج بند']:
   with self.assertRaises(ValueError):apply_patch(self.post,{'edits':[{'block_id':'b1','html':html}]})
 def test_deletion_of_unlinked_bad_block_and_metadata_are_explicit(self):
  out,audit=apply_patch(self.post,{'edits':[{'block_id':'b1','html':''}],'meta_description':'شرح اصلاح شده'})
  self.assertNotIn('علت بی شاهد',out['html']);self.assertEqual(out['meta_description'],'شرح اصلاح شده');self.assertTrue(audit['metadata_changed'])
 def test_ambiguous_identical_blocks_fail_closed(self):
  p={'html':'<p>تکرار</p><p>تکرار</p>'}
  with self.assertRaises(ValueError):apply_patch(p,{'edits':[{'block_id':'b0','html':'<p>اصلاح</p>'}]})
 def test_insufficient_evidence_can_block_without_patch(self):
  result,audit=apply_patch(self.post,{'blocked':True});self.assertEqual(result,{'blocked':True});self.assertTrue(audit['blocked'])
 def test_model_has_no_other_blog_text_to_copy(self):
  prompt=patch_prompt(self.post,{'approved':False},{'facts':[]},{},{},{})
  self.assertIn('فقط اصلاح موضعی',prompt);self.assertIn('block_id',prompt);self.assertNotIn('nearest_other_blog_articles',prompt)
 def run_pipeline(self,*,duplicate=False,invalid_patch=False):
  bundle={'content_scope':'general_education','local':None,'article':{'text':'متن شاهد مستند و کامل درباره نگهداری محصول برای آزمون','url':'https://example.org/source'},'technical':[{'text':'منبع فنی دوم با دستورهای مستند درباره جابجایی صحیح محصول','url':'https://example.org/technical'}],'links':[]}
  post={'title':'عنوان','html':'<h2>بخش</h2><p>ادعای بی شاهد</p><p>بند سالم</p>'}
  review={'approved':False,'semantic_duplicate':duplicate,'unsupported_claims':['ادعای بی شاهد']}
  fix={'edits':[{'block_id':'b0','html':'<p>دستور مستند</p>'}]}if not invalid_patch else {'html':'بازنویسی کامل'}
  outputs=[post,review,fix,{'approved':True}]
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'source_bundle',return_value=bundle),patch.object(n,'all_history',return_value=[]),patch.object(n,'plan_article',return_value={'outline':[]}),patch.object(n,'validate_candidate',return_value=700)as validate,patch.object(n,'bind_review_evidence',side_effect=lambda x,p:x),patch.object(n,'review_passes',side_effect=[False,True])as gate,patch('roya_backlink_queue.agnes',side_effect=outputs)as ai,patch.object(n,'reserve')as reserve:
   row={'id':'general-test','title':'عنوان','angle_ref':'a','content_scope':'general_education'}
   if duplicate or invalid_patch:
    with self.assertRaises(n.PipelineStop):n.generate(row,{'angles':{'a':{'brief':'پرسش'}}},{},{},{},validation_only=True)
    self.assertEqual(ai.call_count,2 if duplicate else 3);self.assertEqual(validate.call_count,1)
   else:
    result=n.generate(row,{'angles':{'a':{'brief':'پرسش'}}},{},{},{},validation_only=True)
    self.assertEqual(result['status'],'validated_not_published');self.assertEqual(validate.call_count,2);self.assertEqual(gate.call_count,2);self.assertEqual(ai.call_count,4)
    self.assertEqual(result['post']['html'],'<h2>بخش</h2><p>دستور مستند</p><p>بند سالم</p>');self.assertTrue((Path(tmp)/'editorial-patches/general-test.json').exists())
   reserve.assert_not_called()
 def test_single_patch_is_fully_revalidated_and_independently_reviewed(self):self.run_pipeline()
 def test_duplicate_verdict_is_not_repaired_into_a_paraphrase(self):self.run_pipeline(duplicate=True)
 def test_invalid_patch_stops_without_extra_model_attempt(self):self.run_pipeline(invalid_patch=True)
if __name__=='__main__':unittest.main()
