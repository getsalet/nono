import tempfile,unittest,time
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import supervised_replay as s
from automation.agri_v2.queue import DATA,atomic_json,load_json
class SupervisedReplayTests(unittest.TestCase):
 def setup(self,d):
  data=Path(d)/'data';out=Path(d)/'out';req=load_json(DATA/'one-hour-supervision-request.json');req['window_end_epoch']=time.time()+120;atomic_json(data/'one-hour-supervision-request.json',req);atomic_json(data/'image-tuning-resume-request.json',{'request_id':'verified-pool-scene-resume-v1','not_before_epoch':0});atomic_json(out/'provider-circuit.json',{'open':False});return data,out
 def test_existing_request_invoked_once_no_new_budget(self):
  with tempfile.TemporaryDirectory() as d:
   data,out=self.setup(d)
   with patch.object(s,'DATA',data),patch.object(s,'OUT',out),patch.object(s,'circuit_open',return_value=False),patch.object(s,'resume',return_value={'status':'fixture'}) as run:
    s.run();s.run();self.assertEqual(run.call_count,1)
 def test_window_expiry_without_admission_has_no_calls(self):
  with tempfile.TemporaryDirectory() as d:
   data,out=self.setup(d);req=load_json(data/'one-hour-supervision-request.json');req['window_end_epoch']=0;atomic_json(data/'one-hour-supervision-request.json',req)
   with patch.object(s,'DATA',data),patch.object(s,'OUT',out),patch.object(s,'resume') as run:
    self.assertEqual(s.run()['status'],'window_ended_before_admission');run.assert_not_called()
