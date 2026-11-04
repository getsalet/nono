import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_claim_scrub as s
class ScrubTest(unittest.TestCase):
 def test_removes_banned_and_latin_sentences_only(self):
  o={'html':'<p>اقلیم این شهر معتدل است. پیش از خرید زمین را بررسی کنید.</p><li>از drip line استفاده کنید.</li>'}
  self.assertEqual(s.scrub(o),2);self.assertEqual(o['html'],'<p>پیش از خرید زمین را بررسی کنید.</p>')
 def test_never_touches_linked_sentence(self):
  o={'html':'<p>متن <a href="https://x.ir">لنگر</a> با اقلیم.</p>'};s.scrub(o);self.assertIn('<a href',o['html'])
 def test_allowed_latin_kept(self):
  o={'html':'<p>نوار AFP با پوشش UV.</p>'};self.assertEqual(s.scrub(o),0)
if __name__=='__main__':unittest.main()
