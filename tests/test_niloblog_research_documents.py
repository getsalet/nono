import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import niloblog_pipeline as n
import niloblog_research_documents as r
class ResearchDocumentsTests(unittest.TestCase):
 def setUp(self):
  self.key=next(iter(r.DOCUMENTS));self.doc=r.DOCUMENTS[self.key];self.raw=b'%PDF-test fixture';self.text='Explicit original reel-handling instruction. '*20
 def verify(self,raw=None,url=None,mime='application/pdf'):
  doc=dict(self.doc,sha256=hashlib.sha256(self.raw).hexdigest())
  with patch.dict(r.DOCUMENTS,{self.key:doc}):return r.verify_pdf(self.raw if raw is None else raw,self.key,url or self.doc['url'],mime,extract=lambda p:self.text)
 def test_document_is_research_only_and_hash_pinned(self):
  out=self.verify();self.assertTrue(out['research_only']);self.assertFalse(out['publication_target']);self.assertEqual(out['document_pages'],[1]);self.assertIn('only',out['document_scope']);self.assertEqual(out['sha256'],hashlib.sha256(self.raw).hexdigest())
 def test_changed_hash_redirect_bad_mime_or_large_document_rejected(self):
  for kw in [{'raw':self.raw+b'x'},{'url':'https://evil.example/file.pdf'},{'mime':'text/html'},{'raw':b'x'*(r.MAX_BYTES+1)}]:
   with self.assertRaises(ValueError):self.verify(**kw)
 def test_unknown_ref_not_fetched(self):
  with patch('urllib.request.urlopen')as fetch:
   with self.assertRaises(ValueError):r.fetch_document('unknown')
  fetch.assert_not_called()
 def test_external_research_cannot_enter_local_or_backlink_routing(self):
  m={'angles':{'a':{'cluster':'test'}},'link_plans':{'p':{}}};row={'angle_ref':'a','link_plan_ref':'p','editorial_source_contract':{'research_refs':['site-test',self.key]}}
  targets={'site-test':{'kind':'article','family':'tape20','target_url':'https://navar-abyari.ir/guide/'}}
  with self.assertRaises(n.PipelineStop):n.research_refs(row,m,targets)
  row['content_scope']='general_education';self.assertEqual(n.research_refs(row,m,targets),['site-test',self.key])
  row['editorial_source_contract']['research_refs']=['unknown-pdf']
  with self.assertRaises(n.PipelineStop):n.research_refs(row,m,targets)
class HeldReviewTests(unittest.TestCase):
 def setUp(self):self.key='nilo-general-507d8406a738597c';self.hold={'attempts':1,'reason':'Article length/section check failed','editorial_source_contract_id':'coil-storage-hazards-v1-general-v1'}
 def run_case(self,*,published=False,intent=False,current=False,item=False):
  state={'held':{self.key:copy.deepcopy(self.hold)},'published':[{'key':self.key}]if published else[],'intent':{'key':'other'}if intent else None,'current':'other'if current else None};before=copy.deepcopy(state);realread=n.read
  def read(p):
   if p==n.STATE:return state
   if p==n.D/'runtime-control.json':return {'enabled':True,'revision':21}
   return realread(p)
  with tempfile.TemporaryDirectory()as tmp,patch.object(n,'A',Path(tmp)),patch.object(n,'read',side_effect=read),patch.object(n,'allowed',return_value=True),patch.object(n,'generate',return_value={'status':'validated_not_published'})as generate,patch.object(n,'checkpoint')as checkpoint:
   if item:
    path=Path(tmp)/'items'/f'{self.key}.json';path.parent.mkdir();path.write_text('{}')
   if published or intent or current or item:
    with self.assertRaises(ValueError):n.validate_only(1,self.key)
    generate.assert_not_called()
   else:
    out=n.validate_only(1,self.key);self.assertEqual(out['validated_count'],1);self.assertEqual(out['read_only_held_review']['original_hold'],self.hold);self.assertFalse(out['read_only_held_review']['retry_permission_granted']);self.assertEqual(generate.call_args.args[0]['id'],self.key);self.assertTrue(generate.call_args.kwargs['validation_only'])
   checkpoint.assert_not_called();self.assertEqual(state,before)
 def test_held_review_is_read_only_and_does_not_release_hold(self):self.run_case()
 def test_publication_intents_items_and_published_keys_cannot_be_overridden(self):
  for k in ['published','intent','current','item']:self.run_case(**{k:True})
if __name__=='__main__':unittest.main()
