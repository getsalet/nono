import io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import calibrate_image_validation as validation
class ExistingImageValidationTests(unittest.TestCase):
 def run_validation(self,error=False):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'existing.webp').write_bytes(b'fixture-only')
   with patch.object(validation,'ROOT',root),patch.object(validation,'CASES',( ('existing.webp',1),)),patch.dict(os.environ,{'GITHUB_RUN_ID':'fixture'}),patch.object(validation.base,'load_items',return_value=[{}, {'key':'published','family':'tape20','_image_article_context':{'title':'context'}}]),patch.object(validation.generated,'generate',side_effect=AssertionError('No new image request allowed'))as gen,patch.object(validation.generated,'checkpoint_asset'),patch.object(validation.gate,'review',side_effect=RuntimeError('service unavailable')if error else None,return_value={'verdict':{'pass':True,'score':95},'closed_package_required':True,'package_finish_policy':'no-protruding-carton-strip-v1','focused_physical_review':{'package_has_protruding_strip':False}}):
    validation.main()
   gen.assert_not_called()
   return json.loads((root/'artifacts/blog-image-calibration/fixture/report.json').read_text())
 def test_validation_is_bounded_and_generates_nothing(self):
  r=self.run_validation();self.assertEqual(r['image_generations'],0);self.assertEqual(r['post_submissions'],0);self.assertEqual(len(r['cases']),1);self.assertTrue(r['cases'][0]['accepted'])
 def test_service_error_is_not_approval(self):
  r=self.run_validation(True);self.assertFalse(r['cases'][0]['accepted']);self.assertEqual(r['cases'][0]['error_type'],'RuntimeError')
if __name__=='__main__':unittest.main()
