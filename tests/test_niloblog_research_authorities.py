import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from niloblog_research_documents import DOCUMENTS,required_authority_coverage,review_covers_required_authorities
class ResearchAuthorityTests(unittest.TestCase):
 def setUp(self):
  self.refs=['research-arizona-sdi-maintenance','research-iran-swri-irrigation-evaluation-128814']
  self.bundle={'local':None,'article':{'url':'https://navar-abyari.ir/','text':'commercial'},'technical':[{'url':DOCUMENTS[r]['url'],'research_ref':r}for r in self.refs],'required_evidence':[{'source_index':i+2,'quote':'actual quote checked separately','excerpt_id':f's{i+2}-contract{i}'}for i in range(2)]}
 def test_both_registered_groups_required_not_two_arbitrary_sources(self):
  before=copy.deepcopy(self.bundle);p=required_authority_coverage(self.bundle);self.assertEqual(self.bundle,before);self.assertFalse(p['publication_authorized']);self.assertEqual(len(p['source_groups']),2)
  for i in [0,1]:
   b=copy.deepcopy(self.bundle);b['technical'][i]['research_ref']='commercial-source'
   with self.assertRaisesRegex(ValueError,'research evidence required'):required_authority_coverage(b)
 def test_authority_cannot_be_self_declared_or_redirected(self):
  b=copy.deepcopy(self.bundle);b['technical'][1]['url']='https://commercial.example.org/';b['technical'][1]['authority_class']='iran_public_research'
  with self.assertRaises(ValueError):required_authority_coverage(b)
 def test_homepage_or_empty_citation_does_not_count_as_research_evidence(self):
  b=copy.deepcopy(self.bundle);b['required_evidence']=b['required_evidence'][:1]
  with self.assertRaises(ValueError):required_authority_coverage(b)
 def test_review_must_bind_both_authority_groups(self):
  self.bundle['research_policy']=required_authority_coverage(self.bundle)
  self.assertFalse(review_covers_required_authorities({'bound_technical_evidence':[{'source_index':2},{'source_index':1}]},self.bundle))
  self.assertTrue(review_covers_required_authorities({'bound_technical_evidence':[{'source_index':2},{'source_index':3}]},self.bundle))
 def test_iranian_study_has_original_publisher_date_doi_and_local_limits(self):
  doc=DOCUMENTS[self.refs[1]];self.assertEqual(doc['published_date'],'2013-05-22');self.assertEqual(doc['doi'],'10.22092/jwra.2013.128814');self.assertTrue(doc['study_context']['historical_not_current_observation']);self.assertEqual(doc['study_context']['study_years_fa'],'۱۳۸۵ و ۱۳۸۶')
if __name__=='__main__':unittest.main()
