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
 def test_missing_native_table_is_not_treated_as_empty_blog(self):
  page=Mock();page.url='https://www.rozblog.com/panel140163524/admin_post';page.wait_for_selector.side_effect=RuntimeError('native table absent')
  with self.assertRaises(RuntimeError):self.publisher.scan(page,page.url)
 def test_native_submit_arms_navigation_before_click(self):
  import inspect
  source=inspect.getsource(self.publisher.main)
  self.assertIn("with page.expect_navigation(wait_until='domcontentloaded',timeout=60000):",source)
  self.assertNotIn("click();page.wait_for_load_state",source)
 def test_custom_native_public_url_is_not_assumed_to_contain_post_id(self):
  row={'row_id':'tr_1','checkbox_id':'1','title':'عنوان واقعی','url':'https://afp-pipe.rozblog.com/custom-title-kmbuy'}
  self.assertEqual(self.publisher.post_records([row]),{'عنوان واقعی':{'pid':1,'url':row['url']}})
 def test_partial_or_wrong_blog_post_rows_fail_closed(self):
  row={'row_id':'tr_1','checkbox_id':'1','title':'عنوان واقعی','url':'https://afp-pipe.rozblog.com/custom-title-kmbuy'}
  for patch in ({'checkbox_id':'2'},{'title':''},{'url':'https://spadan1.rozblog.com/custom'},{'row_id':'invalid'}):
   with self.assertRaises(RuntimeError):self.publisher.post_records([{**row,**patch}])
 def test_duplicate_native_title_is_ambiguous(self):
  row={'row_id':'tr_1','checkbox_id':'1','title':'عنوان واقعی','url':'https://afp-pipe.rozblog.com/custom-title-kmbuy'}
  with self.assertRaises(RuntimeError):self.publisher.post_records([row,{**row,'row_id':'tr_2','checkbox_id':'2','url':'https://afp-pipe.rozblog.com/other'}])
 def test_confirmation_retries_read_only_and_never_submits_twice(self):
  from unittest.mock import patch
  record={'pid':1,'url':'https://afp-pipe.rozblog.com/custom'};page=Mock()
  with patch.object(self.publisher,'scan',side_effect=[{}, {'عنوان':record}])as scan,patch.object(self.publisher.time,'sleep'):
   self.assertEqual(self.publisher.confirm_post(page,'posts','عنوان'),({'عنوان':record},record));self.assertEqual(scan.call_count,2)
  page.get_by_role.assert_not_called()
 def test_native_feedback_requires_explicit_saved_message(self):
  self.assertTrue(self.publisher.native_save_feedback('مطلب با موفقیت ارسال شد')['success'])
  self.assertFalse(self.publisher.native_save_feedback('خطا در ثبت مطلب؛ دوباره بررسی کنید')['success'])
 def test_uncertain_prior_submission_blocks_any_new_post(self):
  from unittest.mock import patch
  entry={'key':'fixture'}
  with patch.object(self.publisher.engine,'load',return_value={'fixture':{'phase':'unconfirmed'}}),patch.object(self.publisher.engine,'save')as save:
   with self.assertRaises(RuntimeError):self.publisher.begin_submission(entry,'عنوان')
   save.assert_not_called()
 def test_login_waits_for_authenticated_menu_before_reading_links(self):
  import inspect
  source=inspect.getsource(self.publisher.wait_for_native_menu)
  self.assertIn('a[href$="/list_site"]',source)
 def test_menu_reload_is_bounded_and_does_not_repeat_signin(self):
  from unittest.mock import patch
  page=Mock();page.url='https://www.rozblog.com/usercp.php';page.wait_for_selector.side_effect=[RuntimeError('transient empty menu'),None]
  with patch.object(self.publisher.time,'sleep'):
   self.publisher.wait_for_native_menu(page)
  page.goto.assert_called_once_with('https://www.rozblog.com/usercp.php',wait_until='domcontentloaded',timeout=60000)
  page.get_by_role.assert_not_called()
 def test_reloads_stop_when_session_has_expired(self):
  from unittest.mock import patch
  page=Mock();page.url='https://www.rozblog.com/login.php';page.wait_for_selector.side_effect=RuntimeError('missing menu')
  with patch.object(self.publisher.time,'sleep'):
   with self.assertRaises(RuntimeError):self.publisher.wait_for_native_menu(page)
  self.assertEqual(page.goto.call_count,1)
 def test_each_blog_preserves_recovery_artifacts(self):
  for blog in ('farsiblog','rozblog'):
   config=(ROOT/'.github/workflows'/f'{blog}-content.yml').read_text()
   self.assertIn('uses: actions/upload-artifact@v4',config);self.assertIn('github.run_attempt',config);self.assertIn('git diff --name-only',config)
 def test_source_cache_is_inside_checkpoint_artifact(self):
  import inspect
  self.assertIn("source_lookup.IMAGE_CACHE=ART/'image-cache.json'",inspect.getsource(self.engine.main))
if __name__=='__main__':unittest.main()
