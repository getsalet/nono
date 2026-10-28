import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n

class FoundationTests(unittest.TestCase):
 def setUp(self):
  self.quote='این یک نقل دقیق و مستند درباره محصول شهرستان است'
  self.bundle={'local':{'text':self.quote},'article':{'text':self.quote+' متن فنی'},'technical':[],'links':[]}
  self.plan={'facts':[{'excerpt_id':'s0-e0','source_index':0,'claim':'گزارش محلی','quote':self.quote},{'excerpt_id':'s1-e0','source_index':1,'claim':'روش عمومی','quote':self.quote}]}
  self.brief={'eligible':True,'grounded':True,'locally_distinct':True,'semantic_duplicate':False,'reader_question':'چه مدارکی برای پاسخ مستند لازم است؟','distinct_value':'پاسخ متفاوت بر اساس شواهد مشخص و بدون تکرار مطلب قبلی','outline':[{'heading':'گزارش محصول','fact_ids':['s0-e0']},{'heading':'روش تصمیم گیری','fact_ids':['s1-e0']},{'heading':'حدود نتیجه گیری','fact_ids':['s0-e0','s1-e0']}]}
  self.row={'id':'test','title':'عنوان','angle_ref':'angle','locality_ref':'loc','review_state':'editorial_review_required'}
  self.matrix={'titles':[self.row],'angles':{'angle':{'cluster':'test'}}}
  self.review={'approved':True,'grounded':True,'locally_distinct':True,'semantic_duplicate':False,'unsupported_claims':[],'local_evidence_id':'s0-e0'}
 def test_valid_brief_does_not_approve_publication(self):
  self.assertEqual(n.validate_brief(self.brief,self.plan),self.brief)
  self.assertNotIn('publication_verified',self.brief)
 def test_brief_flags_require_exact_booleans(self):
  for key,value in [('eligible','true'),('grounded',1),('locally_distinct',False),('semantic_duplicate',True)]:
   with self.subTest(key=key),self.assertRaises(n.PipelineStop):n.validate_brief(dict(self.brief,**{key:value}),self.plan)
 def test_brief_unknown_fact_is_rejected(self):
  bad=copy.deepcopy(self.brief);bad['outline'][0]['fact_ids']=['invented']
  with self.assertRaises(n.PipelineStop):n.validate_brief(bad,self.plan)
 def test_brief_requires_local_and_technical_facts(self):
  for eid in ['s0-e0','s1-e0']:
   bad=copy.deepcopy(self.brief)
   for section in bad['outline']:section['fact_ids']=[eid]
   with self.assertRaises(n.PipelineStop):n.validate_brief(bad,self.plan)
 def test_brief_requires_bounded_nonempty_sections(self):
  for outline in [[],self.brief['outline'][:2],self.brief['outline']*2,[{'heading':'بخش','fact_ids':[]}]*3]:
   with self.assertRaises(n.PipelineStop):n.validate_brief(dict(self.brief,outline=outline),self.plan)
 def test_rejected_brief_never_calls_writer_or_reserves_media(self):
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'source_bundle',return_value=self.bundle),patch.object(n,'all_history',return_value=[]),patch('roya_backlink_queue.agnes',side_effect=[self.plan,dict(self.brief,eligible=False)])as ai,patch.object(n,'reserve')as reserve,patch.object(n,'checkpoint')as checkpoint:
   with self.assertRaisesRegex(n.PipelineStop,'Topic brief rejected'):n.generate(self.row,self.matrix,{},{},{})
   self.assertEqual(ai.call_count,2);reserve.assert_not_called();checkpoint.assert_not_called()
 def test_validation_generation_does_not_mutate_state_or_reserve(self):
  state={'published':[],'media':{},'held':{}};before=copy.deepcopy(state)
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'source_bundle',return_value=self.bundle),patch.object(n,'all_history',return_value=[]),patch('roya_backlink_queue.agnes',side_effect=[self.plan,self.brief,{'title':'عنوان','html':'<p>متن مستند</p>'},self.review])as ai,patch.object(n,'validate_article',return_value=650),patch.object(n,'reserve')as reserve,patch.object(n,'checkpoint')as checkpoint:
   result=n.generate(self.row,self.matrix,{},{},state,validation_only=True)
   self.assertEqual(result['status'],'validated_not_published');self.assertFalse(result['publication_verified']);self.assertEqual(state,before);reserve.assert_not_called();checkpoint.assert_not_called()
   for call in [ai.call_args_list[2],ai.call_args_list[3]]:self.assertIn('independent_review_required',call.args[0]);self.assertIn('word_groups_min',call.args[0])
 def test_failure_policy_stops_unexpected_provider_errors(self):
  p=n.failure_policy(RuntimeError('private response'))
  self.assertFalse(p['continue_candidates']);self.assertNotIn('private',json.dumps(p))
 def test_failure_policy_routes_topic_and_format_separately(self):
  self.assertEqual(n.failure_policy(n.PipelineStop('Topic brief rejected'))['category'],'evidence_or_topic')
  self.assertEqual(n.failure_policy(n.PipelineStop('Mixed-script word requires editorial correction'))['category'],'format_or_language')
  self.assertTrue(n.failure_policy(n.PipelineStop('Independent editorial review rejected'))['continue_candidates'])
 def run_validation(self,error=None,paused=False):
  state={'held':{},'published':[],'intent':None};before=copy.deepcopy(state)
  runtime={'enabled':True,'revision':21}
  def read(path):
   return {str(n.D/'runtime-control.json'):runtime,str(n.STATE):state,str(n.D/'title-matrix.json'):self.matrix,str(n.D/'article-targets.json'):{'targets':[]}}[str(path)]
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'allowed',return_value=not paused),patch.object(n,'read',side_effect=read),patch.object(n,'generate',side_effect=error,return_value={'status':'validated_not_published'})as generate,patch.object(n,'login')as login,patch.object(n,'publish_new')as publish,patch.object(n,'checkpoint')as checkpoint,patch.object(n,'reserve')as reserve:
   out=n.validate_only(1)
   login.assert_not_called();publish.assert_not_called();checkpoint.assert_not_called();reserve.assert_not_called();self.assertEqual(state,before);self.assertFalse(out['publication_verified'])
   if paused:generate.assert_not_called()
   else:self.assertIs(generate.call_args.kwargs['validation_only'],True)
   return out
 def test_validation_runner_success_is_not_publication(self):self.assertEqual(self.run_validation()['status'],'passed')
 def test_validation_runner_records_rejection_without_state_changes(self):self.assertEqual(self.run_validation(n.PipelineStop('Topic brief rejected'))['status'],'blocked')
 def test_validation_respects_pause_before_api_work(self):self.assertEqual(self.run_validation(paused=True)['status'],'stopped')
 def test_validation_sample_limit_is_hard_bounded(self):
  for x in [0,4,True,'3']:
   with self.assertRaises(ValueError):n.validate_only(x)
 def test_validation_workflow_has_no_blog_credentials_or_write_permission(self):
  s=(Path(n.ROOT)/'.github/workflows/niloblog-validation.yml').read_text()
  self.assertIn('contents: read',s);self.assertIn('--validate-only',s);self.assertNotIn('NILOBLOG_PASSWORD',s);self.assertNotIn('NILOBLOG_USERNAME',s);self.assertNotIn('contents: write',s);self.assertNotIn('pip install playwright',s)
 def test_cli_validation_exception_does_not_checkpoint(self):
  s=Path(n.__file__).read_text().split("if '--validate-only' in sys.argv:",1)[1].split('try:main()',1)[0]
  self.assertNotIn('checkpoint(',s);self.assertNotIn('login(',s)
 def test_contract_and_validation_use_same_limit_definition(self):
  contract=n.article_contract(self.row,self.bundle)
  for key,value in n.ARTICLE_LIMITS.items():self.assertEqual(contract[key],value)
  self.assertEqual(set(contract['allowed_tags']),n.ARTICLE_ALLOWED_TAGS)
 def test_no_ready_article_never_logs_in(self):
  runtime={'enabled':True,'phase':'publish','revision':21};state={'published':[],'held':{},'intent':None,'current':None}
  def read(path):
   return {str(n.D/'runtime-control.json'):runtime,str(n.D/'integration-plan.json'):{},str(n.STATE):state,str(n.D/'media-catalog.json'):{},str(n.D/'title-matrix.json'):self.matrix,str(n.D/'article-targets.json'):{'targets':[]}}[str(path)]
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'allowed',return_value=True),patch.object(n,'read',side_effect=read),patch.object(n,'validate_catalog'),patch.object(n,'generate',side_effect=n.PipelineStop('Topic brief rejected')),patch.object(n,'checkpoint'),patch.object(n,'login')as login,patch.object(n,'publish_new')as publish:
   n.main();login.assert_not_called();publish.assert_not_called();self.assertEqual(n.CYCLE['status'],'idle')
 def test_unexpected_error_does_not_consume_three_topics(self):
  runtime={'enabled':True,'phase':'publish','revision':21};state={'published':[],'held':{},'intent':None,'current':None}
  matrix=copy.deepcopy(self.matrix);matrix['titles']=[dict(self.row,id=str(i),angle_ref='angle'+str(i)) for i in range(3)];matrix['angles']={'angle'+str(i):{'cluster':str(i)} for i in range(3)}
  def read(path):
   return {str(n.D/'runtime-control.json'):runtime,str(n.D/'integration-plan.json'):{},str(n.STATE):state,str(n.D/'media-catalog.json'):{},str(n.D/'title-matrix.json'):matrix,str(n.D/'article-targets.json'):{'targets':[]}}[str(path)]
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'allowed',return_value=True),patch.object(n,'read',side_effect=read),patch.object(n,'validate_catalog'),patch.object(n,'generate',side_effect=RuntimeError('private-provider-response'))as generate,patch.object(n,'checkpoint'),patch.object(n,'login')as login:
   with self.assertRaises(RuntimeError):n.main()
   self.assertEqual(generate.call_count,1);login.assert_not_called();self.assertEqual(n.CYCLE['status'],'failed');self.assertNotIn('private-provider-response',json.dumps(state))
if __name__=='__main__':unittest.main()
