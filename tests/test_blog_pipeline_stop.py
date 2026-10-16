import ast,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from check_blog_pipeline_control import decision,BLOGS
class SharedPipelineStopTests(unittest.TestCase):
 def test_pause_blocks_all_blogs(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text('{"pause_image_production":true}')
   for blog in BLOGS:self.assertEqual(decision(blog,root)['reason'],'user_pause');self.assertFalse(decision(blog,root)['proceed'])
 def test_missing_invalid_or_ambiguous_control_fails_closed(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();p=root/'data/blog-generated-image-control.json'
   self.assertFalse(decision('roya',root)['proceed'])
   for value in ('invalid','[]','{}','{"pause_image_production":"false"}'):
    p.write_text(value);self.assertFalse(decision('roya',root)['proceed'])
 def test_release_is_not_implied_by_unpaused_control(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text('{"pause_image_production":false}')
   self.assertEqual(decision('loxblog',root)['reason'],'other_gates_still_required')
 def test_preflight_has_no_costly_imports(self):
  tree=ast.parse((ROOT/'automation/check_blog_pipeline_control.py').read_text())
  imports=[n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)]
  self.assertEqual(imports,['pathlib'])
 def test_all_direct_publishers_return_before_io_or_browser(self):
  for module in ('publish_roya_posts','publish_farsiblog_posts','publish_rozblog_posts','publish_blogfa_posts','publish_loxblog_posts'):
   code="import sys;sys.path.insert(0,'automation');from unittest.mock import patch;import "+module+" as p\nwith patch('blog_image_runtime_control.publication_paused',return_value=True):\n assert p.main()==0\n"
   result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,module+': '+result.stderr)
   self.assertIn('no queue mutation',result.stdout)
 def test_runtime_workflow_steps_are_guarded(self):
  for workflow,blog in [('roya-backlink-queue','roya'),('roya-backlink-publish','roya'),('farsiblog-content','farsiblog'),('rozblog-content','rozblog'),('blogfa-content','blogfa'),('loxblog-content','loxblog')]:
   s=(ROOT/'.github/workflows'/(workflow+'.yml')).read_text();self.assertIn('run: python automation/check_blog_pipeline_control.py '+blog,s)
   after=s.split('id: control',1)[1].split('\n      - ')[1:]
   for step in after:self.assertIn("if: steps.control.outputs.proceed == '1'",step,workflow+': '+step[:100])
if __name__=='__main__':unittest.main()

class DirectStopIntegrityTests(unittest.TestCase):
 def test_direct_publication_fails_closed_without_control(self):
  from blog_image_runtime_control import publication_paused
  with tempfile.TemporaryDirectory()as d:
   self.assertTrue(publication_paused(Path(d)))
   (Path(d)/'data').mkdir();path=Path(d)/'data/blog-generated-image-control.json'
   path.write_text('{"pause_image_production":"false"}');self.assertTrue(publication_paused(Path(d)))
   path.write_text('{"pause_image_production":false}');self.assertFalse(publication_paused(Path(d)))
 def test_loxblog_pause_precedes_wrapper_status_rewrite(self):
  from unittest.mock import patch
  import loxblog_backlink_queue as wrapper
  with patch('blog_image_runtime_control.generation_paused',return_value=True),patch.object(wrapper.engine,'main',side_effect=AssertionError('No generation while paused')):
   self.assertEqual(wrapper.main(),0)
