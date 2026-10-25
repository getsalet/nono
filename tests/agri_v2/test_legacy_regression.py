import io,json,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2.client import parse_text_object,ModelOutputError,TextProviderError,ModelClient,CapabilityError
from automation.agri_v2.cycle import handle_generation_failure
from automation.agri_v2.failure_diagnostics import failure_details
from automation.agri_v2.queue import load_json
from automation.agri_v2 import recovery
class LegacyRegressionTests(unittest.TestCase):
 def test_legacy_json_wrappers(self):
  for raw in ['{"x":1}','```json\n{"x":1}\n```','Here is the JSON: {"x":1}',json.dumps('{"x":1}')]:self.assertEqual(parse_text_object(raw),{'x':1})
 def test_truncated_or_non_object_still_rejected(self):
  for raw in ['',None,'{"x":','[]','not json']:
   with self.assertRaises(ModelOutputError):parse_text_object(raw)
 def test_local_output_error_never_opens_provider_circuit(self):
  with patch('automation.agri_v2.recovery.open_circuit') as circuit:
   for exc in [ModelOutputError('text_json_invalid'),ValueError('bad article'),CapabilityError('model mismatch')]:handle_generation_failure(exc)
   circuit.assert_not_called()
 def test_real_text_outage_carries_scope_and_retry_after(self):
  with tempfile.TemporaryDirectory() as d,patch.object(recovery,'OUT',Path(d)):
   handle_generation_failure(TextProviderError(429,'rate_limited',7200))
   row=load_json(Path(d)/'provider-circuit.json');self.assertEqual(row['request_kind'],'text');self.assertEqual(row['reason'],'rate_limited');self.assertIn('retry_at_epoch',row)
 def test_auth_failure_not_mislabeled_as_outage(self):
  with patch('automation.agri_v2.recovery.open_circuit') as circuit:handle_generation_failure(TextProviderError(401,'invalid_auth'));circuit.assert_not_called()
 def test_diagnostics_never_copy_raw_error(self):
  self.assertEqual(failure_details(ValueError('Bearer private-key')) ,{'kind':'validation','category':'unspecified'})
  self.assertEqual(failure_details(TextProviderError(503,'provider_unavailable')),{'kind':'text_provider','category':'provider_unavailable','http_status':503})
 def test_text_http_error_is_typed(self):
  c=object.__new__(ModelClient);c.keys={'text':[('AGNES_API_KEY','fixture')]};c.used={'text':0};c.env={}
  error=urllib.error.HTTPError('https://example.org',503,'unavailable',{},io.BytesIO(b'private provider body'))
  with patch('automation.agri_v2.client.urllib.request.urlopen',side_effect=error):
   with self.assertRaises(TextProviderError) as cm:c.request('text','/chat/completions',{},1)
  self.assertEqual(cm.exception.category,'provider_unavailable');self.assertNotIn('private',str(cm.exception))
 def test_legacy_image_wait_budget_restored(self):
  c=object.__new__(ModelClient)
  with patch.object(c,'request',return_value={}) as request,patch('automation.agri_v2.client.render_image',return_value=b'fixture'):
   c.image('fixture');self.assertEqual(request.call_args.args[3],600)
