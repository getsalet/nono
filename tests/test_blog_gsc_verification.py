import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_gsc_verification import patched
class VerificationTests(unittest.TestCase):
 def test_additive_idempotent(self):
  source='<html><head><meta name="google-site-verification" content="old" /></head><body>https://navar-abyari.ir/</body></html>';token='a'*43
  result=patched(source,token)
  self.assertIn('content="old"',result);self.assertEqual(result.count(token),1);self.assertEqual(patched(result,token),result)
  self.assertEqual(result.replace('<meta name="google-site-verification" content="'+token+'" />\n',''),source)
 def test_refuse_wrong_site(self):
  with self.assertRaises(ValueError):patched('<head></head>','a'*43)
 def test_refuse_body_only(self):
  with self.assertRaises(ValueError):patched('navar-abyari.ir <body/>','a'*43)
if __name__=='__main__':unittest.main()
