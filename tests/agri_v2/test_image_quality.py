import base64,io,json,tempfile,unittest,hashlib
from pathlib import Path
from unittest.mock import Mock
from PIL import Image
from automation.agri_v2 import media_policy as m,image_quality as q
from automation.agri_v2.queue import load_json,atomic_json
class ImageQualityTests(unittest.TestCase):
 def topic(self):return {'id':'agri-af1a4b491d83','crop':'لوبیا قرمز','title':'زمان مناسب برداشت لوبیا قرمز'}
 def good(self):return {'score':95,'checks':{k:True for k in q.CHECKS},'reasons':['test fixture only']}
 def test_reference_scaling_preserves_original_ratio(self):
  raw=base64.b64decode((m.ASSETS/'afp-tape.webp.b64').read_text());im=Image.open(io.BytesIO(raw));p=m.reference_product()
  self.assertLess(abs(im.width/im.height-p.width/p.height),.02)
 def test_seed_color_not_red_pods_and_role2_not_panorama(self):
  p=m.image_prompt(self.topic(),2);self.assertIn('Red refers to seed-coat color',p);self.assertIn('straw-brown',p);self.assertIn('near-overhead',p);self.assertIn('no horizon',p)
 def test_pinto_distinct_seed_color(self):
  t=self.topic();t.update(crop='لوبیا چیتی',title='برداشت لوبیا چیتی');self.assertIn('brown mottling',m.crop_spec(t));self.assertNotIn('deep burgundy',m.crop_spec(t))
 def test_green_bean_not_dry_kidney(self):
  t=self.topic();t.update(crop='لوبیا سبز',title='برداشت لوبیا سبز');self.assertIn('attached green pods',m.crop_spec(t));self.assertNotIn('straw-brown',m.crop_spec(t));self.assertNotIn('straw-brown',m.scene_plan(t,2)['evidence'])
 def test_other_crop_never_forced_to_dry_beans(self):
  p=m.image_prompt({'crop':'گندم','title':'برداشت گندم'},2);self.assertIn('wheat',p);self.assertNotIn('dry bean',p)
 def test_word_boundary_prevents_garlic_from_masir(self):
  self.assertNotIn('garlic',m.crop_spec({'crop':'نامشخص','title':'مسیر آبیاری مزرعه'}))
 def test_article_content_binds_context_not_only_title(self):
  t=self.topic();self.assertNotEqual(m.contract_hash(t,2),m.contract_hash(t,2,{'content_html':'<p>ویژگی خاص مقاله</p>'}))
 def test_three_roles_are_distinct(self):
  plans=[m.scene_plan(self.topic(),i) for i in (1,2,3)];self.assertEqual(len({p['camera'] for p in plans}),3);self.assertIn('filter',plans[2]['evidence']);self.assertIn('no identifiable crop required',plans[2]['botany'])
 def test_invalid_role_fail_closed(self):
  for i in (0,4,'1',True):
   with self.assertRaises(ValueError):m.scene_plan(self.topic(),i)
 def test_missing_malformed_unknown_never_pass(self):
  for value in ({},{'pass':True,'score':100},None,{'checks':{k:'true' for k in q.CHECKS},'score':100,'reasons':['x']}):
   with self.assertRaises(q.ImageQualityError):q.verdict(value)
 def test_one_failed_critical_check_overrides_score(self):
  v=self.good();v['checks']['packaging_closed_no_protruding_material']=False;v['score']=100;self.assertFalse(q.verdict(v)['passed'])
 def test_no_fast_mode_or_vision_failure_pass(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image-2.webp';p.write_bytes(b'fixture');c=Mock();c.review_image.side_effect=TimeoutError()
   with self.assertRaises(q.ImageQualityError):q.ensure_review(c,p,self.topic(),2)
   self.assertEqual(load_json(q.review_path(p))['status'],'review_unavailable')
   with self.assertRaises(q.ImageQualityError):q.ensure_review(c,p,self.topic(),2)
   self.assertEqual(c.review_image.call_count,1)
 def test_approved_exact_hash_reused_changed_bytes_require_new_review(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image-2.webp';p.write_bytes(b'fixture');c=Mock();c.review_image.return_value=self.good()
   q.ensure_review(c,p,self.topic(),2);q.ensure_review(c,p,self.topic(),2);self.assertEqual(c.review_image.call_count,1)
   p.write_bytes(b'changed')
   with self.assertRaises(q.ImageQualityError):q.valid_record(p,self.topic(),2)
 def test_rejected_image_preserved_not_regenerated_or_reapproved(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'image-2.webp';p.write_bytes(b'fixture');c=Mock();v=self.good();v['checks']['product_scale_match']=False;c.review_image.return_value=v
   for _ in range(2):
    with self.assertRaises(q.ImageQualityError):q.ensure_review(c,p,self.topic(),2)
   self.assertEqual(p.read_bytes(),b'fixture');self.assertEqual(c.review_image.call_count,1)
 def test_require_all_fails_without_receipts(self):
  with tempfile.TemporaryDirectory() as d:
   for k in (1,2,3):(Path(d)/f'image-{k}.webp').write_bytes(b'fixture')
   with self.assertRaises(q.ImageQualityError):q.require_all(d,self.topic())
