import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import activation_health as a
from automation.agri_v2.queue import atomic_json
class ActivationHealthTests(unittest.TestCase):
 def test_exact_nonmutation_authorization(self):
  with tempfile.TemporaryDirectory() as d:
   req=dict(a.REQUEST,publication_authorized=True);atomic_json(Path(d)/'activation-health-request.json',req)
   with patch.object(a,'DATA',Path(d)),self.assertRaises(ValueError):a.run()
 def test_reserved_check_never_repeats_model_or_wordpress(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'activation-health-request.json',a.REQUEST);atomic_json(out/'activation-health'/a.REQUEST['request_id']/'report.json',{'status':'reserved'})
   with patch.object(a,'DATA',data),patch.object(a,'OUT',out),patch.object(a,'WordPress') as wp,patch.object(a,'ModelClient') as model:
    self.assertEqual(a.run()['model_calls'],0);wp.assert_not_called();model.assert_not_called()
 def test_validation_failure_prevents_remote_calls(self):
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';out=Path(d)/'out';atomic_json(data/'activation-health-request.json',a.REQUEST)
   with patch.object(a,'DATA',data),patch.object(a,'OUT',out),patch.object(a,'get_topic',side_effect=ValueError('fixture')),patch.object(a,'WordPress') as wp,patch.object(a,'ModelClient') as model:
    self.assertEqual(a.run()['status'],'readiness_blocked');wp.assert_not_called();model.assert_not_called()
