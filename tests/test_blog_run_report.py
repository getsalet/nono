import copy,json,sys,tempfile,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_run_report as r

def run(**kw):
 d={'id':123,'run_attempt':1,'head_branch':'main','head_repository':{'full_name':'getsalet/nono'},'path':'.github/workflows/loxblog-content.yml','status':'completed','conclusion':'failure','event':'schedule','run_started_at':'2026-10-28T01:00:00Z','updated_at':'2026-10-28T01:10:00Z'};d.update(kw);return d
class Reports(unittest.TestCase):
 def test_all_eight_workflows_and_no_retired_blog(self):
  self.assertEqual(len(r.WORKFLOWS),8);self.assertEqual(set(x[0]for x in r.WORKFLOWS.values()),set(r.HOSTS));self.assertNotIn('blogfa',r.HOSTS)
 def test_reject_foreign_branch_repo_unknown_workflow_and_incomplete_run(self):
  for changes in [{'head_branch':'pr'},{'head_repository':{'full_name':'evil/nono'}},{'path':'.github/workflows/arbitrary.yml'},{'status':'in_progress'},{'id':'1; bad'},{'run_attempt':'../2'}]:
   with self.assertRaises(ValueError):r.build(run(**changes),[])
 def test_failed_stage_without_logs_does_not_invent_authentication_error(self):
  x=r.build(run(),[{'steps':[{'name':'Publish and verify native LoxBlog post','conclusion':'failure','outputs':{'PASSWORD':'SECRET'}}]}]);self.assertEqual(x['phase'],'publication');self.assertEqual(x['reason_code'],'unknown');self.assertNotIn('SECRET',json.dumps(x))
 def test_secrets_raw_errors_and_unknown_fields_are_never_copied(self):
  g={'run_id':'123','completed_at':'2026-10-28T01:09:00Z','status':'failed','reason':'authentication SECRET_ABC','token':'SECRET_DEF'}
  x=r.build(run(),[],generation=g);self.assertEqual(x['reason_code'],'login');self.assertNotIn('SECRET',json.dumps(x))
 def test_old_report_and_wrong_attempt_do_not_explain_new_failure(self):
  for g in [{'run_id':'122','completed_at':'2026-10-28T01:09:00Z'},{'run_id':'123','run_attempt':'2','completed_at':'2026-10-28T01:09:00Z'},{'run_id':'123','completed_at':'2026-10-27T01:09:00Z'}]:
   g.update(status='failed',reason='quality rejected');x=r.build(run(),[],generation=g);self.assertEqual(x['reason_basis'],'workflow');self.assertEqual(x['reason_code'],'unknown')
 def test_current_quality_report_is_classified_without_changing_any_inputs(self):
  g={'run_id':'123','completed_at':'2026-10-28T01:09:00Z','status':'failed','qa_errors':['Text validation rejected']};before=copy.deepcopy(g)
  self.assertEqual(r.build(run(),[],generation=g)['reason_code'],'quality');self.assertEqual(g,before)
 def test_green_run_is_not_publication(self):
  x=r.build(run(conclusion='success'),[]);self.assertEqual(x['publication']['status'],'not_proven');self.assertFalse(x['retry']['automatic_retry_authorized'])
 def test_receipt_overlap_is_explicitly_not_run_attribution(self):
  state={'published':[{'url':'https://afp.lxb.ir/post/69','at':'2026-10-28T01:05:00Z'}]};x=r.build(run(),[],state=state);self.assertEqual(len(x['publication']['receipts']),1);self.assertEqual(x['publication']['scope'],'repository_snapshot_not_run_attribution')
 def test_recovered_old_foreign_unsafe_and_outside_window_receipts_excluded(self):
  rows=[{'url':'https://afp.lxb.ir/post/69','at':'2026-10-28T01:05:00Z','recovered_existing':True}]
  for url in ['https://evil.example/p/1','https://afp.lxb.ir/','javascript:bad','https://u:secret@afp.lxb.ir/p/1','https://afp.lxb.ir/p/1?token=SECRET']:
   rows.append({'url':url,'at':'2026-10-28T01:05:00Z'})
  rows.append({'url':'https://afp.lxb.ir/post/70','at':'2026-10-27T01:05:00Z'})
  self.assertEqual(r.build(run(),[],state={'published':rows})['publication']['receipts'],[])
 def test_unresolved_receipt_never_authorizes_retry(self):
  g={'run_id':'123','completed_at':'2026-10-28T01:09:00Z','reason':'native reconciliation required'};x=r.build(run(),[],generation=g);self.assertEqual(x['retry']['policy'],'reconcile_first');self.assertFalse(x['retry']['automatic_retry_authorized'])
 def test_waiting_status_has_wait_policy(self):
  g={'run_id':'123','completed_at':'2026-10-28T01:09:00Z','status':'waiting_image'};self.assertEqual(r.build(run(conclusion='success'),[],generation=g)['retry']['policy'],'wait')
 def test_archive_order_does_not_replace_newer_latest(self):
  with tempfile.TemporaryDirectory()as td:
   new=r.build(run(id=125),[]);r.write_report(new,td);old=r.build(run(id=124),[]);paths=r.write_report(old,td);self.assertEqual(len(paths),1);self.assertEqual(r.read(Path(td)/'artifacts/blog-run-reports/loxblog/latest.json')['run_id'],'125')
 def test_collection_fetches_attempt_scoped_jobs_and_paginates(self):
  with tempfile.TemporaryDirectory()as td,patch.object(r,'api',side_effect=[run(),{'jobs':[{}]*100},{'jobs':[]}])as api,patch.object(r.subprocess,'check_output',return_value='a'*40):
   r.collect(123,'not-a-real-token',td);self.assertIn('/attempts/1/jobs',api.call_args_list[1].args[0]);self.assertIn('page=2',api.call_args_list[2].args[0])
 def test_persist_refuses_non_report_paths(self):
  with self.assertRaises(ValueError):r.persist(['automation/loxblog_native.py'])
 def test_atomic_report_checkpoint_preserves_unrelated_remote_changes(self):
  def git(cwd,*args):return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.DEVNULL).decode().strip()
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);remote=root/'origin.git';remote.mkdir();git(remote,'init','--bare','--initial-branch=main');work=root/'work';git(root,'clone',str(remote),str(work));git(work,'config','user.name','test');git(work,'config','user.email','test@example.com');(work/'unchanged.txt').write_text('first');git(work,'add','.');git(work,'commit','-m','seed');git(work,'push','origin','main')
   report=r.build(run(),[]);paths=r.write_report(report,work)
   other=root/'other';git(root,'clone',str(remote),str(other));git(other,'config','user.name','test');git(other,'config','user.email','test@example.com');(other/'other-blog.txt').write_text('keep me');r.write_report(r.build(run(id=125),[]),other);git(other,'add','.');git(other,'commit','-m','other blog');git(other,'push','origin','main')
   r.persist(paths,work);git(other,'pull','--ff-only');self.assertEqual((other/'other-blog.txt').read_text(),'keep me');self.assertTrue((other/paths[0]).exists());self.assertEqual(r.read(other/'artifacts/blog-run-reports/loxblog/latest.json')['run_id'],'125');self.assertEqual(git(work,'diff','--cached','--name-only'),'')
 def test_observer_workflow_has_no_provider_secrets_or_publish_command(self):
  w=(ROOT/'.github/workflows/blog-run-report.yml').read_text();self.assertNotIn('secrets.',w);self.assertNotIn('publish_',w);self.assertIn('head_repository.full_name == github.repository',w);self.assertIn('cancel-in-progress: false',w)
if __name__=='__main__':unittest.main()
