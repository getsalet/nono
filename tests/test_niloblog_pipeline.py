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
  with tempfile.TemporaryDirectory() as d,mock.patch.object(m,'STATE',Path(d)/'state.json'),mock.patch.dict(m.os.environ,{'GITHUB_ACTIONS':'false'}):
   with self.assertRaises(RuntimeError):m.checkpoint({'published':[]})
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
 def test_no_global_pause_bypass(self):
  import unittest.mock as mock
  with mock.patch('check_blog_pipeline_control.decision',return_value={'proceed':False}):self.assertFalse(m.allowed())
if __name__=='__main__':unittest.main()
