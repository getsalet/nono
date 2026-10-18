"""Optional absence only; never an image/text quality or publication shortcut."""
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_editorial_image_policy as policy
import city_backlink_policy as city
import blog_image_stock as stock
import farsiblog_backlink_queue as f
import check_blog_ready_image_handoff as handoff
class EditorialImagePolicyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.cfg=json.loads((ROOT/policy.CONFIG).read_text());self.write(policy.CONFIG,self.cfg)
  self.matrix={'approved':True,'approval_note':'offline fixture','templates':{b:{'tape20':['راهنمای نوار تیپ در {city}']}for b in city.BLOGS}}
  self.write('data/blog-city-title-matrix.json',self.matrix)
  self.item={'kind':'city','key':'city-fixture','family':'tape20','city_fa':'آزمایش','province_fa':'آزمایش','site_title':'نوار تیپ در آزمایش','target_url':'https://navar-abyari.ir/city/tape/','status':'failed','failure_stage':'image','next_retry_at':'2099-01-01T00:00:00Z'}
  self.links=city.links_for(self.item)
  body=''.join('<h2>بررسی تجهیزات</h2><p>'+' '.join('بررسیآبیاری'+str(i+n*200)for i in range(200))+'</p>'for n in range(3))
  body+='<ul><li>بررسی مشخصات مدل</li></ul>'+''.join('<p><a href="'+x['url']+'">'+x['anchor']+'</a></p>'for x in self.links)
  body+=''.join('<details><summary>چطور انتخاب کنیم؟</summary><p>مشخصات مدل را بررسی کنید.</p></details>'for _ in range(3))
  self.post={'title':city.matrix_title(self.item,'farsiblog',self.root),'slug':'text-only-fixture','meta_description':'این راهنما به بررسی مشخصات تجهیزات آبیاری و آماده‌سازی اطلاعات مورد نیاز برای انتخاب متناسب با شرایط زمین کمک می‌کند.','tags':['آبیاری'],'html':body}
  self.asset='a'*32
  self.write('data/blog-generated-image-control.json',{'pause_image_production':False,'retired_blogs':['blogfa']})
  self.write(stock.CONFIG,{'enabled':True,'target':12,'per_blog_limit':3,'text_preflight_required':True})
 def write(self,p,v):
  path=self.root/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v,ensure_ascii=False))
 def qa(self,item=None,post=None,blog='farsiblog'):
  return city.qa(item or self.item,post or self.post,self.links,blog,self.root)[0]
 def record(self):return {**self.item,'status':'failed','failure_stage':'image','post':copy.deepcopy(self.post)}
 def test_text_only_passes_full_text_qa_on_active_city_blogs(self):
  for blog in ('farsiblog','rozblog','loxblog'):
   self.assertEqual(self.qa(blog=blog),[])
 def test_absent_policy_preserves_mandatory_image_gate(self):
  (self.root/policy.CONFIG).unlink();self.assertTrue(policy.required(self.item,'farsiblog',self.root));self.assertTrue(self.qa())
 def test_invalid_policy_does_not_become_optional(self):
  for cfg in ({},{**self.cfg,'families':['tape20','hose']},{**self.cfg,'blogs':self.cfg['blogs']+['blogfa']}):
   self.write(policy.CONFIG,cfg)
   with self.assertRaises(RuntimeError):self.qa()
 def test_held_or_retired_scope_cannot_become_image_free(self):
  self.assertTrue(policy.required({**self.item,'family':'hose'},'farsiblog',self.root))
  self.assertTrue(policy.required(self.item,'blogfa',self.root))
  self.assertTrue(policy.required({**self.item,'family':'unknown'},'roya',self.root))
 def test_explicit_need_and_visual_title_or_body_stay_required(self):
  self.assertTrue(self.qa(item={**self.item,'editorial_image_required':True}))
  for title in ('راهنمای تصویری نصب نوار تیپ','نمودار فشار نوار تیپ','عکس نوار تیپ'):
   self.assertTrue(policy.required(self.item,'farsiblog',self.root,{**self.post,'title':title}))
  for text in ('طبق تصویر، مسیر را بررسی کنید','در تصویر زیر فاصله دیده می‌شود','نمودار پیوست را ببینید'):
   p={**self.post,'html':self.post['html']+'<p>'+text+'</p>'};self.assertTrue(self.qa(post=p))
 def test_false_flag_does_not_override_visual_dependency(self):
  self.assertTrue(policy.required({**self.item,'editorial_image_required':False},'roya',self.root,{**self.post,'title':'راهنمای تصویری نصب'}))
  with self.assertRaises(RuntimeError):policy.required({**self.item,'editorial_image_required':'false'},'roya',self.root)
 def test_any_present_image_still_requires_genuine_owner_and_review(self):
  p={**self.post,'html':'<p><img src="https://example.com/fake.webp" alt="تصویر"></p>'+self.post['html']}
  self.assertTrue(self.qa(post=p))
  self.assertTrue(self.qa(item={**self.item,'image_url':'https://example.com/fake.webp'}))
  self.assertTrue(self.qa(item={**self.item,'image_review':{'verdict':{'pass':True,'score':100}}}))
 def test_text_quality_links_and_originality_unchanged(self):
  for p in ({**self.post,'html':'<p>متن کوتاه</p>'},{**self.post,'html':self.post['html'].replace(self.links[0]['url'],'https://evil.example/')},{**self.post,'html':self.post['html']+'<script>bad</script>'}):self.assertTrue(self.qa(post=p))
  self.write('artifacts/rozblog-backlink-queue/items/published.json',{'key':'old','qa':{'passed':True},'post':self.post});self.assertTrue(self.qa())
 def test_optional_preparation_never_calls_image_provider_or_fills_fake_fields(self):
  item=copy.deepcopy(self.item);post=copy.deepcopy(self.post);callback=Mock(side_effect=AssertionError('No image work allowed'))
  with patch('blog_generated_image.identity',return_value=self.asset):self.assertIsNone(policy.prepare_article(item,post,'farsiblog',self.root,callback))
  callback.assert_not_called();self.assertFalse(policy.has_image(item,post));self.assertEqual(item['editorial_image_decision'],'text_only_no_visual_dependency')
 def test_required_preparation_still_calls_real_image_path(self):
  item={**self.item,'editorial_image_required':True};callback=Mock(return_value='genuine-result')
  self.assertEqual(policy.prepare_article(item,self.post,'farsiblog',self.root,callback),'genuine-result');callback.assert_called_once()
 def test_ready_image_is_retained_and_failure_never_falls_back_to_text(self):
  row={'status':'ready'};callback=Mock(return_value='real-cached-image')
  with patch('blog_generated_image.identity',return_value=self.asset),patch.object(stock,'read',return_value=row):
   self.assertEqual(policy.prepare_article(copy.deepcopy(self.item),self.post,'farsiblog',self.root,callback),'real-cached-image')
   callback.side_effect=RuntimeError('Invalid cached bytes')
   with self.assertRaises(RuntimeError):policy.prepare_article(copy.deepcopy(self.item),self.post,'farsiblog',self.root,callback)
 def test_stock_capacity_and_old_provider_timer_do_not_block_optional_prose(self):
  from blog_image_stock_preflight import eligible
  rows=[{'blog':'farsiblog','key':'waiting-'+str(i),'status':'requested'}for i in range(12)]
  with patch('blog_image_stock_preflight.rows',return_value=rows):self.assertEqual(eligible([self.item],'farsiblog',self.root),[self.item])
  self.assertTrue(policy.saved_optional(self.record(),self.item,'farsiblog',self.root))
  self.assertFalse(policy.saved_optional({**self.record(),'failure_stage':'text_validation'},self.item,'farsiblog',self.root))
 def test_text_handoff_requires_intact_saved_draft_and_stop_gate(self):
  self.write('data/farsiblog/backlink-queue.json',{'items':[self.item]});self.write('artifacts/farsiblog-backlink-queue/items/city-fixture.json',self.record())
  self.assertEqual(handoff.handoff('push','farsiblog',self.root),{'proceed':True,'cached_only':True,'target':'city-fixture'})
  self.write('data/blog-generated-image-control.json',{'pause_image_production':True});self.assertFalse(handoff.handoff('push','farsiblog',self.root)['proceed'])
 def test_missing_saved_post_cannot_wake_new_text_generation(self):
  self.write('data/farsiblog/backlink-queue.json',{'items':[self.item]});self.write('artifacts/farsiblog-backlink-queue/items/city-fixture.json',{**self.record(),'post':None})
  self.assertFalse(handoff.handoff('push','farsiblog',self.root)['proceed'])
 def test_worker_cancels_optional_demand_without_generation(self):
  row={'policy':stock.POLICY,'asset_id':self.asset,'status':'requested','blog':'farsiblog','key':self.item['key'],'created_at':1,'attempts':0,'item':self.item}
  self.write(stock.request_path(self.asset),row)
  with patch('blog_image_gate.acceptance_mode',return_value='strict'),patch('blog_generated_image.prepare_now')as api:
   result=stock.worker_once(self.root)
  self.assertEqual(result['status'],'idle');api.assert_not_called()
  saved=json.loads((self.root/stock.request_path(self.asset)).read_text());self.assertEqual(saved['status'],'cancelled');self.assertEqual(saved['attempts'],0)
 def test_shared_generator_recovers_saved_optional_article_with_zero_source_text_or_image_calls(self):
  self.write('data/farsiblog/backlink-queue.json',{'items':[self.item]});self.write('artifacts/farsiblog-backlink-queue/items/city-fixture.json',self.record())
  env={'FARSIBLOG_DRY_RUN':'0','FARSIBLOG_COUNT':'1','FARSIBLOG_TARGET':self.item['key'],'BLOG_READY_IMAGE_HANDOFF':'1'}
  with patch.multiple(f,ROOT=self.root,QUEUE=self.root/'data/farsiblog/backlink-queue.json',ART=self.root/'artifacts/farsiblog-backlink-queue',STATE=self.root/'state/farsiblog-backlink-progress.json',CITY_BLOG='farsiblog'),patch.object(city,'ROOT',self.root),patch.object(city,'build_queue'),patch.object(f.BASE,'AGNES_KEY','offline-test'),patch.dict(os.environ,env),patch('blog_generated_image.family_enabled',return_value=True),patch('blog_generated_image.identity',return_value=self.asset),patch.object(f,'agnes')as text,patch.object(f,'source_text')as source,patch.object(city,'prepare_image')as image,patch.object(stock,'require_generation_open')as throttle:
   self.assertEqual(f.main(),0)
  for call in (text,source,image,throttle):call.assert_not_called()
  record=json.loads((self.root/'artifacts/farsiblog-backlink-queue/items/city-fixture.json').read_text());self.assertTrue(record['qa']['passed']);self.assertEqual(record['status'],'completed');self.assertNotIn('<img',record['post']['html']);self.assertNotIn('image_url',record)
 def test_workflows_keep_real_publication_observation_and_original_safety_guards(self):
  for name in ('roya-backlink-publish','farsiblog-content','rozblog-content','loxblog-content'):
   text=(ROOT/'.github/workflows'/(name+'.yml')).read_text();self.assertIn('python automation/blog_publication_throughput.py',text);self.assertIn('steps.control.outputs.proceed',text);self.assertIn('cancel-in-progress: false',text)
 def test_roya_text_only_still_validates_links_and_missing_image_need(self):
  import roya_backlink_queue as roya
  item={**self.item,'assigned_title':self.post['title']}
  with patch.object(roya,'MIN_LINKS',2),patch.object(roya,'MAX_LINKS',2):
   self.assertEqual(roya.qa(item,self.post,self.links,root=self.root)[0],[])
   self.assertTrue(roya.qa({**item,'editorial_image_required':True},self.post,self.links,root=self.root)[0])
 def test_public_text_body_verification_catches_truncation_missing_links_and_images(self):
  from blog_public_content_verify import verify_text_body
  item={'post':self.post}
  self.assertTrue(verify_text_body(item,self.post['html'],self.links))
  for body in (self.post['html'][:500],self.post['html'].replace(self.links[0]['url'],'https://wrong.example/'),'<img src="fake">'+self.post['html']):
   with self.assertRaises(RuntimeError):verify_text_body(item,body,self.links)
 def test_rebuild_preserves_explicit_editorial_need(self):
  import build_roya_queue as builder
  result=builder.retained_runtime({**self.item,'editorial_image_required':True},self.item['key'])
  self.assertIs(result['editorial_image_required'],True)
 def test_bad_attached_image_without_stock_receipt_is_not_dropped(self):
  item={**self.item,'image_url':'https://example.com/fake','image_review':{'verdict':{'pass':True}},'image_generation':{'policy':'unknown'}}
  with patch('blog_generated_image.identity',return_value=self.asset):
   with self.assertRaises(RuntimeError):policy.prepare_article(item,self.post,'farsiblog',self.root,Mock())
if __name__=='__main__':unittest.main()
