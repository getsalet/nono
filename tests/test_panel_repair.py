import copy, json, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'automation'))
import panel_repair as repair
P='pb-'+'a'*20; L='city-'+'b'*16
class RepairTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.root=Path(self.temp.name)
  self.control={'pause_image_production':False,'enabled_families':['tape20'],'held_families':{'hose':'held'},'cancelled_families':['hose']}
  self.write('data/blog-generated-image-control.json',self.control)
  self.write('state/parsiblog-progress.json',{'items':{P:{'status':'failed','reason':'Text SEO preflight rejected: language','at':'2026-10-28T00:00:00Z'}},'published':[]})
  self.write('data/parsiblog/title-matrix.json',{'approved':True,'items':[{'key':P,'family':'tape20'}]})
  self.write('state/loxblog-backlink-progress.json',{'published':[]})
  self.write('artifacts/loxblog-backlink-queue/submission-attempts.json',{L:{'phase':'unconfirmed'}})
  self.write('artifacts/loxblog-backlink-queue/items/'+L+'.json',{'key':L,'family':'tape20','qa':{'passed':True},'post':{'html':'<p>saved</p>'}})
 def write(self,path,obj):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj))
 def parsi(self): return repair.plan(self.root,'parsiblog',P)
 def blocked(self,code,fn):
  with self.assertRaisesRegex(repair.Blocked,'^'+code+'$'):fn()
 def test_supported_draft_repair(self): self.assertEqual(self.parsi()['operation'],'rewrite_and_validate_draft')
 def test_reconciliation_not_resubmission(self): self.assertEqual(repair.plan(self.root,'loxblog',L)['operation'],'verify_existing_and_recover_receipt')
 def test_unsupported_blog(self): self.blocked('unsupported_blog',lambda:repair.plan(self.root,'blogfa',P))
 def test_injection_rejected(self): self.blocked('invalid_target',lambda:repair.plan(self.root,'parsiblog',P+'; rm'))
 def test_paused(self):
  self.write('data/blog-generated-image-control.json',{**self.control,'pause_image_production':True});self.blocked('paused',self.parsi)
 def test_missing_pause_fails_closed(self):
  self.write('data/blog-generated-image-control.json',{});self.blocked('paused',self.parsi)
 def test_published(self):
  s=repair.load(self.root,'state/parsiblog-progress.json');s['published']=[{'key':P}];self.write('state/parsiblog-progress.json',s);self.blocked('already_published',self.parsi)
 def test_uncertain_native_write_blocks_rewrite(self):
  s=repair.load(self.root,'state/parsiblog-progress.json');s['items'][P]['native_phase']='request_pending';self.write('state/parsiblog-progress.json',s);self.blocked('not_pre_submit_failure',self.parsi)
 def test_unknown_reason_not_retry(self):
  s=repair.load(self.root,'state/parsiblog-progress.json');s['items'][P]['reason']='Timeout';self.write('state/parsiblog-progress.json',s);self.blocked('unsupported_failure',self.parsi)
 def test_held_family(self):
  self.write('data/parsiblog/title-matrix.json',{'approved':True,'items':[{'key':P,'family':'hose'}]});self.blocked('family_held',self.parsi)
 def test_approved_saved_body_not_rewritten(self):
  self.write('artifacts/parsiblog-backlink-queue/items/'+P+'.json',{'qa':{'passed':True}});self.blocked('saved_item_needs_review',self.parsi)
 def test_one_attempt_per_same_failure(self):
  request=self.parsi();self.write('artifacts/panel-repairs/parsiblog/'+P+'.json',request);self.blocked('same_failure_already_attempted',self.parsi)
 def test_verified_journal_not_reconciled(self):
  self.write('artifacts/loxblog-backlink-queue/submission-attempts.json',{L:{'phase':'verified'}});self.blocked('not_uncertain_submission',lambda:repair.plan(self.root,'loxblog',L))
 def test_unapproved_receipt_body(self):
  self.write('artifacts/loxblog-backlink-queue/items/'+L+'.json',{'key':L,'qa':{'passed':False}});self.blocked('approved_body_missing',lambda:repair.plan(self.root,'loxblog',L))
 def run_main(self,mode,confirm=''):
  env={'GITHUB_REF':'refs/heads/main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_RUN_ID':'123','REPAIR_BLOG':'parsiblog','REPAIR_TARGET':P,'REPAIR_MODE':mode,'REPAIR_CONFIRM':confirm}
  with patch.object(repair,'ROOT',self.root),patch.dict(os.environ,env),patch.object(repair,'perform',return_value='repaired_draft')as perform:
   with self.assertRaises(SystemExit)as ctx:repair.main()
  return ctx.exception.code,perform
 def test_inspect_is_read_only(self):
  code,perform=self.run_main('inspect');self.assertEqual(code,0);perform.assert_not_called();self.assertFalse((self.root/f'artifacts/panel-repairs/parsiblog/{P}.json').exists())
 def test_confirmation_required(self):
  code,perform=self.run_main('repair');self.assertEqual(code,1);perform.assert_not_called()
 def test_repair_calls_real_implementation(self):
  code,perform=self.run_main('repair','REPAIR');self.assertEqual(code,0);perform.assert_called_once();self.blocked('same_failure_already_attempted',self.parsi)
 def test_report_does_not_include_raw_exception(self):
  env={'GITHUB_REF':'refs/heads/main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_RUN_ID':'123','REPAIR_BLOG':'parsiblog','REPAIR_TARGET':P,'REPAIR_MODE':'repair','REPAIR_CONFIRM':'REPAIR'}
  with patch.object(repair,'ROOT',self.root),patch.dict(os.environ,env),patch.object(repair,'perform',side_effect=RuntimeError('secret credential')):
   with self.assertRaises(SystemExit):repair.main()
  self.assertNotIn('secret', (self.root/'artifacts/panel-repairs/parsiblog/latest.json').read_text())
if __name__=='__main__':unittest.main()

class ExecutionTests(RepairTests):
 def test_rewrite_uses_generate_only_and_restores_failure(self):
  import types
  previous=repair.load(self.root,'state/parsiblog-progress.json')['items'][P]
  fake=types.SimpleNamespace(RUN={'native_write_attempted':False},stamp=lambda:'now',run_report=lambda **kw:None,save=lambda path,obj:self.write(str(path.relative_to(self.root)),obj))
  def fail(args):
   self.assertEqual(args,['--mode','generate','--target',P,'--retry-pre-submit'])
   self.write('state/parsiblog-progress.json',{'items':{},'published':[]});raise RuntimeError('QA failed')
  fake.main=fail
  with patch.dict(sys.modules,{'parsiblog_pipeline':fake}):
   with self.assertRaises(RuntimeError):repair.perform(self.root,self.parsi())
  self.assertEqual(repair.load(self.root,'state/parsiblog-progress.json')['items'][P],previous)
 def test_rewrite_success_requires_full_approval(self):
  import types
  request=self.parsi()
  def generate(args):
   self.write('state/parsiblog-progress.json',{'items':{P:{'status':'ready'}},'published':[]})
   self.write('artifacts/parsiblog-backlink-queue/items/'+P+'.json',{'qa':{'passed':True},'editorial_review':{'passed':True}})
  fake=types.SimpleNamespace(main=generate,RUN={'native_write_attempted':False})
  with patch.dict(sys.modules,{'parsiblog_pipeline':fake}): self.assertEqual(repair.perform(self.root,request),'repaired_draft')
 def test_reconciliation_requires_persisted_recovered_receipt(self):
  import types
  request=repair.plan(self.root,'loxblog',L)
  fake=types.SimpleNamespace(recover=lambda blog:{'passed':True,'result':'verified_existing','new_submissions':0})
  with patch.dict(sys.modules,{'recover_existing_blog_receipt':fake}):
   self.blocked('receipt_missing',lambda:repair.perform(self.root,request))
   self.write('state/loxblog-backlink-progress.json',{'published':[{'key':L,'recovered_existing':True}]})
   self.assertEqual(repair.perform(self.root,request),'reconciled_receipt')
