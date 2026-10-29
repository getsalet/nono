import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import niloblog_pipeline as n
from niloblog_general_scope import validate_general_visible_prose,general_writer_prompt
from niloblog_source_hygiene import *
class SourceHygieneTests(unittest.TestCase):
 def setUp(self):
  self.good='در صورت آسیب، قطعات معیوب باید تعویض شوند.'
  self.bad='تعویض به موقع اجزاء آسیب دیده از جلوگیری از افت کارایی و ضایعات بیشتر جلوگیری می کند.'
  self.after='خرید و تعویض قطعات یدکی از هزینه های نگهداری است.'
  self.bundle={'content_scope':'general_education','local':None,'locality':{},'article':{'url':'https://example.org/one','text':self.good+' '+self.bad+' '+self.after,'sha256':'raw-hash','checked_at':'time'},'technical':[{'url':'https://example.org/two','text':'نگهداری و تعمیرات دوره ای از سایش زودرس و خرابی ها جلوگیری می کند.'}],'required_evidence':[],'links':[]}
 def test_actual_observed_source_defects_are_quarantined_not_rewritten(self):
  inputs=[self.bad,'حفظ تمیزی و آزاد بودن قطره چکان ها از خاک و ذرات معلق به سایش و کاهش کارایی نوار تیپ کمک می کند.','از پاکسازی دقیق برخوردار بوده تا از مسدود شدن قطره چکان ها و حفظ جریان آب اطمینان حاصل شود.','از حیوانات خردکننده دور نگه دارید.']
  for text in inputs:
   safe,excluded=partition_source(text);self.assertEqual(safe,[]);self.assertEqual(excluded[0]['text'],text)
 def test_corrupt_encoding_and_observed_instrument_term_are_quarantined(self):
  for bad in ['در سراسر ��وار توزیع شود.','مانومترها به شکل یک دستگاه با شاخه نمایشگر فشار ولترهای مختلف تولید می شوند.']:
   safe,excluded=partition_source(bad)
   self.assertEqual(safe,[]);self.assertEqual(excluded[0]['text'],bad)
   with self.assertRaises(n.PipelineStop):validate_general_visible_prose('<p>'+bad+'</p>',n.canon,n.PipelineStop)
 def test_new_questions_have_distinct_ids_and_protected_legacy_topics(self):
  from niloblog_general_scope import apply_general_queue
  q=n.read(n.D/'general-source-queue.json');matrix=n.read(n.D/'title-matrix.json')
  self.assertEqual(len({t['id']for t in q['topics']}),len(q['topics']))
  for t in q['topics'][2:]:
   self.assertEqual({e['source_ref']for e in t['evidence']},set(t['research_refs']))
   for e in t['evidence']:self.assertEqual(sentence_quality(e['quote']),[])
  topic=q['topics'][0];key='nilo-general-'+__import__('hashlib').sha256(topic['id'].encode()).hexdigest()[:16]
  state={'held':{},'published':[{'key':key}],'current':None,'intent':None};before=copy.deepcopy(state)
  out,audit=apply_general_queue(matrix,state,q)
  self.assertEqual(state,before);self.assertNotIn(key,audit['changed_keys']);self.assertEqual(audit['eligible_pending_rows'],2)
 def test_correct_prevention_sentences_are_preserved(self):
  for text in ['پاکسازی از گرفتگی جلوگیری می کند و به حفظ جریان آب کمک می کند.','حفظ تمیزی از سایش زودرس جلوگیری می کند.']:
   safe,excluded=partition_source(text);self.assertEqual(safe,[text]);self.assertEqual(excluded,[])
 def test_model_view_does_not_mutate_raw_sources_or_hashes(self):
  before=copy.deepcopy(self.bundle);view=model_source_view(self.bundle)
  self.assertEqual(self.bundle,before);self.assertNotIn(self.bad,view['article']['text']);self.assertIn(self.good,view['article']['text']);self.assertIn(self.after,view['article']['text'])
  self.assertEqual(view['article']['sha256'],'raw-hash');self.assertEqual(view['article']['source_quality']['excluded_sentence_count'],1)
 def test_ledger_quotes_still_match_raw_and_never_stitch_removed_gap(self):
  catalog=n.evidence_catalog(self.bundle)
  for e in catalog:
   source=([None,self.bundle['article']]+self.bundle['technical'])[e['source_index']]
   self.assertIn(e['quote'],normalize(source['text']));self.assertNotIn('از جلوگیری از افت کارایی',e['quote']);self.assertFalse(self.good in e['quote']and self.after in e['quote'])
 def test_required_quarantine_quote_fails_closed(self):
  b=copy.deepcopy(self.bundle);b['required_evidence']=[{'excerpt_id':'s2-contract0','source_index':2,'scope':'technical_general','quote':self.bad}]
  with self.assertRaisesRegex(n.PipelineStop,'Source contract quote quarantined'):n.evidence_catalog(b)
 def test_clean_required_quotes_keep_their_provenance(self):
  b=copy.deepcopy(self.bundle);q={'excerpt_id':'s1-contract0','source_index':1,'scope':'technical_general','quote':self.good};b['required_evidence']=[q]
  self.assertIn(q,n.evidence_catalog(b));self.assertEqual(b['required_evidence'],[q])
 def test_audit_keeps_exact_public_defects_without_permission_or_raw_edits(self):
  audit=source_quality_audit(self.bundle);self.assertFalse(audit['publication_authorized']);self.assertFalse(audit['raw_sources_modified']);self.assertFalse(audit['rewritten_factual_claims'])
  excluded=audit['sources'][0]['excluded_sentences'];self.assertEqual(excluded,[{'text':self.bad,'reasons':['double_prevention_negation']}])
 def test_writer_receives_clean_sources_and_originals_remain_auditable(self):
  row={'id':'test','title':'راهنمای هزینه های نگهداری','angle_ref':'a'};prompt=general_writer_prompt(row,{'angles':{'a':{'brief':'پرسش'}}},self.bundle,{'facts':[]},{},{},[])
  self.assertNotIn(self.bad,prompt);self.assertIn(self.good,prompt);self.assertIn(self.bad,self.bundle['article']['text'])
 def test_feedback_identifies_bad_sentence_without_inventing_replacement(self):
  feedback=n.generation_feedback({'html':'<p>'+self.bad+'</p>'})['technical_prose_feedback'];self.assertEqual(feedback['unsafe_sentences'][0]['text'],self.bad);self.assertIn('Do not guess',feedback['action'])
 def test_all_quarantined_sentence_types_also_fail_output_gate(self):
  for text in [self.bad,'از مسدود شدن قطره چکان ها و حفظ جریان آب اطمینان حاصل شود.','حفظ تمیزی به سایش و کاهش کارایی کمک می کند.']:
   with self.assertRaises(n.PipelineStop):validate_general_visible_prose('<p>'+text+'</p>',n.canon,n.PipelineStop)
 def test_general_manifest_required_quotes_are_clean(self):
  q=n.read(n.D/'general-source-queue.json')
  for topic in q['topics']:
   if topic.get('source_review_required')is not True:
    for e in topic['evidence']:self.assertEqual(sentence_quality(e['quote']),[])
 def test_known_defective_topic_is_preserved_but_not_generated(self):
  from niloblog_general_scope import apply_general_queue
  q=n.read(n.D/'general-source-queue.json');matrix=n.read(n.D/'title-matrix.json');before=copy.deepcopy(q)
  out,audit=apply_general_queue(matrix,{'held':{},'published':[]},q)
  self.assertEqual(q,before);self.assertEqual(audit['topics'][1]['reason'],'source_quality_review_required');self.assertEqual(audit['topics'][1]['pending_rows'],0)
  self.assertFalse(any(r.get('editorial_source_contract',{}).get('id')==q['topics'][1]['id']for r in out['titles']))
 def test_local_ledger_path_is_not_silently_changed(self):
  bundle=copy.deepcopy(self.bundle);bundle.pop('content_scope');bundle['local']={'text':'این یک گزارش معتبر محلی درباره کشت محصول و شهرستان مورد نظر است'}
  self.assertTrue(any(e['scope']=='local_report'for e in n.evidence_catalog(bundle)))
if __name__=='__main__':unittest.main()
