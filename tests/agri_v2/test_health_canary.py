import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import health_canary as c
from automation.agri_v2.queue import DATA,atomic_json,load_json
class HealthCanaryTests(unittest.TestCase):
 def req(self):return load_json(DATA/'health-canary-request.json')
 def test_exact_one_image_zero_mutations(self):
  r=self.req();c.validate(r);r['max_image_calls']=2
  with self.assertRaises(ValueError):c.validate(r)
 def test_expired_window_no_model_calls(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';r=self.req();r['window_end_epoch']=0;atomic_json(data/'health-canary-request.json',r)
   with patch.object(c,'DATA',data),patch.object(c,'OUT',out),patch.object(c,'update'),patch.object(c,'ModelClient') as model:
    self.assertEqual(c.run()['status'],'window_ended_before_admission');model.assert_not_called()
 def test_report_never_retried(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';r=self.req();atomic_json(data/'health-canary-request.json',r);atomic_json(out/'health-canary'/c.ID/'report.json',{'status':'provider_still_blocked'})
   with patch.object(c,'DATA',data),patch.object(c,'OUT',out),patch.object(c,'ModelClient') as model:
    self.assertEqual(c.run()['model_calls'],0);model.assert_not_called()
