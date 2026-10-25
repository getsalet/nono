import tempfile,unittest,inspect
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import safe_activation as a,cycle
from automation.agri_v2.queue import atomic_json
class SafeActivationTests(unittest.TestCase):
 def test_no_authorization_no_activation(self):
  with tempfile.TemporaryDirectory() as d,patch.object(a,'DATA',Path(d)):self.assertFalse(a.authorized())
 def test_unconditional_activation_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   atomic_json(Path(d)/'safe-activation-request.json',{'request_id':a.ID,'authorized':True,'mode':'publish_everything'})
   with patch.object(a,'DATA',Path(d)),self.assertRaises(ValueError):a.authorized()
 def test_pending_tuning_not_skipped(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'image-tuning-resume-request.json',{'backtest_request_id':'fixture'})
   with patch.object(a,'DATA',data),patch.object(a,'OUT',out):self.assertFalse(a.skip_completed_tuning())
 def test_finished_tuning_can_be_bypassed_only_with_separate_activation_gate(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'image-tuning-resume-request.json',{'backtest_request_id':'fixture'});atomic_json(out/'image-backtests/fixture/report.json',{'status':'stopped_provider_limit_or_failure'})
   with patch.object(a,'DATA',data),patch.object(a,'OUT',out):self.assertTrue(a.skip_completed_tuning())
 def test_source_ready_cycle_no_longer_runs_unbudgeted_full_audit(self):
  source=inspect.getsource(cycle.run);self.assertNotIn('report=audit()',source);self.assertIn('health_evidence_expired',source)
