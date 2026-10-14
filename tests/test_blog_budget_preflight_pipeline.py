import datetime as dt,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from check_blog_run_budget import decision
class BudgetPreflightTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'state').mkdir();self.now=dt.datetime(2026,10,14,13,tzinfo=dt.timezone.utc)
 def tearDown(self):self.tmp.cleanup()
 def write(self,rows):
  for blog in ('farsiblog','rozblog'):(self.root/'state'/(blog+'-backlink-progress.json')).write_text(json.dumps({'published':rows}))
 def test_full_budget_skips_expensive_steps(self):
  self.write([{'at':'2026-10-14T12:50:00Z'}]*3)
  for blog in ('farsiblog','rozblog'):
   d=decision(blog,self.root,self.now);self.assertFalse(d['proceed']);self.assertEqual(d['remaining'],0);self.assertEqual(d['next_eligible_at'],'2026-10-14T13:50:00+00:00')
 def test_expired_history_resumes_automatically(self):
  self.write([{'at':'2026-10-14T11:59:59Z'}]*3);self.assertTrue(decision('farsiblog',self.root,self.now)['proceed'])
 def test_invalid_history_does_not_bypass_limit(self):
  self.write([{'at':'invalid'}])
  with self.assertRaises(RuntimeError):decision('farsiblog',self.root,self.now)
 def test_readonly_diagnostic_can_proceed_without_publication(self):
  self.write([{'at':'2026-10-14T12:50:00Z'}]*3);d=decision('rozblog',self.root,self.now,force=True);self.assertTrue(d['proceed']);self.assertEqual(d['remaining'],0)

class NativeSubmissionPreflightTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);p=self.root/'artifacts/blogfa-backlink-queue';p.mkdir(parents=True);(p/'submission-attempts.json').write_text(json.dumps({'draft-key':{'phase':'unconfirmed','at':'2026-10-14T21:32:09Z'}}))
 def tearDown(self):self.tmp.cleanup()
 def test_uncertain_blogfa_auto_run_stops_before_costly_steps(self):
  d=decision('blogfa',self.root);self.assertFalse(d['proceed']);self.assertEqual(d['reason'],'native_reconciliation_required');self.assertEqual(d['blocked_keys'],['draft-key']);self.assertEqual(d['remaining'],3)
 def test_named_manual_recovery_can_check_existing_public_record(self):self.assertTrue(decision('blogfa',self.root,target='draft-key')['proceed'])
 def test_readonly_login_diagnostic_still_allowed(self):self.assertTrue(decision('blogfa',self.root,force=True)['proceed'])
 def test_other_blogs_are_not_paused(self):
  for blog in ('farsiblog','rozblog'):self.assertTrue(decision(blog,self.root)['proceed'])
