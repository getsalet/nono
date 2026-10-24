import unittest
from unittest.mock import patch
from automation.agri_v2 import progress
class ProgressTests(unittest.TestCase):
 def test_metrics_are_topic_counts_not_total_site_posts(self):
  m=progress.metrics();self.assertEqual(m['new_topics'],2905);self.assertEqual(m['merge_topics'],593);self.assertEqual(m['hold_topics'],370);self.assertEqual(m['remaining_topics'],2905-m['published_verified'])
 def test_markdown_explains_actual_stage_percentage(self):
  d={'status':'running','percent':40,'stage':'متن بررسی شد','topic_id':'fixture','updated_at':'2026-10-24T00:00:00Z','run_url':None,'metrics':progress.metrics()};s=progress.markdown(d);self.assertIn('40',s);self.assertIn('درصد گذشت زمان',s);self.assertNotIn('Authorization',s)
 def test_tests_and_unenabled_jobs_do_not_publish_status(self):
  with patch.dict('os.environ',{},clear=True),patch.object(progress,'publish_file') as p,patch.object(progress,'atomic_json') as a:
   progress.update('fixture',10);p.assert_not_called();a.assert_not_called()
if __name__=='__main__':unittest.main()
