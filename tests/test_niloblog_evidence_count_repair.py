import copy,sys,unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as m
class CountRepairTests(unittest.TestCase):
 def setUp(self):
  quote='این یک نقل قول واقعی و قابل بررسی از منبع معتبر است'
  self.bundle={'local':{'text':quote},'article':{'text':quote}}
  self.catalog=[{'excerpt_id':f's{i}-e0','source_index':i,'scope':'local_report'if i==0 else'technical_general','quote':quote}for i in range(2)]
  self.facts=[{'excerpt_id':f's{i%2}-e0','claim':'ادعای محدود '+str(i)}for i in range(16)]
  self.raw={'blocked':False,'facts':self.facts};self.fixed={'blocked':False,'facts':self.facts[:4]}
 def test_overlong_valid_plan_gets_one_count_repair(self):
  repair=Mock(return_value=self.fixed);old=copy.deepcopy(self.raw);plan=m.bounded_evidence_plan(self.raw,self.catalog,self.bundle,repair)
  self.assertEqual(len(plan['facts']),4);repair.assert_called_once();self.assertEqual(self.raw,old)
  self.assertEqual(repair.call_args.args[0]['actual_fact_count'],16)
 def test_valid_plan_never_calls_model(self):
  repair=Mock();m.bounded_evidence_plan(self.fixed,self.catalog,self.bundle,repair);repair.assert_not_called()
 def test_second_overlong_response_stays_rejected_without_loop(self):
  repair=Mock(return_value=self.raw)
  with self.assertRaises(m.PipelineStop):m.bounded_evidence_plan(self.raw,self.catalog,self.bundle,repair)
  repair.assert_called_once()
 def test_invalid_ids_or_missing_claims_are_not_count_repaired(self):
  for fields in ({'excerpt_id':'made-up'},{'claim':''}):
   raw=copy.deepcopy(self.raw);raw['facts'][-1].update(fields);repair=Mock()
   with self.assertRaises(m.PipelineStop):m.bounded_evidence_plan(raw,self.catalog,self.bundle,repair)
   repair.assert_not_called()
 def test_repair_cannot_introduce_claim_or_change_excerpt(self):
  for fields in ({'claim':'ادعای تازه'},{'excerpt_id':'s1-e0','claim':self.facts[0]['claim']}):
   fixed=copy.deepcopy(self.fixed);fixed['facts'][0].update(fields)
   with self.assertRaises(m.PipelineStop):m.bounded_evidence_plan(self.raw,self.catalog,self.bundle,Mock(return_value=fixed))
 def test_blocked_empty_and_unbounded_lists_are_not_repaired(self):
  for raw in (None,{'blocked':True,'facts':self.facts},{'facts':[]},{'facts':self.facts*2}):
   repair=Mock()
   with self.assertRaises(m.PipelineStop):m.bounded_evidence_plan(raw,self.catalog,self.bundle,repair)
   repair.assert_not_called()
 def test_held_count_retry_is_revision_gated_and_at_most_once(self):
  row={'id':'n','angle_ref':'a','review_state':'editorial_review_required'};held={'n':{'reason':'Evidence plan requires bounded sourced facts','pipeline_revision':20,'attempts':1}}
  self.assertTrue(m.candidate_allowed(row,held,set(),21));self.assertFalse(m.candidate_allowed(row,held,set(),20))
  held['n']['attempts']=2;self.assertFalse(m.candidate_allowed(row,held,set(),22))
