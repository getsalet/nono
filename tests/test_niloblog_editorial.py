import copy,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as m
class EditorialTests(unittest.TestCase):
 def setUp(self):
  self.quote='این یک نقل دقیق و مستند درباره محصول شهرستان است'
  self.bundle={'local':{'text':self.quote},'article':{'text':self.quote+' متن فنی'},'technical':[],'links':[]}
  self.plan={'blocked':False,'facts':[{'excerpt_id':'s0-e0','source_index':0,'claim':'گزارش محصول','quote':self.quote},{'excerpt_id':'s1-e0','source_index':1,'claim':'اطلاعات محصول','quote':self.quote}]}
  self.approved={'approved':True,'grounded':True,'locally_distinct':True,'semantic_duplicate':False,'unsupported_claims':[],'local_evidence_quote':self.quote,'local_evidence_id':'s0-e0'}
 def test_known_mixed_script_typos_normalized_without_changing_urls(self):
  result=m.prepare_article({'html':'<p>هکتar سir زraعی <a href="https://x/سir">منبع</a></p>'},{'links':[]})
  self.assertIn('هکتار سیر زراعی',result['html']);self.assertIn('https://x/سir',result['html'])
 def test_remaining_mixed_words_have_a_fail_closed_gate(self):
  self.assertIn("raise PipelineStop('Mixed-script word requires editorial correction')",Path(m.__file__).read_text())
 def test_read_only_intent_recovery_never_resubmits(self):
  item={'key':'key','status':'reviewed'};state={'current':'key','intent':{'key':'key','operation':'create_public_post','at':'2026-10-23T07:14:00+00:00'},'media':{},'published':[]}
  receipt={'url':'https://afp.niloblog.com/p/4/test','at':'2026-10-23T07:20:00+00:00'}
  with mock.patch.object(m,'read',return_value=item),mock.patch.object(m,'verify_public',return_value=receipt),mock.patch.object(m,'acknowledge',return_value={}),mock.patch.object(m,'save'),mock.patch.object(m,'checkpoint'),mock.patch.object(m,'submit_once') as submit:
   m.reconcile_public_intent(mock.Mock(),state)
  submit.assert_not_called();self.assertIsNone(state['intent']);self.assertEqual(len(state['published']),1);self.assertEqual(state['published'][0]['at'],'2026-10-23T07:14:00+00:00')
 def test_missing_receipt_retains_intent_and_media(self):
  state={'current':'key','intent':{'key':'key','operation':'create_public_post'},'media':{},'published':[]};original=copy.deepcopy(state)
  with mock.patch.object(m,'read',return_value={'key':'key','status':'reviewed'}),mock.patch.object(m,'verify_public',side_effect=m.PipelineStop('missing')),mock.patch.object(m,'acknowledge') as ack,mock.patch.object(m,'checkpoint') as checkpoint:
   with self.assertRaises(m.PipelineStop):m.reconcile_public_intent(mock.Mock(),state)
  ack.assert_not_called();checkpoint.assert_not_called();self.assertEqual(state,original)
 def test_unknown_or_mismatched_intent_never_reads_provider(self):
  with mock.patch.object(m,'verify_public') as verify:
   with self.assertRaises(m.PipelineStop):m.reconcile_public_intent(mock.Mock(),{'current':'x','intent':{'key':'y','operation':'create_public_post'}})
  verify.assert_not_called()
 def test_assigned_title_is_not_regenerated(self):
  result=m.prepare_article({'title':'عنوان تغییر یافته','html':'<p>متن</p>'},{'links':[]},{'title':'عنوان دقیق صف'})
  self.assertEqual(result['title'],'عنوان دقیق صف')
 def test_extra_h2_demoted_without_losing_words(self):
  from bs4 import BeautifulSoup
  body=''.join('<h2>عنوان '+str(i)+'</h2><p>متن مستند</p>' for i in range(7))
  result=m.prepare_article({'html':body},{'links':[]});soup=BeautifulSoup(result['html'],'html.parser')
  self.assertEqual(len(soup.find_all('h2')),5);self.assertEqual(len(soup.find_all('h3')),2)
  self.assertEqual(soup.get_text(' ',strip=True),BeautifulSoup(body,'html.parser').get_text(' ',strip=True))
 def test_description_repair_is_extractive_and_bounded(self):
  body=' '.join(['اطلاعات مستند درباره گزارش محصول و تصمیم آبیاری']*12)
  obj=m.prepare_article({'html':'<p>'+body+'</p>','meta_description':'کوتاه'},{'links':[]})
  self.assertTrue(110<=len(obj['meta_description'])<=165);self.assertIn(obj['meta_description'],body)
  self.assertEqual(obj['html'],'<p>'+body+'</p>')
 def test_valid_description_is_preserved(self):
  meta='م'*120;self.assertEqual(m.prepare_article({'html':'<p>متن</p>','meta_description':meta},{'links':[]})['meta_description'],meta)
 def test_metrics_use_same_persian_counter_as_validation(self):
  metrics=m.article_metrics({'html':'<h2>عنوان بخش</h2><p>متن فارسی</p>','meta_description':'متا'})
  self.assertEqual(metrics,{'persian_word_groups':4,'h2_count':1,'meta_characters':3})
 def test_evidence_extraction_does_not_replace_final_editorial_gate(self):
  code=Path(m.__file__).read_text()
  self.assertIn('وظیفه تو فقط استخراج شواهد است',code)
  self.assertIn('if review_passes(review,bundle):break',code)
  self.assertIn("if review_attempt==1:raise PipelineStop('Independent editorial review rejected')",code)
 def test_both_configured_technical_sources_are_read(self):
  loc={'evidence_status':'previously_reviewed_county_crop','scope':'county','evidence_ref':'e','source_url':'https://news.example/a','crop':'سیب','city_fa':'شهر'}
  matrix={'localities':{'loc':loc},'link_plans':{'plan':{'required_links':[{'target_ref':'article'},{'target_ref':'product','anchor_keyword':'نوار'}],'research_only_target_refs':['tech1','tech2']}}}
  targets={k:{'target_url':'https://navar-abyari.ir/'+k,'site_title':k} for k in ['article','product','tech1','tech2']}
  evidence={'approved_records':[{'id':'e','approved':True,'source_url':loc['source_url'],'scope':'county'}]}
  with mock.patch.object(m,'read',return_value=evidence),mock.patch.object(m,'fetch',side_effect=lambda url,*args:{'url':url,'text':'گزارش سیب در شهر'}) as fetch:
   bundle=m.source_bundle({'locality_ref':'loc','link_plan_ref':'plan'},matrix,targets)
  self.assertEqual(len(bundle['technical']),2);self.assertEqual(fetch.call_count,4)
 def test_bound_links_keep_exact_matching_anchor(self):
  b={'links':[{'url':'https://x/a','anchor':'راهنما'},{'url':'https://x/b','anchor':'نوار تیپ'}]}
  o=m.bind_links({'html':'<p><a href="AFP_LINK_1">عنوان اشتباه</a> و <a href="AFP_LINK_2">دیگر</a></p>'},b)
  self.assertIn('href="https://x/a">راهنما</a>',o['html']);self.assertIn('href="https://x/b">نوار تیپ</a>',o['html'])
 def test_cycle_prefers_new_and_diverse_candidates(self):
  rows=[{'id':str(i),'angle_ref':str(i),'locality_ref':str(i%2)} for i in range(5)]
  matrix={'angles':{str(i):{'cluster':'a' if i<3 else str(i)} for i in range(5)}}
  selected=m.choose_candidates(rows,matrix,{'0':{}},3)
  self.assertEqual([x['id'] for x in selected],['1','4','3']);self.assertEqual(len(selected),3)
 def test_catalog_quotes_are_source_substrings(self):
  for f in m.evidence_catalog(self.bundle):self.assertIn(f['quote'],m.canon([self.bundle['local'],self.bundle['article']][f['source_index']]['text']))
 def test_plan_resolves_ids_not_model_quotations(self):
  raw=copy.deepcopy(self.plan);raw['facts'][0]['quote']='جعلی';raw['facts'][0]['source_index']=99
  plan=m.resolve_evidence_plan(raw,m.evidence_catalog(self.bundle),self.bundle)
  self.assertEqual(plan['facts'][0]['quote'],self.quote);self.assertEqual(plan['facts'][0]['source_index'],0)
  raw['facts'][0]['excerpt_id']='fake'
  with self.assertRaises(m.PipelineStop):m.resolve_evidence_plan(raw,m.evidence_catalog(self.bundle),self.bundle)
 def test_review_requires_selected_local_evidence_id(self):
  for eid in ['s1-e0','fake',None]:
   review=m.bind_review_evidence(dict(self.approved,local_evidence_id=eid),self.plan)
   self.assertFalse(m.review_passes(review,self.bundle))
  self.assertTrue(m.review_passes(m.bind_review_evidence(self.approved,self.plan),self.bundle))
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
  with tempfile.TemporaryDirectory() as tmp,mock.patch.object(m,'A',Path(tmp)),mock.patch.object(m,'source_bundle',return_value=self.bundle),mock.patch.object(m,'all_history',return_value=[]),mock.patch.object(m,'plan_article',return_value={'outline':[]}),mock.patch.object(m,'validate_article',return_value=600) as validate,mock.patch('roya_backlink_queue.agnes',side_effect=outputs) as ai,mock.patch.object(m,'reserve',return_value=({}, {'image_id':'img','video_id':None})) as reserve,mock.patch.object(m,'checkpoint'):
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
