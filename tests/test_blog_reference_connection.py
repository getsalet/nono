import base64,hashlib,io,json,os,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as generated
from blog_image_connection import settings
class ReferenceConnectionTests(unittest.TestCase):
 def setUp(self):
  self.queue=patch('blog_image_queue.provider_slot',side_effect=lambda *a:__import__('contextlib').nullcontext());self.queue.start();self.addCleanup(self.queue.stop)
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

 def test_real_post_context_does_not_redirect_acceptance_report(self):
  import tempfile,copy
  import verify_generated_blog_images as verify
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data/loxblog').mkdir(parents=True)
   posts=root/'artifacts/loxblog-backlink-queue/items';posts.mkdir(parents=True)
   items=[dict(key=f,family=f,published=True,kind='city')for f in ('tape20','hose')]
   (root/'data/loxblog/backlink-queue.json').write_text(json.dumps({'items':items}))
   original=json.dumps({'post':{'title':'موضوع واقعی','html':'متن مقاله واقعی برای بررسی مسیر ذخیره گزارش و تصویر موضوعی است.'}})
   for item in items:(posts/(item['key']+'.json')).write_text(original)
   with patch.object(verify,'ROOT',root),patch.dict(os.environ,{'IMAGE_API_KEY':'fake-test-only'}),patch.object(verify,'prepare',side_effect=RuntimeError('test controlled rejection')),patch.object(verify,'identity',return_value='test'),patch('blog_reference_scene.scene_plan',return_value={}):
    self.assertEqual(verify.main(),1)
   result=json.loads((root/'data/blog-generated-image-acceptance.json').read_text())
   self.assertEqual(len(result['families']),2)
   for item in items:self.assertEqual((posts/(item['key']+'.json')).read_text(),original)

 def test_crop_match_uses_title_and_whole_words_not_garlic_in_path(self):
  import blog_reference_scene as scene
  a={'title':'نوار تیپ بامیه در قرقری؛ مراقبت حین بهره‌برداری','summary':'پایش مسیر جریان آب و فاصله قطره‌چکان‌ها برای آبیاری منظم انجام می‌شود.'}
  self.assertEqual(scene.reference.named_crop(a),'بامیه (okra)')
  self.assertIn('okra',scene.reference.crop_identity_spec(a))
  self.assertEqual(scene.reference.named_crop({'title':'پایش مسیر آبیاری'}),'none; neutral seedlings allowed, no named crop required')
  self.assertEqual(scene.reference.named_crop({'title':'آبیاری سیر','summary':'پایش بامیه'}),'سیر (garlic)')

 def test_retry_after_is_bounded_numeric_metadata_only(self):
  from agnes_key_pool import AgnesProviderError
  self.assertEqual(AgnesProviderError(503,retry_after='90').retry_after_seconds,90)
  self.assertEqual(AgnesProviderError(503,retry_after='999999').retry_after_seconds,120)
  self.assertIsNone(AgnesProviderError(503,retry_after='private-header-value').retry_after_seconds)

 def test_image_transient_retry_honors_provider_cooldown(self):
  from agnes_key_pool import AgnesProviderError
  with patch.dict(os.environ,{'IMAGE_API_KEY':'private-image-test-value'}),patch.object(generated.roya.BASE._key_pool,'fetch_json',side_effect=[AgnesProviderError(503,retry_after='90'),self.response()]),patch.object(generated.time,'sleep')as sleep:
   item=self.item();generated.generate(item,'roya')
   sleep.assert_called_once_with(90)
   self.assertEqual(item['_image_provider_attempts'][0]['retry_delay_seconds'],90)

 def test_transient_failover_uses_only_image_audited_slots(self):
  from agnes_key_pool import AgnesProviderError
  pool=generated.roya.BASE._key_pool
  with patch.dict(os.environ,{'IMAGE_API_KEY':'dedicated-test','AGNES_IMAGE_TRANSIENT_FAILOVER':'1','IMAGE_ENDPOINT':generated.roya.BASE.AGNES_BASE+'/images/generations'}),patch.object(generated,'capability_slots',return_value=['AGNES_API_KEY6']),patch.object(pool,'keys',['text-only-test','image-test']),patch.object(pool,'slots',{'text-only-test':'AGNES_API_KEY3','image-test':'AGNES_API_KEY6'}),patch.object(pool,'fetch_json',side_effect=[AgnesProviderError(503),self.response()])as fetch,patch.object(generated.time,'sleep'):
   item=self.item();generated.generate(item,'roya')
   self.assertEqual(fetch.call_args_list[1].args[1]['Authorization'],'Bearer image-test')
   self.assertNotIn('text-only-test',fetch.call_args_list[1].kwargs['allowed_keys'])
   self.assertEqual(item['_image_provider_attempts'][1]['requested_secret_slot'],'AGNES_API_KEY6')

 def test_transient_failover_never_applies_to_permission_denial(self):
  from agnes_key_pool import AgnesProviderError
  with patch.dict(os.environ,{'IMAGE_API_KEY':'dedicated-test','AGNES_IMAGE_TRANSIENT_FAILOVER':'1'}),patch.object(generated,'capability_slots',side_effect=AssertionError('Do not change credentials on denial')),patch.object(generated.roya.BASE._key_pool,'fetch_json',side_effect=AgnesProviderError(403))as fetch:
   with self.assertRaisesRegex(RuntimeError,'HTTP 403'):generated.generate(self.item(),'roya')
   self.assertEqual(fetch.call_count,1)

 def test_image_request_does_not_add_undocumented_idempotency_header(self):
  with patch.dict(os.environ,{'IMAGE_API_KEY':'private-image-test-value'}),patch.object(generated.roya.BASE._key_pool,'fetch_json',return_value=self.response())as fetch:
   generated.generate(self.item(),'roya')
   self.assertNotIn('Idempotency-Key',fetch.call_args.args[1])

 def test_transient_failover_respects_image_specific_preference(self):
  from agnes_key_pool import AgnesProviderError
  pool=generated.roya.BASE._key_pool
  with patch.dict(os.environ,{'IMAGE_API_KEY':'dedicated-test','AGNES_IMAGE_TRANSIENT_FAILOVER':'1','AGNES_IMAGE_PREFERRED_KEY_SLOTS':'AGNES_API_KEY11','IMAGE_ENDPOINT':generated.roya.BASE.AGNES_BASE+'/images/generations'}),patch.object(generated,'capability_slots',return_value=['AGNES_API_KEY6','AGNES_API_KEY11']),patch.object(pool,'keys',['key6-test','key11-test']),patch.object(pool,'slots',{'key6-test':'AGNES_API_KEY6','key11-test':'AGNES_API_KEY11'}),patch.object(pool,'fetch_json',side_effect=[AgnesProviderError(503),self.response()])as fetch,patch.object(generated.time,'sleep'):
   item=self.item();generated.generate(item,'roya')
   self.assertEqual(fetch.call_args_list[1].args[1]['Authorization'],'Bearer key11-test')
   self.assertEqual(item['_image_provider_attempts'][1]['requested_secret_slot'],'AGNES_API_KEY11')
