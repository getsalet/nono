"""Queue rebuild retains async ownership and restores only matching checkpoints."""
import copy,json,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import build_roya_queue as build
import roya_backlink_queue as roya
class QueueRuntimeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.row={'key':'city/test','status':'failed','attempts':4,'generated_at':'2026-10-17T20:00:00Z','family':'tape20','province':'city'}
  self.record={**self.row,'failure_stage':'image','qa':{'passed':False,'errors':['agnes error: Independent image stock waiting: requested; saved draft retained, no producer image API']},'_image_stock_request':'a'*32,'post':{'title':'نوار تیپ','slug':'real-post','html':'<p>این متن واقعی پیش نویس آموزشی ذخیره شده درباره آبیاری است</p>'}}
  env=patch.object(build,'ROOT',self.root);env.start();self.addCleanup(env.stop)
 def save_record(self,value=None):
  path=self.root/'artifacts/roya-backlink-queue/items/city_test.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value if value is not None else self.record))
 def test_existing_runtime_survives_without_checkpoint(self):
  row={**self.row,'failure_stage':'image','last_error':'saved','next_retry_at':'2099-01-01T00:00:00Z','_image_stock_request':'a'*32,'image_review':{'sha256':'b'*64},'private_unknown':'must not copy'}
  result=build.retained_runtime(row,row['key'])
  for key in ('failure_stage','last_error','next_retry_at','_image_stock_request','image_review'):self.assertEqual(result[key],row[key])
  self.assertNotIn('private_unknown',result)
 def test_matching_failed_checkpoint_recovers_stage_error_and_owner(self):
  self.save_record();result=build.retained_runtime(self.row,self.row['key'])
  self.assertEqual(result['failure_stage'],'image');self.assertEqual(result['_image_stock_request'],'a'*32)
  self.assertIn('Independent image stock waiting:',result['last_error'])
  self.assertEqual(self.row['status'],'failed')
 def test_published_or_ambiguous_native_identity_never_resurrected(self):
  self.save_record()
  for fields in ({'published':True},{'status':'published'},{'status':'completed'},{'pid':'123'},{'published_url':'https://example.test/post'}):
   self.assertEqual(build.retained_runtime({**self.row,**fields},self.row['key']),{})
 def test_mismatched_or_stale_checkpoint_cannot_restore(self):
  for fields in ({'key':'other'},{'generated_at':'old'},{'published':True},{'pid':'123'},{'status':'completed'}):
   self.save_record({**self.record,**fields});self.assertEqual(build.retained_runtime(self.row,self.row['key']),{})
 def test_missing_or_corrupt_checkpoint_stays_closed(self):
  self.assertEqual(build.retained_runtime(self.row,self.row['key']),{})
  self.save_record();(self.root/'artifacts/roya-backlink-queue/items/city_test.json').write_text('not json')
  self.assertEqual(build.retained_runtime(self.row,self.row['key']),{})
 def test_explicit_future_timer_is_not_overwritten_by_old_checkpoint(self):
  self.save_record();row={**self.row,'next_retry_at':'2099-01-01T00:00:00Z'}
  self.assertEqual(build.retained_runtime(row,row['key'])['next_retry_at'],row['next_retry_at'])
 def test_restored_due_capacity_draft_is_selected_but_all_gates_stay(self):
  self.save_record();row={**self.row,**build.retained_runtime(self.row,self.row['key'])}
  with patch.multiple(roya,ROOT=self.root,ITEMS=self.root/'artifacts/roya-backlink-queue/items',RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=True):
   self.assertEqual([r['key']for r in roya.pick({'items':[row]},{},1)],[row['key']])
 def test_main_refresh_preserves_source_and_runtime(self):
  target={'key':self.row['key'],'province':'city','province_fa':'استان','city_slug':'شهر-navar-tip','url':'https://navar-abyari.ir/city','site_title':'نوار تیپ در شهر'}
  data=self.root/'data/roya';data.mkdir(parents=True);queue=data/'backlink-queue.json';targets=data/'backlink-targets.json'
  targets.write_text(json.dumps({'targets':[target]}));row={**self.row,'province_fa':'استان','city_fa':'شهر','target_url':target['url'],'_image_stock_request':'a'*32,'failure_stage':'image'};queue.write_text(json.dumps({'items':[row]}))
  with patch.multiple(build,QUEUE=queue,TARGETS=targets,TITLES=data/'missing-titles.json'):self.assertEqual(build.main(),0)
  result=json.loads(queue.read_text())['items'][0]
  self.assertEqual(result['_image_stock_request'],'a'*32);self.assertEqual(result['failure_stage'],'image');self.assertEqual(result['attempts'],4);self.assertEqual(result['target_url'],target['url'])
 def test_workflow_checks_rebuild_regression_before_generation(self):
  text=(ROOT/'.github/workflows/roya-backlink-queue.yml').read_text()
  self.assertIn('      - automation/build_roya_queue.py',text)
  self.assertLess(text.index("test_roya_queue_runtime.py' -v"),text.index('run: python automation/build_roya_queue.py'))
  self.assertIn('cancel-in-progress: false',text)
if __name__=='__main__':unittest.main()
