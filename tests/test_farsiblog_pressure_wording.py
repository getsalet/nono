import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from farsiblog_pressure_wording import normalize,errors
class WordingTests(unittest.TestCase):
 def test_narrow_nonmutating_repair(self):
  post={'title':'ثابت','html':'<p>نرمال‌کننده فشار و نرمال کننده فشار</p><a href="https://example.test/نرمال‌کننده فشار">مرجع</a>'}
  result=normalize(post)
  self.assertEqual(result['html'],'<p>تنظیم‌کننده فشار و تنظیم‌کننده فشار</p><a href="https://example.test/نرمال‌کننده فشار">مرجع</a>')
  self.assertEqual(result['title'],post['title']);self.assertIn('نرمال',post['html'])
  self.assertEqual(normalize(result),result);self.assertEqual(errors(result),[]);self.assertTrue(errors(post))
 def test_censored_public_text_still_rejected(self):
  from blog_public_content_verify import verify_article_body
  html='<p>نرمال‌کننده فشار</p>'+''.join('<details><summary>پرسش</summary><p>پاسخ</p></details>'for _ in range(3))
  item={'post':{'html':html},'image_url':None}
  with self.assertRaises(RuntimeError):verify_article_body(item,html.replace('نرمال','ن********'),[])
 def test_unrelated_prose_unchanged(self):
  post={'html':'<p>شرایط نرمال و فشار کاری؛ سه پرسش</p>'}
  self.assertEqual(normalize(post),post)
if __name__=='__main__':unittest.main()
