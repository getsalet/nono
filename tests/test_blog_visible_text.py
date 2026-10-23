import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from blog_visible_text import visible_text_errors
class VisiblePersianTextTests(unittest.TestCase):
 def test_approved_technical_abbreviations_remain_allowed(self):
  self.assertEqual(visible_text_errors({'title':'راهنمای AFP','html':'<p>بررسی PE و UV و ISO و cm و mm؛ نوار ۲۰ سانتی</p>'}),[])
 def test_foreign_scripts_and_mixed_words_blocked(self):
  for word in ['首先','привет','α','שלום','آبیarی','tape20','hose','AFP_LINK_1']:
   with self.subTest(word=word):self.assertTrue(visible_text_errors({'html':'<p>بررسی '+word+'</p>'}))
 def test_urls_html_names_and_slugs_are_not_visible_text(self):
  self.assertEqual(visible_text_errors({'slug':'english-slug','html':'<p><a href="https://example.com/русский">راهنما</a><img src="https://example.com/a.webp" alt="تصویر نوار"></p>'}),[])
 def test_metadata_and_alt_also_checked(self):
  for post in [{'title':'首先'},{'meta_description':'тест'},{'tags':['آبیاری','α']},{'html':'<img src="x" alt="آبbیاری">'}]:self.assertTrue(visible_text_errors(post))
 def test_corrupt_replacements_blocked(self):
  for token in ['???','��']:
   self.assertTrue(visible_text_errors({'html':'<p>'+token+'</p>'}))
 def test_shared_qa_paths_call_the_guard(self):
  for name in ['city_backlink_policy.py','roya_backlink_queue.py']:
   self.assertIn('visible_text_errors(obj)',(ROOT/'automation'/name).read_text())
if __name__=='__main__':unittest.main()
