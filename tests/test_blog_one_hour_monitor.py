import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from monitor_blog_generators_one_hour import probe_allowed,DURATION,MAX_PROBES,WORKFLOWS
class FiniteMonitorTests(unittest.TestCase):
 def allowed(self,**kw):
  d=dict(elapsed=600,remaining=3000,attempts=0,last_probe=0,cooldown=100,now=200,received=False,control={'pause_image_production':False,'enabled_families':['tape20']});d.update(kw);return probe_allowed(**d)
 def test_finite_window_and_five_generators(self):self.assertEqual(DURATION,3600);self.assertEqual(MAX_PROBES,5);self.assertEqual(len(WORKFLOWS),5)
 def test_cooldown_and_spacing(self):self.assertTrue(self.allowed());self.assertFalse(self.allowed(cooldown=300));self.assertFalse(self.allowed(elapsed=500))
 def test_budget_and_remaining_window(self):self.assertFalse(self.allowed(attempts=5));self.assertFalse(self.allowed(remaining=650))
 def test_candidate_and_pause_stop_probes(self):self.assertFalse(self.allowed(received=True));self.assertFalse(self.allowed(control={'pause_image_production':True,'enabled_families':['tape20']}))
 def test_ambiguous_or_changed_scope(self):self.assertFalse(self.allowed(control={}));self.assertFalse(self.allowed(control={'pause_image_production':False,'enabled_families':['tape20','hose']}))

class LargeQueueReadTests(unittest.TestCase):
 def test_large_queue_uses_exact_blob(self):
  import base64,json
  from unittest.mock import patch
  import monitor_blog_generators_one_hour as m
  sha='a'*40;encoded=base64.b64encode(json.dumps({'items':[{'key':'fixture'}]}).encode()).decode()
  with patch.object(m,'api',side_effect=[{'content':'','encoding':'none','sha':sha},{'content':encoded,'encoding':'base64'}])as call:
   self.assertEqual(m.content('data/roya/backlink-queue.json')['items'][0]['key'],'fixture')
   self.assertEqual(call.call_args.args[0],'/git/blobs/'+sha)
 def test_small_json_needs_no_extra_request(self):
  import base64
  from unittest.mock import patch
  import monitor_blog_generators_one_hour as m
  with patch.object(m,'api',return_value={'content':base64.b64encode(b'{"items":[]}').decode(),'encoding':'base64'})as call:
   self.assertEqual(m.content('data/roya/backlink-queue.json'),{'items':[]});self.assertEqual(call.call_count,1)
 def test_unverified_blob_identifier_not_followed(self):
  from unittest.mock import patch
  import monitor_blog_generators_one_hour as m
  with patch.object(m,'api',return_value={'content':'','sha':'unverified'})as call:
   with self.assertRaises(RuntimeError):m.content('data/roya/backlink-queue.json')
   self.assertEqual(call.call_count,1)

class StockAwareMonitorTests(unittest.TestCase):
 def test_independent_stock_prevents_extra_manual_dispatch(self):
  from unittest.mock import patch
  import monitor_blog_generators_one_hour as m
  with patch.object(m.urllib.request,'urlopen')as request:
   self.assertIsNone(m.dispatch_next({'image_stock_control':{'enabled':True}},[]));request.assert_not_called()
 def test_monitor_tracks_stock_and_does_not_claim_homepage_as_post(self):
  import inspect,monitor_blog_generators_one_hour as m
  self.assertIn('image_stock_requests',inspect.getsource(m.snapshot))
  self.assertIn('new_post_verified',inspect.getsource(m.public_check))
  self.assertEqual(len(m.PUBLIC_BLOGS),5)
