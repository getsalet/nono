import base64,io,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import blog_reference_scene as scene
import blog_generated_image as generated
class HoseFullReferenceTests(unittest.TestCase):
 def item(self,family='hose'):
  return {'key':'hose-fullrefs-fixture','family':family,'site_title':'لوله نخی'if family=='hose'else'نوار تیپ','_image_article_context':{'title':'پایش اتصال لوله نخی ذرت'if family=='hose'else'نوار تیپ بامیه؛ مراقبت','summary':'این مقاله درباره بررسی اتصال آبیاری و یکنواختی جریان در مزرعه است و صحنه باید شاهد اتصال سالم داشته باشد.'}}
 def test_hose_supplies_two_byte_exact_full_originals_then_guide(self):
  refs=scene.references(self.item());self.assertEqual(len(refs),3)
  for ref,name,mime in zip(refs[:2],('afp-layflat.webp.b64','afp-layflat-bare.jpg.b64'),('image/webp','image/jpeg')):
   self.assertTrue(ref.startswith('data:'+mime+';base64,'))
   self.assertEqual(base64.b64decode(ref.split(',',1)[1]),base64.b64decode((scene.reference.ASSET_DIR/name).read_text().strip()))
  guide=Image.open(io.BytesIO(base64.b64decode(refs[2].split(',',1)[1])))
  self.assertEqual(guide.size,(1200,675))
 def test_reference_bytes_match_original_nono_method(self):
  import image_prompt_policy as original
  self.assertEqual(scene.references(self.item()),original.reference_images(3,scene.article(self.item())))
 def test_tape_reference_and_recipe_are_unchanged(self):
  item=self.item('tape20')
  self.assertEqual(scene.references(item),scene.reference.reference_images(scene.role(item),scene.article(item)))
  self.assertEqual(scene.recipe_for(item),scene.RECIPE_VERSION)
  self.assertEqual(scene.recipe_for(self.item()),scene.RECIPE_VERSION+'-hose-fullrefs-v2')
 def test_real_payload_uses_three_nested_references_and_watermark(self):
  from blog_image_watermark import present
  out=io.BytesIO();Image.new('RGB',(1024,768),'green').save(out,'PNG')
  reply={'data':[{'b64_json':base64.b64encode(out.getvalue()).decode()}]}
  with patch.dict('os.environ',{'IMAGE_API_KEY':'unit-test-only'}),patch.object(generated.roya.BASE._key_pool,'fetch_json',return_value=reply)as fetch:
   image=generated.generate(self.item(),'loxblog',max_attempts=1)
  self.assertEqual(fetch.call_args.args[2]['extra_body']['image'],scene.references(self.item()))
  self.assertTrue(present(Image.open(io.BytesIO(image))))
 def test_production_scope_and_tape_rollout_remain_intact(self):
  control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text())
  self.assertEqual(control['enabled_families'],['tape20'])
  self.assertFalse(generated.family_enabled(self.item(),ROOT))
  for blog in sorted(generated.BLOGS):self.assertTrue(generated.rollout_enabled(blog,ROOT))
