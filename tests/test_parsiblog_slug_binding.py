import copy,inspect,json,unittest
from pathlib import Path
import parsiblog_pipeline as p
import parsiblog_policy as policy
ROOT=Path(__file__).resolve().parents[1]
class SlugMetadata(unittest.TestCase):
 def setUp(self):self.row=copy.deepcopy(json.loads((ROOT/'data/parsiblog/title-matrix.json').read_text())['items'][0])
 def test_observed_placeholder_slug_is_fixed_without_rewriting_article(self):
  post={'slug':'from-order-to-delivery-tape-irrigation-AFP_CITY','title':self.row['assigned_title'],'html':'<p>متن ثابت</p>','meta_description':'شرح ثابت','tags':['آبیاری']};before=copy.deepcopy(post);audit=p.bind_generated_slug(self.row,post);before['slug']=self.row['key'];self.assertEqual(post,before);self.assertEqual(audit['assigned_slug'],self.row['key']);self.assertIsNone(p.bind_generated_slug(self.row,post))
 def test_valid_slugs_are_not_changed(self):
  for slug in ['valid-existing-slug','abc','navar-tip-123']:
   post={'slug':slug};self.assertIsNone(p.bind_generated_slug(self.row,post));self.assertEqual(post['slug'],slug)
 def test_malformed_model_shapes_still_fail_full_qa(self):
  for post in [None,[],{}, {'slug':None},{'slug':123}]:
   before=copy.deepcopy(post);self.assertIsNone(p.bind_generated_slug(self.row,post));self.assertEqual(post,before)
 def test_protected_native_articles_cannot_be_rebound(self):
  for marker in ['published','id','native_phase']:
   row=dict(self.row,**{marker:True});post={'slug':'invalid_AFP_CITY'}
   with self.assertRaises(RuntimeError):p.bind_generated_slug(row,post)
   self.assertEqual(post['slug'],'invalid_AFP_CITY')
 def test_slug_fix_does_not_approve_bad_article(self):
  post={'title':self.row['assigned_title'],'slug':'invalid_AFP_CITY','meta_description':'شرح','tags':['آبیاری'],'html':'<p>для خاک این شهرستان رسی است.</p>'};p.bind_generated_slug(self.row,post);errors,_=policy.qa(self.row,post,require_image=False,originality=False);self.assertNotIn('Invalid Latin slug',errors);self.assertIn('Unexpected foreign-language text in Persian article',errors);self.assertTrue(errors)
 def test_binding_is_before_full_qa_and_review_and_never_in_publish_path(self):
  code=inspect.getsource(p.generate);self.assertLess(code.index('bind_generated_slug(item,obj)'),code.index('errors,report=qa('));self.assertLess(code.index('errors,report=qa('),code.index('review=agnes('));self.assertIn('for attempt in range(3)',code)
