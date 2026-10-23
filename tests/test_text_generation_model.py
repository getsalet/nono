"""User-required Agnes 2.5 Flash for production article text, not image models."""
import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TextGenerationModelTests(unittest.TestCase):
 def test_production_workflows_pin_text_model(self):
  workflows=['roya-backlink-queue','farsiblog-content','rozblog-content','loxblog-content','blogsky-content','parsiblog-content','niloblog-content','city-content-queue','city-rewrite-queue','rewrite-city-posts','translate']
  for name in workflows:
   with self.subTest(workflow=name):
    text=(ROOT/'.github/workflows'/(name+'.yml')).read_text()
    lines=[x.strip()for x in text.splitlines()if x.strip().startswith('AGNES_MODEL:')]
    self.assertEqual(lines,['AGNES_MODEL: agnes-2.5-flash'])
 def test_json_client_sends_same_model_on_retry(self):
  spec=importlib.util.spec_from_file_location('model_contract_client',ROOT/'automation/agnes_json_client.py');client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
  class Base:
   AGNES_KEYS=['unit-test-only'];AGNES_KEY='unit-test-only';AGNES_MODEL='agnes-2.5-flash';AGNES_BASE='https://example.invalid/v1'
   def __init__(self):self.payloads=[]
   def next_agnes_key(self):return self.AGNES_KEY
   def fetch_json(self,url,headers,payload,timeout):
    self.payloads.append(payload)
    return {'choices':[{'message':{'content':'invalid'if len(self.payloads)==1 else '{"ok":true}'}}]}
  base=Base();original=client.time.sleep;client.time.sleep=lambda _:None
  try:self.assertEqual(client.call(base,'test',attempts=2),{'ok':True})
  finally:client.time.sleep=original
  self.assertEqual([p['model']for p in base.payloads],['agnes-2.5-flash']*2)
 def test_shared_engine_default_and_payload(self):
  source=(ROOT/'automation/roya_backlink_queue.py').read_text()
  self.assertIn("os.getenv('AGNES_MODEL', 'agnes-2.5-flash')",source)
  self.assertIn("'model': BASE.AGNES_MODEL",source)
if __name__=='__main__':unittest.main()
