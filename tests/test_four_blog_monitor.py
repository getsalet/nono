import unittest,sys,datetime as dt
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import monitor_four_blogs as m
class MonitorGuards(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,14,16,tzinfo=dt.timezone.utc)
  self.row={'public':{'http_status':200},'workflows':[{'status':'completed','conclusion':'success'}],'remaining_hourly_budget':3,'publication_age_minutes':80,'ready_count':1}
 def test_article_timeout_blocks_recovery_without_erasing_homepage(self):
  self.row['latest_article']={'unverified':'TimeoutError'}
  self.assertIsNone(m.recovery_plan('rozblog',self.row,self.now,{},True)[0]);self.assertEqual(self.row['public']['http_status'],200)
 def test_read_timeout_uses_public_browser_only(self):
  class Page:
   closed=False
   def goto(self,*a,**kw):return type('Response',(),{'status':200})()
   def wait_for_selector(self,*a,**kw):pass
   def content(self):return '<div class="post-content">مقاله</div>'
   def close(self):self.closed=True
  page=Page()
  class Context:
   def new_page(self):return page
  with patch.object(m,'request',side_effect=TimeoutError),patch.object(m,'PUBLIC_BROWSER',object()),patch.object(m,'PUBLIC_CONTEXT',Context()):
   status,body=m.public_read('https://afp-pipe.rozblog.com/actual-native-slug');self.assertEqual(status,200);self.assertIn('مقاله',body);self.assertTrue(page.closed)
 def test_budget_idle_not_recovery(self):
  self.row['remaining_hourly_budget']=0;self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_running_not_duplicate_dispatch(self):
  self.row['workflows'][0]['status']='in_progress';self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_optin_required(self):self.assertIsNone(m.recovery_plan('blogfa',self.row,self.now,{},False)[0])
 def test_unverified_not_guessed(self):
  self.row['public']['unverified']='HTTPError';self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,{},True)[0])
 def test_ready_recovery_no_new_generation(self):
  p,_=m.recovery_plan('farsiblog',self.row,self.now,{},True);self.assertEqual(p['inputs']['count'],'0')
 def test_window_limit(self):
  previous={'farsiblog':{'at':m.iso(self.now-dt.timedelta(hours=2)),'count':2}}
  self.assertIsNone(m.recovery_plan('farsiblog',self.row,self.now,previous,True)[0])
 def test_aware_budget(self):
  rows=[{'at':m.iso(self.now-dt.timedelta(minutes=i))}for i in (10,20,30)]
  b=m.recent_budget('farsiblog',rows,self.now);self.assertEqual(b['remaining_hourly_budget'],0)
 def test_naive_dates_block(self):
  with self.assertRaises(ValueError):m.instant('2026-10-14T16:00:00')
 def test_native_div_cards_and_custom_post_urls(self):
  p=m.Titles();p.feed('<div class="post-card"><div><img src="x"></div><h2><a href="/p/21/test.html">عنوان</a></h2></div>');self.assertEqual(p.posts[0]['url'],'/p/21/test.html')
 def test_rechecks_edited_latest_article(self):
  source=(Path(__file__).resolve().parents[1]/'automation/monitor_four_blogs.py').read_text();self.assertNotIn('if u not in article_cache:',source)
 def test_parser_ignores_faq_heading(self):
  p=m.Titles();p.feed('<article class="post-card"><h2><a href="https://afp-pipe.blogfa.com/post/1">عنوان</a></h2><h2><a href="/post/2">نباید عنوان دوم بشود</a></h2></article>')
  self.assertEqual(len(p.posts),1)
