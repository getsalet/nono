"""Fresh startup requires explicit approval; no cached handoff or stop bypass."""
import contextlib,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_automation_control as a
import check_blog_ready_image_handoff as h
class AutomationApprovalTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.r=Path(self.t.name);(self.r/'data').mkdir()
  self.write('blog-generated-image-control.json',{'pause_image_production':False,'retired_blogs':['blogfa']})
  self.write('blog-automation-control.json',{'policy':'explicit-blog-scheduler-v1','enabled':{'farsiblog':True,'rozblog':True,'loxblog':True,'blogfa':True}})
 def write(self,p,v):(self.r/'data'/p).write_text(json.dumps(v))
 def test_approved_active_providers_only(self):
  for b in a.ACTIVE:self.assertTrue(a.enabled(b,self.r))
  for b in ('blogfa','unknown','roya'):self.assertFalse(a.enabled(b,self.r))
 def test_pause_retirement_and_invalid_config_fail_closed(self):
  self.write('blog-generated-image-control.json',{'pause_image_production':True});self.assertFalse(a.enabled('farsiblog',self.r))
  self.write('blog-generated-image-control.json',{'pause_image_production':False,'retired_blogs':['farsiblog']});self.assertFalse(a.enabled('farsiblog',self.r))
  self.write('blog-automation-control.json',{'enabled':{'farsiblog':'true'}});self.assertFalse(a.enabled('farsiblog',self.r))
 def run_main(self,wake,approved,event='push'):
  out=io.StringIO()
  with patch.object(sys,'argv',['gate','farsiblog']),patch.dict(os.environ,{'GITHUB_EVENT_NAME':event,'BLOG_AUTOMATION_WAKE':wake,'GITHUB_OUTPUT':''}),patch.object(a,'enabled',return_value=approved),patch.object(h,'handoff',return_value={'proceed':False,'cached_only':True,'target':''}),contextlib.redirect_stdout(out):h.main()
  return json.loads(out.getvalue())
 def test_only_explicit_approved_push_can_generate_from_empty_queue(self):
  self.assertTrue(self.run_main('true',True)['proceed']);self.assertFalse(self.run_main('true',True)['cached_only'])
  self.assertFalse(self.run_main('false',True)['proceed']);self.assertFalse(self.run_main('true',False)['proceed']);self.assertFalse(self.run_main('true',True,'workflow_run')['proceed'])
 def test_all_workflows_preserve_publication_quality_and_budget_guards(self):
  for b in a.ACTIVE:
   text=(ROOT/'.github/workflows'/f'{b}-content.yml').read_text()
   for expected in ('automation_enabled','[blog-generators-resume]','check_blog_pipeline_control.py '+b,'check_blog_run_budget.py '+b,'publish_'+b+'_posts.py','cancel-in-progress: false'):self.assertIn(expected,text)
if __name__=='__main__':unittest.main()
