import base64,hashlib,io,json,os,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as generated
from blog_image_connection import settings
class ReferenceConnectionTests(unittest.TestCase):
 def item(self):return {'key':'reference-connection','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز؛ فاصله کشت','summary':'مقاله درباره فاصله خطوط کشت پیاز و یکنواختی آبیاری در مزرعه است و از همان موضوع برای صحنه استفاده می‌شود.'}}
 def response(self):
  out=io.BytesIO();Image.new('RGB',(1024,768),'green').save(out,'PNG')
  return {'data':[{'b64_json':base64.b64encode(out.getvalue()).decode()}]}
 def test_configured_image_connection_is_used_without_text_pool_audit(self):
  env={'IMAGE_API_KEY':'private-image-test-value','IMAGE_ENDPOINT':'https://image.example.invalid/v1/images/generations','IMAGE_MODEL':'configured-image-model'}
  with patch.dict(os.environ,env),patch.object(generated,'capability_slots',side_effect=AssertionError('text/image legacy audit must not select this image connection')),patch.object(generated.roya.BASE._key_pool,'fetch_json',return_value=self.response())as fetch:
   item=self.item();generated.generate(item,'roya')
   self.assertEqual(fetch.call_args.args[0],env['IMAGE_ENDPOINT']);self.assertEqual(fetch.call_args.args[2]['model'],env['IMAGE_MODEL'])
   self.assertEqual(fetch.call_args.args[1]['Authorization'],'Bearer '+env['IMAGE_API_KEY']);self.assertEqual(fetch.call_args.kwargs['timeout'],600)
   self.assertNotIn(env['IMAGE_API_KEY'],json.dumps(item))
 def test_dedicated_denial_is_not_retried_using_text_credentials(self):
  with patch.dict(os.environ,{'IMAGE_API_KEY':'private-image-test-value'}),patch.object(generated.roya.BASE._key_pool,'fetch_json',side_effect=RuntimeError('Agnes/provider HTTP 403; raw response withheld'))as fetch:
   with self.assertRaisesRegex(RuntimeError,'HTTP 403'):generated.generate(self.item(),'roya')
   self.assertEqual(fetch.call_count,1)
 def test_endpoint_credentials_are_rejected_without_exposing_them(self):
  with patch.dict(os.environ,{'IMAGE_ENDPOINT':'https://private-user:private-password@image.example.invalid/v1/images/generations'}):
   with self.assertRaisesRegex(RuntimeError,'credential-free HTTPS'):settings('https://example.invalid/v1')
 def test_reference_policy_is_byte_identical_to_pinned_upstream(self):
  data=json.loads((ROOT/'data/blog-image-reference-contract.json').read_text())
  actual=hashlib.sha256((ROOT/'automation/blog_reference_image_policy.py').read_bytes()).hexdigest()
  self.assertEqual(actual,data['maghala2_policy']['sha256'])
 def test_acceptance_workflow_passes_the_existing_image_settings(self):
  text=(ROOT/'.github/workflows/blog-generated-image-acceptance.yml').read_text()
  for value in ('secrets.IMAGE_API_KEY || secrets.AGNES_API_KEY','vars.IMAGE_ENDPOINT','vars.IMAGE_MODEL',"'agnes-3.0-flash'"):
   self.assertIn(value,text)

 def test_configuration_failure_replaces_any_stale_acceptance_success(self):
  import tempfile
  import verify_generated_blog_images as verify
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();path=root/'data/blog-generated-image-acceptance.json';path.write_text('{"passed":true}')
   with patch.object(verify,'ROOT',root),patch.dict(os.environ,{'IMAGE_ENDPOINT':'https://private-user:private-password@image.example.invalid/v1/images/generations'}):
    self.assertEqual(verify.main(),1)
   result=json.loads(path.read_text());self.assertFalse(result['passed']);self.assertEqual(result['preflight_error']['type'],'RuntimeError')
   self.assertNotIn('private-password',path.read_text())

 def test_initialize_only_invalidates_report_without_api_or_queue(self):
  import tempfile
  import verify_generated_blog_images as verify
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)
   with patch.object(verify,'ROOT',root),patch.object(verify,'settings',side_effect=AssertionError('no API configuration during initialization')):
    self.assertEqual(verify.main(initialize_only=True),0)
   result=json.loads((root/'data/blog-generated-image-acceptance.json').read_text())
   self.assertFalse(result['passed']);self.assertEqual(result['families'],[])
