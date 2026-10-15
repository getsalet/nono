import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from repair_rozblog_images import replace_image,invariant
class ImageOnlyRepairTests(unittest.TestCase):
 def test_only_selected_image_src_changes(self):
  body='<p><img src="https://old.example/a.webp" alt="نوار تیپ" width="1200"></p><p>متن اصلی <a href="https://navar-abyari.ir/">نوار تیپ</a></p>'
  changed=replace_image(body,'https://old.example/a.webp','https://new.example/b.webp')
  self.assertEqual(invariant(body),invariant(changed));self.assertIn('alt="نوار تیپ"',changed);self.assertNotIn('https://old.example',changed)
 def test_missing_duplicate_or_wrong_image_blocks_all_writes(self):
  for body in ('<p>بدون عکس</p>','<img src="old"><img src="old">','<img src="other">'):
   with self.assertRaises(RuntimeError):replace_image(body,'old','new')
if __name__=='__main__':unittest.main()
