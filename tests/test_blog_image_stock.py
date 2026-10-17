"""Offline stock tests: no credentials, provider requests or public posts."""
import copy,json,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import nullcontext
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_stock as stock
import blog_generated_image as generated
from blog_image_backpressure import ImageProviderBusy
class StockTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.env=patch.dict(os.environ,{'GITHUB_ACTIONS':'false'});self.env.start();self.addCleanup(self.env.stop)
  (self.root/'data').mkdir()
  (self.root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3}))
  self.item={'key':'stock-topic','family':'tape20','kind':'city','site_title':'نوار تیپ پیاز','_image_article_context':{'title':'آبیاری پیاز با نوار تیپ','summary':'این متن واقعی پیش نویس آموزشی درباره نصب خطوط نوار تیپ در ردیف های پیاز و بررسی توزیع رطوبت خاک است'}}
 def enqueue(self,item=None,blog='roya'):
  item=self.item if item is None else item
  with self.assertRaises(stock.ImagePending):stock.request_image(item,blog,self.root)
  return stock.rows(self.root)[-1]
 def source(self,item=None,blog='roya'):
  p=self.root/'data'/blog/'backlink-queue.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'items':[item or self.item]}))
 def worker(self,operation):
  with patch.object(generated,'rollout_enabled',return_value=True),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open'),patch.object(generated,'prepare_now',side_effect=operation)as prepare:
   result=stock.worker_once(self.root)
  return result,prepare
 def test_enqueue_is_idempotent_and_never_generates(self):
  with patch.object(generated,'generate')as gen:
   self.enqueue();self.enqueue();gen.assert_not_called()
  self.assertEqual(len(stock.rows(self.root)),1);self.assertTrue(stock.awaiting(self.item,self.root))
 def test_snapshot_is_allowlisted_no_private_fields(self):
  self.item.update(AGNES_API_KEY='do-not-persist',password='do-not-persist',post={'secret':'do-not-persist'})
  row=self.enqueue();self.assertNotIn('do-not-persist',json.dumps(row));self.assertNotIn('post',row['item'])
 def test_context_is_required_before_request(self):
  self.item.pop('_image_article_context')
  with self.assertRaisesRegex(RuntimeError,'Actual post title'):self.enqueue()
  self.assertEqual(stock.rows(self.root),[])
 def test_cancelled_hose_never_enqueued(self):
  (self.root/'data/blog-generated-image-control.json').write_text(json.dumps({'cancelled_families':['hose'],'enabled_families':['tape20']}))
  self.item['family']='hose';self.item['site_title']='لوله نخی'
  with self.assertRaisesRegex(RuntimeError,'cancelled or held'):stock.request_image(self.item,'roya',self.root)
  self.assertEqual(stock.rows(self.root),[])
 def test_maximum_twelve_total_and_three_per_blog(self):
  for blog in ['roya','farsiblog','rozblog','blogfa']:
   for i in range(3):self.enqueue({**copy.deepcopy(self.item),'key':blog+str(i)},blog)
  with self.assertRaises(stock.ImagePending):stock.request_image({**self.item,'key':'extra'},'loxblog',self.root)
  self.assertEqual(len(stock.rows(self.root)),12)
 def test_fourth_request_same_blog_is_not_saved(self):
  for i in range(4):self.enqueue({**copy.deepcopy(self.item),'key':str(i)})
  self.assertEqual(len(stock.rows(self.root)),3)
 def test_no_inline_generation_for_missing_ready_asset(self):
  self.enqueue();row=stock.rows(self.root)[0];row['status']='ready';stock.persist(self.root,row)
  with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'generate')as gen:
   with self.assertRaisesRegex(RuntimeError,'asset missing'):stock.request_image(self.item,'roya',self.root)
   gen.assert_not_called()
 def test_ready_consumption_rechecks_qa_and_cannot_generate(self):
  self.enqueue();row=stock.rows(self.root)[0];row['status']='ready';stock.persist(self.root,row)
  with patch.object(generated,'existing_asset',return_value='approved-cache'),patch('blog_image_gate.review')as review,patch.object(generated,'prepare_now',return_value='approved-cache')as prep:
   self.assertEqual(stock.request_image(self.item,'roya',self.root),'approved-cache')
   review.assert_called_once();self.assertFalse(prep.call_args.kwargs['allow_generate'])
  self.assertEqual(stock.rows(self.root)[0]['status'],'consumed')
 def test_direct_rejection_cannot_be_consumed(self):
  self.enqueue();row=stock.rows(self.root)[0];row['status']='ready';stock.persist(self.root,row)
  with patch.object(generated,'existing_asset',return_value='cached'),patch('blog_image_gate.review',side_effect=RuntimeError('Product image rejected: direct review')):
   with self.assertRaisesRegex(RuntimeError,'direct review'):stock.request_image(self.item,'roya',self.root)
  self.assertEqual(stock.rows(self.root)[0]['status'],'ready')
 def test_changed_article_has_new_identity_and_supersedes_old(self):
  self.enqueue();self.item['_image_article_context']['summary']+=' تغییر واقعی در خلاصه مقاله'
  self.enqueue();rows=stock.rows(self.root);self.assertEqual(len(rows),2);self.assertEqual(sum(x['status']=='requested'for x in rows),1)
 def test_worker_processes_only_one_request_and_marks_ready_after_qa(self):
  for i in range(2):self.enqueue({**copy.deepcopy(self.item),'key':str(i)})
  p=self.root/'data/roya/backlink-queue.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'items':[{'key':str(i)}for i in range(2)]}))
  def approved(item,*args,**kw):
   self.assertEqual(kw['max_rounds'],1);item['image_review']={'sha256':'f'*64};return 'immutable-approved-url'
  result,prepare=self.worker(approved);self.assertEqual(prepare.call_count,1);self.assertEqual(result['status'],'ready');self.assertFalse(result['publication_attempted'])
  self.assertEqual(sum(x['status']=='ready'for x in stock.rows(self.root)),1)
 def test_provider_busy_retains_request_with_retry_after(self):
  self.enqueue();self.source();retry=time.time()+900
  result,prepare=self.worker(lambda *a,**k:(_ for _ in ()).throw(ImageProviderBusy(retry)))
  row=stock.rows(self.root)[0];self.assertEqual(row['status'],'requested');self.assertGreaterEqual(row['retry_at'],retry)
  result,prepare=self.worker(lambda *a,**k:self.fail('No retry during cooldown'));prepare.assert_not_called()
 def test_worker_preflight_wait_does_not_touch_provider(self):
  self.enqueue();self.source()
  with patch.object(generated,'rollout_enabled',return_value=True),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open',side_effect=ImageProviderBusy(time.time()+100)),patch.object(generated,'prepare_now')as prep:
   self.assertEqual(stock.worker_once(self.root)['status'],'waiting_provider');prep.assert_not_called()
 def test_processing_request_recovers_after_interruption(self):
  self.enqueue();self.source();row=stock.rows(self.root)[0];row['status']='processing';stock.persist(self.root,row)
  def approved(item,*args,**kw):item['image_review']={'sha256':'a'*64};return 'approved'
  result,prepare=self.worker(approved);self.assertEqual(result['status'],'ready');self.assertEqual(prepare.call_count,1)
 def test_visual_rejection_has_bounded_slow_corrective_retries(self):
  self.enqueue();self.source()
  for attempt in range(3):
   row=stock.rows(self.root)[0];row['retry_at']=0;stock.persist(self.root,row)
   result,prepare=self.worker(lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Product image rejected: geometry')))
  row=stock.rows(self.root)[0];self.assertEqual(row['status'],'rejected');self.assertEqual(row['visual_rejections'],3)
  result,prepare=self.worker(lambda *a,**k:self.fail('No fourth image request'));prepare.assert_not_called()
 def test_published_or_removed_topic_cancelled_without_image(self):
  for published in [True,False]:
   with self.subTest(published=published):
    self.item['key']='published'if published else'removed';self.enqueue();self.source({'key':self.item['key'],'published':True}if published else{'key':'different'})
    _,prepare=self.worker(lambda *a,**k:self.fail('Published/missing post cannot generate'));prepare.assert_not_called()
 def test_disabled_or_paused_worker_does_not_mutate_queue(self):
  self.enqueue();before=stock.rows(self.root)
  with patch('blog_image_runtime_control.generation_paused',return_value=True),patch.object(generated,'prepare_now')as prep:
   self.assertEqual(stock.worker_once(self.root)['status'],'paused');prep.assert_not_called()
  self.assertEqual(stock.rows(self.root),before)
 def test_producer_cooldown_is_independent_but_legacy_preserved(self):
  with patch('blog_image_backpressure.require_open')as check:stock.require_generation_open(self.root);check.assert_not_called()
  (self.root/stock.CONFIG).unlink()
  with patch('blog_image_backpressure.require_open')as check:stock.require_generation_open(self.root);check.assert_called_once()
 def test_corrupt_control_fails_closed(self):
  (self.root/stock.CONFIG).write_text('not json')
  with self.assertRaises(ValueError):stock.enabled(self.root)
 def test_workflow_has_one_worker_no_publishing_and_offline_tests(self):
  text=(ROOT/'.github/workflows/blog-image-stock.yml').read_text()
  self.assertIn('cancel-in-progress: false',text);self.assertIn('needs: tests',text);self.assertNotIn('publish_',text);self.assertNotIn('AGNES_API_KEY8:',text)
 def test_scene_and_router_fixes_trigger_offline_gated_worker(self):
  text=(ROOT/'.github/workflows/blog-image-stock.yml').read_text()
  for path in ('automation/blog_image_key_router.py','automation/blog_image_gate.py','automation/blog_reference_scene.py','automation/blog_draft_preflight.py','data/blog-image-key-pool.json'):
   self.assertIn('      - '+path,text)
  self.assertIn('needs: tests',text)
 def test_waiting_status_not_failed_or_published(self):
  from blog_generation_status import outcome
  self.assertEqual(outcome([],[],waiting=['key']),'waiting_image');self.assertEqual(outcome([],['bad'],waiting=['key']),'failed')
 def test_admission_uses_same_cross_runner_mutex(self):
  with patch.object(stock,'hosted',return_value=True),patch('blog_image_queue.Queue')as queue,patch.object(stock,'refresh'):
   queue.return_value.slot.return_value=nullcontext()
   with stock.admission(self.root,'roya','a'*32):pass
   queue.assert_called_once_with(minimum_interval=0,wait=30)
 def test_cache_only_mode_never_generates(self):
  with patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'generate')as gen:
   with self.assertRaisesRegex(RuntimeError,'inline generation forbidden'):generated.prepare_now(self.item,'roya',self.root,allow_generate=False)
   gen.assert_not_called()
if __name__=='__main__':unittest.main()

class StockPipelineTests(unittest.TestCase):
 def test_saved_farsiblog_draft_waits_then_resumes_without_text_regeneration(self):
  import farsiblog_backlink_queue as f
  with tempfile.TemporaryDirectory()as directory,patch.dict(os.environ,{'GITHUB_ACTIONS':'false','FARSIBLOG_COUNT':'1','FARSIBLOG_DRY_RUN':'0','FARSIBLOG_TARGET':''}):
   root=Path(directory);art=root/'artifacts/farsiblog-backlink-queue';art.mkdir(parents=True)
   (root/'data').mkdir();(root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3}))
   queue=root/'data/farsiblog/backlink-queue.json';state=root/'state.json'
   item={'key':'integration','family':'tape20','kind':'city','site_title':'نوار تیپ پیاز','status':'pending'}
   f.save(queue,{'items':[item]})
   post={'title':'نوار تیپ پیاز','slug':'onion-topic','html':'<p>این متن واقعی درباره نصب نوار تیپ در ردیف های پیاز و بررسی توزیع رطوبت در خاک است</p>'}
   def prepare(item):return stock.request_image(item,'farsiblog',root)
   def qa(item,obj,links):return ([]if '<img' in obj['html']else['image required']),{}
   with patch.multiple(f,ROOT=root,QUEUE=queue,ART=art,STATE=state),patch.object(f.BASE,'AGNES_KEY','offline-only-fixture'),patch.object(f,'remaining_publication_budget',return_value=3),patch.object(f,'links_for',return_value=[]),patch.object(f,'source_text',return_value='source'),patch.object(f,'prompt',return_value='offline prompt'),patch.object(f,'qa',side_effect=qa),patch('city_backlink_policy.build_queue'),patch('city_backlink_policy.matrix_ready',return_value=True),patch('city_backlink_policy.matrix_title',return_value=post['title']),patch('city_backlink_policy.resolve_editorial_link_tokens'),patch('city_backlink_policy.prepare_image',side_effect=prepare),patch.object(f,'agnes',return_value=copy.deepcopy(post))as text:
    self.assertEqual(f.main(),0);self.assertEqual(text.call_count,1)
    self.assertEqual(json.loads((art/'publish-queue.json').read_text())['count'],0)
    self.assertEqual(json.loads((art/'generation-status.json').read_text())['status'],'waiting_image')
    record=json.loads((art/'items/integration.json').read_text());self.assertEqual(record['post']['html'],post['html'])
    row=stock.rows(root)[0];row.update(status='ready');stock.persist(root,row)
    q=json.loads(queue.read_text());q['items'][0].pop('next_retry_at',None);f.save(queue,q)
    def cache(item,*args,**kwargs):
     self.assertFalse(kwargs['allow_generate']);item.update(image_url='approved',image_alt='نوار تیپ',image_width=1200,image_height=675);return 'approved'
    with patch.object(generated,'existing_asset',return_value='approved'),patch('blog_image_gate.review'),patch.object(generated,'prepare_now',side_effect=cache):
     self.assertEqual(f.main(),0)
    self.assertEqual(text.call_count,1)
    self.assertEqual(json.loads((art/'publish-queue.json').read_text())['count'],1)
    self.assertEqual(stock.rows(root)[0]['status'],'consumed')
