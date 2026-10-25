import unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import curated_continuation as c
from automation.agri_v2.queue import DATA,OUT,load_json,get_topic
from automation.agri_v2.pipeline import validate_article,validate_for_publication
from automation.agri_v2.failure_diagnostics import failure_details
class CuratedContinuationTests(unittest.TestCase):
 def req(self):return load_json(DATA/'curated-continuation-request.json')
 def test_exact_separate_budget_and_bound_source_hashes(self):
  r=self.req();c.validate(r);f=OUT/'new'/c.TOPIC
  self.assertEqual(c.sha(f/'article.json'),r['article_sha256']);self.assertEqual(c.sha(f/'model-candidate.json'),r['original_candidate_sha256']);self.assertEqual(load_json(f/'cycle-attempts.json')['attempts'],2)
  r['max_image_calls']=4
  with self.assertRaises(ValueError):c.validate(r)
 def test_curated_article_existing_scientific_and_language_gates(self):
  a=load_json(OUT/'new'/c.TOPIC/'article.json');b=load_json(DATA/'briefs'/f'{c.TOPIC}.json');validate_article(a,get_topic('new',c.TOPIC),b);validate_for_publication(a)
 def test_never_generates_more_article_text(self):
  with self.assertRaises(c.CapabilityError):c.BoundedClient.text(object(),'fixture')
 def test_safe_validation_reason_not_raw_exception(self):
  self.assertEqual(failure_details(ValueError('Draft must cite approved sources inline'))['category'],'missing_approved_inline_citation')
  self.assertEqual(failure_details(ValueError('private data'))['category'],'unspecified')
