import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import image_diagnostic as d
from automation.agri_v2.queue import atomic_json
class ImageDiagnosticTests(unittest.TestCase):
 def test_control_never_contains_product_reference(self):
  p=d.payload('control',refs=False);self.assertNotIn('image',p['extra_body']);self.assertEqual(p['model'],'agnes-image-2.5-flash');self.assertEqual(p['n'],1)
 def test_only_optional_n_changes_in_matched_payload(self):
  a=d.payload('exact');b=d.payload('exact',omit_n=True);a.pop('n');self.assertEqual(a,b)
 def test_rate_billing_queue_errors_stop_no_rotation(self):
  for row in [{'http_status':429},{'http_status':402},{'http_status':401},{'http_status':403},{'http_status':503,'provider_code':'image_queue_full'},{'http_status':503,'provider_code':'insufficient_quota'}]:self.assertTrue(d.stop_for_limits(row))
  self.assertFalse(d.stop_for_limits({'http_status':503,'provider_code':'service_unavailable'}))
 def test_reservation_prevents_repeating_diagnostic(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'image-diagnostic-request.json',{'request_id':d.REQUEST_ID,'topic_id':d.TOPIC,'max_provider_requests':4,'publication_authorized':False});atomic_json(out/'image-diagnostics'/d.REQUEST_ID/'report.json',{'status':'started'})
   with patch.object(d,'DATA',data),patch.object(d,'OUT',out),patch.object(d,'probe') as p:
    self.assertEqual(d.run()['status'],'diagnostic_already_reserved');p.assert_not_called()
 def test_invalid_authorization_blocks_before_provider(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t);atomic_json(data/'image-diagnostic-request.json',{'request_id':d.REQUEST_ID,'topic_id':d.TOPIC,'max_provider_requests':99,'publication_authorized':True})
   with patch.object(d,'DATA',data),patch.object(d,'probe') as p:
    with self.assertRaises(d.DiagnosticBlocked):d.run()
    p.assert_not_called()
 def test_production_decoder_rejects_invalid_image(self):
  from automation.agri_v2.client import render_image,CapabilityError
  with self.assertRaises(CapabilityError):render_image({'data':[]})
if __name__=='__main__':unittest.main()
