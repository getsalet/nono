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
