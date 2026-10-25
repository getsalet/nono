import unittest,tempfile,copy
from unittest.mock import patch,Mock
from pathlib import Path
from automation.agri_v2 import internal_links as l,internal_link_repair as repair
from automation.agri_v2.queue import DATA,load_json
class InternalLinksTests(unittest.TestCase):
 def topic(self):return {'title':'برداشت لوبیا چیتی','crop':'لوبیا چیتی'}
 def url(self):return 'https://navar-abyari.ir/pinto-bean-harvest-loss-timing-tools/'
 def test_primary_keywords_and_related_post_are_real_internal_destinations(self):
  rows=l.selected_links(self.topic(),self.url());self.assertEqual(len(rows),3)
  self.assertEqual(rows[0]['anchor'],'نوار تیپ');self.assertEqual(rows[0]['url'],'https://navar-abyari.ir/')
  self.assertEqual(rows[1]['anchor'],'نوار آبیاری قطره‌ای');self.assertIn('product-category/',rows[1]['url'])
  self.assertEqual(rows[2]['post_id'],36763)
 def test_no_unrelated_crop_links_or_self_link(self):
  rows=l.selected_links({'crop':'گندم'},self.url());self.assertEqual(len(rows),2)
  related=l.selected_links(self.topic(),l.selected_links(self.topic(),self.url())[2]['url']);self.assertEqual(len(related),2)
 def test_preserves_scientific_sources_images_and_final_faq(self):
  body='<!-- owned --><p>متن منبع <a href="https://example.edu/science">منبع دانشگاهی</a>.</p><figure><img src="https://navar-abyari.ir/a.webp"/></figure><h2>سؤالات متداول</h2><div class="faq-section"><details>FAQ</details></div>'
  result=l.augment(body,self.topic(),self.url());self.assertEqual(l.external_links(result),['https://example.edu/science'])
  self.assertIn('<figure><img src="https://navar-abyari.ir/a.webp"/></figure>',result);self.assertTrue(result.endswith('<div class="faq-section"><details>FAQ</details></div>'))
  l.verify_links(result,l.selected_links(self.topic(),self.url()));self.assertLess(result.index('برای آشنایی'),result.index('<h2>سؤالات'))
 def test_linkifies_first_natural_occurrence_only(self):
  result=l.augment('<p>نوار تیپ در مزرعه؛ نوار تیپ و نوار آبیاری قطره ای.</p>',{'crop':'گندم'},self.url())
  self.assertIn('<a href="https://navar-abyari.ir/">نوار تیپ</a>',result);self.assertNotIn('برای آشنایی',result)
  self.assertEqual(len(l.anchors(result)),2)
 def test_idempotent_and_no_nested_anchors(self):
  body='<p><a href="https://example.edu/science">منبع نوار تیپ</a></p>'
  first=l.augment(body,self.topic(),self.url());self.assertEqual(l.augment(first,self.topic(),self.url()),first)
  self.assertEqual(l.external_links(first),['https://example.edu/science']);self.assertNotIn('<a href="https://example.edu/science">منبع <a',first)
 def test_headings_attributes_and_code_not_rewritten(self):
  body='<h2>نوار تیپ</h2><p data-note="نوار تیپ"><code>نوار تیپ</code></p>'
  result=l.augment(body,{'crop':'گندم'},self.url());self.assertIn('<h2>نوار تیپ</h2>',result);self.assertIn('data-note="نوار تیپ"',result);self.assertIn('<code>نوار تیپ</code>',result)
 def test_external_or_unsafe_internal_destination_rejected(self):
  for url in ['https://evil.invalid/','http://navar-abyari.ir/','https://user@navar-abyari.ir/','https://navar-abyari.ir:444/','https://navar-abyari.ir/?redirect=bad']:
   with self.assertRaises(ValueError):l.canonical(url)
 def test_verification_rejects_unlinked_keyword(self):
  with self.assertRaises(ValueError):l.verify_links('<p>نوار تیپ</p>',l.selected_links({'crop':'گندم'},self.url()))
 def test_only_one_owned_post_and_no_new_models_or_posts(self):
  r=load_json(DATA/'internal-link-repair-request.json');repair.validate(r)
  for key,value in [('post_id',1),('max_new_posts',1),('max_model_calls',1),('max_existing_posts',2)]:
   bad=copy.deepcopy(r);bad[key]=value
   with self.assertRaises(ValueError):repair.validate(bad)
 def test_repair_receipt_prevents_repeated_mutation(self):
  from automation.agri_v2.queue import atomic_json
  with tempfile.TemporaryDirectory() as tmp,patch.object(repair,'OUT',Path(tmp)),patch.object(repair,'WordPress') as wp:
   atomic_json(Path(tmp)/'internal-link-repairs'/repair.ID/'receipt.json',{'status':'public_links_verified'})
   self.assertEqual(repair.run()['status'],'already_reserved');wp.assert_not_called()
 def test_owned_live_repair_updates_content_only_and_preserves_sources(self):
  from automation.agri_v2.queue import atomic_json
  from automation.agri_v2.client import ModelClient
  request=load_json(DATA/'internal-link-repair-request.json');before='<!-- afp-agri-v2:'+repair.TOPIC+' --><p>متن برداشت <a href="https://example.edu/source">منبع دانشگاهی</a></p><figure><img src="https://navar-abyari.ir/a.webp"/></figure><h2>سؤالات متداول</h2><div>FAQ</div>'
  post={'id':repair.POST,'author':7,'status':'publish','modified_gmt':request['expected_modified_gmt'],'content':{'raw':before},'featured_media':101,'title':{'raw':'عنوان آزمایشی','rendered':'عنوان آزمایشی'},'link':self.url()};mutations=[]
  wp=Mock();wp.user_id=7;wp.verify.return_value={'public_verified':True,'url':self.url()}
  def call(path,method='GET',data=None):
   if method=='POST':mutations.append(data);post['content']['raw']=data['content']
   result=copy.deepcopy(post)
   if '?context=edit' not in path:result['content']['rendered']=result['content']['raw']
   return result,{}
  wp.call=call
  with tempfile.TemporaryDirectory() as tmp,patch.object(repair,'OUT',Path(tmp)),patch.object(repair,'authorized',return_value=True),patch.object(repair,'WordPress',return_value=wp),patch.object(repair,'validate_targets'),patch.object(ModelClient,'request',side_effect=AssertionError('No model calls')) as provider:
   atomic_json(Path(tmp)/'new'/repair.TOPIC/'wordpress-receipt.json',{'post_id':repair.POST})
   result=repair.run();self.assertEqual(result['status'],'public_links_verified');self.assertEqual(len(mutations),1);self.assertEqual(set(mutations[0]),{'content'})
   self.assertEqual(l.external_links(post['content']['raw']),l.external_links(before));self.assertEqual(post['content']['raw'].count('<figure>'),1)
   backup=load_json(Path(tmp)/'internal-link-repairs'/repair.ID/'before.json');self.assertEqual(backup['content_raw'],before);provider.assert_not_called()
 def test_unowned_post_is_never_modified(self):
  wp=Mock();wp.user_id=7;wp.call.return_value=({'id':repair.POST,'author':99,'status':'publish','content':{'raw':'<!-- afp-agri-v2:'+repair.TOPIC+' -->'}},{})
  with tempfile.TemporaryDirectory() as tmp,patch.object(repair,'OUT',Path(tmp)),patch.object(repair,'authorized',return_value=True),patch.object(repair,'WordPress',return_value=wp):
   with self.assertRaises(repair.WPError):repair.run()
   self.assertEqual(wp.call.call_count,1)
