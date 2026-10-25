import unittest,tempfile,json
from pathlib import Path
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
 def test_switching_topic_id_never_keeps_another_articles_title(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);status=root/'live.json';status.write_text(json.dumps({'topic_id':'old','topic_title':'Old article','status':'idle'}))
   with patch.dict('os.environ',{'AFP_PROGRESS_ENABLED':'1'}),patch.object(progress,'ROOT',root),patch.object(progress,'STATUS_PATH',status),patch.object(progress,'publish_file',return_value=False):
    progress.update('Waiting',20,topic_id='new',status='provider_cooldown')
   self.assertEqual(json.loads(status.read_text())['topic_id'],'new');self.assertIsNone(json.loads(status.read_text())['topic_title'])

 def test_expired_circuit_is_not_reported_as_active_cooldown(self):
  from automation.agri_v2.queue import atomic_json
  with tempfile.TemporaryDirectory() as d,patch.object(progress,'OUT',Path(d)):
   atomic_json(Path(d)/'provider-circuit.json',{'open':True,'at':'2026-01-01T00:00:00+00:00','retry_at_epoch':1})
   self.assertFalse(progress.provider_snapshot()['open'])
 def test_future_circuit_is_reported_active(self):
  import time
  from automation.agri_v2.queue import atomic_json
  with tempfile.TemporaryDirectory() as d,patch.object(progress,'OUT',Path(d)):
   atomic_json(Path(d)/'provider-circuit.json',{'open':True,'at':'2026-01-01T00:00:00+00:00','retry_at_epoch':time.time()+3600})
   self.assertTrue(progress.provider_snapshot()['open'])

if __name__=='__main__':unittest.main()
