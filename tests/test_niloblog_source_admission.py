import copy,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
class AdmissionTests(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':str(i),'angle_ref':'a'+str(i%2),'locality_ref':str(i),'title':'پرسش','link_plan_ref':'p'}for i in range(3)]
  self.m={'titles':self.rows,'angles':{'a0':{'cluster':'x','brief':'پرسش اول'},'a1':{'cluster':'x','brief':'پرسش دوم'}},'link_plans':{'p':{'required_links':[{'target_ref':'t'}],'research_only_target_refs':[]}}}
  self.targets={'t':{'kind':'article','family':'tape20','target_url':'https://navar-abyari.ir/guide/'}}
  self.source={'url':self.targets['t']['target_url'],'text':'این نقل دقیق از راهنمای فنی درباره روش اجرا است و فقط شاهد روش عمومی است.','sha256':'digest','checked_at':'today'}
  self.choice={'id':'1','technical_evidence':[{'source_ref':'t','quote':self.source['text']}]}
 def run_case(self,choices):
  before=copy.deepcopy(self.rows)
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'fetch',return_value=self.source)as fetch,patch('roya_backlink_queue.agnes',return_value={'candidates':choices})as ai,patch.object(n,'login')as login,patch.object(n,'checkpoint')as checkpoint:
   result=n.evidence_first_candidates(self.rows,self.m,{},self.targets)
   fetch.assert_called_once();self.assertEqual(len(__import__('json').loads(ai.call_args.args[0].split('\n',1)[1])['questions']),2)
   login.assert_not_called();checkpoint.assert_not_called();self.assertEqual(before,self.rows)
   return result
 def test_selects_existing_question_only_not_matrix_order(self):self.assertEqual(self.run_case([self.choice]),[self.rows[1]])
 def test_zero_coverage_stops_without_fallback(self):self.assertEqual(self.run_case([]),[])
 def test_fabricated_quote_or_unknown_target_fails_closed(self):
  for change in [{'source_ref':'unknown','quote':self.source['text']},{'source_ref':'t','quote':'نقل ساختگی و غیرموجود در متن راهنمای فنی اصلی است'}]:
   choice=copy.deepcopy(self.choice);choice['technical_evidence']=[change]
   with self.assertRaisesRegex(n.PipelineStop,'Invalid source admission'):self.run_case([choice])
 def test_duplicate_or_new_candidate_fails_closed(self):
  for choices in [[self.choice,self.choice],[dict(self.choice,id='invented')]]:
   with self.assertRaisesRegex(n.PipelineStop,'Invalid source admission'):self.run_case(choices)
 def test_no_source_admission_is_publication_approval(self):
  self.assertFalse(n.failure_policy(n.PipelineStop('Invalid source admission'))['continue_candidates'])
if __name__=='__main__':unittest.main()
