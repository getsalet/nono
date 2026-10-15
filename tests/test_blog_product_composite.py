import io,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_product_composite import remove_edge_background,compose,provenance
from blog_generated_image import background_brief
class AuthenticPhotoTests(unittest.TestCase):
 def test_enclosed_white_label_is_preserved(self):
  source=Image.new('RGB',(80,80),'white');d=ImageDraw.Draw(source);d.rectangle((10,10,69,69),fill=(180,180,180));d.rectangle((20,20,59,59),fill='white')
  result=remove_edge_background(source);self.assertEqual(result.size,(60,60));self.assertEqual(result.getpixel((30,30)),(255,255,255,255))
 def test_both_families_fit_and_have_real_photo_provenance(self):
  for family,n in [('tape20',1),('hose',2)]:
   image=compose(Image.new('RGB',(1200,675),(110,95,70)),family,'abcdef123456');self.assertEqual(image.size,(1200,675));self.assertEqual(image.mode,'RGB');self.assertEqual(len(provenance(family)),n)
   self.assertTrue(all(len(r['sha256'])==64 for r in provenance(family)))
 def test_unknown_family_and_wrong_frame_refused(self):
  with self.assertRaises(RuntimeError):compose(Image.new('RGB',(1200,675)),'unknown','abcdef')
  with self.assertRaises(RuntimeError):compose(Image.new('RGB',(100,100)),'hose','abcdef')
 def test_model_generates_background_not_rewritten_products(self):
  text=background_brief({'key':'test','family':'hose','site_title':'لوله نخی'},'loxblog');self.assertIn('BACKGROUND',text);self.assertIn('do not generate any product',text);self.assertIn('No people',text)
if __name__=='__main__':unittest.main()
