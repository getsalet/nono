import inspect,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from playwright.sync_api import TimeoutError as NativeWaitTimeout
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import loxblog_native as n
class IdentityWaitTests(unittest.TestCase):
 def page(self,targets):
  links=Mock();links.evaluate_all.side_effect=targets
  return SimpleNamespace(url=n.PANEL+'/adminnew.php?page=postslist',locator=Mock(return_value=links),wait_for_function=Mock(),evaluate=Mock(return_value={'server_error':False,'login_form':False,'access_denied':False}))
 def test_ready_identity_does_not_wait(self):
  p=self.page([['https://afp.lxb.ir'],['https://afp.lxb.ir']]);n.assert_management(p);p.wait_for_function.assert_not_called()
 def test_late_menu_waits_for_same_exact_identity(self):
  p=self.page([[],['https://afp.lxb.ir/']]);n.assert_management(p);self.assertEqual(p.wait_for_function.call_args.kwargs['timeout'],10000)
 def test_missing_or_wrong_blog_is_never_accepted(self):
  for targets in ([],['https://other.lxb.ir/'],['https://afp.lxb.ir.example.org/']):
   p=self.page([targets]);p.wait_for_function.side_effect=NativeWaitTimeout('untrusted secret detail')
   with self.assertRaisesRegex(RuntimeError,'identity wait exhausted')as caught:n.assert_management(p)
   self.assertNotIn('untrusted',str(caught.exception));self.assertFalse(hasattr(p,'goto'))
 def test_route_rechecked_after_wait(self):
  p=self.page([[]]);p.wait_for_function.side_effect=lambda *a,**k:setattr(p,'url','https://example.com/adminnew.php')
  with self.assertRaisesRegex(RuntimeError,'session not active'):n.assert_management(p)
 def test_wrong_route_fails_before_wait(self):
  p=self.page([]);p.url='https://loxblog.com/login.php'
  with self.assertRaises(RuntimeError):n.assert_management(p)
  p.locator.assert_not_called();p.wait_for_function.assert_not_called()
 def test_wait_has_no_credential_or_publication_path(self):
  code=inspect.getsource(n.assert_management)
  for operation in ('.click(','.fill(','.goto(','.reload(','.screenshot(','.inner_text('):self.assertNotIn(operation,code)
 def test_diagnostics_only_fixed_boolean_flags(self):
  from contextlib import redirect_stdout
  from io import StringIO
  p=self.page([[]]);p.wait_for_function.side_effect=NativeWaitTimeout('secret');p.evaluate.return_value={'server_error':True,'login_form':'secret','access_denied':False,'unexpected':'private account'};out=StringIO()
  with redirect_stdout(out),self.assertRaises(RuntimeError):n.assert_management(p)
  self.assertNotIn('secret',out.getvalue());self.assertNotIn('private',out.getvalue());self.assertIn('"server_error": true',out.getvalue())
if __name__=='__main__':unittest.main()
