import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import research,cycle
from automation.agri_v2.queue import atomic_json,load_json,utcnow

TOPIC={'id':'agri-123456789abc','title':'نشانه‌های رسیدگی لوبیا','crop':'لوبیا','intent':'maturity','priority':'P1','origin':'NEW','overlap_review_required':False,'related_existing_ids':[]}
QUOTE='Harvest mature beans before pods begin to shatter in the field or the pods will split open, spilling beans onto the ground.'
CLAIM='پیش از بازشدن غلاف و ریختن دانه باید وضعیت رسیدگی محصول در مزرعه بررسی شود.'
COND='محدود به لوبیای خشک در شرایط منبع؛ تاریخ تقویمی یا نسخه عددی برای ایران تعیین نشده است.'
def fixtures():
 docs=[{'url':'https://extension.msu.edu/beans','text':'Intro '+QUOTE+' end','fetched_at':utcnow(),'sha256':'a'*64},{'url':'https://extension.iastate.edu/beans','text':'Intro '+QUOTE+' end','fetched_at':utcnow(),'sha256':'b'*64}]
 candidate={'topic_id':TOPIC['id'],'slug':'bean-maturity-check','answers_intent':True,'local_or_numeric_prescription_required':False,'outline':['رسیدگی','پایش','بازار'],'facts':[{'claim':CLAIM,'conditions':COND,'source_url':docs[i%2]['url'],'evidence_quote':QUOTE} for i in range(4)]}
 review={'grounded':True,'all_claims_supported':True,'crop_and_intent_match':True,'safe_qualitative':True,'overlap_decision':'distinct','novelty_reason':'این بررسی درباره نشانه رسیدگی است و با موضوع عملکرد در هکتار یکی نیست.','source_scope_limitations':'این منابع خارجی هستند و تقویم یا دستور محلی برای تمام مناطق ایران ارائه نمی‌کنند.'}
 inventory={'source_generated_at':utcnow(),'scope':'all published titles','records':[{'id':1,'title':'موضوع دیگر','url':'https://navar-abyari.ir/other/','status':'publish'}]}
 return docs,candidate,review,inventory
class ResearchTests(unittest.TestCase):
 def test_verified_quotes_build_explicit_ai_not_human_brief(self):
  d,c,r,i=fixtures();b=research.build_brief(TOPIC,d,c,r,i)
  self.assertTrue(b['publish_authorized']);self.assertFalse(b['human_agronomy_review_done']);self.assertIsNone(b['agronomy_reviewer']);self.assertEqual(b['review_mode'],research.MODE)
 def test_invented_quote_rejected(self):
  d,c,r,i=fixtures();c['facts'][0]['evidence_quote']='fabricated quote '*12
  with self.assertRaisesRegex(research.ResearchBlocked,'quote_not'):research.validate_evidence(TOPIC,c,d)
 def test_numeric_recommendation_rejected(self):
  d,c,r,i=fixtures();c['facts'][0]['claim']+=' ۲۰ درصد'
  with self.assertRaisesRegex(research.ResearchBlocked,'numeric'):research.validate_evidence(TOPIC,c,d)
 def test_independent_review_must_accept_all_claims(self):
  d,c,r,i=fixtures();r['all_claims_supported']=False
  with self.assertRaisesRegex(research.ResearchBlocked,'independent'):research.build_brief(TOPIC,d,c,r,i)
 def test_uncertain_overlap_is_not_permission(self):
  d,c,r,i=fixtures();r['overlap_decision']='uncertain'
  with self.assertRaises(research.ResearchBlocked):research.build_brief(TOPIC,d,c,r,i)
 def test_same_institution_twice_is_not_independent(self):
  d,c,r,i=fixtures();d[1]['url']='https://www.extension.msu.edu/beans';c['facts'][1]['source_url']=d[1]['url'];c['facts'][3]['source_url']=d[1]['url']
  with self.assertRaisesRegex(research.ResearchBlocked,'independent'):research.validate_evidence(TOPIC,c,d)
 def test_conflicting_slug_blocks(self):
  d,c,r,i=fixtures();i['records'][0]['url']='https://navar-abyari.ir/bean-maturity-check/'
  with self.assertRaisesRegex(research.ResearchBlocked,'existing'):research.build_brief(TOPIC,d,c,r,i)
 def test_source_host_allowlist_and_credentials(self):
  for url in ['http://extension.msu.edu/x','https://fake.edu.evil.org/x','https://user:pass@extension.msu.edu/x','https://extension.msu.edu:444/x','https://localhost/x']:
   with self.assertRaises(research.ResearchBlocked):research.source_host(url)
 def test_private_address_rejected_before_open(self):
  with patch.object(research.socket,'getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]),patch.object(research.urllib.request,'build_opener') as op:
   with self.assertRaisesRegex(research.ResearchBlocked,'non_public'):research.fetch_source('https://extension.msu.edu/x')
   op.assert_not_called()
 def test_feeder_persists_evidence_and_one_brief(self):
  d,c,r,i=fixtures()
  class Client:
   def __init__(self,*a,**k):self.answers=iter([{'urls':[x['url'] for x in d]},c,r])
   def text(self,p):return next(self.answers)
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'config.json',{'research_feeder':{'enabled':True}});atomic_json(data/'health/latest.json',{'checked_at':utcnow()})
   with patch.object(research,'items',return_value=[TOPIC]),patch.object(research,'update'):
    result=research.prepare_one(i,client_factory=Client,fetcher=lambda u:next(x for x in d if x['url']==u),data=data,out=out)
    self.assertEqual(result['status'],'brief_ready');self.assertTrue((data/'briefs'/f"{TOPIC['id']}.json").exists());self.assertTrue((out/'research-evidence'/TOPIC['id']/'review.json').exists())
    again=research.prepare_one(i,client_factory=Client,data=data,out=out);self.assertEqual(again['status'],'no_research_candidate')
 def test_source_failure_becomes_review_not_fabricated_approval(self):
  d,c,r,i=fixtures()
  class Client:
   def __init__(self,*a,**k):pass
   def text(self,p):return {'urls':[]}
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'config.json',{'research_feeder':{'enabled':True}});atomic_json(data/'health/latest.json',{'checked_at':utcnow()})
   with patch.object(research,'items',return_value=[TOPIC]),patch.object(research,'update'):
    result=research.prepare_one(i,client_factory=Client,data=data,out=out)
   self.assertEqual(result['status'],'research_needs_review');self.assertFalse((data/'briefs').exists())
 def test_scheduled_cycle_invokes_feeder_once_when_no_brief(self):
  with tempfile.TemporaryDirectory() as t:
   data=Path(t);atomic_json(data/'config.json',{'publication_enabled':True,'automatic_generation':True,'research_feeder':{'enabled':True}})
   with patch.object(cycle,'DATA',data),patch.object(cycle,'WordPress') as wp,patch.object(research,'prepare_one',return_value={'status':'no_research_candidate'}) as prep:
    result=cycle.run(scheduled=True);prep.assert_called_once();wp.return_value.preflight.assert_called_once();self.assertEqual(result['status'],'no_research_candidate')
if __name__=='__main__':unittest.main()
