import copy,datetime,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blogsky_recovery as recovery
import blogsky_native as native
import publish_blogsky_posts as publisher

class RecoveryTests(unittest.TestCase):
 def test_exact_fresh_run_scoped_permit_only(self):
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'GITHUB_ACTIONS':'true','GITHUB_RUN_ID':'123'}):
   root=Path(d);key='city-66afad426708678b';path=root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json';path.parent.mkdir(parents=True)
   journal={'key':key,'phase':'submitting','submittedAt':'old','bodySha256':'fixed'};path.write_text(json.dumps(journal))
   p=recovery.AbsencePermit(key,recovery.fingerprint(journal),'123',publisher.now(),{})
   with self.assertRaises(RuntimeError):publisher.pending(root)
   publisher.pending(root,p)
   for bad in [recovery.AbsencePermit(key,'wrong','123',publisher.now(),{}),recovery.AbsencePermit(key,p.prior_digest,'other',publisher.now(),{}),recovery.AbsencePermit(key,p.prior_digest,'123',(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(minutes=6)).isoformat(),{})]:
    with self.assertRaises(RuntimeError):publisher.pending(root,bad)
   path.write_text(json.dumps({**journal,'submittedAt':'new'}))
   with self.assertRaises(RuntimeError):publisher.pending(root,p)
 def test_other_unresolved_journal_still_blocks(self):
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'GITHUB_ACTIONS':'true','GITHUB_RUN_ID':'123'}):
   root=Path(d);key='city-66afad426708678b';folder=root/'artifacts/blogsky-backlink-queue/native-publications';folder.mkdir(parents=True)
   j={'key':key,'phase':'submitting'};(folder/(key+'.json')).write_text(json.dumps(j));(folder/'other.json').write_text('{"phase":"submitting"}')
   p=recovery.AbsencePermit(key,recovery.fingerprint(j),'123',publisher.now(),{})
   with self.assertRaises(RuntimeError):publisher.pending(root,p)
 def test_disabled_or_consumed_recovery_never_opens_browser(self):
  with tempfile.TemporaryDirectory() as d,patch.object(publisher,'gate'):
   context=Mock()
   with self.assertRaises(RuntimeError):recovery.authorize(context,'city-66afad426708678b',Path(d))
   context.new_page.assert_not_called()
 def test_invalid_form_fails_before_any_click(self):
  page=Mock();page.evaluate.return_value={'valid':False,'errorFields':['post-title']}
  with self.assertRaises(RuntimeError):native.validate_form(page)
  page.locator.assert_not_called()
 def test_valid_form_allowed_without_click(self):
  page=Mock();page.evaluate.return_value={'valid':True,'errorFields':[]};self.assertTrue(native.validate_form(page)['valid']);page.locator.assert_not_called()
 def test_capture_waits_for_actual_editor_before_filling(self):
  page=Mock()
  with patch.object(native,'assert_editor'):native.fill(page,{'title':'t','tags':[],'slug':'s'},'<p>body</p>')
  capture=page.evaluate.call_args_list[0].args[0]
  self.assertNotIn('old.call(this)',capture)
  page.wait_for_function.assert_called_once();self.assertIn('afpNativeEditor._doc?.body',page.wait_for_function.call_args.args[0])
 def test_validation_precedes_journal_and_click(self):
  import inspect
  source=inspect.getsource(publisher.run)
  self.assertLess(source.index('native.validate_form(page)'),source.index("journal={'key'"))
  self.assertLess(source.index('durable_automatic_intent'),source.index("page.locator('#publish').click()"))
if __name__=='__main__':unittest.main()
