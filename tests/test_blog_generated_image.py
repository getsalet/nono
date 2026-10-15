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

class ConditioningTests(unittest.TestCase):
 def test_single_combined_reference_both_families(self):
  import base64,io
  from PIL import Image
  from blog_generated_image import conditioning_image
  for family in ('hose','tape20'):
   refs=conditioning_image(family);self.assertEqual(len(refs),1)
   image=Image.open(io.BytesIO(base64.b64decode(refs[0].split(',',1)[1])))
   self.assertEqual(image.size,(1200,675))
 def test_generation_retries_only_transient(self):
  import io
  from PIL import Image
  from unittest.mock import patch
  import blog_generated_image as m
  image=Image.new('RGB',(1024,768),'green');buf=io.BytesIO();image.save(buf,'PNG')
  import base64
  data={'data':[{'b64_json':base64.b64encode(buf.getvalue()).decode()}]}
  item={'key':'fake','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'فاصله نوار تیپ در کشت گوجه فرنگی','summary':'فاصله خطوط تیپ و آرایش بوته‌های گوجه فرنگی در آبیاری قطره‌ای و توزیع یکنواخت رطوبت'}}
  with patch.object(m,'capability_slots',return_value=['AGNES_API_KEY14']),patch.object(m.roya.BASE._key_pool,'keys',['fake-key']),patch.object(m.roya.BASE._key_pool,'slots',{'fake-key':'AGNES_API_KEY14'}),patch.object(m.roya.BASE._key_pool,'fetch_json',side_effect=[RuntimeError('Agnes/provider HTTP 503; raw response withheld'),data])as fetch,patch.object(m.time,'sleep'):
   result=m.generate(item,'roya');self.assertEqual(fetch.call_count,2);self.assertEqual(Image.open(io.BytesIO(result)).size,(1200,675))
  with patch.object(m,'capability_slots',return_value=['AGNES_API_KEY14']),patch.object(m.roya.BASE._key_pool,'keys',['fake-key']),patch.object(m.roya.BASE._key_pool,'slots',{'fake-key':'AGNES_API_KEY14'}),patch.object(m.roya.BASE._key_pool,'fetch_json',side_effect=RuntimeError('Agnes/provider HTTP 403; raw response withheld'))as fetch,self.assertRaisesRegex(RuntimeError,'HTTP 403'):
   m.generate(item,'roya')
  self.assertEqual(fetch.call_count,1)


class DirectVisualReviewTests(unittest.TestCase):
 def test_rejected_image_cannot_reuse_positive_ai_cache(self):
  import tempfile,json
  from blog_image_gate import visual_override_rejected
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir()
   self.assertFalse(visual_override_rejected('a'*64,root))
   (root/'data/blog-generated-image-visual-review.json').write_text(json.dumps({'rejected_sha256':['a'*64]}))
   self.assertTrue(visual_override_rejected('a'*64,root));self.assertFalse(visual_override_rejected('b'*64,root))
 def test_broken_visual_decision_file_is_fail_closed(self):
  import tempfile
  from blog_image_gate import visual_override_rejected
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-visual-review.json').write_text('broken')
   with self.assertRaises(RuntimeError):visual_override_rejected('a'*64,root)
