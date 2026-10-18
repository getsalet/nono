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
if __name__=='__main__':unittest.main()
