"""Image identity, mandatory audited routing, safe retries and five-blog wiring."""
import base64,copy,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as generated
import blog_image_gate as gate
import blog_product_composite as composite
import city_backlink_policy as city
import roya_backlink_queue as roya

class ImageRolloutTests(unittest.TestCase):
 def setUp(self):
  self.image_env=patch.dict('os.environ',{'IMAGE_API_KEY':''});self.image_env.start();self.addCleanup(self.image_env.stop)
  self.queue=patch('blog_image_queue.provider_slot',side_effect=lambda *a:__import__('contextlib').nullcontext());self.queue.start();self.addCleanup(self.queue.stop)
  self.item={'key':'image-fixture','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'فاصله نوار تیپ در کشت گوجه فرنگی','summary':'فاصله خطوط تیپ و آرایش بوته‌های گوجه فرنگی در آبیاری قطره‌ای و توزیع یکنواخت رطوبت'}}
  buf=io.BytesIO();__import__('blog_image_watermark').apply(Image.new('RGB',(1200,675),(190,170,140))).save(buf,'WEBP');self.raw=buf.getvalue()
 def test_generation_never_calls_rejected_compositor(self):
  source=__import__('inspect').getsource(generated.generate)+__import__('inspect').getsource(generated._generate)
  self.assertNotIn('compose(',source)
  self.assertIn('blog_reference_scene',source)
  from blog_reference_scene import prompt,references,topic_hash
  text=prompt(self.item,'roya')
  self.assertIn(self.item['_image_article_context']['title'],text)
  self.assertIn('not a flat layer to paste',text)
  self.assertEqual(len(references(self.item)),1)
  changed=copy.deepcopy(self.item);changed['_image_article_context']['summary']+=' بررسی فشار'
  self.assertNotEqual(topic_hash(self.item),topic_hash(changed))
  self.assertNotEqual(generated.identity(self.item,'roya'),generated.identity(changed,'roya'))
  feedback={**self.item,'_image_qa_feedback':'retry: shadow'}
  self.assertEqual(topic_hash(self.item),topic_hash(feedback))
 def test_generic_body_terms_do_not_force_every_article_into_hardware_scene(self):
  from blog_reference_scene import role
  item=copy.deepcopy(self.item);item['_image_article_context']['summary']+=' فیلتر و فشار و نگهداری'
  self.assertEqual(role(item),1)
  item['_image_article_context']['title']='رفع گرفتگی نوار تیپ گوجه فرنگی'
  self.assertEqual(role(item),3)
 def test_actual_article_body_is_required(self):
  from blog_reference_scene import prompt
  with self.assertRaisesRegex(RuntimeError,'Actual post title and body'):
   prompt({'key':'x','family':'tape20','site_title':'نوار تیپ'},'roya')
 def test_explicit_pause_cannot_fall_back_to_rejected_source_images(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir()
   (root/'data/blog-generated-image-control.json').write_text(json.dumps({'enabled':False,'pause_image_production':True}))
   with self.assertRaisesRegex(RuntimeError,'explicitly paused'):generated.rollout_enabled('roya',root)
 def test_legacy_pool_requires_its_image_audit(self):
  with patch.object(generated,'capability_slots',side_effect=RuntimeError('audit missing')),patch.dict('os.environ',{'IMAGE_API_KEY':''}):
   with self.assertRaisesRegex(RuntimeError,'audit missing'):generated.generate(self.item,'roya')
 def test_requested_pool_does_not_fall_back_to_text_only_keys(self):
  pool=roya.BASE._key_pool
  with patch.object(pool,'keys',['text-key']),patch.object(pool,'slots',{'text-key':'AGNES_API_KEY3'}):
   with self.assertRaisesRegex(RuntimeError,'No audited healthy'):generated.generate(self.item,'roya',slots=['AGNES_API_KEY14'])
 def test_rejected_cached_candidate_is_archived_and_regenerated(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);asset_id=generated.identity(self.item,'roya')
   cache=root/'artifacts/roya-backlink-queue/generated-images'/f'{asset_id}.webp';cache.parent.mkdir(parents=True);cache.write_bytes(self.raw)
   item=copy.deepcopy(self.item)
   url='https://raw.githubusercontent.com/getsalet/nono/'+'a'*40+'/assets/blog-generated/roya/'+asset_id+'.webp'
   with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'generate',return_value=self.raw)as gen,patch.object(gate,'review',side_effect=[RuntimeError('Product image rejected: wrong product'),{},{}])as review,patch.object(generated,'checkpoint_asset',return_value=url):
    self.assertEqual(generated.prepare(item,'roya',root),url)
    self.assertEqual(gen.call_count,1);self.assertEqual(review.call_count,3)
   self.assertEqual(len(list((cache.parent/'rejected').glob('*.webp'))),1)
   self.assertEqual(len(item['_image_rejections']),1)
 def test_visual_failure_bounded_to_three_candidates(self):
  with tempfile.TemporaryDirectory()as d:
   with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'generate',return_value=self.raw)as gen,patch.object(gate,'review',side_effect=RuntimeError('Product image rejected: wrong product')),patch.object(generated,'checkpoint_asset')as checkpoint:
    with self.assertRaisesRegex(RuntimeError,'Product image rejected'):generated.prepare(copy.deepcopy(self.item),'roya',Path(d))
    self.assertEqual(gen.call_count,3);checkpoint.assert_not_called()
 def test_vision_auth_failure_does_not_discard_candidate_or_regenerate(self):
  with tempfile.TemporaryDirectory()as d:
   with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'generate',return_value=self.raw)as gen,patch.object(gate,'review',side_effect=RuntimeError('Vision credential required')):
    with self.assertRaisesRegex(RuntimeError,'Vision credential required'):generated.prepare(copy.deepcopy(self.item),'roya',Path(d))
    self.assertEqual(gen.call_count,1)
 def test_qa_receives_whole_scene_actual_article_and_identity_reference(self):
  verdict={'pass':True,'score':90,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'product_role_plausible':True,'packaging_not_used_as_hardware':True,'package_soil_gap_visible':True,'irrigation_geometry_plausible':True,'technical_evidence_match':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False}
  reply={'choices':[{'message':{'content':json.dumps(verdict)}}]}
  with tempfile.TemporaryDirectory()as d:
   with patch.object(gate,'fetch',return_value=(self.raw,(1200,675),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='test-key'),patch.object(roya.BASE,'fetch_json',return_value=reply)as call:
    gate.review(copy.deepcopy(self.item),'generated://roya/'+'a'*32,Path(d),_candidate=self.raw)
   content=call.call_args.args[2]['messages'][0]['content']
   self.assertEqual(len([x for x in content if x['type']=='image_url']),4)
   text=' '.join(x['text']for x in content if x['type']=='text')
   for label in ('CANDIDATE FULL FRAME','CANDIDATE DETAIL LEFT','CANDIDATE DETAIL RIGHT','APPROVED PRODUCT REFERENCE',self.item['_image_article_context']['title']):self.assertIn(label,text)
   self.assertIn('topic_match',text);self.assertIn('collage_or_split_layout',text)
 def test_split_layout_and_topic_mismatch_are_rejected(self):
  base={'pass':True,'score':90,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'product_role_plausible':True,'packaging_not_used_as_hardware':True,'package_soil_gap_visible':True,'irrigation_geometry_plausible':True,'technical_evidence_match':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False}
  for change in ({'topic_match':False},{'product_integrated':False},{'product_fully_in_frame':False},{'product_count_match':False},{'technical_evidence_match':False},{'observed_product_count':3},{'collage_or_split_layout':True},{'crop_contradiction':True}):
   reply={'choices':[{'message':{'content':json.dumps({**base,**change})}}]}
   with tempfile.TemporaryDirectory()as d,patch.object(gate,'fetch',return_value=(self.raw,(1200,675),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='test-key'),patch.object(roya.BASE,'fetch_json',return_value=reply):
    with self.assertRaisesRegex(RuntimeError,'Integrated/topic'):
     gate.review(copy.deepcopy(self.item),'generated://roya/'+'a'*32,Path(d),_candidate=self.raw)
 def test_identical_image_bytes_cannot_belong_to_two_posts(self):
  import hashlib
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);folder=root/'artifacts/blog-image-reviews';folder.mkdir(parents=True)
   digest=hashlib.sha256(self.raw).hexdigest()
   (folder/('tape20-'+digest+'.json')).write_text(json.dumps({'article_owner':'roya|different-post'}))
   with self.assertRaisesRegex(RuntimeError,'identical image bytes'):
    gate.review(copy.deepcopy(self.item),'generated://roya/'+'a'*32,root,_candidate=self.raw)
 def test_four_blog_engine_and_roya_use_enabled_generated_route(self):
  for blog in ('farsiblog','rozblog','blogfa','loxblog'):
   item={**self.item,'_image_blog':blog}
   with patch.object(generated,'rollout_enabled',return_value=True),patch.object(generated,'prepare',return_value='generated')as prep:
    self.assertEqual(city.prepare_image(item),'generated');prep.assert_called_once_with(item,blog)
  with patch.object(generated,'rollout_enabled',return_value=True),patch.object(generated,'prepare',return_value='generated')as prep:
   self.assertEqual(roya.prepare_roya_image(self.item),'generated');prep.assert_called_once_with(self.item,'roya')
 def test_disabled_rollout_does_not_generate(self):
  with patch.object(generated,'rollout_enabled',return_value=False),patch.object(generated,'prepare')as prep,patch.object(roya,'target_image',return_value='existing'):
   self.assertEqual(roya.prepare_roya_image(self.item),'existing');prep.assert_not_called()
 def test_rejected_or_unapproved_acceptance_cannot_enable(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();path=root/'data/blog-generated-image-control.json'
   path.write_text(json.dumps({'enabled':True,'policy':generated.POLICY,'direct_visual_approval':False}))
   with self.assertRaisesRegex(RuntimeError,'direct visual acceptance'):generated.rollout_enabled('roya',root)

 def test_generated_record_is_bound_to_blog_key_policy_and_real_photos(self):
  item=copy.deepcopy(self.item);asset=generated.identity(item,'roya')
  url='https://raw.githubusercontent.com/getsalet/nono/'+'a'*40+'/assets/blog-generated/roya/'+asset+'.webp'
  item.update(image_review={'scene_guard_version':gate.SCENE_GUARD,'verdict':{'product_role_plausible':True,'packaging_not_used_as_hardware':True,'package_soil_gap_visible':True,'irrigation_geometry_plausible':True,'observed_product_count':1,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'technical_evidence_match':True,'collage_or_split_layout':False,'crop_contradiction':False},'watermark':__import__('blog_image_watermark').TEXT,'topic_sha256':__import__('blog_reference_scene').topic_hash(item)},image_url=url,image_generation={'policy':generated.POLICY,'topic_sha256':__import__('blog_reference_scene').topic_hash(item),'blog':'roya','asset_id':asset,'url':url,'watermark':__import__('blog_image_watermark').TEXT,'watermark_policy':__import__('blog_image_watermark').POLICY,'product_photos':composite.provenance('tape20')})
  self.assertEqual(gate.generated_record_errors(item,'roya'),[])
  for changed in ({**item,'key':'other'}, {**item,'image_url':url.replace('a'*40,'main')}, {**item,'image_generation':{**item['image_generation'],'product_photos':[]}}):
   self.assertTrue(gate.generated_record_errors(changed,'roya'))
  self.assertTrue(gate.generated_record_errors(item,'farsiblog'))
 def test_active_rollout_rejects_legacy_draft_without_generated_image(self):
  with patch.object(generated,'rollout_enabled',return_value=True):
   self.assertTrue(gate.generated_record_errors(self.item,'roya'))
 def test_nonfinite_scores_never_pass_visual_gate(self):
  verdict={'pass':True,'score':'NaN','observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'product_role_plausible':True,'packaging_not_used_as_hardware':True,'package_soil_gap_visible':True,'irrigation_geometry_plausible':True,'technical_evidence_match':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False}
  self.assertIn('Image score below 70',gate.verdict_errors(verdict,'tape20'))

if __name__=='__main__':unittest.main()
