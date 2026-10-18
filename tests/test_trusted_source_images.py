"""Owner-trusted exact-site images need no vision, pixel fetch or second check."""
import copy,json,os,sys,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_source_image as source
import blog_editorial_image_policy as policy
import activate_blog_publication as activate
import test_blog_editorial_image_policy as fixtures
class TrustedSourceTests(unittest.TestCase):
 write=fixtures.EditorialImagePolicyTests.write
 qa=fixtures.EditorialImagePolicyTests.qa
 def setUp(self):
  fixtures.EditorialImagePolicyTests.setUp(self)
  self.cfg.update(source_image_preferred=True,source_image_review_required=False);self.write(policy.CONFIG,self.cfg)
  self.url='https://navar-abyari.ir/wp-content/uploads/own-article.webp'
  self.page='<article><img src="'+self.url+'"></article>'
 def prepare(self,blog='farsiblog'):
  with patch.object(source,'read_page',return_value=self.page)as page,patch('blog_image_gate.fetch',side_effect=AssertionError('No image fetch')),patch.object(source,'review_candidate',side_effect=AssertionError('No vision')),patch('blog_generated_image.prepare_now',side_effect=AssertionError('No generation')):
   self.assertEqual(policy.prepare_article(self.item,self.post,blog,self.root,Mock(side_effect=AssertionError('No callback'))),self.url)
  page.assert_called_once_with(self.item['target_url'])
 def test_initial_discovery_has_no_image_api_review_score_or_fake_dimensions(self):
  self.prepare()
  self.assertFalse(self.item['image_source']['visual_review_performed'])
  for key in ('source_image_review','image_review','image_generation','image_width','image_height'):self.assertNotIn(key,self.item)
  self.assertNotIn('score',json.dumps(self.item['image_source']))
 def test_every_active_blog_trusts_existing_exact_source(self):
  for blog in ('roya','farsiblog','rozblog','loxblog'):
   self.item.pop('image_source',None);self.prepare(blog)
   self.assertEqual(source.source_record_errors(self.item,blog,self.root),[])
 def test_saved_selection_is_reused_without_even_reading_source_page(self):
  self.prepare()
  with patch.object(source,'read_page',side_effect=AssertionError('No repeat source page')),patch('blog_image_gate.fetch',side_effect=AssertionError('No fetch')),patch.object(source,'review_candidate',side_effect=AssertionError('No vision')):
   self.assertEqual(source.prepare_source(self.item,self.post,'farsiblog',self.root),self.url)
 def test_publication_has_no_network_or_model_or_fabricated_pass(self):
  self.prepare()
  with patch.object(source,'read_page',side_effect=AssertionError('No page recheck')),patch('blog_image_gate.fetch',side_effect=AssertionError('No pixel recheck')),patch.object(source,'review_candidate',side_effect=AssertionError('No vision')):
   result=source.review_for_publication(self.item,'farsiblog',self.root)
  self.assertIs(result['visual_review_performed'],False);self.assertIs(result['recheck_performed'],False)
  self.assertNotIn('score',result);self.assertNotIn('pass',result)
 def test_prior_reviewed_source_is_trusted_without_requiring_stale_score(self):
  self.prepare();self.item['image_source']['policy']=source.POLICY
  self.item['source_image_review']={'verdict':{'pass':False,'score':88}}
  with patch.object(source,'read_page',side_effect=AssertionError('No page')):
   self.assertEqual(source.prepare_source(self.item,self.post,'farsiblog',self.root),self.url)
  self.assertNotIn('source_image_review',self.item)
 def test_wrong_destination_owner_or_external_url_still_rejected_locally(self):
  self.prepare()
  for fields in ({'target_url':'https://navar-abyari.ir/other/'},{'key':'other'},{'image_url':'https://evil.example/a.webp'},{'image_generation':{'fake':True}}):
   self.assertTrue(source.source_record_errors({**self.item,**fields},'farsiblog',self.root))
 def test_missing_optional_source_publishes_text_without_generation(self):
  with patch.object(source,'read_page',return_value='<article>متن</article>'),patch('blog_generated_image.prepare_now',side_effect=AssertionError('No generation')):
   self.assertIsNone(source.prepare_source(self.item,self.post,'farsiblog',self.root))
  self.assertEqual(self.qa(),[])
 def test_required_illustration_missing_still_stops(self):
  self.item['editorial_image_required']=True
  with patch.object(source,'read_page',return_value='<article>متن</article>'):
   with self.assertRaises(source.SourceImageUnavailable):source.prepare_source(self.item,self.post,'farsiblog',self.root)
 def test_text_and_two_link_quality_gates_still_apply(self):
  self.prepare();self.post['html']=source.image_markup(self.item)+self.post['html'];self.post['image_url']=self.url
  self.assertEqual(self.qa(),[])
  for p in ({**self.post,'html':'<p>متن کوتاه</p>'},{**self.post,'html':self.post['html'].replace(self.links[0]['url'],'https://evil.example/')}):self.assertTrue(self.qa(post=p))
 def test_natural_proportions_and_attribute_escaping(self):
  self.prepare();markup=source.image_markup(self.item,'متن " تست')
  self.assertNotIn('width=',markup);self.assertNotIn('height=',markup);self.assertIn('&quot;',markup)
  import roya_backlink_queue as roya
  post=roya.inject_image(self.item,{'html':'<p>متن</p>'},self.url)
  self.assertNotIn('height=',post['html'])
  self.item.update(image_width=640,image_height=480);self.assertIn('width="640" height="480"',source.image_markup(self.item))
 def test_malformed_flag_fails_closed_and_scope_excludes_hose_blogfa(self):
  for value in (0,'false',None):
   self.write(policy.CONFIG,{**self.cfg,'source_image_review_required':value})
   with self.assertRaises(RuntimeError):source.trusted_source(self.item,'farsiblog',self.root)
  self.write(policy.CONFIG,self.cfg)
  self.assertFalse(source.trusted_source({**self.item,'family':'hose'},'roya',self.root))
  self.assertFalse(source.trusted_source(self.item,'blogfa',self.root))
 def test_activation_dispatches_only_one_per_active_blog_without_vision_gate(self):
  control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text());self.write('data/blog-generated-image-control.json',control)
  response=Mock();response.__enter__=Mock(return_value=Mock(status=204));response.__exit__=Mock(return_value=False)
  with patch.object(activate,'ROOT',self.root),patch.object(activate.urllib.request,'urlopen',return_value=response)as api,patch('blog_generated_image.rollout_enabled',side_effect=AssertionError('No generated-image acceptance')),patch.dict(os.environ,{'GH_TOKEN':'offline-fixture','GITHUB_STEP_SUMMARY':''}):
   self.assertEqual(activate.main(),0)
  self.assertEqual(api.call_count,4)
  for call in api.call_args_list:
   req=call.args[0];payload=json.loads(req.data);self.assertEqual(payload['inputs']['count'],'1');self.assertNotIn('blogfa',req.full_url)
 def test_activation_still_honors_pause_and_explicit_trust(self):
  control=json.loads((ROOT/'data/blog-generated-image-control.json').read_text());control['pause_image_production']=True;self.write('data/blog-generated-image-control.json',control)
  with patch.object(activate,'ROOT',self.root),patch.object(activate.urllib.request,'urlopen')as api:self.assertEqual(activate.main(),0)
  api.assert_not_called();control['pause_image_production']=False;self.write('data/blog-generated-image-control.json',control);self.cfg['source_image_review_required']=True;self.write(policy.CONFIG,self.cfg)
  with patch.object(activate,'ROOT',self.root),patch.object(activate.urllib.request,'urlopen')as api:
   with self.assertRaises(RuntimeError):activate.main()
  api.assert_not_called()
