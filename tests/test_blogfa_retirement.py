"""Retirement must prevent provider/browser/account calls, not just hide a menu."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
class BlogfaRetirementTests(unittest.TestCase):
 def test_active_control_and_dispatch_monitors_exclude_blogfa(self):
  from check_blog_pipeline_control import decision
  import activate_blog_publication as a,monitor_blog_generators_one_hour as h,monitor_four_blogs as m
  c=json.loads((ROOT/'data/blog-generated-image-control.json').read_text())
  self.assertIn('blogfa',c['retired_blogs']);self.assertNotIn('blogfa',c['blogs'])
  self.assertFalse(decision('blogfa',ROOT)['proceed'])
  for active in (a.WORKFLOWS,h.WORKFLOWS,h.PUBLIC_BLOGS,m.BLOGS):self.assertNotIn('blogfa',active)
  self.assertIsNone(m.recovery_plan('blogfa',{},None,{},True)[0])
 def test_native_login_and_main_cannot_touch_page(self):
  import blogfa_native as n
  page=Mock()
  with self.assertRaisesRegex(RuntimeError,'retired'):n.login(page)
  self.assertEqual(page.mock_calls,[]);self.assertEqual(n.main(),0)
 def test_direct_publisher_returns_before_queue_or_api(self):
  import publish_blogfa_posts as p
  with patch.object(p,'matrix_ready',side_effect=AssertionError('Must not access queue')),patch('blog_image_runtime_control.publication_paused',return_value=False):
   self.assertEqual(p.main(),0)
 def test_queue_and_shared_engine_return_without_generation(self):
  import blogfa_backlink_queue as q, farsiblog_backlink_queue as e
  self.assertEqual(q.main(),0)
  with patch.object(e,'CITY_BLOG','blogfa'),patch('blog_image_runtime_control.generation_paused',side_effect=AssertionError('No generation preflight needed')):
   self.assertEqual(e.main(),0)
 def test_direct_images_and_stock_cannot_run(self):
  import blog_generated_image as g,blog_image_stock as s
  with patch.object(g,'existing_asset',side_effect=AssertionError('No I/O')),patch.object(g.roya.BASE._key_pool,'fetch_json')as api:
   for call in (lambda:g.generate({},'blogfa'),lambda:g._generate({},'blogfa'),lambda:g.prepare({},'blogfa',ROOT),lambda:g.prepare_now({},'blogfa',ROOT),lambda:s.request_image({},'blogfa',ROOT)):
    with self.assertRaisesRegex(RuntimeError,'retired'):call()
   api.assert_not_called()
  self.assertFalse(g.rollout_enabled('blogfa',ROOT))
 def test_originality_preserves_history_without_blogfa_network_fallback(self):
  from content_originality import published_snapshot
  with tempfile.TemporaryDirectory()as tmp,patch('urllib.request.urlopen',side_effect=AssertionError('No Blogfa network'))as request:
   with self.assertRaisesRegex(RuntimeError,'local-cache only'):published_snapshot(Path(tmp),'blogfa',{'key':'old','published_url':'https://afp-pipe.blogfa.com/post/1'})
   request.assert_not_called()
 def test_both_workflows_have_no_automatic_trigger_and_all_jobs_false(self):
  for name,num in (('blogfa-content.yml',2),('blogfa-login-diagnostic.yml',1)):
   src=(ROOT/'.github/workflows'/name).read_text()
   self.assertNotIn('schedule:',src);self.assertNotIn('  push:',src)
   self.assertEqual(src.count('if: ${{ false }}'),num)
if __name__=='__main__':unittest.main()
