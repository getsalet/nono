import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
class AdmissionTests(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':str(i),'angle_ref':'a'+str(i%2),'locality_ref':str(i),'title':'پرسش','link_plan_ref':'p'}for i in range(3)]
  self.m={'titles':self.rows,'angles':{'a0':{'cluster':'x','brief':'نمونه برداری آزمایشگاهی شوری چگونه است؟'},'a1':{'cluster':'x','brief':'مانومتر فشارسنج فشار چگونه متصل شود؟'}},'link_plans':{'p':{'required_links':[{'target_ref':'t'}],'research_only_target_refs':[]}}}
  self.targets={'t':{'kind':'article','family':'tape20','target_url':'https://navar-abyari.ir/guide/'}}
  self.source={'url':self.targets['t']['target_url'],'text':'مانومتر فشارسنج فشار به اتصال متصل شود و فقط شاهد روش عمومی است.','sha256':'digest','checked_at':'today'}
 def run_case(self,history=None,source=None):
  before=copy.deepcopy(self.rows)
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'fetch',return_value=source or self.source)as fetch,patch.object(n,'all_history',return_value=history or []),patch('roya_backlink_queue.agnes')as model,patch.object(n,'login')as login,patch.object(n,'checkpoint')as checkpoint:
   result=n.evidence_first_candidates(self.rows,self.m,{},self.targets)
   fetch.assert_called_once();model.assert_not_called();login.assert_not_called();checkpoint.assert_not_called();self.assertEqual(before,self.rows)
   report=n.read(Path(tmp)/'selection/report.json');self.assertFalse(report['publication_authorized']);self.assertTrue(report['coverage_is_not_answerability_or_approval'])
   return result,report
 def test_selects_existing_question_by_source_coverage_not_row_order(self):self.assertEqual(self.run_case()[0],[self.rows[1]])
 def test_zero_coverage_stops_without_random_fallback(self):
  source=dict(self.source,text='متن نامرتبط درباره محصول دیگری است')
  self.assertEqual(self.run_case(source=source)[0],[])
 def test_prior_content_is_penalty_not_evidence_or_approval(self):
  _,before=self.run_case();_,after=self.run_case([{'html':'<p>مانومتر فشارسنج فشار</p>'}])
  self.assertLess(after['selected'][0]['priority'],before['selected'][0]['priority'])
 def test_source_provenance_is_recorded(self):
  _,report=self.run_case();self.assertEqual(report['source_checks']['t']['sha256'],'digest')
 def test_unapproved_source_fails_closed(self):
  self.targets['t']['target_url']='https://example.org/fake'
  with self.assertRaisesRegex(n.PipelineStop,'Unapproved research source'):self.run_case()
 def test_only_one_locality_variant_per_angle_is_selected(self):
  source=dict(self.source,text=self.source['text']+' نمونه برداری آزمایشگاهی شوری')
  result,_=self.run_case(source=source);self.assertEqual(len(result),2);self.assertEqual(len({r['angle_ref']for r in result}),2)
if __name__=='__main__':unittest.main()
