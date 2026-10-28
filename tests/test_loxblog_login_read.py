import sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import loxblog_native as n
class LoginReadTests(unittest.TestCase):
 @patch('time.sleep')
 def test_only_initial_get_is_retried(self,sleep):
  page=SimpleNamespace(url=n.PANEL+'/login.php',goto=Mock(side_effect=[RuntimeError('net::ERR_CONNECTION_CLOSED'),SimpleNamespace(status=200)]))
  n.read_login_page(page);self.assertEqual(page.goto.call_count,2)
 @patch('time.sleep')
 def test_exhaustion_sanitizes_message_and_prevents_credentials(self,sleep):
  page=SimpleNamespace(url=n.PANEL+'/login.php',goto=Mock(side_effect=RuntimeError('net::ERR_CONNECTION_CLOSED untrusted page secret')))
  with self.assertRaisesRegex(RuntimeError,'no credentials submitted')as caught:n.read_login_page(page)
  self.assertNotIn('untrusted',str(caught.exception));self.assertEqual(page.goto.call_count,3)
 @patch('time.sleep')
 def test_wrong_host_is_not_accepted(self,sleep):
  page=SimpleNamespace(url='https://example.com/login.php',goto=Mock(return_value=SimpleNamespace(status=200)))
  with self.assertRaises(RuntimeError):n.read_login_page(page)
  self.assertEqual(page.goto.call_count,1)
 @patch('time.sleep')
 def test_denied_get_is_not_repeated(self,sleep):
  page=SimpleNamespace(url=n.PANEL+'/login.php',goto=Mock(return_value=SimpleNamespace(status=403)))
  with self.assertRaises(RuntimeError):n.read_login_page(page)
  self.assertEqual(page.goto.call_count,1)
 def test_visual_model_does_not_inherit_article_model(self):
  import json,os
  import roya_backlink_queue as roya
  response=Mock();response.read.return_value=json.dumps({'choices':[{'message':{'content':'{"digits":"12345"}'}}]}).encode()
  manager=Mock();manager.__enter__=Mock(return_value=response);manager.__exit__=Mock(return_value=False)
  with patch.dict(os.environ,{'IMAGE_REVIEW_MODEL':'agnes-3.0-flash'},clear=True),patch.object(roya.BASE,'next_agnes_key',return_value='test-only'),patch.object(n.urllib.request,'urlopen',return_value=manager)as send:
   self.assertEqual(n.transcribe_captcha(b'test-image'),'12345')
   self.assertEqual(json.loads(send.call_args.args[0].data)['model'],'agnes-3.0-flash')
  with patch.dict(os.environ,{'LOXBLOG_CAPTCHA_MODEL':'explicit-vision'},clear=True),patch.object(roya.BASE,'next_agnes_key',return_value='test-only'),patch.object(n.urllib.request,'urlopen',return_value=manager)as send:
   n.transcribe_captcha(b'test-image')
   self.assertEqual(json.loads(send.call_args.args[0].data)['model'],'explicit-vision')
 def test_credential_post_is_outside_retry_helper(self):
  import inspect
  body=inspect.getsource(n.read_login_page)
  self.assertNotIn('.fill(',body);self.assertNotIn('.click(',body);self.assertNotIn('logininc.php',body)
if __name__=='__main__':unittest.main()
