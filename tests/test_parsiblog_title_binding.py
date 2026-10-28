"""Approved title metadata is deterministic; body QA and independent review stay mandatory."""
import copy,inspect,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import parsiblog_pipeline as p
import parsiblog_policy as policy
class TitleBindingTests(unittest.TestCase):
 def setUp(self):
  self.row=copy.deepcopy(json.loads((ROOT/'data/parsiblog/title-matrix.json').read_text())['items'][0])
 def test_real_matrix_title_is_authoritative(self):
  self.assertEqual(p.approved_assigned_title(self.row),self.row['assigned_title'])
 def test_changed_row_metadata_cannot_bind(self):
  for key,value in [('assigned_title','عنوان ساخته شده جدید'),('family','other'),('city_fa','جای دیگر'),('target_url','https://example.invalid')]:
   row=dict(self.row);row[key]=value
   with self.subTest(key=key),self.assertRaises(RuntimeError):p.approved_assigned_title(row)
 def test_unapproved_missing_duplicate_and_invalid_titles_fail_closed(self):
  for edit in ('unapproved','missing','duplicate','badtitle'):
   with self.subTest(edit=edit),tempfile.TemporaryDirectory()as td:
    row=copy.deepcopy(self.row);data={'approved':True,'count':1000,'items':[row]}
    if edit=='unapproved':data['approved']=False
    if edit=='missing':data['items']=[]
    if edit=='duplicate':data['items']*=2
    if edit=='badtitle':row['assigned_title']='invalid foreign title'
    path=Path(td);(path/'title-matrix.json').write_text(json.dumps(data))
    with patch.object(p,'DATA',path),self.assertRaises(RuntimeError):p.approved_assigned_title(row)
 def test_binding_changes_only_title_and_is_auditable_and_idempotent(self):
  obj={'title':'عنوان مدل با واژه متفاوت','slug':'stable-slug','meta_description':'شرح ثابت','tags':['آبیاری'],'html':'<p>متن ثابت و لینک https://x.test/</p>'};before=copy.deepcopy(obj)
  audit=p.bind_assigned_title(obj,self.row['assigned_title']);self.assertTrue(audit['changed']);before['title']=self.row['assigned_title'];self.assertEqual(obj,before);self.assertNotEqual(audit['model_title_sha256'],audit['assigned_title_sha256']);self.assertFalse(p.bind_assigned_title(obj,self.row['assigned_title'])['changed'])
 def test_invalid_model_shape_is_not_silently_repaired(self):
  for obj in (None,[],{}, {'title':None},{'title':[]}):
   before=copy.deepcopy(obj);self.assertIsNone(p.bind_assigned_title(obj,self.row['assigned_title']));self.assertEqual(obj,before)
 def test_wrong_body_still_fails_actual_quality_gate(self):
  obj={'title':'عنوان متفاوت','slug':'stable-slug','meta_description':'شرح','tags':['آبیاری'],'html':'<p>или خاک این شهرستان رسی است.</p>'};p.bind_assigned_title(obj,self.row['assigned_title'])
  errors,_=policy.qa(self.row,obj,require_image=False,originality=False)
  self.assertNotIn('Assigned matrix title required',errors);self.assertIn('Unexpected foreign-language text in Persian article',errors);self.assertTrue(any('Unverified locality' in e for e in errors));self.assertTrue(policy.review_errors(self.row,obj))
 def test_binding_precedes_full_qa_review_and_images_with_same_retry_budget(self):
  code=inspect.getsource(p.generate);self.assertLess(code.index('approved_assigned_title(item)'),code.index('agnes(request'));self.assertLess(code.index('bind_assigned_title(obj,assigned_title)'),code.index('errors,report=qa('));self.assertLess(code.index('errors,report=qa('),code.index('review=agnes('));self.assertLess(code.index('review=agnes('),code.index("run_report(phase='image_preflight'"));self.assertIn('for attempt in range(3)',code)
if __name__=='__main__':unittest.main()
