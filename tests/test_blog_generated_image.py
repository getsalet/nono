import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_generated_image import identity,brief
from blog_image_gate import approved_url
class GeneratedImageTests(unittest.TestCase):
 def test_unique_article_and_blog(self):
  a={'key':'city-a','family':'tape20','site_title':'نوار تیپ'};b={**a,'key':'city-b'}
  self.assertNotEqual(identity(a,'roya'),identity(a,'loxblog'));self.assertNotEqual(identity(a,'roya'),identity(b,'roya'));self.assertEqual(identity(a,'roya'),identity(a,'roya'))
 def test_family_conflict_refused(self):
  with self.assertRaises(RuntimeError):identity({'key':'x','family':'tape20','site_title':'لوله نخی'},'roya')
 def test_reference_brief(self):
  p=brief({'key':'x','family':'hose','site_title':'لوله نخی'},'roya');self.assertIn('polygonal',p);self.assertIn('No people',p);self.assertIn('non-geolocated',p)
 def test_strict_asset_url(self):
  good='https://raw.githubusercontent.com/getsalet/nono/'+'a'*40+'/assets/blog-generated/roya/'+'b'*32+'.webp'
  self.assertTrue(approved_url(good));self.assertFalse(approved_url(good.replace('/nono/','/evil/')));self.assertFalse(approved_url(good.replace('a'*40,'main')));self.assertFalse(approved_url(good+'?token=bad'))
if __name__=='__main__':unittest.main()
