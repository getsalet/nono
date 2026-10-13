import importlib,sys,unittest
from pathlib import Path
from unittest.mock import Mock
from contextlib import nullcontext
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
class DestinationTests(unittest.TestCase):
 def setUp(self):
  import farsiblog_backlink_queue as engine
  import publish_roya_posts as state
  self.engine=engine;self.state=state
  self.saved_engine={k:getattr(engine,k)for k in ('CITY_BLOG','BLOG','QUEUE','ART','STATE')}
  self.saved_state={k:getattr(state,k)for k in ('QUEUE','ART','PUBLISH_QUEUE','STATE','LOG','EXPORT')}
  self.publisher=importlib.import_module('publish_rozblog_posts')
  self.routes=['http://afp-pipe.rozblog.com/','https://www.rozblog.com/panel140163524/admin_post','https://www.rozblog.com/panel140163524/new_post']
 def tearDown(self):
  for obj,values in ((self.engine,self.saved_engine),(self.state,self.saved_state)):
   for k,v in values.items():setattr(obj,k,v)
 def page(self,urls,url='https://www.rozblog.com/usercp.php'):
  page=Mock();page.url=url;page.locator.return_value.evaluate_all.return_value=urls;return page
 def test_expected_host_and_matching_routes_pass(self):
  self.assertEqual(self.publisher.active(self.page(self.routes)),tuple(self.routes[1:]))
 def test_wrong_or_lookalike_host_fails(self):
  for host in ('spadan1.rozblog.com','drip-irrigation.rozblog.com','afp-pipe.rozblog.com.example.org'):
   with self.assertRaises(RuntimeError):self.publisher.active(self.page(['https://'+host+'/']+self.routes[1:]))
 def test_empty_account_switch_document_fails_closed(self):
  with self.assertRaises(RuntimeError):self.publisher.active(self.page(self.routes,'https://www.rozblog.com/panel140163524/list_site?change_accont=800519'))
 def test_mismatched_or_ambiguous_routes_fail(self):
  for routes in (self.routes[:2]+['https://www.rozblog.com/panel999/new_post'],self.routes+['https://www.rozblog.com/panel999/new_post'],self.routes[:2]+['https://example.org/panel140163524/new_post']):
   with self.assertRaises(RuntimeError):self.publisher.active(self.page(routes))
 def test_selection_reopens_protected_panel_before_identity_check(self):
  page=Mock();page.url='';events=[];links=Mock();choice=Mock();manage=Mock()
  choice.count.return_value=1;manage.count.return_value=1;choice.get_by_role.return_value=manage
  links.filter.return_value=choice
  def goto(url,**kwargs):
   page.url=url;events.append(('goto',url))
   links.evaluate_all.return_value=(self.routes+['https://www.rozblog.com/panel140163524/list_site'])if url.endswith('/usercp.php')else['https://afp-pipe.rozblog.com/']
  def click():page.url='https://www.rozblog.com/panel140163524/list_site?change_accont=800519';links.evaluate_all.return_value=[];events.append(('select',page.url))
  page.goto.side_effect=goto;page.locator.return_value=links;page.expect_navigation.return_value=nullcontext();manage.click.side_effect=click
  self.assertEqual(self.publisher.login(page),tuple(self.routes[1:]));self.assertEqual(events[-1],('goto','https://www.rozblog.com/usercp.php'));manage.click.assert_called_once()
 def test_each_blog_preserves_recovery_artifacts(self):
  for blog in ('farsiblog','rozblog'):
   config=(ROOT/'.github/workflows'/f'{blog}-content.yml').read_text()
   self.assertIn('uses: actions/upload-artifact@v4',config);self.assertIn('github.run_attempt',config);self.assertIn('git diff --name-only',config)
 def test_source_cache_is_inside_checkpoint_artifact(self):
  import inspect
  self.assertIn("source_lookup.IMAGE_CACHE=ART/'image-cache.json'",inspect.getsource(self.engine.main))
if __name__=='__main__':unittest.main()
