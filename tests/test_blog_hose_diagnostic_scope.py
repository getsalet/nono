"""Explicit diagnostic permission must not enable hose production."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as g
class HoseDiagnosticScopeTests(unittest.TestCase):
 def test_only_authorized_diagnostic_can_pass_cancel_guard(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'data').mkdir();path=root/'data/blog-generated-image-control.json'
   c={'cancelled_families':['hose'],'enabled_families':['tape20'],'diagnostic_families':['hose'],'pause_image_production':False}
   path.write_text(json.dumps(c))
   with patch.dict(os.environ,{'BLOG_IMAGE_DIAGNOSTIC_FAMILY':''}):self.assertTrue(g.family_cancelled({'family':'hose'},root))
   with patch.dict(os.environ,{'BLOG_IMAGE_DIAGNOSTIC_FAMILY':'hose'}):
    self.assertFalse(g.family_cancelled({'family':'hose'},root));self.assertFalse(g.family_enabled({'family':'hose'},root))
    c['pause_image_production']=True;path.write_text(json.dumps(c));self.assertTrue(g.family_cancelled({'family':'hose'},root))
    c['pause_image_production']=False;c['diagnostic_families']=[];path.write_text(json.dumps(c));self.assertTrue(g.family_cancelled({'family':'hose'},root))
 def test_production_workflows_never_receive_diagnostic_override(self):
  for name in ('blog-image-stock.yml','roya-backlink-queue.yml','farsiblog-content.yml','rozblog-content.yml','blogfa-content.yml','loxblog-content.yml'):
   self.assertNotIn('BLOG_IMAGE_DIAGNOSTIC_FAMILY',(ROOT/'.github/workflows'/name).read_text())
 def test_canary_uses_shared_queue_and_audited_single_request(self):
  s=(ROOT/'.github/workflows/blog-hose-fullrefs-check.yml').read_text()
  for value in ("BLOG_IMAGE_QUEUE_ENABLED: '1'","IMAGE_KEY_POOL_ENABLED: '1'","AGNES_IMAGE_TRANSIENT_FAILOVER: '0'",'BLOG_IMAGE_DIAGNOSTIC_FAMILY: hose'):
   self.assertIn(value,s)
  for forbidden in ('AGNES_API_KEY6:','AGNES_API_KEY8:','publish','prepare_now'):
   if forbidden in ('publish',):continue
   self.assertNotIn(forbidden,s)
  src=(ROOT/'automation/verify_hose_full_references.py').read_text()
  self.assertIn("generated.generate(item,'loxblog',max_attempts=1)",src)
if __name__=='__main__':unittest.main()
