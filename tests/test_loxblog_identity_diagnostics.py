import sys,unittest,inspect
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import loxblog_native as n
class DiagnosticsTests(unittest.TestCase):
 def test_only_known_aggregate_values_survive(self):
  page=SimpleNamespace(evaluate=Mock(return_value={'archive_route':True,'editor_route':'private','archive_search':False,'editor_title':False,'expected_href_count':3,'exact_label_count':True,'normalized_label_count':-1,'body':'PRIVATE'}))
  d=n.management_diagnostics(page)
  self.assertTrue(d['archive_route']);self.assertFalse(d['editor_route']);self.assertEqual(d['expected_href_count'],3);self.assertIsNone(d['exact_label_count']);self.assertIsNone(d['normalized_label_count']);self.assertNotIn('PRIVATE',str(d));self.assertEqual(len(d),7)
 def test_large_counts_and_invalid_payload_never_escape(self):
  for raw in (None,[],{'expected_href_count':1001,'normalized_label_count':'PRIVATE'}):
   d=n.management_diagnostics(SimpleNamespace(evaluate=Mock(return_value=raw)));self.assertIsNone(d['expected_href_count']);self.assertNotIn('PRIVATE',str(d))
 def test_login_diagnostic_installs_browser_even_when_publication_is_off(self):
  root=Path(__file__).resolve().parents[1]
  workflow=(root/'.github/workflows/loxblog-content.yml').read_text()
  install=workflow.split('      - name: Install Playwright',1)[1].split('      - name:',1)[0]
  self.assertIn("(env.LOXBLOG_PUBLISH == '1' || env.LOXBLOG_LOGIN_DIAGNOSTIC == '1')",install)
  self.assertIn("env.LOXBLOG_DRY_RUN != '1'",install)
  for gate in ('control','release','budget'):self.assertIn("steps."+gate+".outputs.proceed == '1'",install)
  publish=workflow.split('      - name: Publish and verify native LoxBlog post',1)[1].split('      - name:',1)[0]
  self.assertIn('LOXBLOG_LOGIN_DIAGNOSTIC',publish)
  self.assertLess(publish.index('python automation/loxblog_native.py'),publish.index('else'))
 def test_read_only_no_acceptance_or_secret_collection(self):
  source=inspect.getsource(n.management_diagnostics)
  for bad in ('.click(','.fill(','.goto(','.reload(','.innerText','innerHTML','input_value','cookie','localStorage','storage_state'):self.assertNotIn(bad,source)
if __name__=='__main__':unittest.main()
