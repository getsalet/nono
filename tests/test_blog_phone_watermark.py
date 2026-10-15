import io,sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_image_watermark import apply,present,TEXT,layout
class PhoneWatermarkTests(unittest.TestCase):
 def test_exact_reference_number(self):self.assertEqual(TEXT,'AFP | 09134922013')
 def test_stamp_detectable_on_light_and_dark_background_after_webp(self):
  for color in ('white','black',(190,170,140)):
   image=apply(Image.new('RGB',(1200,675),color));out=io.BytesIO();image.save(out,'WEBP',quality=88)
   self.assertTrue(present(Image.open(io.BytesIO(out.getvalue()))))
 def test_unwatermarked_and_removed_number_are_rejected(self):
  for color in ('white','black'):
   self.assertFalse(present(Image.new('RGB',(1200,675),color)))
  image=apply(Image.new('RGB',(1200,675),'white'));font,point,box=layout(image.size)
  image.paste('gray',tuple(map(int,box)));self.assertFalse(present(image))
if __name__=='__main__':unittest.main()
