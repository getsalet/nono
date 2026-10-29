import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import niloblog_pipeline as n
from niloblog_general_scope import *
class GeneralScopeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.matrix=n.read(n.D/'title-matrix.json');cls.queue=n.read(n.D/'general-source-queue.json');cls.active_count=sum(t.get('source_review_required')is not True for t in cls.queue['topics'])
 def setUp(self):
  self.state={'held':{},'published':[],'current':None,'intent':None}
  self.bundle={'content_scope':SCOPE,'local':None,'locality':{},'article':{'url':'https://example.org/article','text':'مقاله عمومی فنی معتبر با اطلاعات درباره نگهداری نوار تیپ'},'technical':[{'url':'https://example.org/technical','text':'منبع فنی دوم با دستورهای روشن درباره نگهداری و تمیزی خطوط'}],'links':[]}
  self.plan=n.source_evidence_plan({'angle_ref':'a'},{'angles':{'a':{'brief':'نگهداری'}}},n.evidence_catalog(self.bundle),self.bundle)
  ids=[f['excerpt_id']for f in self.plan['facts']]
  self.brief={'eligible':True,'grounded':True,'scope_appropriate':True,'independently_useful':True,'semantic_duplicate':False,'contains_local_claims':False,'reader_question':'هزینه های نگهداری از چه بخش هایی تشکیل شده است؟','distinct_value':'طبقه بندی محدود هزینه ها با شرح مستند و بدون تکرار موضوع های قبلی','outline':[{'heading':h,'fact_ids':ids}for h in ['دسته نخست','دسته دوم','حدود ادعا']]}
  self.review={'reader_ready':True,'causal_consistency':True,'approved':True,'grounded':True,'scope_appropriate':True,'independently_useful':True,'semantic_duplicate':False,'contains_local_claims':False,'unsupported_claims':[],'technical_evidence_ids':ids}
 def test_internal_labels_and_observed_corrupt_prose_are_blocked(self):
  for text in ['منبع س2 صراحتا بیان می کند','منبع s2 درباره هزینه','s2-contract0','از سرهنگ کردن هزینه ها جلوگیری می کند','تعویض از جلوگیری از افت کارایی و ضایعات بیشتر جلوگیری می کند']:
   with self.assertRaises(n.PipelineStop):validate_general_visible_prose('<p>'+text+'</p>',n.canon,n.PipelineStop)
  validate_general_visible_prose('<p>مقاله نگهداری نوار تیپ و هزینه های آن سه دسته هزینه را توضیح می دهد.</p>',n.canon,n.PipelineStop)
 def test_reviewer_cannot_approve_a_self_rewritten_candidate(self):
  good=n.bind_review_evidence(self.review,self.plan)
  self.assertTrue(n.review_passes(good,self.bundle))
  for key in ['candidate','html','post','rewritten_candidate','revised_candidate','corrected_candidate']:
   for value in [None,{},'متن اصلاح شده']:
    review=copy.deepcopy(good);review[key]=value
    self.assertFalse(n.review_passes(review,self.bundle),key)
  self.assertNotIn('candidate',self.review)
 def test_review_prompt_forbids_conditional_self_repair(self):
  prompt=general_review_prompt()
  self.assertIn('متن را اصلاح یا بازنویسی نکن',prompt)
  self.assertIn('اگر اصلاح لازم است approved=false',prompt)
 def test_general_comparison_context_preserves_prose_not_old_article_ids(self):
  examples=[{'label':'rozblog:article-51d0fbccb1b93b06','text':'نمونه قبلی فقط برای مقایسه است','contrast_only_not_evidence':True}]
  before=copy.deepcopy(examples);out=general_contrast_view(examples)
  self.assertEqual(examples,before);self.assertEqual(out[0]['text'],examples[0]['text'])
  self.assertTrue(out[0]['contrast_only_not_evidence']);self.assertEqual(out[0]['comparison_number'],1)
  self.assertNotIn('rozblog:article-',json.dumps(out))
 def test_comparison_id_in_fact_ids_still_fails_closed(self):
  bad=copy.deepcopy(self.brief);bad['outline'][0]['fact_ids'].append('rozblog:article-51d0fbccb1b93b06')
  callback=unittest.mock.Mock(side_effect=AssertionError('do not silently repair invalid evidence'))
  with self.assertRaises(n.PipelineStop):validate_or_complete_outline(bad,self.plan,callback,n.PipelineStop)
  callback.assert_not_called()
 def test_writing_budget_matches_unchanged_validator_and_preserves_headings(self):
  budget=general_writing_budget(self.brief,n.ARTICLE_LIMITS)
  self.assertEqual(budget['hard_min'],500);self.assertEqual(budget['hard_max'],1100)
  self.assertEqual([x['heading']for x in budget['section_targets']],[x['heading']for x in self.brief['outline']])
  self.assertGreaterEqual(sum(x['target_groups']for x in budget['section_targets']),800)
  self.assertTrue(budget['no_padding_or_new_claims']);self.assertEqual(budget['insufficient_evidence_action'],'blocked=true')
 def test_source_groups_count_documents_not_number_of_quotes(self):
  plan={'facts':[{'excerpt_id':'s2-contract'+str(i),'source_index':2}for i in range(3)]+[{'excerpt_id':'s3-contract3','source_index':3}]}
  groups=general_source_groups(plan);self.assertEqual(len(groups),2);self.assertEqual([len(g['fact_ids'])for g in groups],[3,1])
  self.assertEqual([g['source_index']for g in groups],[2,3])
 def test_reader_readiness_and_causal_consistency_are_mandatory(self):
  for key in ['reader_ready','causal_consistency']:
   for value in [False,None,'true']:
    review=copy.deepcopy(self.review);review[key]=value
    self.assertFalse(n.review_passes(n.bind_review_evidence(review,self.plan),self.bundle))
 def test_outline_completion_is_bounded_and_preserves_admission_verdict(self):
  raw=copy.deepcopy(self.brief);raw['outline']=[s['heading']for s in self.brief['outline']]
  repair=lambda data:{'outline':self.brief['outline']}
  fixed=validate_or_complete_outline(raw,self.plan,repair,n.PipelineStop)
  self.assertEqual(fixed['outline'],self.brief['outline']);self.assertEqual(raw['outline'],[s['heading']for s in self.brief['outline']])
  for k in ['eligible','grounded','scope_appropriate','independently_useful']:
   bad=copy.deepcopy(raw);bad[k]=False
   with patch('builtins.print')as unused:
    callback=unittest.mock.Mock(side_effect=AssertionError('must not retry rejected topic'))
    with self.assertRaises(n.PipelineStop):validate_or_complete_outline(bad,self.plan,callback,n.PipelineStop)
    callback.assert_not_called()
 def test_outline_completion_cannot_change_headings_or_invent_evidence(self):
  raw=copy.deepcopy(self.brief);raw['outline']=[s['heading']for s in self.brief['outline']]
  for bad in [{'outline':[{'heading':'عنوان تازه','fact_ids':['invented']}]*3},{'outline':[{'heading':h,'fact_ids':['invented']}for h in raw['outline']]},{'blocked':True}]:
   with self.assertRaises(n.PipelineStop):validate_or_complete_outline(raw,self.plan,lambda data:bad,n.PipelineStop)
 def test_source_label_rendering_is_exact_known_provenance_not_claim_rewrite(self):
  bundle=copy.deepcopy(self.bundle);bundle['technical'][0]['source_label']='نگهداری نوار تیپ و هزینه های آن'
  before='منبع س2 هزینه ابزار را بیان می کند.'
  self.assertEqual(render_source_labels(before,bundle),'مقاله «نگهداری نوار تیپ و هزینه های آن» هزینه ابزار را بیان می کند.')
  for unknown in ['منبع س9','منبع s2-contract0','منبع س0']:
   self.assertEqual(render_source_labels(unknown,bundle),unknown)
 def test_rendering_preserves_markup_and_unknown_ids_still_block(self):
  bundle=copy.deepcopy(self.bundle);bundle['technical'][0]['source_label']='عنوان واقعی مقاله'
  obj=n.prepare_article({'title':'عنوان','html':'<p>منبع س2 هزینه ابزار را بیان می کند.</p>'},bundle)
  self.assertEqual(obj['html'],'<p>مقاله «عنوان واقعی مقاله» هزینه ابزار را بیان می کند.</p>')
  validate_general_visible_prose(obj['html'],n.canon,n.PipelineStop)
  bad=n.prepare_article({'title':'عنوان','html':'<p>منبع س9</p>'},bundle)
  with self.assertRaises(n.PipelineStop):validate_general_visible_prose(bad['html'],n.canon,n.PipelineStop)
 def test_overlay_preserves_original_thousand_rows_and_state(self):
  m=copy.deepcopy(self.matrix);s=copy.deepcopy(self.state);out,a=apply_general_queue(m,s,self.queue)
  self.assertEqual(m,self.matrix);self.assertEqual(s,self.state);self.assertEqual(out['titles'][:1000],self.matrix['titles']);self.assertEqual(len(out['titles']),1000+self.active_count)
  for row in out['titles'][1000:]:self.assertNotIn('locality_ref',row);self.assertNotIn('شهرستان',row['title'])
  self.assertFalse(a['publication_permission_granted']);self.assertFalse(a['retry_permission_granted'])
 def test_one_stable_identity_per_question_not_per_county(self):
  a,_=apply_general_queue(self.matrix,self.state,self.queue);m=copy.deepcopy(self.matrix);m['localities']={}
  b,_=apply_general_queue(m,self.state,self.queue)
  self.assertEqual([r['id']for r in a['titles'][1000:]],[r['id']for r in b['titles'][1000:]])
 def test_held_published_current_intent_and_saved_general_keys_not_recreated(self):
  out,_=apply_general_queue(self.matrix,self.state,self.queue);key=out['titles'][1000]['id']
  for s,protected in [({'held':{key:{}}},[]),({'published':[{'key':key}]},[]),({'current':key},[]),({'intent':{'key':key}},[]),({},[key])]:
   out,_=apply_general_queue(self.matrix,s,self.queue,protected);self.assertNotIn(key,[r['id']for r in out['titles'][1000:]])
 def test_legacy_holds_preserved_and_general_failure_stops_same_question(self):
  s={'held':{'legacy':{'editorial_source_contract_id':'maintenance-cost-components-v2'}}};before=copy.deepcopy(s)
  out,_=apply_general_queue(self.matrix,s,self.queue);self.assertEqual(len(out['titles']),1000+self.active_count);self.assertEqual(s,before)
  s['held']['general']={'editorial_source_contract_id':self.queue['topics'][0]['id']}
  out,a=apply_general_queue(self.matrix,s,self.queue);self.assertEqual(a['topics'][0]['pending_rows'],0)
 def test_manifest_cannot_grant_permissions_or_duplicate_topic_identity(self):
  for key in ['publication_permission_granted','retry_permission_granted']:
   q=copy.deepcopy(self.queue);q[key]=True
   with self.assertRaises(ValueError):apply_general_queue(self.matrix,self.state,q)
  q=copy.deepcopy(self.queue);q['topics'].append(q['topics'][0])
  with self.assertRaises(ValueError):apply_general_queue(self.matrix,self.state,q)
 def test_general_source_bundle_never_fetches_local_news(self):
  m,_=apply_general_queue(self.matrix,self.state,self.queue);row=m['titles'][1000];targets={t['key']:t for t in n.read(n.D/'article-targets.json')['targets']}
  topic=row['editorial_source_contract'];quotes={e['source_url']:' '.join(x['quote']for x in topic['evidence']if x['source_url']==e['source_url'])for e in topic['evidence']}
  def fetch(url,host=None):return {'url':url,'text':quotes.get(url,'منبع فنی عمومی با اطلاعات معتبر درباره نوار تیپ و نگهداری'),'checked_at':'test'}
  with patch.object(n,'fetch',side_effect=fetch)as f:
   bundle=n.source_bundle(row,m,targets)
   self.assertIsNone(bundle['local']);self.assertEqual(len(f.call_args_list),3)
   self.assertTrue(all(c.args[1]=='navar-abyari.ir'for c in f.call_args_list))
 def test_general_ledger_has_no_local_fact(self):
  self.assertTrue(is_general(self.plan));self.assertTrue(all(f['source_index']>0 and f['scope']=='technical_general'for f in self.plan['facts']))
  self.assertFalse(self.plan['publication_authorized'])
 def test_fabricated_local_source_index_is_rejected(self):
  bad=copy.deepcopy(self.plan);bad['facts'][0]['source_index']=0
  with self.assertRaises(n.PipelineStop):n.verify_evidence_plan(bad,self.bundle)
 def test_general_requires_two_technical_sources(self):
  bad=copy.deepcopy(self.plan);bad['facts']=[bad['facts'][0],bad['facts'][0]]
  with self.assertRaises(n.PipelineStop):n.verify_evidence_plan(bad,self.bundle)
 def test_general_brief_does_not_need_fake_local_flag(self):
  self.assertEqual(n.validate_brief(self.brief,self.plan),self.brief);self.assertNotIn('locally_distinct',self.brief)
 def test_general_brief_unknown_ids_duplicates_local_claims_and_unsupported_scope_blocked(self):
  for k,v in [('contains_local_claims',True),('semantic_duplicate',True),('grounded',False),('scope_appropriate',False),('independently_useful',False)]:
   bad=copy.deepcopy(self.brief);bad[k]=v
   with self.assertRaises(n.PipelineStop):n.validate_brief(bad,self.plan)
  bad=copy.deepcopy(self.brief);bad['outline'][0]['fact_ids']=['invented']
  with self.assertRaises(n.PipelineStop):n.validate_brief(bad,self.plan)
 def test_review_binds_real_technical_quotes_without_fake_local_quote(self):
  bound=n.bind_review_evidence(self.review,self.plan)
  self.assertTrue(n.review_passes(bound,self.bundle));self.assertNotIn('local_evidence_quote',bound)
 def test_general_review_rejects_unsupported_inverted_duplicate_and_local_claims(self):
  for k,v in [('unsupported_claims',['خلاف منبع']),('semantic_duplicate',True),('contains_local_claims',True),('scope_appropriate',False),('independently_useful',False),('technical_evidence_ids',['invented','s1-e0'])]:
   review=copy.deepcopy(self.review);review[k]=v
   self.assertFalse(n.review_passes(n.bind_review_evidence(review,self.plan),self.bundle))
 def test_local_contract_still_requires_actual_local_evidence(self):
  plan=copy.deepcopy(self.plan);plan.pop('content_scope')
  with self.assertRaises(n.PipelineStop):n.validate_brief(self.brief,plan)
  review=copy.deepcopy(self.review);review['locally_distinct']=True
  self.assertFalse(n.review_passes(review,dict(self.bundle,content_scope='local',local={'text':'واقعیت محلی'})))
 def test_general_writer_uses_no_legacy_local_prompt(self):
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'source_bundle',return_value=self.bundle),patch.object(n,'all_history',return_value=[]),patch.object(n,'plan_article',return_value=self.brief),patch.object(n,'validate_candidate',return_value=700),patch('roya_backlink_queue.agnes',side_effect=[{'title':'عنوان','html':'<p>متن فارسی</p>'},self.review])as ai,patch.object(n,'reserve')as reserve,patch.object(n,'checkpoint')as checkpoint:
   row={'id':'general-test','title':'عنوان','content_scope':SCOPE,'angle_ref':'a'}
   item=n.generate(row,{'angles':{'a':{'brief':'پرسش عمومی'}}},{},{},self.state,validation_only=True)
   self.assertEqual(item['status'],'validated_not_published');self.assertFalse(item['publication_verified']);reserve.assert_not_called();checkpoint.assert_not_called()
   self.assertIn('آموزشی عمومی',ai.call_args_list[0].args[0]);self.assertNotIn('گزارش تاریخی',ai.call_args_list[0].args[0]);self.assertIn('بازبین مستقل',ai.call_args_list[1].args[0])
if __name__=='__main__':unittest.main()
