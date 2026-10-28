import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from niloblog_titles import instructional_title,migrate_pending_titles
import niloblog_pipeline as n
class InstructionalTitleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.matrix=json.loads((n.D/'title-matrix.json').read_text())
 def test_all_titles_fit_cap_with_explicit_guidance_and_county_scope(self):
  for row in self.matrix['titles']:
   title=instructional_title(row,self.matrix);loc=self.matrix['localities'][row['locality_ref']]
   self.assertTrue(title.startswith('راهنمای '));self.assertLessEqual(len(title),78);self.assertIn(loc['crop'],title);self.assertIn(loc['place_label'],title)
 def test_new_template_preserves_unique_topics(self):
  self.assertEqual(len({instructional_title(r,self.matrix)for r in self.matrix['titles']}),1000)
 def test_protected_titles_and_all_other_row_fields_are_unchanged(self):
  matrix=copy.deepcopy(self.matrix)
  for row in matrix['titles']:row['title']='عنوان قدیمی '+row['id'];row.pop('title_policy_version',None)
  ids=[r['id']for r in matrix['titles'][:5]]
  state={'published':[{'key':ids[0]}],'held':{ids[1]:{}},'current':ids[2],'intent':{'key':ids[3]}}
  before=copy.deepcopy(state);out,report=migrate_pending_titles(matrix,state,[ids[4]])
  self.assertEqual(state,before);self.assertEqual(out['titles'][:5],matrix['titles'][:5]);self.assertFalse(out['publication_enabled'])
  for old,new in zip(matrix['titles'][5:],out['titles'][5:]):
   for key in ['id','angle_ref','locality_ref','review_state','link_plan_ref']:self.assertEqual(new[key],old[key])
 def test_migration_is_idempotent(self):
  a,_=migrate_pending_titles(self.matrix,{});b,r=migrate_pending_titles(a,{})
  self.assertEqual(a,b);self.assertEqual(r['changed_count'],0)
 def test_title_cap_does_not_silently_truncate_claims(self):
  m=copy.deepcopy(self.matrix);r=m['titles'][0];m['angles'][r['angle_ref']]['seo_short_label']='متن بلند '*30
  with self.assertRaises(ValueError):instructional_title(r,m)
 def test_instructional_policy_does_not_remove_final_review(self):
  scope=n.topic_scope({'title':'راهنمای ثبت وضعیت اولیه نوار تیپ','title_policy_version':2},{'brief':'ثبت وضعیت اولیه'})
  self.assertEqual(scope['mode'],'conditional_instruction');self.assertTrue(scope['distinct_usefulness_still_required']);self.assertTrue(scope['do_not_assume_local_installation_or_fault'])
if __name__=='__main__':unittest.main()
