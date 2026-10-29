import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import niloblog_pipeline as n
from niloblog_source_queue import apply_source_queue,verify_source_contract
class SourceQueueTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.matrix=n.read(n.D/'title-matrix.json');cls.queue=n.read(n.D/'source-bound-queue.json')
 def setUp(self):self.state={'held':{},'published':[],'current':None,'intent':None}
 def test_cost_evidence_contains_explanations_not_only_contents_headings(self):
  quote=self.queue['topics'][0]['evidence'][0]['quote']
  for detail in ('خرید تجهیزات و ابزارهای','خرید و تعویض قطعات یدکی','هزینه های مرتبط با کارکنان'):
   self.assertIn(detail,quote)
 def test_causal_polarity_rejects_observed_inversions(self):
  bad=['از پاکسازی دقیق باید اطمینان حاصل شود تا از مسدود شدن قطره چکان ها و حفظ جریان آب جلوگیری گردد.','حفظ تمیزی و آزاد بودن قطره چکان ها از خاک و ذرات معلق، مستقیماً به سایش و کاهش کارایی نوار تیپ کمک می کند.']
  for text in bad:
   with self.assertRaisesRegex(n.PipelineStop,'Causal polarity'):n.validate_causal_polarity('<p>'+text+'</p>')
 def test_causal_polarity_allows_correct_prevention_statements(self):
  for text in ['پاکسازی از مسدود شدن قطره چکان ها جلوگیری می کند و به حفظ جریان آب کمک می کند.','تمیزی از سایش و کاهش کارایی جلوگیری می کند.']:
   n.validate_causal_polarity('<p>'+text+'</p>')
 def test_observed_approved_candidate_is_now_blocked_before_publication(self):
  with self.assertRaisesRegex(n.PipelineStop,'Causal polarity'):
   n.validate_article({'title':'عنوان'},{'title':'عنوان','html':'<p>تمیزی به سایش زودرس کمک می کند.</p>'},{'links':[]})
 def test_overlay_keeps_original_matrix_and_state_unchanged(self):
  matrix=copy.deepcopy(self.matrix);state=copy.deepcopy(self.state)
  out,audit=apply_source_queue(matrix,state,self.queue)
  self.assertEqual(matrix,self.matrix);self.assertEqual(state,self.state);self.assertEqual(len(out['titles']),1000)
  self.assertFalse(audit['publication_permission_granted']);self.assertFalse(audit['retry_permission_granted']);self.assertTrue(out['source_queue_required'])
  self.assertGreater(audit['eligible_pending_rows'],0)
 def test_protected_rows_are_byte_for_byte_unchanged(self):
  rows=[r for r in self.matrix['titles']if r['angle_ref']==self.queue['topics'][0]['angle_ref']]
  state={'held':{rows[0]['id']:{'reason':'old'}},'published':[],'current':rows[1]['id'],'intent':{'key':rows[2]['id']}}
  out,_=apply_source_queue(self.matrix,state,self.queue)
  for original in rows[:3]:self.assertEqual(next(r for r in out['titles']if r['id']==original['id']),original)
 def test_published_or_saved_angle_is_never_reframed(self):
  original=next(r for r in self.matrix['titles']if r['angle_ref']==self.queue['topics'][0]['angle_ref'])
  for state,protected in [({'published':[{'key':original['id']}]},[]),(self.state,[original['id']])]:
   out,_=apply_source_queue(self.matrix,state,self.queue,protected)
   self.assertEqual(out['angles'][original['angle_ref']],self.matrix['angles'][original['angle_ref']])
   self.assertFalse(any(r.get('editorial_source_contract')for r in out['titles']if r['angle_ref']==original['angle_ref']))
 def test_only_source_bound_pending_rows_are_selected(self):
  out,_=apply_source_queue(self.matrix,self.state,self.queue)
  rows=[r for r in out['titles']if r.get('editorial_source_contract')]
  selected=n.evidence_first_candidates(rows,out,{}, {},3)
  self.assertEqual([r['editorial_source_contract']['id']for r in selected],[t['id']for t in self.queue['topics']])
 def test_unverified_locality_remains_held(self):
  out,_=apply_source_queue(self.matrix,self.state,self.queue)
  for r in out['titles']:
   if r['review_state']!='editorial_review_required':self.assertNotIn('editorial_source_contract',r)
 def test_contract_cannot_grant_permission_or_duplicate_angles(self):
  for key in ['publication_permission_granted','retry_permission_granted']:
   bad=copy.deepcopy(self.queue);bad[key]=True
   with self.assertRaises(ValueError):apply_source_queue(self.matrix,self.state,bad)
  bad=copy.deepcopy(self.queue);bad['topics'].append(bad['topics'][0])
  with self.assertRaises(ValueError):apply_source_queue(self.matrix,self.state,bad)
 def sources(self,topic):
  return [{'research_ref':ref,'url':next(e['source_url']for e in topic['evidence']if e['source_ref']==ref),'text':' '.join(e['quote']for e in topic['evidence']if e['source_ref']==ref)}for ref in topic['research_refs']]
 def test_missing_quote_wrong_url_or_provenance_stops_before_generation(self):
  topic=self.queue['topics'][0]
  for field,value in [('text','متن عوض شده'),('url','https://example.org/'),('research_ref','wrong')]:
   sources=self.sources(topic);sources[0][field]=value
   with self.assertRaises(ValueError):verify_source_contract(topic,sources,n.canon)
 def test_method_quotes_are_exact_and_pinned_into_evidence_ledger(self):
  topic=self.queue['topics'][0];sources=self.sources(topic)
  required=verify_source_contract(topic,sources,n.canon)
  bundle={'local':{'text':'منبع معتبر درباره کشت محصول شهرستان با تاریخ گزارش مشخص است'},'article':{'text':'یک متن فنی درباره نوار تیپ و روش عمومی نگهداری وجود دارد'},'technical':sources,'required_evidence':required}
  catalog=n.evidence_catalog(bundle);plan=n.source_evidence_plan({'angle_ref':'a'},{'angles':{'a':{'brief':topic['reader_question']}}},catalog,bundle)
  ids={f['excerpt_id']for f in plan['facts']}
  self.assertTrue({f['excerpt_id']for f in required}<=ids)
  for fact in plan['facts']:self.assertEqual(fact['claim'],fact['quote'])
  self.assertFalse(plan['publication_authorized'])
 def test_rejected_contract_is_not_retried_in_another_county(self):
  topic=self.queue['topics'][0];state=copy.deepcopy(self.state);state['held']['previous']={'editorial_source_contract_id':topic['id'],'failure_policy':{'category':'evidence_or_topic'}}
  out,audit=apply_source_queue(self.matrix,state,self.queue)
  self.assertFalse(any(r.get('editorial_source_contract',{}).get('id')==topic['id']for r in out['titles']))
  self.assertEqual(audit['topics'][0]['reason'],'contract_requires_editorial_review')
 def test_backlinks_and_global_matrix_permission_stay_unchanged(self):
  out,_=apply_source_queue(self.matrix,self.state,self.queue)
  self.assertEqual(out['link_plans'],self.matrix['link_plans']);self.assertFalse(out['publication_enabled'])
if __name__=='__main__':unittest.main()
