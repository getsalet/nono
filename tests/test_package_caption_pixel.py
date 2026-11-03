import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_package_labels as L
GOOD={'english_text':L.ENGLISH,'english_legible':True,'persian_text':L.PERSIAN,'persian_legible':True}
MISREAD={**GOOD,'persian_text':'آبگستر فرایران'}
def px(fa):return {'policy':L.PIXEL_POLICY,'sha256':'x','scores':{'persian':fa}}
class PixelCaptionTest(unittest.TestCase):
 def test_strong_pixel_match_overrides_ocr_misread(self):self.assertEqual(L.combined_errors(MISREAD,px(0.95)),[])
 def test_weak_pixel_match_keeps_ocr_error(self):self.assertTrue(L.combined_errors(MISREAD,px(0.87)))
 def test_pixel_mismatch_rejects_even_if_ocr_passes(self):self.assertIn('Package caption pixel mismatch: persian',L.combined_errors(GOOD,px(0.4)))
 def test_no_pixel_proof_is_unchanged(self):self.assertEqual(L.combined_errors(MISREAD,None),L.exact_errors(MISREAD))
if __name__=='__main__':unittest.main()
class EnglishUnchangedTest(unittest.TestCase):
 def test_english_ocr_error_never_overridden(self):
  r={**GOOD,'english_text':'Drip Tape'}
  self.assertIn('Exact package caption not independently read: english',L.combined_errors(r,px(0.99)))
