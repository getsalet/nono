import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import image_backtest as b,tuning_resume as t
from automation.agri_v2.queue import DATA,OUT,load_json,atomic_json
class VerifiedPoolSceneTests(unittest.TestCase):
 def req(self):return copy.deepcopy(b.POOL_REQUEST)
 def test_exact_new_request_no_larger_budget(self):
  req=self.req();b.validate(req);req['max_image_calls']=3
  with self.assertRaises(ValueError):b.validate(req)
 def test_old_request_remains_distinct(self):
  old={k:v for k,v in self.req().items() if k not in ('source_audit_sha256','source_audit_run_id','required_image_slots')};old['request_id']=b.ID;b.validate(old);self.assertNotEqual(old['request_id'],self.req()['request_id'])
 def test_current_evidence_matches_actual_diagnostic_bytes(self):b.verify_pool_evidence(self.req(),load_json(DATA/'health/latest.json'))
 def test_missing_verified_key_blocks_scene_test(self):
  health=load_json(DATA/'health/latest.json');health['eligible_image_slots']=['AGNES_API_KEY']
  with self.assertRaises(ValueError):b.verify_pool_evidence(self.req(),health)
 def test_changed_audit_hash_blocks_scene_test(self):
  req=self.req();req['source_audit_sha256']='0'*64
  with self.assertRaises(ValueError):b.verify_pool_evidence(req,load_json(DATA/'health/latest.json'))
 def test_cooldown_does_not_reserve_new_request_or_touch_old_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'image-backtest-request.json',self.req());old=out/'image-backtests'/b.ID/'report.json';atomic_json(old,{'status':'stopped_provider_limit_or_failure'});before=old.read_bytes()
   with patch.object(b,'DATA',data),patch.object(b,'OUT',out),patch.object(b,'circuit_open',return_value=True),patch.object(b,'ModelClient') as client:
    self.assertTrue(b.run()['no_request_reserved']);client.assert_not_called();self.assertEqual(old.read_bytes(),before);self.assertFalse((out/'image-backtests'/b.POOL_ID/'report.json').exists())
