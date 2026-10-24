import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import recovery,revise
from automation.agri_v2.queue import atomic_json,load_json,utcnow
from automation.agri_v2.client import CapabilityError
class RecoveryTests(unittest.TestCase):
 def test_open_circuit_blocks_repeated_paid_calls(self):
  with tempfile.TemporaryDirectory() as t,patch.object(recovery,'OUT',Path(t)):
   self.assertFalse(recovery.circuit_open());recovery.open_circuit();self.assertTrue(recovery.circuit_open())
 def test_old_circuit_expires(self):
  with tempfile.TemporaryDirectory() as t,patch.object(recovery,'OUT',Path(t)):
   atomic_json(Path(t)/'provider-circuit.json',{'open':True,'at':'2026-01-01T00:00:00Z'});self.assertFalse(recovery.circuit_open())
 def test_failed_recovery_retains_hold_and_is_not_retried(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';ident='agri-af1a4b491d83'
   atomic_json(data/'research-request.json',{'request_id':'research-feeder-rollout-v1','pilot_recovery':{'topic_id':ident,'authorized':True,'max_additional_cycles':1}})
   atomic_json(data/'config.json',{'publication_holds':{ident:'image provider'}})
   with patch.object(recovery,'DATA',data),patch.object(recovery,'OUT',out),patch.object(recovery,'update'),patch.object(revise,'run',side_effect=CapabilityError('provider_unavailable')) as r:
    self.assertEqual(recovery.recover_once()['status'],'recovery_provider_failed');self.assertIn(ident,load_json(data/'config.json')['publication_holds']);self.assertEqual(recovery.recover_once()['status'],'recovery_already_attempted');self.assertEqual(r.call_count,1)
 def test_verified_recovery_removes_only_its_hold(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';ident='agri-af1a4b491d83'
   atomic_json(data/'research-request.json',{'request_id':'research-feeder-rollout-v1','pilot_recovery':{'topic_id':ident,'authorized':True,'max_additional_cycles':1}});atomic_json(data/'config.json',{'publication_holds':{ident:'image','other':'retain'}})
   with patch.object(recovery,'DATA',data),patch.object(recovery,'OUT',out),patch.object(revise,'run',return_value={'status':'revised'}):
    recovery.recover_once();self.assertEqual(load_json(data/'config.json')['publication_holds'],{'other':'retain'})
