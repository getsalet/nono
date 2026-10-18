"""Source-conditioning geometry regression, without provider calls."""
import base64,hashlib,io,sys,unittest
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import blog_reference_scene as scene
import blog_generated_image as generated

class TapeReferenceProportionTests(unittest.TestCase):
 def item(self):
  return {'key':'proportion-fixture','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ؛ نگهداری','summary':'این مقاله درباره نگهداری نوار تیپ و پایش آبیاری در مزرعه و بررسی رطوبت خاک است.'}}
 def test_uniform_scale_preserves_original_pixels_and_aspect(self):
  path=scene.reference.ASSET_DIR/'afp-tape.webp.b64';before=hashlib.sha256(path.read_bytes()).hexdigest()
  source=Image.open(io.BytesIO(base64.b64decode(path.read_text().strip()))).convert('RGB')
  self.assertEqual(source.size,(386,382))
  expected=source.copy();expected.thumbnail((280,280),Image.Resampling.LANCZOS)
  product=scene.tape_reference_product()
  self.assertEqual(product.size,(280,277))
  self.assertIsNone(ImageChops.difference(product,expected).getbbox())
  self.assertAlmostEqual(product.width/product.height,source.width/source.height,delta=.003)
  self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
 def test_single_guide_shared_with_compatibility_path(self):
  refs=scene.references(self.item());self.assertEqual(len(refs),1)
  self.assertEqual(refs,generated.conditioning_image('tape20'))
  canvas=Image.open(io.BytesIO(base64.b64decode(refs[0].split(',',1)[1])))
  self.assertEqual(canvas.size,(1200,675))
  self.assertNotEqual(refs,scene.reference.reference_images(3,scene.article(self.item())))
 def test_normal_and_retry_prompts_preserve_shape_without_new_gate(self):
  item=self.item()
  for feedback in ('','Remove every protruding white ribbon'):
   item['_image_qa_feedback']=feedback;text=scene.prompt(item,'roya')
   self.assertIn('sidewall-height-to-diameter proportions',text)
   self.assertNotIn('low wide',text);self.assertNotIn('diameter larger than height',text)
  self.assertIn('full carton sidewall',text)
 def test_missing_article_context_still_fails(self):
  with self.assertRaises(RuntimeError):scene.references({'family':'tape20'})
if __name__=='__main__':unittest.main()
