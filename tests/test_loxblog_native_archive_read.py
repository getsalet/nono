import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
import loxblog_native as n
class NativeArchiveRead(unittest.TestCase):
 def page(self,flags=None):return SimpleNamespace(url=n.ARCHIVE,goto=Mock(return_value=SimpleNamespace(status=200)),evaluate=Mock(return_value=flags or {'empty':True,'forms':0,'password':False}))
 def test_identity_success_has_no_retry(self):
  p=self.page()
  with patch.object(n,'assert_management')as guard:n.read_native_archive(p,n.ARCHIVE)
  self.assertEqual(p.goto.call_count,1);guard.assert_called_once_with(p);p.evaluate.assert_not_called()
 def test_truly_empty_archive_has_one_get_reread_and_same_strict_identity(self):
  p=self.page()
  with patch.object(n,'assert_management',side_effect=[RuntimeError('strict identity'),None])as guard:n.read_native_archive(p,n.ARCHIVE)
  self.assertEqual(p.goto.call_count,2);self.assertEqual(guard.call_count,2)
  self.assertTrue(all(c.args==(n.ARCHIVE,)for c in p.goto.call_args_list))
 def test_still_empty_exhausts_without_new_submit_or_login(self):
  p=self.page()
  with patch.object(n,'assert_management',side_effect=RuntimeError('strict identity')),patch.object(n,'login')as login:
   with self.assertRaisesRegex(RuntimeError,'strict identity'):n.read_native_archive(p,n.ARCHIVE)
  self.assertEqual(p.goto.call_count,2);login.assert_not_called()
 def test_nonempty_wrong_account_or_login_form_is_never_retried(self):
  for flags in [{'empty':False,'forms':0,'password':False},{'empty':True,'forms':1,'password':False},{'empty':True,'forms':0,'password':True},{'empty':'yes','forms':0,'password':False}]:
   p=self.page(flags)
   with patch.object(n,'assert_management',side_effect=RuntimeError('not managing expected blog')):
    with self.assertRaises(RuntimeError):n.read_native_archive(p,n.ARCHIVE)
   self.assertEqual(p.goto.call_count,1)
 def test_wrong_destination_is_rejected_before_navigation(self):
  for u in [n.NEW,'https://example.org/adminnew.php?page=postslist','http://loxblog.com/adminnew.php?page=postslist']:
   p=self.page()
   with self.assertRaises(RuntimeError):n.read_native_archive(p,u)
   p.goto.assert_not_called()
 def test_redirect_to_login_or_other_host_is_not_reread(self):
  p=self.page();p.url='https://loxblog.com/login.php'
  with patch.object(n,'assert_management',side_effect=RuntimeError('not active')):
   with self.assertRaises(RuntimeError):n.read_native_archive(p,n.ARCHIVE)
  self.assertEqual(p.goto.call_count,1);p.evaluate.assert_not_called()
