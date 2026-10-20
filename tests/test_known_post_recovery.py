import io,sys,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import loxblog_native as native
class RecoveryTests(unittest.TestCase):
 def test_consensus_requires_two_matching_readings(self):
  self.assertEqual(native.captcha_consensus(['12345','12345']),'12345')
  self.assertEqual(native.captcha_consensus(['99999','12345','12345']),'12345')
  for values in ([],['12345'],['12345','54321','99999'],['abcde','abcde']):
   with self.assertRaises(RuntimeError):native.captcha_consensus(values)
 def test_same_in_memory_image_and_no_credential_retry(self):
  from PIL import Image
  raw=io.BytesIO();Image.new('RGB',(100,45),'white').save(raw,format='PNG')
  with patch.object(native,'transcribe_captcha',side_effect=['12345','54321','54321'])as read:
   self.assertEqual(native.read_captcha(raw.getvalue()),'54321');self.assertEqual(read.call_count,3)
  with patch.object(native,'transcribe_captcha',side_effect=['12345','54321','99999']):
   with self.assertRaises(RuntimeError):native.read_captcha(raw.getvalue())
 def test_single_existing_edit_and_strict_public_verification(self):
  s=(ROOT/'automation/reconcile_known_blog_posts.py').read_text()
  self.assertNotIn('expect_navigation(',s)
  self.assertIn("page.expect_response(",s)
  self.assertIn("path.rstrip('/')=='/Op'",s)
  self.assertIn("feedback.startswith('success:')",s)
  self.assertEqual(s.count('window.jQuery(e.form).submit()'),1)
  self.assertIn('verified_url=publisher.verify(public,corrected,pid)',s)
  self.assertIn("if not matches(censored,actual,links)",s)
  self.assertIn("publisher.journal(entry,'verified')",s)
 def test_transient_get_retry_is_bounded(self):
  import publish_loxblog_posts as publisher
  from playwright.sync_api import Error
  page=Mock();ok=Mock();page.goto.side_effect=[Error('net::ERR_NAME_NOT_RESOLVED'),ok]
  with patch.object(publisher.time,'sleep'):
   self.assertIs(publisher.navigate_public(page,'https://afp.lxb.ir/'),ok)
  self.assertEqual(page.goto.call_count,2)
  page=Mock();page.goto.side_effect=Error('net::ERR_NAME_NOT_RESOLVED')
  with patch.object(publisher.time,'sleep'):
   with self.assertRaises(Error):publisher.navigate_public(page,'https://afp.lxb.ir/')
  self.assertEqual(page.goto.call_count,3)
  page=Mock();page.goto.side_effect=Error('net::ERR_CERT_AUTHORITY_INVALID')
  with self.assertRaises(Error):publisher.navigate_public(page,'https://afp.lxb.ir/')
  self.assertEqual(page.goto.call_count,1)
 def test_public_alias_fallback_is_get_only_and_observed(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertIn("if len(candidates)!=1",s)
  self.assertIn("x['title']==item['post']['title']",s)
  self.assertIn("urlsplit(x['url']).hostname==HOST",s)
  self.assertIn("for attempt in range(3):",s)
 def test_no_authentication_retry(self):
  s=(ROOT/'automation/loxblog_native.py').read_text()
  self.assertEqual(s.count("page.locator('#submitlogin').click()"),1)
  self.assertIn('no automatic credential retry',s)
if __name__=='__main__':unittest.main()
