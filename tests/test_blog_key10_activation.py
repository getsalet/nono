import base64,io,json,os,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as g
class Key10ActivationTests(unittest.TestCase):
 def item(self):return {'key':'key10-test','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز','summary':'بررسی فاصله خطوط نوار تیپ برای کشت پیاز و یکنواختی آبیاری و نصب درست خطوط در خاک'}}
 def test_five_generators_bind_only_proven_key(self):
  for name in ['roya-backlink-queue.yml','farsiblog-content.yml','rozblog-content.yml','blogfa-content.yml','loxblog-content.yml']:
   s=(ROOT/'.github/workflows'/name).read_text()
   self.assertIn('IMAGE_API_KEY: ${{ secrets.AGNES_API_KEY10 }}',s);self.assertIn('IMAGE_KEY_SLOT: AGNES_API_KEY10',s)
   self.assertIn("AGNES_IMAGE_TRANSIENT_FAILOVER: '0'",s);self.assertIn("BLOG_IMAGE_QUEUE_ENABLED: '1'",s)
   self.assertNotIn('IMAGE_API_KEY: ${{ secrets.IMAGE_API_KEY ||',s)
 def test_missing_mismatched_or_unknown_slot_never_falls_back(self):
  for env in [{'IMAGE_API_KEY':'','AGNES_API_KEY10':''},{'IMAGE_API_KEY':'fixture-one','AGNES_API_KEY10':'fixture-two'},{'IMAGE_API_KEY':'fixture-one','AGNES_API_KEY10':'fixture-one','IMAGE_KEY_SLOT':'UNKNOWN'}]:
   with patch.dict(os.environ,{'IMAGE_KEY_SLOT':'AGNES_API_KEY10',**env}),patch.object(g.roya.BASE._key_pool,'fetch_json')as api:
    with self.assertRaisesRegex(RuntimeError,'binding unavailable'):g._generate(self.item(),'farsiblog',max_attempts=1)
    api.assert_not_called()
 def test_actual_attempt_records_slot_not_secret_and_uses_that_key(self):
  b=io.BytesIO();Image.new('RGB',(1024,768),'white').save(b,'PNG');response={'data':[{'b64_json':base64.b64encode(b.getvalue()).decode()}]}
  env={'IMAGE_KEY_SLOT':'AGNES_API_KEY10','IMAGE_API_KEY':'fixture-private-10','AGNES_API_KEY10':'fixture-private-10','AGNES_IMAGE_TRANSIENT_FAILOVER':'0'}
  with patch.dict(os.environ,env),patch.object(g.roya.BASE._key_pool,'fetch_json',return_value=response)as api:
   item=self.item();g._generate(item,'farsiblog',max_attempts=1)
  self.assertEqual(api.call_args.args[1]['Authorization'],'Bearer fixture-private-10')
  self.assertEqual(item['_image_provider_attempts'][-1]['requested_secret_slot'],'AGNES_API_KEY10')
  self.assertNotIn('fixture-private',json.dumps(item))
 def test_tape_only_and_phone_controls_unchanged(self):
  c=json.loads((ROOT/'data/blog-generated-image-control.json').read_text())
  self.assertEqual(c['enabled_families'],['tape20']);self.assertIn('hose',c['cancelled_families'])
  self.assertEqual(c['required_watermark'],'AFP | 09134922013')
if __name__=='__main__':unittest.main()
