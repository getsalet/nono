import importlib.util,json,tempfile,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'automation/audit_agnes_keys.py';spec=importlib.util.spec_from_file_location('audit_agnes_keys',p);audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class HealthTests(unittest.TestCase):
 def test_all_25_explicit_slots(self):
  self.assertEqual(len(audit.NAMES),25);self.assertEqual(len(set(audit.NAMES)),25);self.assertIn('AGNES_API_KEY25',audit.NAMES);self.assertNotIn('AGNES_API_KEY1',audit.NAMES)
 def test_server_failure_is_not_bad_auth(self):
  self.assertEqual(audit.classify_http(503),'provider_unavailable');self.assertEqual(audit.classify_http(401),'authentication_rejected');self.assertEqual(audit.classify_http(429),'rate_limited_or_quota')
 def test_no_values_or_fingerprints_and_duplicates_do_not_spend_twice(self):
  with tempfile.TemporaryDirectory()as t:
   old=audit.OUT;audit.OUT=Path(t)/'report.json';calls=[]
   try:
    def worker(value):calls.append(value);return {'status':'healthy','http_status':200,'image_capability':'not_tested'}
    report=audit.audit({'AGNES_API_KEY':'SECRET_SENTINEL_A','AGNES_API_KEY2':'SECRET_SENTINEL_A','AGNES_API_KEY25':'SECRET_SENTINEL_B'},worker)
    raw=audit.OUT.read_text();self.assertNotIn('SECRET_SENTINEL',raw);self.assertEqual(len(calls),2);self.assertEqual(report['configured_slots'],3);self.assertEqual(report['healthy_unique_credentials'],2);self.assertEqual(report['keys'][1]['duplicate_of'],'AGNES_API_KEY');self.assertEqual(report['keys'][2]['status'],'not_configured')
   finally:audit.OUT=old
if __name__=='__main__':unittest.main()
