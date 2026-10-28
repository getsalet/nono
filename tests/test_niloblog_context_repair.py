import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
class ContextRepairTests(unittest.TestCase):
 def test_novelty_examples_rank_relevant_body_and_are_bounded(self):
  history=[{'html':'<p>گزارش محصول دیگر</p>','label':'other'},{'html':'<p>سیب زمینی بهار بررسی مدارک ' + 'متن '*1000 + '</p>','label':'matching'}]+[{'html':'<p>مورد دیگر</p>','label':str(i)}for i in range(8)]
  out=n.novelty_context(history,{'title':'سیب زمینی بهار'},{'brief':'بررسی مدارک'})
  self.assertEqual(len(out),4);self.assertEqual(out[0]['label'],'matching')
  self.assertTrue(all(x['contrast_only_not_evidence'] is True and len(x['text'])<=1800 for x in out))
 def test_empty_or_malformed_history_does_not_break_writer(self):
  self.assertEqual(n.novelty_context([None,{}, {'html':None}],{'title':'متن'},{}),[])
 def test_draft_failure_is_retained_after_repair_not_silenced(self):
  row={'id':'test'};obj={'html':'<p>کلمه خراب</p>'}
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'validate_article',side_effect=n.PipelineStop('Mixed-script word requires editorial correction')):
   with self.assertRaises(n.PipelineStop):n.validate_candidate(row,obj,{},'repaired-validation')
   saved=json.loads((Path(tmp)/'rejected/test-repaired-validation.json').read_text());self.assertEqual(saved['post'],obj);self.assertEqual(saved['stage'],'repaired-validation')
 def test_successful_validation_unchanged(self):
  with patch.object(n,'validate_article',return_value=750),patch.object(n,'save')as save:
   self.assertEqual(n.validate_candidate({}, {}, {}, 'initial'),750);save.assert_not_called()
 def test_diagnostic_never_serializes_exception_body(self):
  try:raise RuntimeError('password=private-provider-response')
  except Exception as e:result=n.candidate_diagnostic(e)
  self.assertNotIn('password',json.dumps(result));self.assertTrue(result['raw_exception_withheld']);self.assertEqual(result['error_type'],'RuntimeError')
 def test_cycle_report_links_to_exact_run_without_claiming_publication(self):
  old=n.CYCLE.copy()
  try:
   n.CYCLE.clear();n.CYCLE.update(status='idle',held_this_run=3,publication_verified_by_this_report=False)
   with patch.dict(os.environ,{'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'2'}):out=n.cycle_report({'intent':None},'publish')
   self.assertEqual(out['run_id'],'123');self.assertEqual(out['run_attempt'],'2');self.assertEqual(out['status'],'idle');self.assertFalse(out['publication_verified_by_this_report'])
  finally:n.CYCLE.clear();n.CYCLE.update(old)
 def test_missing_installation_not_required_for_requesting_documents(self):
  code=Path(n.__file__).read_text();self.assertIn('وجود شاهد نصب واقعی نوار تیپ شرط استخراج نیست',code)
  self.assertIn('اگر عنوان واقعاً مدعی اجرای ثبت شده یا اندازه گیری محلی است و منبع ندارد، blocked=true بماند',code)
 def test_independent_review_and_no_video_not_changed(self):
  code=Path(n.__file__).read_text();self.assertIn("if review_attempt==1:raise PipelineStop('Independent editorial review rejected')",code);self.assertIn('video_probability=0',code);self.assertIn('require_image_only(item)',code)
 def test_no_held_reset_or_new_model_in_patch(self):
  code=Path(n.__file__).read_text();self.assertNotIn("s['held']={}",code);self.assertIn("hold.get('pipeline_revision',0)<revision",code)
if __name__=='__main__':unittest.main()

class GenerationContractTests(unittest.TestCase):
 def test_negated_guarantee_is_reported_not_auto_approved(self):
  p={'html':'<p>تضمینی برای سودآوری نیست.</p>'}
  out=n.generation_feedback(p)
  self.assertTrue(any(x['term']=='تضمین' for x in out['blocked_phrase_hits']))
  self.assertIn('تضمینی برای سودآوری نیست',out['blocked_phrase_hits'][0]['context'])
 def test_mixed_token_from_live_editorial_repair_is_reported(self):
  out=n.generation_feedback({'html':'<p>در_operation_mزارعی</p>'})
  self.assertTrue(any('operation' in x['invalid_visible_token'] for x in out['invalid_visible_tokens']))
 def test_clean_persian_has_no_false_feedback(self):
  out=n.generation_feedback({'html':'<p>درباره سودآوری نمی توان نتیجه گرفت.</p>'})
  self.assertEqual(out['blocked_phrase_hits'],[]);self.assertEqual(out['invalid_visible_tokens'],[])
 def test_context_is_bounded(self):
  out=n.generation_feedback({'html':'<p>'+('الف '*10000)+'تضمین'+('ب '*10000)+'</p>'})
  self.assertLessEqual(len(out['blocked_phrase_hits'][0]['context']),180)
 def test_contract_and_validator_share_the_exact_original_terms(self):
  self.assertEqual(n.generation_contract()['blocked_visible_phrases'],['ارسال رایگان','تضمین افزایش','نمایندگی رسمی','تخفیف ویژه','تضمین','شرایط مناسب اقلیمی'])
  code=Path(n.__file__).read_text();self.assertIn('any(x in text for x in COMMERCIAL_BLOCK_TERMS)',code)
 def test_both_existing_repair_prompts_receive_specific_feedback(self):
  code=Path(n.__file__).read_text();self.assertIn("'validation_feedback':feedback",code);self.assertIn("'validation_feedback':generation_feedback(obj)",code)
  self.assertNotIn('\ufffd',code)
