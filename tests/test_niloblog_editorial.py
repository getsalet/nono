import copy,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as m
class EditorialTests(unittest.TestCase):
 def setUp(self):
  self.quote='این یک نقل دقیق و مستند درباره محصول شهرستان است'
  self.bundle={'local':{'text':self.quote},'article':{'text':self.quote+' متن فنی'},'technical':[],'links':[]}
  self.plan={'blocked':False,'facts':[{'source_index':0,'claim':'گزارش محصول','quote':self.quote},{'source_index':1,'claim':'اطلاعات محصول','quote':self.quote}]}
  self.approved={'approved':True,'grounded':True,'locally_distinct':True,'semantic_duplicate':False,'unsupported_claims':[],'local_evidence_quote':self.quote}
 def test_evidence_quotes_checked_against_exact_source(self):
  self.assertEqual(m.verify_evidence_plan(self.plan,self.bundle),self.plan)
  for field,value in [('quote','یک نقل ساختگی که در هیچ کدام از منابع وجود ندارد'),('source_index',9),('source_index',True)]:
   bad=copy.deepcopy(self.plan);bad['facts'][0][field]=value
   with self.assertRaises(m.PipelineStop):m.verify_evidence_plan(bad,self.bundle)
 def test_local_fact_and_sufficient_evidence_required(self):
  for plan in [{'blocked':True},{'facts':[]},{'facts':[dict(f,source_index=1) for f in self.plan['facts']]}]:
   with self.assertRaises(m.PipelineStop):m.verify_evidence_plan(plan,self.bundle)
 def test_review_never_relaxes_any_gate(self):
  self.assertTrue(m.review_passes(self.approved,self.bundle))
  for key,value in [('approved',False),('grounded',False),('locally_distinct',False),('semantic_duplicate',True),('unsupported_claims',['ادعای بی منبع']),('local_evidence_quote','نقل ساختگی')]:
   bad=dict(self.approved,**{key:value});self.assertFalse(m.review_passes(bad,self.bundle))
 def test_held_retry_is_bounded_and_revision_gated(self):
  row={'id':'test','angle_ref':'angle','review_state':'editorial_review_required'}
  hold={'test':{'reason':'Independent editorial review rejected','pipeline_revision':12,'attempts':1}}
  self.assertTrue(m.candidate_allowed(row,hold,set(),13));self.assertFalse(m.candidate_allowed(row,hold,set(),12))
  self.assertFalse(m.candidate_allowed(row,hold,{'angle'},13))
  hold['test']['attempts']=2;self.assertFalse(m.candidate_allowed(row,hold,set(),14))
 def run_generation(self,second_review=None,repair_blocked=False):
  row={'id':'test','title':'عنوان','angle_ref':'angle'}
  article={'title':'عنوان','html':'<p>متن اولیه</p>'};fixed={'title':'عنوان','html':'<p>متن اصلاح شده</p>'}
  rejected=dict(self.approved,approved=False,unsupported_claims=['ادعای حذف شدنی'],reason='حذف ادعا')
  outputs=[self.plan,article,rejected,{'blocked':True} if repair_blocked else fixed]
  if not repair_blocked:outputs.append(second_review or self.approved)
  with tempfile.TemporaryDirectory() as tmp,mock.patch.object(m,'A',Path(tmp)),mock.patch.object(m,'source_bundle',return_value=self.bundle),mock.patch.object(m,'all_history',return_value=[]),mock.patch.object(m,'validate_article',return_value=600) as validate,mock.patch('roya_backlink_queue.agnes',side_effect=outputs) as ai,mock.patch.object(m,'reserve',return_value=({}, {'image_id':'img','video_id':None})) as reserve,mock.patch.object(m,'checkpoint'):
   args=(row,{'angles':{'angle':{}}},{},{'assets':[{'id':'img','url':'https://x/a.webp','alt':'محصول','width':100,'height':100}]},{})
   if repair_blocked or (second_review and not m.review_passes(second_review,self.bundle)):
    with self.assertRaises(m.PipelineStop):m.generate(*args)
    reserve.assert_not_called()
   else:
    result=m.generate(*args);self.assertIn('متن اصلاح شده',result['post']['html']);self.assertEqual(result['selection']['video_id'],None)
    self.assertEqual(validate.call_count,2)
   self.assertEqual(ai.call_count,4 if repair_blocked else 5)
   self.assertIn('editorial_feedback',ai.call_args_list[3].args[0])
 def test_rejected_article_repaired_then_independently_reviewed(self):self.run_generation()
 def test_second_rejection_never_reserves_or_publishes(self):self.run_generation(dict(self.approved,approved=False))
 def test_insufficient_evidence_after_repair_stays_held(self):self.run_generation(repair_blocked=True)
if __name__=='__main__':unittest.main()
