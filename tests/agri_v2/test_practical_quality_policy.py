import hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from automation.agri_v2 import image_quality as q
from automation.agri_v2.queue import load_json,atomic_json,OUT,get_topic
class PracticalQualityPolicyTests(unittest.TestCase):
 def good(self):return {'score':85,'checks':{k:True for k in q.CHECKS},'reasons':['fixture']}
 def test_cosmetic_differences_not_hard_rejections(self):
  v=self.good()
  for key in q.COSMETIC_CHECKS:v['checks'][key]=False
  self.assertTrue(q.verdict(v)['passed']);v['score']=84;self.assertFalse(q.verdict(v)['passed'])
 def test_every_critical_defect_still_blocks(self):
  for key in q.CHECKS:
   if key in q.COSMETIC_CHECKS:continue
   v=self.good();v['score']=100;v['checks'][key]=False;self.assertFalse(q.verdict(v)['passed'],key)
 def test_owner_accepted_real_85_evidence_reassessed_without_calls_or_score_change(self):
  f=OUT/'new/agri-a4f1fee1e3ee';p=f/'image-1.webp';before=q.review_path(p).read_bytes();c=Mock()
  row=q.ensure_review(c,p,get_topic('new','agri-a4f1fee1e3ee'),1,load_json(f/'article.json'))
  self.assertEqual(row['verdict']['score'],85);self.assertTrue(row['verdict']['passed']);self.assertFalse(row['new_visual_review_claimed']);c.review_image.assert_not_called();self.assertEqual(q.review_path(p).read_bytes(),before)
 def test_changed_image_cannot_reuse_old_policy_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image.webp';p.write_bytes(b'old');t={'id':'fixture','title':'برداشت لوبیا چیتی','crop':'لوبیا چیتی'}
   row={**q.binding(p,t,1),'status':'reviewed','verdict':self.good(),'review_policy':q.PREVIOUS_REVIEW_POLICY};row['verdict']['passed']=False;atomic_json(q.review_path(p),row);p.write_bytes(b'new')
   with self.assertRaises(q.ImageQualityError):q.valid_record(p,t,1)
 def test_prior_critical_rejection_not_reassessed_into_pass(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image.webp';p.write_bytes(b'fixture');t={'id':'fixture','title':'برداشت لوبیا چیتی','crop':'لوبیا چیتی'};v=self.good();v['checks']['single_product']=False;v['passed']=False
   atomic_json(q.review_path(p),{**q.binding(p,t,1),'status':'reviewed','review_policy':q.PREVIOUS_REVIEW_POLICY,'verdict':v})
   with self.assertRaises(q.ImageQualityError):q.valid_record(p,t,1)
