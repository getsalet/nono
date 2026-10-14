import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_post_excerpt import native_split,native_bodies
class NativeExcerptTests(unittest.TestCase):
 def setUp(self):
  self.body='<p><img src="https://example.com/image.webp" alt="AFP" /></p><p>'+('محتوای واقعی مقاله برای معرفی روش انتقال آب. '*4)+'</p><h2>ادامه مطلب</h2><p>'+('متن کامل باقی می‌ماند. '*30)+'</p>'
 def test_royablog_split_preserves_full_html_exactly(self):
  short,full=native_bodies(self.body,'https://www.royablog.ir')
  self.assertEqual(short+full,self.body);self.assertLess(len(short),600)
  self.assertNotIn('<h2>',short);self.assertIn('image.webp',short)
 def test_farsiblog_not_migrated_by_royablog_fix(self):
  self.assertEqual(native_bodies(self.body,'https://www.farsiblog.com'),(self.body,''))
 def test_escapes_real_paragraph_text(self):
  short,full=native_split('<p>'+('بررسی واقعی 2 &lt; 3 و انتقال آب. '*3)+'</p><p>'+('ادامه متن کامل. '*20)+'</p>');self.assertIn('&lt;',short)
 def test_empty_body_fails_closed(self):
  with self.assertRaises(ValueError):native_split('<p><img src="x"></p>')
 def test_real_publisher_fills_both_native_fields(self):
  text=(Path(__file__).resolve().parents[1]/'automation/publish_roya_posts.py').read_text()
  self.assertIn("setContent(post.native_short_html)",text)
  self.assertIn("setContent(post.native_full_html)",text)
