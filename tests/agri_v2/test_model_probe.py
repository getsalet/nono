import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import model_probe as p
from automation.agri_v2.queue import atomic_json
class ModelProbeTests(unittest.TestCase):
 def req(self):return {'request_id':p.ID,'models':p.MODELS,'max_requests':2,'topic_id':p.TOPIC,'publication_authorized':False}
 def test_only_documented_models_and_strict_budget(self):
  r=self.req();p.validate(r);r['models']=['other-model']
  with self.assertRaises(ValueError):p.validate(r)
 def test_real_reference_and_canonical_image_prompt(self):
  d=p.payload(p.MODELS[0],{'crop':'لوبیا قرمز','title':'برداشت لوبیا قرمز'});self.assertTrue(d['extra_body']['image'][0].startswith('data:image/'));self.assertNotIn('n',d);self.assertNotIn('response_format',d);self.assertIn('near-overhead',d['prompt'])
 def test_no_repeat_of_reserved_test(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'model-switch-request.json',self.req());atomic_json(out/'model-switch'/p.ID/'report.json',{'status':'reserved'})
   with patch.object(p,'DATA',data),patch.object(p,'OUT',out),patch.object(p,'probe') as call:
    self.assertEqual(p.run()['model_calls'],0);call.assert_not_called()
 def test_provider_cooldown_is_not_bypassed_by_model_change(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'model-switch-request.json',self.req())
   with patch.object(p,'DATA',data),patch.object(p,'OUT',out),patch.object(p,'circuit_open',return_value=True),patch.object(p,'update'),patch.object(p,'probe') as call:
    self.assertEqual(p.run()['status'],'provider_cooldown_honored');call.assert_not_called()
if __name__=='__main__':unittest.main()
