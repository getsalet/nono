import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import city_backlink_policy as c
import blog_image_gate as g
from content_originality import corpus
class CityBlogTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.matrix={'approved':True,'approval_note':'unit-test fixture only, never production','templates':{b:{'tape20':['راهنمای نوار تیپ در {city}'],'hose':['راهنمای لوله نخی و تاشو در {city}']}for b in c.BLOGS}}
  c.write(self.root/'data/blog-city-title-matrix.json',self.matrix)
  self.item={'kind':'city','key':'city-fixture','family':'tape20','city_fa':'آزمایش','province_fa':'آزمایش','site_title':'نوار تیپ در آزمایش','target_url':'https://navar-abyari.ir/city/tape/','hub_url':'https://navar-abyari.ir/province/','image_url':'https://navar-abyari.ir/wp-content/uploads/fixture.webp'}
  self.verdict={'pass':True,'score':85,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False}
  self.item['image_review']={'policy':g.POLICY,'family':'tape20','sha256':'a'*64,'source_url':self.item['image_url'],'verdict':self.verdict}
  self.links=c.links_for(self.item)
  body='<p><img src="'+self.item['image_url']+'" alt="نمای نوار تیپ"></p>'
  for n in range(3):body+='<h2>بررسی انتخاب تجهیزات</h2><p>'+' '.join('بررسیآبیاری'+str(i+n*200)for i in range(200))+'</p>'
  body+='<ul><li>بررسی مدل</li></ul>'+''.join('<p><a href="'+x['url']+'">'+x['anchor']+'</a></p>'for x in self.links)
  body+=''.join('<details><summary>چگونه انتخاب کنیم؟</summary><p>مشخصات همان مدل را بررسی کنید.</p></details>'for _ in range(3))
  self.post={'title':c.matrix_title(self.item,'farsiblog',self.root),'slug':'city-test-fixture','tags':['آبیاری'],'meta_description':'این راهنما به بررسی مشخصات تجهیزات آبیاری و آماده‌سازی اطلاعات مورد نیاز برای انتخاب متناسب با شرایط زمین کمک می‌کند.','html':body}
 def tearDown(self):self.tmp.cleanup()
 def test_valid_city_fixture(self):self.assertEqual(c.qa(self.item,self.post,self.links,'farsiblog',self.root)[0],[])
 def test_wrong_product_never_passes(self):
  v=copy.deepcopy(self.verdict);v['observed_family']='hose';self.assertTrue(g.verdict_errors(v,'tape20'))
  v=copy.deepcopy(self.verdict);v['wrong_product_present']=True;self.assertTrue(g.verdict_errors(v,'tape20'))
  self.assertTrue(g.verdict_errors({'pass':True,'score':100},'tape20'))
 def test_unknown_family_does_not_default_to_tape(self):
  with self.assertRaises(RuntimeError):g.family({'family':'unknown'})
  with self.assertRaises(RuntimeError):g.family({'family':'tape20','site_title':'لوله نخی و تاشو'})
 def test_unapproved_matrix_blocks_qa(self):
  self.matrix['approved']=False;c.write(self.root/'data/blog-city-title-matrix.json',self.matrix);self.assertTrue(c.qa(self.item,self.post,self.links,'farsiblog',self.root)[0])
 def test_title_and_image_change_rejected(self):
  p=copy.deepcopy(self.post);p['title']='عنوان دیگری در آزمایش';self.assertTrue(c.qa(self.item,p,self.links,'farsiblog',self.root)[0])
  i=copy.deepcopy(self.item);i['image_url']='https://navar-abyari.ir/wp-content/uploads/other.webp';self.assertTrue(g.validate_record(i))
 def test_city_queue_no_hubs_and_no_text_copy(self):
  row={**self.item,'key':'source','status':'published','post':{'html':'Never copied'}}
  hub={**row,'key':'hub','family':'hub'}
  c.write(self.root/'data/roya/backlink-queue.json',{'items':[row,hub]})
  a=c.build_queue('rozblog',self.root);b=c.build_queue('rozblog',self.root)
  self.assertEqual(len(a['items']),1);self.assertEqual(len(b['items']),1);self.assertNotIn('post',a['items'][0]);self.assertEqual(a['items'][0]['status'],'pending')
 def test_third_blog_originality_history_included(self):
  path=self.root/'artifacts/rozblog-backlink-queue/items/a.json';c.write(path,{'key':'a','qa':{'passed':True},'post':self.post})
  self.assertEqual(len(corpus(self.root,'farsiblog','other')),1)
 def test_hose_keywords_not_forced_to_home(self):
  i={**self.item,'family':'hose','site_title':'لوله نخی در آزمایش'};links=c.links_for(i);self.assertFalse(any(x['role']=='home'for x in links));self.assertTrue(any(x['role']=='shop'for x in links))
 def test_distinct_assigned_titles_for_same_source_title(self):
  self.matrix['templates']['farsiblog']['tape20'].append('چک‌لیست نوار تیپ در {city}');c.write(self.root/'data/blog-city-title-matrix.json',self.matrix)
  row={**self.item,'key':'s1'};other={**self.item,'key':'s2','target_url':'https://navar-abyari.ir/city/other/'}
  c.write(self.root/'data/roya/backlink-queue.json',{'items':[row,other]})
  q=c.build_queue('farsiblog',self.root);self.assertEqual(len({x['assigned_title']for x in q['items']}),2)
 def test_missing_vision_record_blocks_publication(self):
  i=copy.deepcopy(self.item);del i['image_review'];self.assertTrue(c.qa(i,self.post,self.links,'farsiblog',self.root)[0])
if __name__=='__main__':unittest.main()
