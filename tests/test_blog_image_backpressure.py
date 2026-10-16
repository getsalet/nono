import json,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_backpressure as b
import blog_generated_image as g
from agnes_key_pool import AgnesProviderError
class BackpressureTests(unittest.TestCase):
 def item(self):return {'key':'capacity-fixture','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'پایش آبیاری پیاز','summary':'این مقاله درباره یکنواختی آبیاری، خطوط نصب شده و ناحیه ریشه پیاز است و تصویر باید همان موضوع را نشان دهد.'}}
 def test_exact_error_is_classified_without_retaining_message(self):
  e=AgnesProviderError(503,b'{"error":{"message":"image queue is full, please retry later (request id: private-id)"}}')
  self.assertEqual(e.provider_code,'image_queue_full');self.assertNotIn('private-id',str(e))
  self.assertIsNone(AgnesProviderError(401,b'{"error":{"message":"image queue is full"}}').provider_code)
 def test_full_queue_never_rotates_credentials_or_retries_immediately(self):
  e=AgnesProviderError(503,b'{"error":{"message":"image queue is full, please retry later"}}')
  with patch.dict('os.environ',{'IMAGE_API_KEY':'capacity-test-only','AGNES_IMAGE_TRANSIENT_FAILOVER':'1'}),patch.object(g.roya.BASE._key_pool,'fetch_json',side_effect=e)as fetch,patch.object(g,'capability_slots',side_effect=AssertionError('Do not rotate on shared capacity')),patch.object(g.time,'sleep')as sleep:
   with self.assertRaises(b.ImageProviderBusy):g.generate(self.item(),'roya')
   self.assertEqual(fetch.call_count,1);sleep.assert_not_called()
 def test_prepare_persists_one_shared_cooldown_then_suppresses_new_api_calls(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);busy=b.ImageProviderBusy(time.time()+300)
   with patch.object(g,'existing_asset',return_value=None),patch.object(g,'generate',side_effect=busy)as generate,patch.object(g,'checkpoint_asset')as checkpoint:
    with self.assertRaises(b.ImageProviderBusy):g.prepare(self.item(),'roya',root)
    self.assertEqual(checkpoint.call_args.args[0],b.STATE)
    with self.assertRaises(b.ImageProviderBusy):g.prepare(self.item(),'roya',root)
    self.assertEqual(generate.call_count,1)
 def test_checkpoint_failure_still_defers_instead_of_repeating_requests(self):
  with tempfile.TemporaryDirectory()as d:
   item=self.item()
   with patch.object(g,'existing_asset',return_value=None),patch.object(g,'generate',side_effect=b.ImageProviderBusy(time.time()+300)),patch.object(g,'checkpoint_asset',side_effect=RuntimeError('checkpoint failed')):
    with self.assertRaises(b.ImageProviderBusy):g.prepare(item,'roya',Path(d))
   self.assertTrue(item['_provider_cooldown_checkpoint_failed'])
 def test_expiry_is_bounded_and_corrupt_state_fails_closed(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);p=root/b.STATE;p.parent.mkdir(parents=True);p.write_text(json.dumps({'retry_at_epoch':1000}))
   with self.assertRaises(b.ImageProviderBusy):b.require_open(root,current=999)
   b.require_open(root,current=1001)
   p.write_text('{broken')
   with self.assertRaises(RuntimeError):b.require_open(root)
 def test_cooldown_does_not_stop_ready_post_publication(self):
  from check_blog_pipeline_control import decision
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text('{"pause_image_production":false}')
   (root/b.STATE).write_text(json.dumps({'retry_at_epoch':time.time()+300}))
   for blog in('roya','farsiblog','rozblog','blogfa','loxblog'):self.assertTrue(decision(blog,root)['proceed'])
 def test_shared_transient_wrapper_does_not_retry_capacity_errors(self):
  import farsiblog_backlink_queue as f
  with patch.object(f.time,'sleep')as sleep:
   calls=[]
   def operation():calls.append(1);raise b.ImageProviderBusy(time.time()+300)
   with self.assertRaises(b.ImageProviderBusy):f.retry_transient(operation)
   self.assertEqual(len(calls),1);sleep.assert_not_called()

class CooldownWorktreeIntegrityTests(unittest.TestCase):
 def test_defer_preserves_tracked_control_and_unrelated_edits(self):
  import subprocess
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)
   def git(*args):return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.DEVNULL)
   git('init');git('config','user.name','fixture');git('config','user.email','fixture@example.invalid')
   p=root/b.STATE;p.parent.mkdir(parents=True);original=b'{"retry_at_epoch":0}';p.write_bytes(original)
   other=root/'unrelated.txt';other.write_text('before');git('add','.');git('commit','-qm','fixture');other.write_text('pending edit')
   before=git('diff','--name-only')
   calls=[];b.defer(root,time.time()+300,lambda *args:calls.append(args))
   self.assertEqual(p.read_bytes(),original,'Provider cooldown must not dirty tracked shared state in generator checkout')
   self.assertEqual(git('diff','--name-only'),before)
   self.assertEqual(calls[0][0],b.STATE)
   with self.assertRaises(b.ImageProviderBusy):b.require_open(root)
 def test_runtime_cooldown_survives_remote_checkpoint_failure(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)
   def fail(*args):raise RuntimeError('checkpoint unavailable')
   with self.assertRaises(RuntimeError):b.defer(root,time.time()+300,fail)
   with self.assertRaises(b.ImageProviderBusy):b.require_open(root)
