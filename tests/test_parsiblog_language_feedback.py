import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from parsiblog_text import language_feedback,post_language_errors
class LanguageFeedbackTests(unittest.TestCase):
 def test_mixed_word_identified_and_original_never_mutated(self):
  obj={'title':'عنوان فارسی','html':'<p>نامodel را ثبت کنید.</p>'};old=copy.deepcopy(obj)
  self.assertEqual(language_feedback(obj),[{'field':'body','invalid_visible_token':'نامodel'}]);self.assertEqual(obj,old);self.assertTrue(post_language_errors(obj))
 def test_urls_slug_html_and_afp_are_not_prose_errors(self):
  obj={'title':'راهنمای AFP','slug':'navar-tip','html':'<p><a href="https://navar-abyari.ir/path/">بررسی نوار تیپ AFP</a></p>'}
  self.assertEqual(language_feedback(obj),[])
 def test_foreign_scripts_and_metadata_are_diagnosed(self):
  x=language_feedback({'title':'بررسی α','tags':['مدلЖ'],'meta_description':'توضیح model','html':'<p>检查 مشخصات</p>'})
  self.assertEqual({t['field']for t in x},{'title','tag','meta_description','body'})
 def test_feedback_is_bounded_and_language_gate_unchanged(self):
  self.assertEqual(len(language_feedback({'html':'<p>'+' '.join('word'+str(i)for i in range(30))+'</p>'})),8)
  self.assertTrue(post_language_errors({'html':'<p>الف x ب</p>'}))
if __name__=='__main__':unittest.main()
