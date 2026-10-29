import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from parsiblog_native import persisted_diagnostic,persisted_errors
class Tests(unittest.TestCase):
 def fixture(self):
  body='<h2>آبیاری</h2><p>انتخاب نوار 20 سانتی</p>'+''.join('<a href="https://example.org/%d">راهنما</a>'%i for i in range(3))+'<img src="https://example.org/image.webp"><h3>پرسش</h3>'
  return {'image_url':'https://example.org/image.webp'},{'title':'نوار آبیاری','html':body}
 def test_identical_is_clean(self):
  item,p=self.fixture();d=persisted_diagnostic(item,p,p);self.assertEqual(d['errors'],[]);self.assertEqual(d['text']['differences'],[])
 def test_changed_numeric_value_still_blocked(self):
  item,p=self.fixture();a=dict(p,html=p['html'].replace('20','30'));d=persisted_diagnostic(item,p,a)
  self.assertIn('Saved article text differs from approved draft',d['errors']);self.assertNotEqual(d['text']['expected_sha256'],d['text']['actual_sha256']);self.assertTrue(d['text']['differences']);self.assertEqual(persisted_errors(item,p,a),d['errors'])
 def test_no_body_or_native_response_in_report(self):
  import json
  item,p=self.fixture();a=dict(p,html=p['html']+'<p>SENSITIVE_RESPONSE_MARKER</p>',cookie='private-session',password='private-password');d=persisted_diagnostic(item,p,a);text=json.dumps(d,ensure_ascii=False)
  for secret in ('SENSITIVE_RESPONSE_MARKER','private-session','private-password','<p>'):self.assertNotIn(secret,text)
if __name__=='__main__':unittest.main()
