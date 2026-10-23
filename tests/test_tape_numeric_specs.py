import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from roya_backlink_queue import product_semantics_errors
class NumericTapeSpecTests(unittest.TestCase):
 def test_unsupported_numeric_examples_rejected(self):
  for text in ('ضخامت ۱٫۵ میلی‌متر برای کشت یک‌ساله','ضخامت 2 میلی متر','فشار ۰٫۸ بار','ضخامت ۱۷۵ میکرون','pressure 0.8 psi','film 1.5 mm'):
   self.assertTrue(product_semantics_errors({'family':'tape20'},'<p>'+text+'</p>'),text)
 def test_known_product_spacing_and_non_numeric_review_remain_allowed(self):
  self.assertEqual(product_semantics_errors({'family':'tape20'},'<p>نوار تیپ ۲۰ سانتی؛ ضخامت و فشار مجاز همان مدل را از تولیدکننده درخواست کنید.</p>'),[])
 def test_number_of_visits_is_not_a_pressure_spec(self):
  self.assertEqual(product_semantics_errors({'family':'tape20'},'<p>در ۲ بار بازدید، وضعیت را ثبت کنید.</p>'),[])
 def test_html_image_dimensions_are_not_article_specs(self):
  self.assertEqual(product_semantics_errors({'family':'tape20'},'<img width="1200" height="675"><p>مشخصات را بررسی کنید.</p>'),[])
if __name__=='__main__':unittest.main()
