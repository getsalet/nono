"""Primary keyword + corresponding source article/city; no extra hub links."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import city_backlink_policy as city
import roya_backlink_queue as roya
import test_city_blog_pipeline as city_tests

class TwoLinkPolicyTests(unittest.TestCase):
 def setUp(self):
  self.item={'key':'two-links','kind':'city','family':'tape20','city_fa':'آزمایش','province_fa':'استان آزمایش','site_title':'نوار تیپ در آزمایش','target_url':'https://navar-abyari.ir/city/example/','hub_url':'https://navar-abyari.ir/province/example/'}
  self.lib=json.loads((ROOT/'data/roya/link-library.json').read_text())
 def test_city_and_article_each_have_primary_and_corresponding_destination(self):
  for family in ('tape20','hose'):
   for kind in ('city','article'):
    item={**self.item,'family':family,'kind':kind,'site_title': 'لوله نخی در آزمایش' if family=='hose' else self.item['site_title']}
    links=city.links_for(item)
    self.assertEqual(len(links),2)
    self.assertEqual(len({x['url']for x in links}),2)
    self.assertEqual({x['role']for x in links},{kind,'home'if family=='tape20'else'shop'})
    self.assertNotIn(item['hub_url'],[x['url']for x in links])
 def test_roya_uses_two_contextual_links_for_both_families(self):
  for family in ('tape20','hose'):
   item={**self.item,'family':family,'site_title':'لوله نخی در آزمایش' if family=='hose' else self.item['site_title']}
   links=roya.approved_links(item,self.lib)
   self.assertEqual(len(links),2)
   self.assertEqual({x['role']for x in links},{'city','home'if family=='tape20'else'shop'})
   self.assertNotIn(item['hub_url'],[x['url']for x in links])
   if family=='hose':self.assertNotIn('تیپ',links[1]['anchor'])
 def test_roya_rejects_same_target_and_primary_destination(self):
  with self.assertRaisesRegex(RuntimeError,'must differ'):
   roya.approved_links({**self.item,'target_url':self.lib['home']['url']},self.lib)
 def test_legacy_range_cannot_require_three_links(self):
  self.assertEqual((roya.MIN_LINKS,roya.MAX_LINKS),(2,2))
 def test_roya_no_longer_requires_province_and_rejects_extra_link(self):
  links=roya.approved_links(self.item,self.lib)
  body=''.join('<p><a href="'+x['url']+'">'+x['anchor']+'</a></p>'for x in links)
  errors=roya.qa(self.item,{'title':self.item['site_title'],'html':body},links)[0]
  self.assertNotIn('missing the province hub link',errors)
  self.assertNotIn('Exactly two distinct approved contextual destinations, each once',errors)
  errors=roya.qa(self.item,{'title':self.item['site_title'],'html':body+'<a href="'+self.item['hub_url']+'">استان</a>'},links)[0]
  self.assertIn('Exactly two distinct approved contextual destinations, each once',errors)
 def test_acceptance_workflow_uses_audited_pool_not_single_key(self):
  text=(ROOT/'.github/workflows/blog-generated-image-acceptance.yml').read_text()
  self.assertIn("AGNES_IMAGE_REQUIRE_CAPABILITY_AUDIT: '1'",text)
  self.assertNotIn('AGNES_IMAGE_KEY_SLOTS:',text)
 def test_shared_qa_rejects_extra_missing_duplicate_and_foreign_links(self):
  fixture=city_tests.CityBlogTests('test_valid_city_fixture');fixture.setUp()
  try:
   error='Exactly two distinct approved contextual destinations, each once'
   base=fixture.post
   self.assertEqual(city.qa(fixture.item,copy.deepcopy(base),fixture.links,'farsiblog',fixture.root)[0],[])
   first=fixture.links[0]
   link='<a href="'+first['url']+'">'+first['anchor']+'</a>'
   for body in (base['html'].replace(link,''),base['html']+'<p>'+link+'</p>',base['html']+'<a href="https://other.example/">دیگر</a>',base['html']+'<a href="'+fixture.item['hub_url']+'">استان</a>'):
    with self.subTest(body=body[-80:]):
     post={**base,'html':body}
     self.assertIn(error,city.qa(fixture.item,post,fixture.links,'farsiblog',fixture.root)[0])
  finally:fixture.tearDown()

if __name__=='__main__':unittest.main()
