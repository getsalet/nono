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
 def test_owner_start_preserves_hold_and_binds_policy_and_proof(self):
  import copy,hashlib
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out'
   proof=out/'activation-health/one-hour-activation-health-v1/report.json'
   atomic_json(proof,{'article_validation_passed':True,'post_mutations':0,'wordpress_connection':{'can_publish':True}})
   config={'publication_holds':{a.TOPIC:{'reason':'failed pilot'}},'max_posts_per_run':1,'automatic_generation':True,'publication_enabled':True}
   atomic_json(data/'config.json',config);atomic_json(data/'health/latest.json',{'image_model':a.IMAGE_MODEL,'eligible_image_slots':['AGNES_API_KEY3']})
   req={'request_id':a.OWNER_ID,'authorized':True,'mode':'source_ready_gt90_critical_checks','score_strictly_greater_than':90,'review_policy':a.REVIEW_POLICY,'max_posts_per_run':1,'preserve_publication_holds':True,'readiness_report_sha256':hashlib.sha256(proof.read_bytes()).hexdigest()}
   def save(value):atomic_json(data/'safe-activation-request.json',value)
   with patch.object(a,'OUT',out):
    save(req);self.assertTrue(a.authorized(data))
    for key,value in [('authorized',False),('score_strictly_greater_than',89),('review_policy','old'),('max_posts_per_run',2),('preserve_publication_holds',False),('readiness_report_sha256','wrong')]:
     bad=copy.deepcopy(req);bad[key]=value;save(bad)
     with self.assertRaises(ValueError,msg=key):a.authorized(data)
    save(req);config['publication_holds']={};atomic_json(data/'config.json',config)
    with self.assertRaises(ValueError):a.authorized(data)
