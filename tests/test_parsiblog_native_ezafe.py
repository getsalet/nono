import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from parsiblog_text import render_native_ezafe,post_language_errors
class Tests(unittest.TestCase):
 def test_known_orthography_rendered_without_changing_destinations(self):
  p={'title':'نوار آبیاری','html':'<h2>برگهٔ فنی</h2><p>مطالعهٔ ۲۰ مدل <a href="https://example.org/برگهٔ">راهنما</a></p>','meta_description':'مشاهدهٔ مشخصات','tags':['برگهٔ فنی']}
  self.assertEqual(render_native_ezafe(p),4);self.assertIn('برگه\u200cی فنی',p['html']);self.assertIn('https://example.org/برگهٔ',p['html']);self.assertIn('۲۰',p['html']);self.assertNotIn('Unsupported combining hamza requires native-safe Persian spelling',post_language_errors(p));before=copy.deepcopy(p);self.assertEqual(render_native_ezafe(p),0);self.assertEqual(p,before)
 def test_unknown_combining_form_remains_blocked(self):
  p={'html':'<p>أ آزمون</p>'};self.assertEqual(render_native_ezafe(p),0);self.assertTrue(post_language_errors(p))
 def test_title_not_silently_changed(self):
  p={'title':'برگهٔ فنی','html':'<p>متن</p>'};render_native_ezafe(p);self.assertEqual(p['title'],'برگهٔ فنی');self.assertTrue(post_language_errors(p))
 def test_corrupt_question_marks_are_not_accepted_as_equivalent(self):
  from parsiblog_native import normalized_body
  self.assertNotEqual(normalized_body('برگهٔ'),normalized_body('برگه?'))
if __name__=='__main__':unittest.main()
