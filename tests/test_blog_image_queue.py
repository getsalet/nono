import contextlib,copy,datetime,json,os,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_queue as q
import blog_generated_image as g
import blog_image_backpressure as b
class FakeClient:
 def __init__(self):self.refs={};self.commits={'a'*40:{'tree':{'sha':'b'*40}}};self.runs={};self.mutex=threading.RLock();self.calls=[];self.counter=0
 def call(self,method,path,data=None,allowed=(200,201,204)):
  with self.mutex:
   self.calls.append((method,path,copy.deepcopy(data)))
   status=200;row=None
   if path.startswith('/git/commits/')and method=='GET':row=self.commits[path.split('/')[-1]]
   elif path=='/git/commits'and method=='POST':
    self.counter+=1;sha=f'{self.counter:040x}';self.commits[sha]=copy.deepcopy(data);row={'sha':sha};status=201
   elif path=='/git/refs'and method=='POST':
    ref=data['ref'][5:]
    if ref in self.refs:status=422
    else:self.refs[ref]=data['sha'];row={'object':{'sha':data['sha']}};status=201
   elif path.startswith('/git/ref/')and method=='GET':
    sha=self.refs.get(path[len('/git/ref/'):]);status=200 if sha else 404;row={'object':{'sha':sha}}if sha else None
   elif path.startswith('/git/refs/')and method=='DELETE':self.refs.pop(path[len('/git/refs/'):],None);status=204
   elif path.startswith('/git/matching-refs/'):
    prefix=path.split('?',1)[0][len('/git/matching-refs/'):];row=[{'ref':'refs/'+ref,'object':{'sha':sha}}for ref,sha in self.refs.items()if ref.startswith(prefix)]
   elif path.startswith('/actions/runs/'):row=self.runs.get((path.split('/')[3],path.split('/')[-1]),self.runs.get(path.split('/')[3],{'status':'in_progress'}))
   else:raise AssertionError((method,path))
   if status not in allowed:raise RuntimeError('fixture HTTP '+str(status))
   return status,row
class SharedQueueTests(unittest.TestCase):
 def queue(self,client=None,run='1',**kw):return q.Queue(client=client or FakeClient(),run=run,source='a'*40,wait=0,poll=0,minimum_interval=0,**kw)
 def test_atomic_lock_and_exception_release(self):
  client=FakeClient();queue=self.queue(client)
  with self.assertRaisesRegex(ValueError,'fixture'):
   with queue.slot('roya','f'*32):
    self.assertEqual(client.refs[q.LOCK],queue.sha);raise ValueError('fixture')
  self.assertEqual(client.refs,{})
 def test_parallel_callers_have_no_overlapping_critical_sections(self):
  client=FakeClient();active=0;peak=0;errors=[];guard=threading.Lock()
  def worker(run):
   nonlocal active,peak
   try:
    queue=q.Queue(client=client,run=run,source='a'*40,wait=2,poll=.005,minimum_interval=0)
    with queue.slot('roya','f'*32):
     with guard:active+=1;peak=max(peak,active)
     time.sleep(.03)
     with guard:active-=1
   except Exception as e:errors.append(type(e).__name__)
  with patch.object(q.random,'uniform',return_value=0):
   threads=[threading.Thread(target=worker,args=(str(i),))for i in range(1,4)]
   for t in threads:t.start()
   for t in threads:t.join()
  self.assertEqual(errors,[]);self.assertEqual(peak,1);self.assertEqual(client.refs,{})
 def test_busy_wait_is_bounded_and_does_not_remove_live_owner(self):
  client=FakeClient();first=self.queue(client);first.create_ticket('roya','e'*32);self.assertTrue(first.try_lock())
  second=self.queue(client,run='2')
  with self.assertRaises(q.ImageQueueBusy):
   with second.slot('blogfa','f'*32):self.fail('No admission while occupied')
  self.assertEqual(client.refs[q.LOCK],first.sha);self.assertNotIn(second.ticket,client.refs)
 def test_fifo_head_is_required_before_attempting_lock(self):
  client=FakeClient();first=self.queue(client);first.ticket=q.PREFIX+'1000000000000-1-1-'+'a'*32;first.create_ticket('roya','e'*32)
  second=self.queue(client,run='2')
  with patch.object(second,'try_lock')as lock,self.assertRaises(q.ImageQueueBusy):
   with second.slot('loxblog','f'*32):pass
  lock.assert_not_called()
 def test_completed_owner_requires_quarantine_before_stale_lock_recovery(self):
  client=FakeClient();first=self.queue(client);first.create_ticket('roya','e'*32);first.try_lock();client.refs.pop(first.ticket)
  second=self.queue(client,run='2');second.create_ticket('blogfa','f'*32)
  client.runs['1']={'status':'completed','updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  self.assertFalse(second.try_lock());self.assertEqual(client.refs[q.LOCK],first.sha)
  client.runs['1']['updated_at']='2020-01-01T00:00:00Z'
  self.assertFalse(second.try_lock());self.assertNotIn(q.LOCK,client.refs)
  self.assertTrue(second.try_lock());self.assertEqual(client.refs[q.LOCK],second.sha)
 def test_completed_old_attempt_of_same_run_is_recovered(self):
  client=FakeClient();old=self.queue(client,attempt='1');old.create_ticket('roya','e'*32);old.try_lock()
  client.runs[('1','1')]={'status':'completed','updated_at':'2020-01-01T00:00:00Z'}
  current=self.queue(client,attempt='2');current.create_ticket('roya','f'*32)
  self.assertEqual(current.clean_and_list(),[current.ticket])
  self.assertFalse(current.try_lock());self.assertTrue(current.try_lock())
 def test_retained_lock_is_not_released_after_checkpoint_uncertainty(self):
  client=FakeClient();queue=self.queue(client)
  with queue.slot('roya','f'*32):queue.retain=True
  self.assertEqual(client.refs[q.LOCK],queue.sha)
 def test_unknown_lock_metadata_fails_closed(self):
  client=FakeClient();client.commits['c'*40]={'message':'foreign'};client.refs[q.LOCK]='c'*40
  queue=self.queue(client)
  with self.assertRaisesRegex(RuntimeError,'Unknown lock'):
   with queue.slot('roya','f'*32):self.fail('No unknown owner takeover')
  self.assertEqual(client.refs[q.LOCK],'c'*40)
 def test_hosted_queue_requires_configuration_and_token(self):
  with patch.dict(os.environ,{'GITHUB_ACTIONS':'true','BLOG_IMAGE_QUEUE_ENABLED':'','BLOG_IMAGE_QUEUE_TOKEN':''}):
   with self.assertRaisesRegex(RuntimeError,'not configured'):
    with q.provider_slot('roya','f'*32):self.fail()
   os.environ['BLOG_IMAGE_QUEUE_ENABLED']='1'
   with self.assertRaisesRegex(RuntimeError,'credential unavailable'):
    with q.provider_slot('roya','f'*32):self.fail()
 def test_owned_delete_never_removes_a_different_sha(self):
  client=FakeClient();client.refs[q.LOCK]='c'*40;queue=self.queue(client)
  self.assertFalse(queue.delete_owned(q.LOCK,'d'*40));self.assertIn(q.LOCK,client.refs)
 def test_local_offline_fixture_never_calls_github(self):
  with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(q,'Client')as client:
   with q.provider_slot('roya','f'*32)as lease:self.assertIsNone(lease)
   client.assert_not_called()
class QueueIntegrationTests(unittest.TestCase):
 def test_shared_cooldown_is_rechecked_after_lock_before_image_api(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'data').mkdir();(root/b.STATE).write_text(json.dumps({'retry_at_epoch':time.time()+300}))
   with patch.object(g.roya,'ROOT',root),patch.object(q,'provider_slot',return_value=contextlib.nullcontext(object())),patch.object(g,'git')as fetch,patch.object(g,'_generate')as generate:
    with self.assertRaises(b.ImageProviderBusy):g.generate({'key':'k','family':'tape20'},'roya')
    generate.assert_not_called();fetch.assert_called_once()
 def test_provider_backoff_persisted_before_mutex_release(self):
  events=[];lease=type('Lease',(),{'retain':False})()
  @contextlib.contextmanager
  def slot(*args):
   events.append('acquired')
   try:yield lease
   finally:events.append('released')
  with patch.object(q,'provider_slot',side_effect=slot),patch.object(g,'git'),patch.object(b,'require_open'),patch.object(g,'_generate',side_effect=b.ImageProviderBusy(time.time()+300)),patch.object(b,'defer',side_effect=lambda *a:events.append('persisted')or time.time()+600):
   with self.assertRaises(b.ImageProviderBusy)as busy:g.generate({'key':'k','family':'tape20'},'roya')
   self.assertTrue(busy.exception.shared_cooldown_saved)
  self.assertEqual(events,['acquired','persisted','released'])
 def test_failed_checkpoint_retains_mutex_and_prevents_duplicate_defer(self):
  lease=type('Lease',(),{'retain':False})()
  with patch.object(q,'provider_slot',return_value=contextlib.nullcontext(lease)),patch.object(g,'git'),patch.object(b,'require_open'),patch.object(g,'_generate',side_effect=b.ImageProviderBusy(time.time()+300)),patch.object(b,'defer',side_effect=RuntimeError('fixture')):
   with self.assertRaises(b.ImageProviderBusy)as busy:g.generate({'key':'k','family':'tape20'},'roya')
   self.assertTrue(lease.retain);self.assertTrue(busy.exception.shared_cooldown_attempted)
 def test_all_five_generation_steps_receive_same_queue_gate(self):
  root=Path(__file__).resolve().parents[1]
  for name in ['roya-backlink-queue','farsiblog-content','rozblog-content','blogfa-content','loxblog-content']:
   source=(root/'.github/workflows'/(name+'.yml')).read_text()
   self.assertIn("BLOG_IMAGE_QUEUE_ENABLED: '1'",source);self.assertIn('BLOG_IMAGE_QUEUE_TOKEN: ${{ github.token }}',source);self.assertIn('actions: read',source)
class AdaptiveBackoffTests(unittest.TestCase):
 def test_repeated_full_queue_increases_delay_then_real_success_resets(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);clock=1800000000
   def checkpoint(*args):pass
   for expected in [300,600,1200,1800,1800]:
    with patch.object(b.time,'time',return_value=clock):stamp=b.defer(root,clock+300,checkpoint)
    self.assertEqual(stamp,clock+expected)
    clock=stamp+1
   with patch.object(b.time,'time',return_value=clock):b.mark_success(root,checkpoint)
   with patch.object(b.time,'time',return_value=clock+1):stamp=b.defer(root,clock+301,checkpoint)
   self.assertEqual(stamp,clock+301)
