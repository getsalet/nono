import unittest,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from blogfa_wire_audit import url_shape,cookie_names,app_fingerprint
class NativeWireAuditTests(unittest.TestCase):
 def test_url_redacts_values_and_cookie_names_only(self):
  d=url_shape('https://www.blogfa.com/Desktop/Post.aspx?action=new&r=123456789&t=987');s=json.dumps(d);self.assertNotIn('123456789',s);self.assertNotIn('987',s);self.assertNotIn('new',s);self.assertEqual(cookie_names('sid=secret; auth=private'),['sid','auth'])
 def test_fingerprint_excludes_secrets_and_native_time(self):
  a={'txtPostTitle':['public title'],'__VIEWSTATE':['secret'],'txtPostPW':['password'],'txtHour':['1']};b={**a,'__VIEWSTATE':['other'],'txtPostPW':['different'],'txtHour':['2']};self.assertEqual(app_fingerprint(a),app_fingerprint(b))
 def test_publication_interception_always_aborts(self):
  s=(ROOT/'automation/blogfa_wire_audit.py').read_text();self.assertIn("route.abort('aborted');return",s);self.assertIn("'sent_to_server':False",s)
