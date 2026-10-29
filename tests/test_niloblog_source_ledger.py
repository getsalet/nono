import copy,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
class SourceLedgerTests(unittest.TestCase):
 def setUp(self):
  self.row={'title':'راهنمای نشتی اتصال؛ محصول در شهرستان','angle_ref':'a'}
  self.matrix={'angles':{'a':{'brief':'پس از تعمیر چه کنترل هایی انجام دهیم؟','cluster':'نشتی و آسیب'}}}
  self.bundle={'local':{'text':'گزارش کشت گوجه فرنگی در شهرستان اسدآباد با تاریخ مشخص و منبع معتبر منتشر شده است. ' * 100},'article':{'text':'راهنمای عمومی بررسی و تعمیر نشتی اتصال بدون ادعای اجرای محلی است. '*100},'technical':[{'text':'روش عمومی نگهداری نوار و کنترل فشار مطابق دستور سازنده و بدون نسخه اختصاصی مزرعه است. '*100},{'text':'پس از تعمیر اتصال، کنترل نشتی مطابق دستور فنی انجام شود و نتیجه مستند شود. '*100}],'locality':{'city_fa':'اسدآباد','crop':'گوجه فرنگی'}}
 def test_instructional_title_does_not_need_local_fault_for_extraction(self):
  with patch('roya_backlink_queue.agnes')as model:
   plan=n.source_evidence_plan(self.row,self.matrix,n.evidence_catalog(self.bundle),self.bundle)
   model.assert_not_called()
  self.assertEqual(len(plan['facts']),11)
  self.assertFalse(plan['article_sufficiency_verified']);self.assertFalse(plan['publication_authorized'])
 def test_every_claim_and_quote_is_verbatim_and_provenance_bound(self):
  catalog=n.evidence_catalog(self.bundle);before=copy.deepcopy(catalog)
  plan=n.source_evidence_plan(self.row,self.matrix,catalog,self.bundle)
  lookup={e['excerpt_id']:e for e in catalog}
  for fact in plan['facts']:
   self.assertEqual(fact['claim'],fact['quote']);self.assertEqual(fact['quote'],lookup[fact['excerpt_id']]['quote']);self.assertEqual(fact['source_index'],lookup[fact['excerpt_id']]['source_index'])
  self.assertEqual(catalog,before);self.assertEqual({f['source_index']for f in plan['facts']},{0,1,2,3})
 def test_no_local_or_technical_evidence_fails_closed(self):
  for index in (0,1):
   bundle=copy.deepcopy(self.bundle);bundle['technical']=[]
   bundle['local'if index==0 else'article']['text']=''
   with self.assertRaises(n.PipelineStop):n.source_evidence_plan(self.row,self.matrix,n.evidence_catalog(bundle),bundle)
 def test_deterministic_ledger_does_not_approve_factual_event(self):
  row=dict(self.row,title='گزارش خرابی در مزرعه')
  plan=n.source_evidence_plan(row,self.matrix,n.evidence_catalog(self.bundle),self.bundle)
  self.assertFalse(plan['publication_authorized']);self.assertEqual(n.topic_scope(row,self.matrix['angles']['a'])['mode'],'factual_report')
  with self.assertRaisesRegex(n.PipelineStop,'Topic brief rejected'):n.validate_brief({'eligible':False,'grounded':False,'locally_distinct':False,'semantic_duplicate':False},plan)
 def test_echoed_input_is_invalid_not_editorial_rejection(self):
  with self.assertRaisesRegex(n.PipelineStop,'Topic brief invalid'):n.validate_brief({'title':self.row['title'],'contract':{}},{'facts':[]})
if __name__=='__main__':unittest.main()
