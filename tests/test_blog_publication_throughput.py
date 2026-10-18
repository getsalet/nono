"""Only real native verification checkpoints count toward the rolling target."""
import copy,datetime as dt,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_publication_throughput as t
class PublicationThroughputTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,18,5,tzinfo=dt.timezone.utc)
  self.states={b:{'published':[]}for b in t.BLOGS}
 def row(self,blog='roya',pid=1,minutes=5,**extra):
  return {'key':'key-'+str(pid),'pid':pid,'url':'https://'+t.BLOGS[blog]+'/post/'+str(pid),'at':(self.now-dt.timedelta(minutes=minutes)).isoformat(),**extra}
 def test_zero_is_a_shortfall_even_if_workflow_is_successful(self):
  self.states['roya'].update(last_publish_run={'status':'success'},completed_keys=['a','b','c'])
  r=t.evaluate(self.states,self.now);self.assertEqual((r['count'],r['shortfall'],r['status']),(0,3,'target_shortfall'))
 def test_three_verified_posts_across_blogs_meet_target(self):
  for b in ('roya','farsiblog','loxblog'):self.states[b]['published']=[self.row(b)]
  r=t.evaluate(self.states,self.now);self.assertEqual((r['count'],r['status']),(3,'target_met'))
 def test_old_boundary_and_future_do_not_count(self):
  self.states['roya']['published']=[self.row(pid=1,minutes=30),self.row(pid=2,minutes=31),self.row(pid=3,minutes=-1),self.row(pid=4,minutes=0)]
  r=t.evaluate(self.states,self.now);self.assertEqual(r['count'],1);self.assertEqual(r['status'],'unverified')
 def test_duplicate_rows_and_later_revisions_are_not_new_posts(self):
  old=self.row(minutes=90);self.states['roya']['published']=[old,old,self.row(minutes=1),self.row(pid=2),self.row(pid=3,url=self.row(pid=2)['url'])]
  r=t.evaluate(self.states,self.now);self.assertEqual(r['count'],1)
 def test_missing_states_invalid_times_and_wrong_urls_never_assert_target(self):
  for bad in (None,{}, {'published':'success'},{'published':[self.row(at='ambiguous')]},{'published':[self.row(pid=True)]},{'published':[self.row(url='https://wrong.example/post/1')]}):
   states=copy.deepcopy(self.states);states['roya']=bad
   for b in ('farsiblog','rozblog','loxblog'):states[b]['published']=[self.row(b)]
   r=t.evaluate(states,self.now);self.assertEqual(r['status'],'unverified')
 def test_naive_timestamps_are_rejected(self):
  self.states['roya']['published']=[self.row(at='2026-10-18T04:59:00')]
  self.assertEqual(t.evaluate(self.states,self.now)['status'],'unverified')
  with self.assertRaises(ValueError):t.evaluate(self.states,self.now.replace(tzinfo=None))
 def test_blogfa_is_not_read_or_counted(self):
  self.states['blogfa']={'published':[self.row()]};self.assertEqual(t.evaluate(self.states,self.now)['count'],0)
 def test_recovered_existing_post_is_not_assumed_new_at_reconciliation_time(self):
  self.states['roya']['published']=[self.row(recovered_existing=True)]
  r=t.evaluate(self.states,self.now);self.assertEqual(r['count'],0);self.assertEqual(r['status'],'unverified')
 def test_main_is_read_only_and_shortfall_does_not_fail_handoff(self):
  with tempfile.TemporaryDirectory()as d,patch('blog_image_stock.refresh')as refresh,patch('blog_image_stock.read',side_effect=lambda root,path:self.states[path.split('/')[1].split('-')[0]]):
   self.assertEqual(t.main(Path(d)),0)
   r=json.loads((Path(d)/'artifacts/blog-throughput/latest.json').read_text());self.assertEqual(r['count'],0);refresh.assert_called_once()
 def test_worker_reports_target_without_extra_provider_or_native_actions(self):
  s=(ROOT/'.github/workflows/blog-image-stock.yml').read_text()
  self.assertIn('run: python automation/blog_publication_throughput.py',s)
  self.assertIn('artifacts/blog-throughput',s)
if __name__=='__main__':unittest.main()
