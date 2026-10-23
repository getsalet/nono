import datetime as dt,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
class TwoPostLimitTests(unittest.TestCase):
 def test_shared_budget_two_in_rolling_hour_not_calendar_hour(self):
  from farsiblog_backlink_queue import remaining_publication_budget
  now=dt.datetime(2026,10,23,19,tzinfo=dt.timezone.utc)
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'state.json'
   for minutes,want in [([],2),([59],1),([21,59],0),([21,61],1),([1,2,3],0)]:
    p.write_text(json.dumps({'published':[{'at':(now-dt.timedelta(minutes=n)).isoformat()}for n in minutes]}))
    self.assertEqual(remaining_publication_budget(p,now),want)
 def test_roya_budget_exhausted_never_opens_browser(self):
  import publish_roya_posts as p
  with patch.object(p,'BLOG','https://afp.royablog.ir'),patch.object(p,'roya_hourly_budget',return_value=0),patch('playwright.sync_api.sync_playwright',side_effect=AssertionError('No browser')):
   self.assertEqual(p.publish([{'key':'fixture'}]),0)
 def test_roya_rechecks_before_every_new_native_post(self):
  import inspect,publish_roya_posts as p
  text=inspect.getsource(p.publish)
  self.assertIn("if BLOG=='https://afp.royablog.ir' and not roya_hourly_budget()",text)
if __name__=='__main__':unittest.main()
