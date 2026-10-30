"""Offline regressions; no credentials, provider requests or publication."""
import copy,json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from parsiblog_text import render_city_token
from city_backlink_policy import Inspect
from agnes_key_pool import AgnesProviderError
class CityMarkupTests(unittest.TestCase):
 def test_exact_placeholder_forms_render_before_html_qa(self):
  for token in ('<AFP_CITY>','<AFP_CITY/>','<AFP_CITY />','<AFP_CITY></AFP_CITY>','<afp_city>'):
   post={'html':'<p>در '+token+' اطلاعات زمین را ثبت کنید.</p>','slug':'AFP_CITY','title':'عنوان ثابت'}
   self.assertEqual(render_city_token({'city_fa':'هندیجان'},post),1)
   parser=Inspect();parser.feed(post['html']);self.assertEqual(parser.errors,[]);self.assertIn('هندیجان',post['html']);self.assertEqual(post['slug'],'AFP_CITY');self.assertEqual(post['title'],'عنوان ثابت')
   before=copy.deepcopy(post);self.assertEqual(render_city_token({'city_fa':'هندیجان'},post),0);self.assertEqual(post,before)
 def test_nonempty_attributed_and_unknown_tags_still_fail_html_qa(self):
  for token in ('<AFP_CITY>ادعای دیگر</AFP_CITY>','<AFP_CITY onclick="x">','<AFP_CITY_OTHER>','<script>x</script>'):
   post={'html':'<p>'+token+'</p>'};before=copy.deepcopy(post)
   self.assertEqual(render_city_token({'city_fa':'هندیجان'},post),0);self.assertEqual(post,before)
   parser=Inspect();parser.feed(post['html']);self.assertTrue(parser.errors)
class ProviderLimitTests(unittest.TestCase):
 def base(self):return SimpleNamespace(AGNES_KEYS=['offline-fixture'],AGNES_KEY='offline-fixture',AGNES_MODEL='test',AGNES_BASE='https://example.invalid',fetch_json=Mock(side_effect=AgnesProviderError(429,retry_after='300')))
 def test_json_client_propagates_429_once_without_repair_or_sleep(self):
  import agnes_json_client as c
  base=self.base()
  with patch.object(c.time,'sleep')as sleep,self.assertRaises(AgnesProviderError)as e:c.call(base,'offline',attempts=5)
  self.assertEqual(e.exception.rate_limit_retry_after_seconds,300);self.assertEqual(base.fetch_json.call_count,1);sleep.assert_not_called()
 def test_retry_wrapper_does_not_multiply_429_calls(self):
  import farsiblog_backlink_queue as f
  op=Mock(side_effect=AgnesProviderError(429))
  with patch.object(f.time,'sleep')as sleep,self.assertRaises(AgnesProviderError):f.retry_transient(op)
  op.assert_called_once();sleep.assert_not_called()
 def test_legacy_client_also_propagates_429_once(self):
  import roya_backlink_queue as r
  base=self.base();base.key_for_call=lambda:'offline-fixture'
  with patch.object(r,'agnes_client',None),patch.object(r,'BASE',base),patch.object(r.time,'sleep')as sleep,self.assertRaises(AgnesProviderError):r.agnes('offline')
  base.fetch_json.assert_called_once();sleep.assert_not_called()
class RemovalTests(unittest.TestCase):
 def test_drivers_workflows_queue_and_state_absent(self):
  for path in ('automation/blogfa_native.py','automation/blogfa_backlink_queue.py','automation/publish_blogfa_posts.py','.github/workflows/blogfa-content.yml','.github/workflows/blogfa-login-diagnostic.yml','.github/workflows/retire-blogfa.yml','data/blogfa/backlink-queue.json','state/blogfa-backlink-progress.json'):
   self.assertFalse((ROOT/path).exists(),path)
 def test_no_active_routing_but_obsolete_caller_denied(self):
  import city_backlink_policy as c,blog_generated_image as g
  from check_blog_pipeline_control import BLOGS,decision
  for blogs in (c.BLOGS,c.ANGLES,g.BLOGS,BLOGS):self.assertNotIn('blogfa',blogs)
  self.assertFalse(decision('blogfa',ROOT)['proceed'])
  matrix=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for table in ('templates','article_templates'):self.assertNotIn('blogfa',matrix[table])
 def test_requests_and_report_are_safe(self):
  for p in (ROOT/'data/blog-image-stock/requests').glob('*.json'):self.assertNotEqual(json.loads(p.read_text()).get('blog'),'blogfa')
  report=json.loads((ROOT/'docs/generator-removal-repair-2026-10-30.json').read_text());self.assertFalse(report['native_account_contacted']);self.assertFalse(report['live_generation_triggered'])
if __name__=='__main__':unittest.main()
