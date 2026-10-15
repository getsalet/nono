import datetime as dt,io,json,sys,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from agnes_key_pool import AgnesKeyPool,NAMES,DEFAULT_BASE
class KeyPoolTests(unittest.TestCase):
 def test_all_slots_and_duplicate(self):
  self.assertEqual(len(NAMES),25);env={n:f'fake-{i}'for i,n in enumerate(NAMES)};env['AGNES_API_KEY8']=env['AGNES_API_KEY'];p=AgnesKeyPool(env,report_path='/absent');self.assertEqual(len(p.keys),24);self.assertIn('fake-24',p.keys)
 def test_fresh_health_filter_and_expiration(self):
  now=dt.datetime.now(dt.timezone.utc)
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'health.json';report={'complete':True,'tested_at':now.isoformat(),'endpoint':DEFAULT_BASE+'/chat/completions','keys':[{'secret_name':'AGNES_API_KEY14','status':'authentication_rejected','http_status':401}]};path.write_text(json.dumps(report));env={'AGNES_API_KEY':'fake-good','AGNES_API_KEY14':'fake-bad','AGNES_API_KEYS':'fake-bad,fake-good'}
   self.assertEqual(AgnesKeyPool(env,path,now).keys,['fake-good']);self.assertEqual(len(AgnesKeyPool(env,path,now+dt.timedelta(hours=7)).keys),2)
 def test_only_401_disables(self):
  p=AgnesKeyPool({'AGNES_API_KEY':'fake-a'},report_path='/absent')
  for status in (403,429,503):self.assertFalse(p.disable('fake-a',status));self.assertEqual(p.next(),'fake-a')
  p.disable('fake-a',401)
  with self.assertRaises(RuntimeError):p.next()
 def test_auth_retry_and_redacted_503(self):
  p=AgnesKeyPool({'AGNES_API_KEY':'fake-a','AGNES_API_KEY2':'fake-b'},report_path='/absent');first=urllib.error.HTTPError(DEFAULT_BASE,401,'no',{},io.BytesIO(b'PRIVATE_SENTINEL'))
  with patch('urllib.request.urlopen',side_effect=[first,io.BytesIO(b'{"ok":true}')])as mock:
   self.assertEqual(p.fetch_json(DEFAULT_BASE+'/chat/completions',{'Authorization':'Bearer fake-a'},{}),{'ok':True});self.assertEqual(mock.call_count,2);self.assertEqual(p.next(),'fake-b')
  error=urllib.error.HTTPError(DEFAULT_BASE,503,'no',{},io.BytesIO(b'PRIVATE_SENTINEL'))
  with patch('urllib.request.urlopen',side_effect=error),self.assertRaises(RuntimeError)as caught:p.fetch_json(DEFAULT_BASE+'/chat/completions',{'Authorization':'Bearer fake-b'}, {})
  self.assertNotIn('PRIVATE_SENTINEL',str(caught.exception));self.assertIn('503',str(caught.exception));self.assertEqual(p.next(),'fake-b')
if __name__=='__main__':unittest.main()

class HealthyOnlyRoutingTests(unittest.TestCase):
 def make_report(self,path,now):
  path.write_text(json.dumps({'complete':True,'tested_at':(now-dt.timedelta(days=2)).isoformat(),'endpoint':DEFAULT_BASE+'/chat/completions','keys':[{'secret_name':'AGNES_API_KEY','status':'healthy','http_status':200},{'secret_name':'AGNES_API_KEY14','status':'healthy','http_status':200},{'secret_name':'AGNES_API_KEY15','status':'healthy','http_status':200},{'secret_name':'AGNES_API_KEY16','status':'authentication_rejected','http_status':401},{'secret_name':'AGNES_API_KEY2','status':'nonconforming_response','http_status':200}]}))
 def test_stale_audit_never_reenables_broken_or_unknown_values(self):
  now=dt.datetime.now(dt.timezone.utc)
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'health.json';self.make_report(path,now)
   env={'AGNES_HEALTHY_SLOTS_ONLY':'1','AGNES_PREFERRED_KEY_SLOTS':'AGNES_API_KEY14,AGNES_API_KEY15','AGNES_API_KEY':'fake-main','AGNES_API_KEY14':'fake-14','AGNES_API_KEY15':'fake-15','AGNES_API_KEY16':'fake-rejected','AGNES_API_KEY2':'fake-uncertain','AGNES_API_KEYS':'fake-rejected,fake-main,fake-unknown'}
   pool=AgnesKeyPool(env,path,now);self.assertEqual(pool.keys,['fake-14','fake-15','fake-main']);self.assertEqual([pool.next()for _ in range(4)],['fake-14','fake-15','fake-main','fake-14'])
 def test_missing_or_wrong_endpoint_report_cannot_bypass_strict_mode(self):
  with self.assertRaisesRegex(RuntimeError,'audit required'):AgnesKeyPool({'AGNES_HEALTHY_SLOTS_ONLY':'1','AGNES_API_KEY':'fake'},report_path='/absent')
  now=dt.datetime.now(dt.timezone.utc)
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'health.json';self.make_report(path,now)
   with self.assertRaises(RuntimeError):AgnesKeyPool({'AGNES_HEALTHY_SLOTS_ONLY':'1','AGNES_API_KEY':'fake'},path,now,base='https://other.example/v1')
 def test_unconfigured_confirmed_slots_do_not_allow_aggregate_smuggling(self):
  now=dt.datetime.now(dt.timezone.utc)
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'health.json';self.make_report(path,now)
   with self.assertRaisesRegex(RuntimeError,'No configured credential'):AgnesKeyPool({'AGNES_HEALTHY_SLOTS_ONLY':'1','AGNES_API_KEYS':'fake-unknown'},path,now)

class CapabilitySubsetTests(unittest.TestCase):
 def test_image_auth_fallback_cannot_use_text_only_slots(self):
  p=AgnesKeyPool({'AGNES_API_KEY':'fake-text','AGNES_API_KEY14':'fake-image'},report_path='/absent')
  error=urllib.error.HTTPError(DEFAULT_BASE,401,'no',{},io.BytesIO(b'PRIVATE_SENTINEL'))
  with patch('urllib.request.urlopen',side_effect=error)as request,self.assertRaisesRegex(RuntimeError,'requested Agnes capability pool'):
   p.fetch_json(DEFAULT_BASE+'/images/generations',{'Authorization':'Bearer fake-image'},{},allowed_keys=['fake-image'])
  self.assertEqual(request.call_count,1);self.assertEqual(p.next(),'fake-text')
 def test_capability_pool_refuses_outside_key(self):
  p=AgnesKeyPool({'AGNES_API_KEY':'fake-text','AGNES_API_KEY14':'fake-image'},report_path='/absent')
  with patch('urllib.request.urlopen')as request,self.assertRaisesRegex(RuntimeError,'outside requested'):
   p.fetch_json(DEFAULT_BASE+'/images/generations',{'Authorization':'Bearer fake-text'},{},allowed_keys=['fake-image'])
  request.assert_not_called()
