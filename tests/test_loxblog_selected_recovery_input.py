import contextlib,io,json,os,sys,textwrap,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import recover_existing_blog_receipt as recovery
class SelectedLoxRecoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.workflow=(ROOT/'.github/workflows/loxblog-selected-receipt-recovery.yml').read_text()
  cls.step=cls.workflow.split('      - name: Read existing article, verify and recover receipt without submission\n',1)[1].split('      - name:',1)[0]
  cls.code=textwrap.dedent(cls.step.split("          python - <<'PY'\n",1)[1].split('          PY',1)[0])
 def run_code(self,key,journal):
  old=dict(recovery.TARGETS)
  try:
   with patch.dict(os.environ,{'RECOVERY_TARGET':key}),patch.object(Path,'read_text',return_value=json.dumps(journal)),patch.object(recovery,'recover',return_value={'passed':True})as recover,contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(SystemExit)as error:exec(compile(self.code,'workflow','exec'),{})
    return error.exception.code,recover.call_count
  finally:recovery.TARGETS=old
 def test_named_uncertain_target_reaches_existing_only_recovery(self):
  for phase in ['submitting','unconfirmed','reconciled_absent','verified']:
   with self.subTest(phase=phase):self.assertEqual(self.run_code('city-11a278cd4336d1e7',{'city-11a278cd4336d1e7':{'phase':phase}}),(0,1))
 def test_unknown_or_never_submitted_target_is_rejected(self):
  self.assertEqual(self.run_code('city-11a278cd4336d1e7',{})[1],0)
  self.assertEqual(self.run_code('city-11a278cd4336d1e7',{'city-11a278cd4336d1e7':{'phase':'ready'}})[1],0)
 def test_path_and_code_injection_rejected(self):
  for key in ['../state/x','city-11a278cd4336d1e7;echo x','',"';raise SystemExit(0)#"]:
   with self.subTest(key=key):self.assertEqual(self.run_code(key,{})[1],0)
 def test_input_transported_as_environment_not_shell_code(self):
  self.assertIn('  workflow_dispatch:\n    inputs:\n      target:',self.workflow);self.assertIn('RECOVERY_TARGET: ${{ inputs.target',self.step);self.assertNotIn('${{',self.code)
 def test_core_recovery_has_no_new_submission_path(self):
  s=(ROOT/'automation/recover_existing_blog_receipt.py').read_text()
  for forbidden in ['save_post(','.click(','.submit(','.begin(','.agnes(']:self.assertNotIn(forbidden,s)
if __name__=='__main__':unittest.main()
