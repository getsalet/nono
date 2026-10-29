import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import niloblog_pipeline as n
class ImageDiagnostics(unittest.TestCase):
 def test_quality_failure_is_not_transport_and_does_not_select_another_topic(self):
  p=n.failure_policy(n.PipelineStop('Generated image quality rejected'))
  self.assertEqual(p['category'],'image_quality');self.assertFalse(p['continue_candidates'])
 def test_unknown_exception_still_stops(self):
  self.assertEqual(n.failure_policy(RuntimeError('private'))['category'],'infrastructure_or_unclassified')
 def test_safe_saved_diagnostic_and_no_publication(self):
  with tempfile.TemporaryDirectory()as t,patch('blog_image_restore.prepare',side_effect=RuntimeError('Product image rejected: private detail')):
   item={'key':'nilo-general-a468fb68d3399c4b','_generation_stage':'local_vision_qa'}
   with self.assertRaisesRegex(n.PipelineStop,'Generated image quality rejected'):n.prepare_reviewed_image(item,{},'niloblog',Path(t))
   files=list(Path(t).rglob('*.json'));self.assertEqual(len(files),1);d=json.loads(files[0].read_text())
   self.assertEqual(d['code'],'image_quality_rejected');self.assertFalse(d['publication_verified']);self.assertNotIn('private detail',files[0].read_text())
 def test_transport_is_not_retried_or_relabelled_quality(self):
  error=RuntimeError('private provider error')
  with tempfile.TemporaryDirectory()as t,patch('blog_image_restore.prepare',side_effect=error)as p:
   with self.assertRaises(RuntimeError)as c:n.prepare_reviewed_image({'key':'test','_generation_stage':'generation_api'},{},'niloblog',Path(t))
   self.assertIs(c.exception,error);self.assertEqual(p.call_count,1)
 def test_success_preserves_image_adapter_result(self):
  with patch('blog_image_restore.prepare',return_value='https://example.org/approved.webp'):
   self.assertEqual(n.prepare_reviewed_image({'key':'test'},{},'niloblog'),'https://example.org/approved.webp')
 def test_empty_validation_pool_reports_reason_without_retry_permission(self):
  state={'held':{'saved':{'attempts':1}},'published':[]}
  def read(p):
   if p==n.STATE:return state
   if p==n.D/'runtime-control.json':return {'enabled':True,'revision':21}
   if p==n.D/'article-targets.json':return {'targets':[]}
   raise AssertionError('Unexpected read')
  with tempfile.TemporaryDirectory()as t,patch.object(n,'A',Path(t)),patch.object(n,'allowed',return_value=True),patch.object(n,'read',side_effect=read),patch.object(n,'load_runtime_matrix',return_value={'titles':[]}),patch.object(n,'evidence_first_candidates',return_value=[]),patch.object(n,'generate')as gen,patch.object(n,'checkpoint')as checkpoint:
   d=n.validate_only(1);self.assertEqual(d['reason_code'],'no_eligible_candidates');self.assertFalse(d['state_changed']);self.assertFalse(d['retry_permission_granted']);self.assertEqual(d['held_count'],1);gen.assert_not_called();checkpoint.assert_not_called()
