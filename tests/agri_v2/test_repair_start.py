import tempfile,unittest,time
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import repair_start as s
from automation.agri_v2.queue import atomic_json,load_json
class RepairStartTests(unittest.TestCase):
 def req(self):return {'request_id':s.ID,'authorized':True,'max_cycle_invocations':1,'max_posts_per_run':1,'preserve_publication_holds':True,'review_policy':s.REVIEW_POLICY,'scene_policy':s.POLICY,'max_wait_seconds':2700}
 def test_exact_budget_only(self):
  r=self.req();s.validate(r);r['max_cycle_invocations']=2
  with self.assertRaises(ValueError):s.validate(r)
 def test_long_provider_deadline_means_zero_calls(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'repair-start-request.json',self.req())
   with patch.object(s,'DATA',data),patch.object(s,'OUT',out),patch.object(s,'authorized',return_value=True),patch.object(s,'update'),patch.object(s,'circuit_open',return_value=True),patch.object(s,'deadline',return_value=time.time()+7200),patch('automation.agri_v2.cycle.run') as cycle:
    self.assertEqual(s.run()['model_calls'],0);cycle.assert_not_called()
 def test_one_invocation_then_preserve_reservation(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'repair-start-request.json',self.req())
   with patch.object(s,'DATA',data),patch.object(s,'OUT',out),patch.object(s,'authorized',return_value=True),patch.object(s,'update'),patch.object(s,'circuit_open',return_value=False),patch('automation.agri_v2.cycle.run',return_value={'status':'fixture'}) as cycle:
    self.assertEqual(s.run()['status'],'cycle_finished');self.assertEqual(s.run()['model_calls'],0);self.assertEqual(cycle.call_count,1)
 def test_failure_is_sanitized_and_never_retried(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'repair-start-request.json',self.req())
   with patch.object(s,'DATA',data),patch.object(s,'OUT',out),patch.object(s,'authorized',return_value=True),patch.object(s,'update'),patch.object(s,'failed'),patch.object(s,'circuit_open',return_value=False),patch('automation.agri_v2.cycle.run',side_effect=ValueError('private secret')) as cycle:
    row=s.run();self.assertEqual(row['failure']['kind'],'validation');self.assertNotIn('private',str(row));s.run();self.assertEqual(cycle.call_count,1)
