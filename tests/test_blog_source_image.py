"""Source article image reuse is not a fabricated generated-image QA pass."""
import copy,hashlib,io,json,sys,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from PIL import Image
import test_blog_editorial_image_policy as fixtures
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_source_image as source
import blog_editorial_image_policy as policy
import blog_image_stock as stock
import city_backlink_policy as city
from blog_reference_scene import context_from_post,topic_hash
class SourceImageTests(unittest.TestCase):
 write=fixtures.EditorialImagePolicyTests.write
 qa=fixtures.EditorialImagePolicyTests.qa
 def setUp(self):
  fixtures.EditorialImagePolicyTests.setUp(self)
  self.cfg['source_image_preferred']=True;self.cfg['source_image_review_required']=True;self.write(policy.CONFIG,self.cfg)
  self.item['_image_article_context']=context_from_post(self.post)
  self.url='https://navar-abyari.ir/wp-content/uploads/article-own.webp'
  self.page='<meta property="og:image" content="'+self.url+'"><article><p>راهنمای نوار تیپ</p><img src="'+self.url+'"></article>'
  buf=io.BytesIO();Image.new('RGB',(640,480),'olive').save(buf,'WEBP');self.raw=buf.getvalue()
  self.verdict={'pass':True,'score':93,'topic_match':True,'family_match':True,'decorative_or_logo':False,'wrong_product_present':False,'people_present':False,'fake_main_branding':False,'gross_impossible_geometry':False,'crop_contradiction':False,'reasons':['offline fixture']}
 def review(self,item,url,blog,root,raw,dimensions,fmt,page_url):
  return {'policy':source.REVIEW,'review_model':'offline','page_url':page_url,'image_url':url,'sha256':hashlib.sha256(raw).hexdigest(),'topic_sha256':topic_hash(item),'verdict':copy.deepcopy(self.verdict),'width':640,'height':480}
 def prepare(self,item=None,post=None,verdict=None):
  item=item if item is not None else copy.deepcopy(self.item);post=post if post is not None else copy.deepcopy(self.post)
  with patch.object(source,'read_page',return_value=self.page),patch('blog_image_gate.fetch',return_value=(self.raw,(640,480),'WEBP')),patch.object(source,'review_candidate',side_effect=self.review):
   result=source.prepare_source(item,post,'farsiblog',self.root)
  return result,item,post
 def test_selects_only_exact_page_image_not_related_cards_or_logo(self):
  s='<meta property="og:image" content="https://navar-abyari.ir/wp-content/uploads/logo.webp"><header><img src="/wp-content/uploads/header.webp"></header><article><img src="/wp-content/uploads/own.webp"><div class="related"><img src="/wp-content/uploads/other.webp"></div></article>'
  self.assertEqual(source.candidates(s,self.item['target_url']),['https://navar-abyari.ir/wp-content/uploads/own.webp'])
 def test_external_and_unsafe_page_or_image_never_selected(self):
  for url in ('http://navar-abyari.ir/a','https://evil.example/a','https://navar-abyari.ir.evil/a','https://x@navar-abyari.ir/a','https://navar-abyari.ir/'):
   self.assertFalse(source.safe_page(url))
  self.assertEqual(source.candidates('<article><img src="https://evil.example/a.webp"></article>',self.item['target_url']),[])
 def test_source_url_is_encoded_but_never_reuploaded_or_replaced(self):
  rows=source.candidates('<article><img src="/wp-content/uploads/تصویر اصلی.webp"></article>',self.item['target_url'])
  self.assertEqual(len(rows),1);self.assertIn('%D8',rows[0]);self.assertNotIn('raw.githubusercontent',rows[0])
 def test_reuses_original_image_url_with_real_provenance_and_no_generator(self):
  item=copy.deepcopy(self.item);post=copy.deepcopy(self.post);generator=Mock(side_effect=AssertionError('No generation'))
  with patch.object(source,'read_page',return_value=self.page),patch('blog_image_gate.fetch',return_value=(self.raw,(640,480),'WEBP')),patch.object(source,'review_candidate',side_effect=self.review):
   self.assertEqual(policy.prepare_article(item,post,'farsiblog',self.root,generator),self.url)
  generator.assert_not_called();self.assertNotIn('image_generation',item);self.assertEqual(item['image_source']['page_url'],self.item['target_url']);self.assertEqual(item['source_image_review']['verdict']['score'],93)
 def test_approved_source_passes_full_text_qa_but_not_generated_asset_gate(self):
  url,item,post=self.prepare();post['html']='<p><img src="'+url+'" alt="تصویر مرتبط با نوار تیپ"></p>'+post['html'];post['image_url']=url
  self.assertEqual(self.qa(item,post),[])
  from blog_image_gate import generated_record_errors
  with patch('blog_generated_image.rollout_enabled',return_value=True):self.assertTrue(generated_record_errors(item,'farsiblog',self.root))
 def test_wrong_family_unrelated_or_low_score_source_is_not_used(self):
  for fields in ({'score':89},{'topic_match':False},{'family_match':False},{'decorative_or_logo':True},{'wrong_product_present':True}):
   self.verdict.update(fields);url,item,post=self.prepare();self.assertIsNone(url);self.assertNotIn('image_url',item);self.assertNotIn('image_source',item)
   self.verdict.update(score=93,topic_match=True,family_match=True,decorative_or_logo=False,wrong_product_present=False)
 def test_invalid_scores_and_non_boolean_flags_never_pass(self):
  for fields in ({'score':True},{'score':float('nan')},{'score':101},{'pass':'true'},{'topic_match':1}):self.assertTrue(source.verdict_errors({**self.verdict,**fields}))
 def test_missing_or_unavailable_optional_source_allows_text_not_fake_approval(self):
  item=copy.deepcopy(self.item);post=copy.deepcopy(self.post)
  with patch.object(source,'read_page',side_effect=OSError('offline')),patch('blog_generated_image.prepare_now')as generation:
   self.assertIsNone(source.prepare_source(item,post,'farsiblog',self.root))
  generation.assert_not_called();self.assertFalse(policy.has_image(item,post));self.assertEqual(self.qa(item,post),[])
 def test_required_visual_source_failure_stops_without_image_generation(self):
  item={**self.item,'editorial_image_required':True}
  with patch.object(source,'read_page',return_value='<article>بدون تصویر</article>'),patch('blog_generated_image.prepare_now')as generation:
   with self.assertRaises(source.SourceImageUnavailable):source.prepare_source(item,copy.deepcopy(self.post),'farsiblog',self.root)
  generation.assert_not_called()
 def test_source_first_never_consumes_or_generates_a_new_immutable_asset(self):
  with patch.object(source,'prepare_source',return_value=self.url)as own,patch('blog_generated_image.identity')as identity,patch.object(stock,'request_image')as request:
   cb=Mock();self.assertEqual(policy.prepare_article(self.item,self.post,'farsiblog',self.root,cb),self.url)
  own.assert_called_once();identity.assert_not_called();request.assert_not_called();cb.assert_not_called()
 def test_altered_destination_owner_or_topic_rejects_source_record(self):
  _,item,post=self.prepare()
  for modified in ({**item,'target_url':'https://navar-abyari.ir/different/'},{**item,'key':'other'},{**item,'_image_article_context':{**item['_image_article_context'],'title':'موضوع متفاوت'}}):
   self.assertTrue(source.source_record_errors(modified,'farsiblog',self.root))
 def test_publisher_rechecks_actual_source_membership_and_bytes(self):
  _,item,_=self.prepare()
  with patch.object(source,'read_page',return_value=self.page),patch('blog_image_gate.fetch',return_value=(self.raw,(640,480),'WEBP')):
   self.assertEqual(source.review_for_publication(item,'farsiblog',self.root)['verdict']['score'],93)
  with patch.object(source,'read_page',return_value='<article>تصویر حذف شده</article>'):
   with self.assertRaises(source.SourceImageUnavailable):source.review_for_publication(item,'farsiblog',self.root)
  with patch.object(source,'read_page',return_value=self.page),patch('blog_image_gate.fetch',return_value=(b'changed',(640,480),'WEBP')):
   with self.assertRaises(source.SourceImageUnavailable):source.review_for_publication(item,'farsiblog',self.root)
 def test_real_review_is_cached_without_inventing_or_raising_score(self):
  import roya_backlink_queue as roya
  response={'choices':[{'message':{'content':json.dumps({**self.verdict,'score':88,'pass':False})}}]}
  with patch.object(roya.BASE,'next_agnes_key',return_value='offline-fixture'),patch.object(roya.BASE,'fetch_json',return_value=response)as api:
   first=source.review_candidate(self.item,self.url,'farsiblog',self.root,self.raw,(640,480),'WEBP',self.item['target_url'])
   second=source.review_candidate(self.item,self.url,'farsiblog',self.root,self.raw,(640,480),'WEBP',self.item['target_url'])
  self.assertEqual(first['verdict']['score'],88);self.assertEqual(second['verdict']['score'],88);self.assertEqual(api.call_count,1);self.assertTrue(source.verdict_errors(first['verdict']))
 def test_generation_cooldown_and_capacity_irrelevant_even_when_image_required(self):
  from blog_image_stock_preflight import eligible
  item={**self.item,'editorial_image_required':True}
  rows=[{'key':item['key'],'blog':'farsiblog','status':'requested'}]*12
  with patch('blog_image_stock_preflight.rows',return_value=rows):self.assertEqual(eligible([item],'farsiblog',self.root),[item])
  self.assertFalse(policy.generation_needed(item,'farsiblog',self.root))
 def test_source_preferred_worker_never_generates_even_for_visual_required_item(self):
  row={'policy':stock.POLICY,'asset_id':self.asset,'status':'requested','blog':'farsiblog','key':self.item['key'],'created_at':1,'attempts':0,'item':{**self.item,'editorial_image_required':True}}
  self.write(stock.request_path(self.asset),row)
  with patch('blog_image_gate.acceptance_mode',return_value='strict'),patch('blog_generated_image.prepare_now')as api:self.assertEqual(stock.worker_once(self.root)['status'],'idle')
  api.assert_not_called()
 def test_source_mode_cannot_bypass_held_hose_or_retired_blog(self):
  self.assertFalse(source.source_preferred({**self.item,'family':'hose'},'farsiblog',self.root));self.assertFalse(source.source_preferred(self.item,'blogfa',self.root))
 def test_real_public_body_check_verifies_exact_image_url_and_two_links(self):
  from blog_public_content_verify import verify_article_body
  url,item,post=self.prepare();post['html']='<p><img src="'+url+'" alt="نوار تیپ"></p>'+post['html'];item['post']=post
  self.assertTrue(verify_article_body(item,post['html'],self.links))
  with self.assertRaises(RuntimeError):verify_article_body(item,post['html'].replace(url,'https://evil.example/wrong.webp'),self.links)
if __name__=='__main__':unittest.main()
