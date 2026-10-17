"""Retry only the known visible-domain instruction conflict, once, with full QA."""
import copy,datetime,inspect,json,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import roya_backlink_queue as roya
import build_roya_queue as build
class RoyaDomainRepairTests(unittest.TestCase):
 def setUp(self):
  self.item={'key':'domain/test','province':'test','status':'failed','family':'tape20','failure_stage':'text_validation','generated_at':'2026-10-17T22:00:00Z'}
  self.post={'title':'نوار تیپ پیاز','slug':'onion-irrigation','html':'<p>بررسی مشخصات در سایت navar-abyari.ir انجام شود.</p>'}
  self.record={**self.item,'post':self.post,'qa':{'passed':False,'errors':['unexpected latin words: abyari, ir']}}
 def test_exact_domain_conflict_recovers_actual_article_without_mutation(self):
  before=copy.deepcopy(self.record);post=roya.domain_repair_draft(self.record,self.item)
  self.assertEqual(post,self.post);self.assertEqual(self.record,before);self.assertIsNot(post,self.post)
 def test_only_one_policy_retry(self):
  for target in ('item','record'):
   item=copy.deepcopy(self.item);record=copy.deepcopy(self.record)
   (item if target=='item'else record)['text_policy_retry']=roya.DOMAIN_REPAIR_POLICY
   self.assertIsNone(roya.domain_repair_draft(record,item))
 def test_other_failures_and_mixed_errors_never_auto_repaired(self):
  for errors in (['unexpected latin words: other'],['Product image rejected: geometry'],['unexpected latin words: abyari','numeric price claim'],[]):
   record={**self.record,'qa':{'errors':errors}};self.assertIsNone(roya.domain_repair_draft(record,self.item))
 def test_published_stale_or_wrong_identity_stay_closed(self):
  for fields in ({'published':True},{'pid':'123'},{'published_url':'https://example.test/p'},{'key':'other'},{'generated_at':'old'},{'status':'completed'}):
   self.assertIsNone(roya.domain_repair_draft({**self.record,**fields},self.item))
 def test_future_or_bad_timer_not_bypassed(self):
  for timer in ('2099-01-01T00:00:00Z','bad',True,'2026-01-01T00:00:00'):
   self.assertIsNone(roya.domain_repair_draft(self.record,{**self.item,'next_retry_at':timer}))
 def test_visible_domain_evidence_required_not_href_only(self):
  record=copy.deepcopy(self.record);record['post']['html']='<p><a href="https://navar-abyari.ir/">وب‌سایت AFP</a></p>'
  self.assertIsNone(roya.domain_repair_draft(record,self.item))
 def test_domain_split_across_inline_tags_is_still_recognized(self):
  record=copy.deepcopy(self.record);record['post']['html']='<p>سایت <em>navar</em>-abyari</p>';record['qa']['errors']=['unexpected latin words: abyari']
  self.assertIsNotNone(roya.domain_repair_draft(record,self.item))
 def test_pick_includes_due_matching_case_only(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);roya.save_json(root/'domain_test.json',self.record)
   with patch.multiple(roya,ROOT=root,ITEMS=root,RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=True):
    self.assertEqual([x['key']for x in roya.pick({'items':[self.item]},{},1)],[self.item['key']])
 def test_policy_marker_persists_and_real_qa_is_not_weakened(self):
  self.assertIn('text_policy_retry',build.RUNTIME_FIELDS)
  self.assertIn("test_roya_domain_repair.py' -v",(ROOT/'.github/workflows/roya-backlink-queue.yml').read_text())
  self.assertNotIn('abyari',roya.LATIN_OK);self.assertNotIn('ir',roya.LATIN_OK)
  source=inspect.getsource(roya.main);self.assertIn("item['text_policy_retry']=DOMAIN_REPAIR_POLICY",source)
  self.assertIn('errors, info = qa(item, obj, links)',source)
  prompt=inspect.getsource(roya.build_prompt);self.assertIn('نام دامنه یا نشانی لاتین را در متن قابل‌نمایش ننویس',prompt)
if __name__=='__main__':unittest.main()
