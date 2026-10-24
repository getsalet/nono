import io,json,tempfile,unittest,urllib.error,datetime,time
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2.client import ModelClient,ImageProviderError,CapabilityError
from automation.agri_v2 import pilot_resume as p,recovery,revise
from automation.agri_v2.queue import atomic_json,load_json,utcnow
class QueueAwareTests(unittest.TestCase):
 def client(self):
  c=object.__new__(ModelClient);c.keys={'image':[('AGNES_API_KEY','fixture-first'),('AGNES_API_KEY2','fixture-second')],'text':[('AGNES_API_KEY','fixture-first'),('AGNES_API_KEY2','fixture-second')]};c.used={'image':0,'text':0};c.env={'GITHUB_ACTIONS':'false'};return c
 def test_queue_full_never_rotates_to_second_key(self):
  error=urllib.error.HTTPError('https://apihub.agnes-ai.com/v1/images/generations',503,'error',{},io.BytesIO(b'{"error":{"message":"image queue is full"}}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(ImageProviderError) as cm:self.client().request('image','/images/generations',{'prompt':'fixture'},1)
   self.assertEqual(cm.exception.provider_code,'image_queue_full');self.assertEqual(call.call_count,1)
 def test_image_rate_limit_never_rotates(self):
  error=urllib.error.HTTPError('https://apihub.agnes-ai.com/v1/images/generations',429,'error',{'Retry-After':'900'},io.BytesIO(b'{"error":{"code":"rate_limit_exceeded"}}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(ImageProviderError) as cm:self.client().request('image','/images/generations',{'prompt':'fixture'},1)
   self.assertEqual(cm.exception.retry_after_seconds,900);self.assertEqual(call.call_count,1)
 def test_text_rate_limit_does_not_rotate(self):
  error=urllib.error.HTTPError('https://apihub.agnes-ai.com/v1/chat/completions',429,'error',{},io.BytesIO(b'{}'))
  with patch('urllib.request.urlopen',side_effect=error) as call:
   with self.assertRaises(CapabilityError):self.client().request('text','/chat/completions',{},1)
   self.assertEqual(call.call_count,1)
 def test_new_backoff_does_not_shorten_old_cooldown(self):
  with tempfile.TemporaryDirectory() as t,patch.object(p,'OUT',Path(t)):
   old=utcnow();atomic_json(Path(t)/'provider-circuit.json',{'open':True,'at':old})
   deadline=p.defer_provider(ImageProviderError(503,'image_queue_full','provider_unavailable'))
   self.assertGreaterEqual(deadline,datetime.datetime.fromisoformat(old).timestamp()+3600)
 def test_explicit_deadline_controls_recovery(self):
  with tempfile.TemporaryDirectory() as t,patch.object(recovery,'OUT',Path(t)):
   atomic_json(Path(t)/'provider-circuit.json',{'open':True,'at':utcnow(),'retry_at_epoch':time.time()-1});self.assertFalse(recovery.circuit_open())
   atomic_json(Path(t)/'provider-circuit.json',{'open':True,'at':utcnow(),'retry_at_epoch':time.time()+300});self.assertTrue(recovery.circuit_open())
 def request(self):return {'request_id':p.REQUEST,'topic_id':p.TOPIC,'post_id':524163,'max_additional_cycles':2,'max_new_posts':0,'diagnostic_run_id':40117693942}
 def test_budget_exhaustion_prevents_another_revision(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);data=root/'data';out=root/'out';atomic_json(data/'pilot-resume-request.json',self.request());atomic_json(data/'config.json',{'publication_holds':{p.TOPIC:'queue full'}});atomic_json(out/'pilot-resume'/p.REQUEST/'receipt.json',{'status':'provider_deferred','cycles_started':2})
   with patch.object(p,'DATA',data),patch.object(p,'OUT',out),patch.object(p,'update'),patch.object(revise,'run') as r:
    self.assertEqual(p.run()['status'],'pilot_recovery_budget_exhausted');r.assert_not_called()
 def test_active_cooldown_means_zero_model_calls(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);atomic_json(root/'data/pilot-resume-request.json',self.request());atomic_json(root/'data/config.json',{'publication_holds':{p.TOPIC:'queue full'}})
   with patch.object(p,'DATA',root/'data'),patch.object(p,'OUT',root/'out'),patch.object(p,'update'),patch.object(p,'circuit_open',return_value=True),patch.object(revise,'run') as r:
    result=p.run();self.assertEqual(result['model_calls'],0);r.assert_not_called()
if __name__=='__main__':unittest.main()
