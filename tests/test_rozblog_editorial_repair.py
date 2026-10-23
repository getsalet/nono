import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from repair_rozblog_editorial import corrected,structure,digest
class ExistingPostRepairTests(unittest.TestCase):
 def setUp(self):
  self.plan=json.loads((ROOT/'data/rozblog-editorial-repair-plan.json').read_text())
  self.body='<p><img src="https://navar-abyari.ir/a.jpg" alt="تصویر"></p><a href="https://navar-abyari.ir/">نوار تیپ</a>'+''.join('<p>'+x['old']+'</p>'for x in self.plan['replacements'])+'<p>'+('متن فارسی آموزشی ' * 160)+'</p>'+('<details><summary>پرسش</summary><p>پاسخ</p></details>'*3)
 def test_exact_plan_repair(self):
  new=corrected({'mtex':self.body,'mtex2':''},self.plan)['mtex']
  self.assertNotIn('۱٫۵',new);self.assertNotIn('首先',new);self.assertEqual(structure(new),structure(self.body));self.assertNotEqual(digest(new),digest(self.body))
 def test_both_native_sections_preserved(self):
  split=self.body.index('<p>نکات طراحی')
  new=corrected({'mtex':self.body[:split],'mtex2':self.body[split:]},self.plan)
  self.assertTrue(new['mtex2']);self.assertEqual(structure(''.join(new.values())),structure(self.body))
 def test_unknown_or_missing_source_refuses_edit(self):
  for body in [self.body.replace('首先','نخست'),self.body+self.body]:
   with self.assertRaises(RuntimeError):corrected({'mtex':body,'mtex2':''},self.plan)
 def test_creation_policy_cannot_be_enabled(self):
  plan=copy.deepcopy(self.plan);plan['post_creations_allowed']=1
  with self.assertRaises(RuntimeError):corrected({'mtex':self.body,'mtex2':''},plan)
 def test_html_in_replacement_is_rejected(self):
  plan=copy.deepcopy(self.plan);plan['replacements'][0]['new']='<a href="https://example.com">تبلیغ</a>'
  with self.assertRaises(RuntimeError):corrected({'mtex':self.body,'mtex2':''},plan)
 def test_links_are_invariant(self):
  plan=copy.deepcopy(self.plan);plan['replacements'].append({'old':'href="https://navar-abyari.ir/"','new':'href="https://example.com/"'})
  with self.assertRaises(RuntimeError):corrected({'mtex':self.body,'mtex2':''},plan)
 def test_native_serialization_does_not_allow_fuzzy_or_unrelated_edits(self):
  source=(ROOT/'automation/repair_rozblog_editorial.py').read_text()
  self.assertIn("verify_body(''.join(before.values()),item['post']['html'])",source)
  self.assertIn('Unexpected nonempty continuation',source)
  self.assertIn("after={'mtex':expected_html,'mtex2':before['mtex2']}",source)
 def test_checkpoint_configures_identity_before_rebase(self):
  import inspect
  from repair_rozblog_editorial import checkpoint
  source=inspect.getsource(checkpoint)
  self.assertLess(source.index("'config','user.name'"),source.index("'pull','--rebase'"))
  self.assertLess(source.index("'config','user.email'"),source.index("'pull','--rebase'"))
 def test_workflow_has_same_native_lock_and_no_generation(self):
  s=(ROOT/'.github/workflows/rozblog-editorial-repair.yml').read_text()
  self.assertIn('group: rozblog-content-pipeline',s);self.assertNotIn('AGNES_API_KEY',s)
if __name__=='__main__':unittest.main()
