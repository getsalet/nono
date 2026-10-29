import unittest
import niloblog_general_scope as g
class RepetitionScope(unittest.TestCase):
 def test_internal_repetition_is_rejected_not_approved_or_cross_blog_identity(self):
  p=g.general_review_prompt();self.assertIn('semantic_duplicate فقط تکرار معنایی با مقاله قبلی',p);self.assertIn('approved=false و reader_ready=false',p);self.assertIn('nearest_other_blog_articles',p)
 def test_cross_blog_duplicate_gate_remains_fail_closed(self):
  r={k:True for k in ['approved','grounded','scope_appropriate','independently_useful','reader_ready','causal_consistency']};r.update(semantic_duplicate=True,contains_local_claims=False,unsupported_claims=[])
  self.assertFalse(g.general_review_passes(r,{},str))
 def test_writer_requires_one_table_and_exact_measurement_location(self):
  import inspect
  p=inspect.getsource(g.general_writer_prompt);self.assertIn('آن را فقط یک بار بیاور',p);self.assertIn('خروجی فیلتر',p);self.assertIn('همه نقاط تعمیم نده',p)
