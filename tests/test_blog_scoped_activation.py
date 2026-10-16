import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generated_image as image
import blog_image_gate as gate
from blog_reference_scene import RECIPE_VERSION,recipe_for
from blog_image_connection import settings
class ScopedActivationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);(self.root/'data').mkdir();self.digest='a'*64
  self.control={'enabled':True,'pause_image_production':False,'policy':image.POLICY,'direct_visual_approval':True,'recipe_version':RECIPE_VERSION,'blogs':list(image.BLOGS),'enabled_families':['tape20'],'approved_samples':{'tape20':self.digest}}
  self.report={'policy':image.POLICY,'recipe_version':RECIPE_VERSION,'connection':settings(image.roya.BASE.AGNES_BASE),'passed':False,'families':[{'family':'tape20','passed':True,'request_contract':{'family_recipe':recipe_for({'family':'tape20'})},'review':{'sha256':self.digest,'policy':gate.POLICY}},{'family':'hose','passed':False}]}
  self.write()
 def write(self):
  for name,value in [('blog-generated-image-control',self.control),('blog-generated-image-acceptance',self.report),('blog-generated-image-visual-review',{'approved_sha256':[self.digest],'rejected_sha256':[]})]:(self.root/'data'/(name+'.json')).write_text(json.dumps(value))
 def test_only_directly_approved_subset_can_activate(self):
  for blog in image.BLOGS:self.assertTrue(image.rollout_enabled(blog,self.root))
  self.assertTrue(image.family_enabled({'family':'tape20'},self.root));self.assertFalse(image.family_enabled({'family':'hose'},self.root))
 def test_hose_never_reaches_cache_or_api(self):
  with patch.object(image,'existing_asset',side_effect=AssertionError('no network')),patch.object(image,'generate',side_effect=AssertionError('no image request')):
   with self.assertRaisesRegex(RuntimeError,'held'):image.prepare({'family':'hose','key':'held'},'roya',self.root)
 def test_enabling_unapproved_hose_is_rejected(self):
  self.control['enabled_families'].append('hose');self.write()
  with self.assertRaisesRegex(RuntimeError,'pass image acceptance'):image.rollout_enabled('roya',self.root)
 def test_absent_subset_keeps_both_family_requirement(self):
  self.control.pop('enabled_families');self.write()
  with self.assertRaisesRegex(RuntimeError,'Both genuine'):image.rollout_enabled('roya',self.root)
 def test_stale_family_recipe_and_wrong_digest_are_rejected(self):
  self.report['families'][0]['request_contract']['family_recipe']='old';self.write()
  with self.assertRaisesRegex(RuntimeError,'recipe'):image.rollout_enabled('roya',self.root)
 def test_failed_tape_sample_cannot_activate(self):
  self.report['families'][0]['passed']=False;self.write()
  with self.assertRaisesRegex(RuntimeError,'pass image acceptance'):image.rollout_enabled('roya',self.root)

class ActivationDispatchPlanTests(unittest.TestCase):
 def test_activation_requests_one_canary_per_blog(self):
  from activate_blog_publication import plan,WORKFLOWS
  jobs=plan({'enabled':True,'pause_image_production':False,'enabled_families':['tape20'],'blogs':list(WORKFLOWS)})
  self.assertEqual(len(jobs),5)
  for job in jobs:self.assertEqual(job['inputs']['count'],'1');self.assertEqual(job['inputs']['dry_run'],'0')
 def test_paused_control_does_not_dispatch(self):
  from activate_blog_publication import plan
  self.assertEqual(plan({'enabled':True,'pause_image_production':True}),[])
