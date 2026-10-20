import io,sys,unittest
from pathlib import Path
from unittest.mock import patch
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
  self.assertEqual(s.count('window.jQuery(e.form).submit()'),1)
  self.assertIn('verified_url=publisher.verify(public,corrected,pid)',s)
  self.assertIn("if not matches(censored,actual,links)",s)
  self.assertIn("publisher.journal(entry,'verified')",s)
 def test_no_authentication_retry(self):
  s=(ROOT/'automation/loxblog_native.py').read_text()
  self.assertEqual(s.count("page.locator('#submitlogin').click()"),1)
  self.assertIn('no automatic credential retry',s)
if __name__=='__main__':unittest.main()
