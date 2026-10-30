import io,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from PIL import Image,ImageChops
from blog_image_edit_reference import masked_finish_reference
from blog_image_watermark import apply,present
class EditReferenceTests(unittest.TestCase):
 def test_stamp_masked_reference_only_product_area_unchanged(self):
  original=apply(Image.new('RGB',(1200,900),(120,85,60)))
  self.assertTrue(present(original))
  out=io.BytesIO();original.save(out,'PNG');raw=out.getvalue()
  masked=Image.open(io.BytesIO(masked_finish_reference(raw)))
  self.assertEqual(masked.size,original.size)
  self.assertFalse(present(masked))
  self.assertIsNone(ImageChops.difference(original.crop((0,0,768,900)),masked.crop((0,0,768,900))).getbbox())
  self.assertTrue(present(Image.open(io.BytesIO(raw))))
 def test_small_reference_fails_closed(self):
  f=io.BytesIO();Image.new('RGB',(100,100)).save(f,'PNG')
  with self.assertRaises(ValueError):masked_finish_reference(f.getvalue())
if __name__=='__main__':unittest.main()
