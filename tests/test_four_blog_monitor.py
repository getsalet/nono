import unittest,sys,datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import monitor_four_blogs as m
class MonitorGuards(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,14,16,tzinfo=dt.timezone.utc)
  self.row={'public':{'http_status':200},'workflows':[{'status':'completed','conclusion':'success'}],'remaining_hourly_budget':3,'publication_age_minutes':80,'ready_count':1}
 def test_budget_idle_not_recovery(self):
  self.row['remaining_hourly_budget']=0;self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_running_not_duplicate_dispatch(self):
  self.row['workflows'][0]['status']='in_progress';self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_optin_required(self):self.assertIsNone(m.recovery_plan('blogfa',self.row,self.now,{},False)[0])
 def test_unverified_not_guessed(self):
  self.row['public']['unverified']='HTTPError';self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_ready_recovery_no_new_generation(self):
  p,_=m.recovery_plan('blogfa',self.row,self.now,{},True);self.assertEqual(p['inputs']['count'],'0')
 def test_window_limit(self):
  previous={'farsiblog':{'at':m.iso(self.now-dt.timedelta(hours=2)),'count':2}}
  self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,previous,True)[0])
 def test_aware_budget(self):
  rows=[{'at':m.iso(self.now-dt.timedelta(minutes=i))}for i in (10,20,30)]
  b=m.recent_budget('farsiblog',rows,self.now);self.assertEqual(b['remaining_hourly_budget'],0)
 def test_naive_dates_block(self):
  with self.assertRaises(ValueError):m.instant('2026-10-14T16:00:00')
 def test_parser_ignores_faq_heading(self):
  p=m.Titles();p.feed('<article class="post-card"><h2><a href="https://afp-pipe.blogfa.com/post/1">عنوان</a></h2><h2><a href="/post/2">نباید عنوان دوم بشود</a></h2></article>')
  self.assertEqual(len(p.posts),1)
