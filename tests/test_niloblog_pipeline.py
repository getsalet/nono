import datetime,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import niloblog_pipeline as m
class RuntimeTests(unittest.TestCase):
 def test_placeholder_binding_is_exact(self):
  b={'links':[{'url':'https://navar-abyari.ir/a','anchor':'a'},{'url':'https://navar-abyari.ir/','anchor':'b'}]}
  o=m.bind_links({'html':'<p><a href="AFP_LINK_1">a</a><a href="AFP_LINK_2">b</a></p>'},b)
  self.assertNotIn('AFP_LINK_',o['html']);self.assertIn('https://navar-abyari.ir/a',o['html'])
 def test_binding_does_not_hide_unknown_destinations(self):
  o=m.bind_links({'html':'<a href="https://evil.example/">x</a>'},{'links':[]})
  self.assertIn('https://evil.example/',o['html'])
 def test_native_body_round_trip(self):
  body='<p>متن فارسی <a href="https://navar-abyari.ir/a">راهنما</a></p><img src="https://navar-abyari.ir/a.webp" alt="رول نوار تیپ">'
  item={'post':{'html':body}};self.assertTrue(m.verify_stored_body(item,body)['webp_verified'])
  with self.assertRaises(ValueError):m.verify_stored_body(item,body.replace('راهنما','متن دیگر'))
 def test_provider_numeric_range_dash_sanitization_is_accepted(self):
  expected='<p>در سال ۱۴۰۴–۱۴۰۵ بررسی شد</p><img src="https://navar-abyari.ir/a.webp" alt="محصول">'
  actual='<p>در سال ۱۴۰۴ ۱۴۰۵ بررسی شد</p><img src="https://navar-abyari.ir/a.webp" alt="محصول">'
  self.assertTrue(m.verify_stored_body({'post':{'html':expected}},actual)['body_text_verified'])

 def test_native_video_must_not_disappear(self):
  body='<p>متن</p><img src="https://navar-abyari.ir/a.webp" alt="محصول"><video src="https://navar-abyari.ir/a.mp4" controls></video>'
  with self.assertRaises(ValueError):m.verify_stored_body({'post':{'html':body}},body.split('<video')[0])
 def test_two_per_rolling_hour(self):
  n=datetime.datetime.now(datetime.timezone.utc);s={'published':[{'at':(n-datetime.timedelta(minutes=5)).isoformat()},{'at':(n-datetime.timedelta(minutes=45)).isoformat()}]};self.assertEqual(m.budget(s,n),0)
  s['published'][1]['at']=(n-datetime.timedelta(minutes=61)).isoformat();self.assertEqual(m.budget(s,n),1)
 def test_invalid_clock_fails_closed(self):
  with self.assertRaises(ValueError):m.budget({'published':[{'at':'invalid'}]})
 def test_local_checkpoint_never_allows_publish(self):
  import unittest.mock as mock
  with tempfile.TemporaryDirectory() as d,mock.patch.object(m,'STATE',Path(d)/'state.json'),mock.patch.object(m,'A',Path(d)/'artifacts'),mock.patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}):
   with self.assertRaises(RuntimeError):m.checkpoint({'published':[]})
 def test_non_runner_checkpoint_does_not_mutate_any_state(self):
  import unittest.mock as mock
  with mock.patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}),mock.patch.object(m,'save') as save,mock.patch.object(m.subprocess,'run') as git:
   with self.assertRaises(RuntimeError):m.checkpoint({'published':[]})
   save.assert_not_called();git.assert_not_called()
 def test_initial_phase_not_live(self):
  c=json.loads((ROOT/'data/niloblog/runtime-control.json').read_text());self.assertEqual(c['rolling_hourly_limit'],2);self.assertTrue(c['publication_authorized_by_user']);self.assertIn(c['phase'],('draft_canary','live_canary','publish','native_server_blocked'))
 def test_public_intent_precedes_submit(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def publish_new',1)[1]
  self.assertLess(code.index("s['intent']={'key'"),code.index('submit_once(f)'))
  self.assertLess(code.index('checkpoint(s);recheck(s,True)'),code.index('submit_once(f)'))
 def test_native_extra_literal_n_is_rejected(self):
  body='<p>متن</p><img src="https://navar-abyari.ir/a.webp" alt="محصول">'
  with self.assertRaises(ValueError):m.verify_stored_body({'post':{'html':body}},body+'<p>nn</p>')
 def test_public_receipt_precedes_media_and_state_advance(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def publish_new',1)[1]
  self.assertLess(code.index('receipt=verify_public'),code.index('acknowledge('))
  self.assertLess(code.index('receipt=verify_public'),code.index("s['intent']=None"))
 def test_navigation_uses_observed_link_inside_ready_frame(self):
  import unittest.mock as mock
  page=mock.Mock();page.url='https://www.niloblog.com/management.php';link=page.get_by_text.return_value;link.count.return_value=1;link.get_attribute.return_value='desktop.php?a=observed';frame=mock.Mock()
  with mock.patch.object(m,'management_frame',return_value=frame):self.assertIs(m.navigate(page,'ارسال مطلب جدید'),frame)
  frame.goto.assert_called_once_with('https://www.niloblog.com/desktop.php?a=observed',wait_until='domcontentloaded',timeout=45000);link.click.assert_not_called()
 def test_navigation_rejects_unexpected_host(self):
  import unittest.mock as mock
  page=mock.Mock();page.url='https://www.niloblog.com/management.php';link=page.get_by_text.return_value;link.count.return_value=1;link.get_attribute.return_value='https://evil.example/desktop.php';frame=mock.Mock()
  with mock.patch.object(m,'management_frame',return_value=frame):
   with self.assertRaises(ValueError):m.navigate(page,'ارسال مطلب جدید')
  frame.goto.assert_not_called()
 def test_frame_waits_for_attachment(self):
  import unittest.mock as mock
  page=mock.Mock();slot=page.locator.return_value;slot.count.return_value=1;frame=slot.element_handle.return_value.content_frame.return_value
  self.assertIs(m.management_frame(page),frame);slot.wait_for.assert_called_once_with(state='attached',timeout=30000)
 def test_no_public_write_without_durable_checkpoint(self):
  import unittest.mock as mock
  page=mock.Mock();page.context.new_page.return_value.locator.return_value.all_inner_texts.return_value=[];item={'key':'example','post':{'title':'عنوان'}};state={}
  with mock.patch.object(m,'scan',return_value=None),mock.patch.object(m,'navigate'),mock.patch.object(m,'fill_form'),mock.patch.object(m,'verify_stored_body'),mock.patch.object(m,'checkpoint',side_effect=RuntimeError('not durable')),mock.patch.object(m,'submit_once') as submit:
   with self.assertRaises(RuntimeError):m.publish_new(page,item,state)
   submit.assert_not_called();self.assertEqual(state['intent']['operation'],'create_public_post')
 def test_public_receipt_failure_retains_intent_and_media(self):
  import unittest.mock as mock
  page=mock.Mock();page.context.new_page.return_value.locator.return_value.all_inner_texts.return_value=[];item={'key':'example','post':{'title':'عنوان'}};state={}
  with mock.patch.object(m,'scan',return_value=None),mock.patch.object(m,'navigate'),mock.patch.object(m,'fill_form'),mock.patch.object(m,'verify_stored_body'),mock.patch.object(m,'checkpoint'),mock.patch.object(m,'recheck'),mock.patch.object(m,'submit_once') as submit,mock.patch.object(m,'verify_public',side_effect=m.PipelineStop('missing receipt')),mock.patch.object(m,'acknowledge') as ack:
   with self.assertRaises(ValueError):m.publish_new(page,item,state)
   submit.assert_called_once();ack.assert_not_called();self.assertIsNotNone(state['intent'])
 def test_native_editor_readback_guards_uninitialized_library(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def edit_existing',1)[1].split('def native_readback',1)[0]
  self.assertIn('typeof CKEDITOR!=="undefined"',code)
 def test_login_never_clicks_unscoped_ad_close_glyph(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def login(',1)[1].split('def management_frame',1)[0]
  self.assertNotIn("get_by_text('×'",code)
 def test_public_verification_uses_explicit_multi_page_context(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def main():',1)[1]
  self.assertIn('context=browser.new_context()',code);self.assertIn('page=context.new_page()',code);self.assertNotIn('page=browser.new_page()',code)
 def test_checkbox_adapter_rejects_unknown_controls(self):
  import unittest.mock as mock
  frame=mock.Mock()
  with self.assertRaises(ValueError):m.set_native_checkbox(frame,'unknown',False)
  frame.locator.assert_not_called()
 def test_native_submit_uses_form_events_not_ad_obstructed_pointer(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def submit_once',1)[1].split('def verify_public',1)[0]
  self.assertIn('requestSubmit(e)',code);self.assertNotIn('.click()',code)
 def test_public_discovery_bypasses_stale_homepage_cache(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def verify_public',1)[1].split('def publish_new',1)[0]
  self.assertIn('/?afp_verify=',code);self.assertIn('time.time_ns()',code)
 def test_no_global_pause_bypass(self):
  import unittest.mock as mock
  with mock.patch('check_blog_pipeline_control.decision',return_value={'proceed':False}):self.assertFalse(m.allowed())
 def test_new_publication_rejects_queued_video_before_browser_use(self):
  import unittest.mock as mock
  for item in [
   {'post':{'html':'<p>متن</p><video controls src="x.mp4"></video>'}},
   {'post':{'html':'<p>متن</p>'},'selection':{'video_id':'video-004'}},
   {'post':{'html':'<iframe src="x"></iframe>'}},
  ]:
   page=mock.Mock()
   with mock.patch.object(m,'scan') as scan:
    with self.assertRaises(m.PipelineStop):m.publish_new(page,item,{})
    scan.assert_not_called();self.assertEqual(page.mock_calls,[])
 def test_new_generation_explicitly_disables_video(self):
  code=(ROOT/'automation/niloblog_pipeline.py').read_text().split('def generate',1)[1].split('def verify_stored_body',1)[0]
  self.assertIn('video_probability=0',code);self.assertNotIn('markup+=',code)
 def test_image_only_item_passes_new_media_gate(self):
  m.require_image_only({'selection':{'image_id':'image-001','video_id':None},'post':{'html':'<p>متن</p><img src="x.webp">'}})
if __name__=='__main__':unittest.main()
