import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import calibrate_blog_images as c
from blog_image_art_direction import closed_package_prompt
class CalibrationTests(unittest.TestCase):
 def test_bounded_matched_cases(self):
  items=c.load_items();before=[x['key']for x in items];rows=c.cases(items)
  self.assertEqual(len(rows),6);self.assertEqual([x['key']for x in items],before)
  self.assertEqual([r['source_index']for _,r in rows],[0,1,0,1,2,0])
  self.assertEqual(len({x['key']for x,_ in rows}),6)
 def test_prompt_keeps_identity_and_actual_evidence(self):
  import blog_reference_scene as s
  for item in c.load_items():
   plan=s.scene_plan(item,'roya');p=closed_package_prompt(s.article(item),plan)
   self.assertIn(plan['evidence'],p);self.assertIn('tucked entirely INSIDE',p)
   self.assertIn('No loose white ribbon',p);self.assertIn('authentic AFP mark',p)
   self.assertIn('thin BLACK',p);self.assertLess(len(p),2600)
 def test_source_does_not_invoke_post_publication(self):
  text=Path(c.__file__).read_text()
  for term in ('save_post(', 'publish_post(', 'prepare_now(', 'runtime-control.json'):
   self.assertNotIn(term,text)
if __name__=='__main__':unittest.main()
