import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_hose_trial import decision
class HoseTrialTests(unittest.TestCase):
 def cfg(self):return {'enabled':True,'trial_id':'test','maximum_requests':3,'minimum_interval_seconds':1200,'expires_at_epoch':10000,'baseline_runs':['39086561494'],'baseline_last_attempt_epoch':100}
 def base(self):return {'workflow_run_id':'39086561494','image_received':False,'provider_attempts':[{'http_status':503,'provider_code':'image_queue_full'}]}
 def test_spacing_and_expiry(self):
  self.assertEqual(decision(self.cfg(),[self.base()],1299),'trial_spacing')
  self.assertEqual(decision(self.cfg(),[self.base()],1300),'allowed')
  self.assertEqual(decision(self.cfg(),[self.base()],10000),'expired')
 def test_stops_on_real_candidate(self):
  b=self.base();b['image_received']=True;self.assertEqual(decision(self.cfg(),[b],2000),'candidate_received')
 def test_reserved_uncertain_attempts_consume_budget(self):
  rows=[self.base(),{'trial_id':'test','provider_request_reserved':True},{'trial_id':'test','provider_request_reserved':True}]
  self.assertEqual(decision(self.cfg(),rows,9000),'request_budget_exhausted')
 def test_no_double_counting_completed_reservation(self):
  rows=[self.base(),{'trial_id':'test','provider_request_reserved':True,'trial_attempt_at_epoch':1400,'provider_attempts':[{'http_status':503}]}]
  self.assertEqual(decision(self.cfg(),rows,2600),'allowed')
 def test_account_limits_stop_trials(self):
  for code in (401,402,403,429):
   b=self.base();b['provider_attempts'][0]['http_status']=code
   self.assertEqual(decision(self.cfg(),[b],2000),'provider_limit_requires_review')
 def test_no_reuse_of_unrelated_old_candidates_or_missing_baseline(self):
  self.assertEqual(decision(self.cfg(),[self.base(),{'workflow_run_id':'old','image_received':True}],2000),'allowed')
  with self.assertRaises(RuntimeError):decision(self.cfg(),[],2000)
if __name__=='__main__':unittest.main()
