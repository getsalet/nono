"""Cached-only image/article handoff: stdlib gate, no API, no approval shortcut."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import check_blog_ready_image_handoff as h
class ReadyImageHandoffTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.asset='a'*32;self.key='city-existing';self.raw=b'saved-asset-fixture';self.digest=hashlib.sha256(self.raw).hexdigest()
  self.post={'title':'عنوان مقاله','slug':'saved','meta_description':'شرح مقاله','html':'<p>این متن واقعی مقاله ذخیره شده است و در مرحله تصویر متوقف شده است.</p>'}
  self.context={'title':self.post['title'],'meta_description':self.post['meta_description'],'summary':'این متن واقعی مقاله ذخیره شده است و در مرحله تصویر متوقف شده است.'}
  self.source={'key':self.key,'family':'tape20','status':'failed','_image_stock_request':self.asset,'_image_article_context':self.context}
  self.row={'blog':'rozblog','status':'ready','asset_id':self.asset,'key':self.key,'review_sha256':self.digest,'ready_at':10,'item':{'_image_article_context':self.context}}
  self.record={'status':'failed','failure_stage':'image','post':self.post}
  self.save()
 def write(self,p,v):
  p=self.root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
 def save(self):
  self.write('data/blog-generated-image-control.json',{'pause_image_production':False})
  self.write('data/rozblog/backlink-queue.json',{'items':[self.source]})
  self.write('data/blog-image-stock/requests/'+self.asset+'.json',self.row)
  self.write('artifacts/rozblog-backlink-queue/items/'+self.key+'.json',self.record)
  p=self.root/'assets/blog-generated/rozblog'/f'{self.asset}.webp';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(self.raw)
 def test_selects_existing_ready_image_and_saved_draft(self):
  self.assertEqual(h.select('rozblog',self.root),self.key)
  for event in ('push','workflow_run'):self.assertEqual(h.handoff(event,'rozblog',self.root),{'proceed':True,'cached_only':True,'target':self.key})
 def test_normal_schedules_do_not_become_cached_only(self):
  self.assertEqual(h.handoff('schedule','rozblog',self.root),{'proceed':True,'cached_only':False,'target':''})
 def test_consumed_waiting_or_published_never_select(self):
  for status in ('requested','processing','consumed'):
   self.row['status']=status;self.save();self.assertIsNone(h.select('rozblog',self.root))
  self.row['status']='ready';self.source['published']=True;self.save();self.assertIsNone(h.select('rozblog',self.root))
 def test_changed_article_context_or_wrong_owner_never_select(self):
  self.post['html']+='<p>متن تغییر کرده است</p>';self.save();self.assertIsNone(h.select('rozblog',self.root))
  self.post['html']=self.post['html'].split('<p>متن تغییر')[0];self.source['_image_stock_request']='b'*32;self.save();self.assertIsNone(h.select('rozblog',self.root))
 def test_missing_or_tampered_asset_never_select(self):
  p=self.root/'assets/blog-generated/rozblog'/f'{self.asset}.webp';p.write_bytes(b'changed');self.assertIsNone(h.select('rozblog',self.root))
  p.unlink();self.assertIsNone(h.select('rozblog',self.root))
 def test_non_image_stage_or_missing_draft_cannot_start_generation(self):
  self.record['failure_stage']='text_validation';self.save();self.assertIsNone(h.select('rozblog',self.root))
  self.record['failure_stage']='image';self.record['post']=None;self.save();self.assertFalse(h.handoff('push','rozblog',self.root)['proceed'])
 def test_user_pause_still_blocks_handoff(self):
  self.write('data/blog-generated-image-control.json',{'pause_image_production':True});self.assertIsNone(h.select('rozblog',self.root))
 def test_workflow_limits_handoff_to_saved_target_and_existing_gates(self):
  text=(ROOT/'.github/workflows/rozblog-content.yml').read_text()
  for value in ('workflow_run:',"workflows: ['Independent AFP article image stock (no publication)']",'needs: [tests, image_handoff]','head_repository.full_name == github.repository','BLOG_READY_IMAGE_HANDOFF:','needs.image_handoff.outputs.target','check_blog_run_budget.py rozblog','check_blog_pipeline_control.py rozblog','publish_rozblog_posts.py'):
   self.assertIn(value,text)
  self.assertIn('ROZBLOG_AUTOMATION_ENABLED',text);self.assertIn("with: {ref: main}",text)
 def install_blog(self,blog,key='city-existing'):
  import re
  self.row['blog']=blog;self.row['key']=key;self.source['key']=key
  self.write('data/'+blog+'/backlink-queue.json',{'items':[self.source]})
  self.write('data/blog-image-stock/requests/'+self.asset+'.json',self.row)
  filename=re.sub(r'[^A-Za-z0-9._-]+','_',key)if blog=='roya'else key
  self.write('artifacts/'+blog+'-backlink-queue/items/'+filename+'.json',self.record)
  p=self.root/'assets/blog-generated'/blog/(self.asset+'.webp');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(self.raw)
 def test_all_active_blogs_use_the_same_exact_owner_and_digest_gate(self):
  for blog in ('farsiblog','loxblog','roya'):
   key='south_khorasan/%d9%86-test'if blog=='roya'else self.key
   with self.subTest(blog=blog):
    self.install_blog(blog,key);self.assertEqual(h.select(blog,self.root),key)
    self.row['review_sha256']='b'*64;self.install_blog(blog,key);self.assertIsNone(h.select(blog,self.root));self.row['review_sha256']=self.digest
 def test_roya_sanitized_path_collision_is_rejected(self):
  key='province/city';self.install_blog('roya',key)
  self.write('data/roya/backlink-queue.json',{'items':[self.source,{**self.source,'key':'province_city'}]})
  self.assertIsNone(h.select('roya',self.root))
 def test_roya_control_characters_and_retired_blog_are_rejected(self):
  self.install_blog('roya','province/city\nunsafe');self.assertIsNone(h.select('roya',self.root))
  with self.assertRaises(ValueError):h.select('blogfa',self.root)
 def test_workflows_preserve_trust_release_budget_and_native_gates(self):
  for blog in ('farsiblog','loxblog'):
   text=(ROOT/'.github/workflows'/f'{blog}-content.yml').read_text()
   for value in ('workflow_run:', 'head_repository.full_name == github.repository', 'BLOG_READY_IMAGE_HANDOFF:', 'needs.image_handoff.outputs.target','check_blog_run_budget.py '+blog,'publish_'+blog+'_posts.py'):
    self.assertIn(value,text)
   if blog=='loxblog':self.assertIn('check_loxblog_release.py',text)
   else:self.assertIn('vars.FARSIBLOG_AUTOMATION_ENABLED',text)
  text=(ROOT/'.github/workflows/roya-backlink-queue.yml').read_text()
  self.assertIn('head_repository.full_name == github.repository',text);self.assertIn('BLOG_READY_IMAGE_HANDOFF:',text)
 def test_stock_schedule_can_support_six_images_per_hour_without_a_burst(self):
  text=(ROOT/'.github/workflows/blog-image-stock.yml').read_text()
  self.assertIn("cron: '*/5 * * * *'",text)
  self.assertIn('group: blog-image-independent-stock',text);self.assertIn('cancel-in-progress: false',text)
  self.assertIn('Process at most one article-owned image',text)
if __name__=='__main__':unittest.main()
