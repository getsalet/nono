import tempfile,unittest,inspect
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import tuning_resume as t,image_backtest as b
from automation.agri_v2.queue import DATA,atomic_json,load_json
class WatchSafetyTests(unittest.TestCase):
 def test_provider_failure_is_not_displayed_as_quality_success(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';r=load_json(DATA/'image-tuning-resume-request.json');atomic_json(data/'image-tuning-resume-request.json',r);atomic_json(out/'image-backtests'/r['backtest_request_id']/'report.json',{'status':'stopped_provider_limit_or_failure'})
   with patch.object(t,'DATA',data),patch.object(t,'OUT',out),patch.object(t,'circuit_open',return_value=True),patch.object(t,'update') as update,patch.object(b,'run') as backtest:
    t.run();self.assertEqual(update.call_args.kwargs['status'],'provider_cooldown');self.assertEqual(update.call_args.args[1],15);backtest.assert_not_called()
 def test_expired_cooldown_does_not_automatically_retry_reserved_failure(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';r=load_json(DATA/'image-tuning-resume-request.json');atomic_json(data/'image-tuning-resume-request.json',r);atomic_json(out/'image-backtests'/r['backtest_request_id']/'report.json',{'status':'stopped_provider_limit_or_failure'})
   with patch.object(t,'DATA',data),patch.object(t,'OUT',out),patch.object(t,'circuit_open',return_value=False),patch.object(t,'update') as update,patch.object(b,'run') as backtest:
    t.run();self.assertEqual(update.call_args.kwargs['status'],'awaiting_provider_recovery');backtest.assert_not_called()
 def test_uncertain_generation_does_not_continue_to_another_role_key(self):
  # Guard the exception branch that had continued into the next paid role.
  source=inspect.getsource(b.run);branch=source.split("except Exception as exc:\n    row.update(status='generation_failed'",1)[1].split('finally:',1)[0]
  self.assertIn('return report',branch);self.assertNotIn('continue',branch)
