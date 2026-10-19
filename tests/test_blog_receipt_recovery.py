import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from blog_public_content_verify import verify_article_body
class ReceiptRecoveryTests(unittest.TestCase):
 def setUp(self):
  self.html='<p>کیفیت و كميت آب؛ مقدار ۱۲ ثابت است.</p><a href="https://example.com/a">الف</a><a href="https://example.com/b">ب</a>'+''.join('<details><summary>پرسش</summary><p>پاسخ</p></details>'for _ in range(3))
  self.item={'post':{'html':self.html}};self.links=[{'url':'https://example.com/a'},{'url':'https://example.com/b'}]
 def test_persian_native_letter_conversion_is_equivalent(self):
  self.assertTrue(verify_article_body(self.item,self.html.replace('ك','ک').replace('ي','ی'),self.links))
 def test_changed_words_numbers_backlinks_or_faqs_still_fail(self):
  for body in [self.html.replace('۱۲','۱۳'),self.html.replace('ثابت','متغیر'),self.html.replace('example.com/b','evil.example/b'),self.html.replace('<details>','<div>').replace('</details>','</div>')]:
   with self.subTest(body=body),self.assertRaises(RuntimeError):verify_article_body(self.item,body,self.links)
 def test_recovery_has_no_native_submit_or_generation(self):
  s=(ROOT/'automation/recover_existing_blog_receipt.py').read_text()
  for forbidden in ['.click(','.submit(','.publish(','.begin(','.agnes(','button.click']:
   self.assertNotIn(forbidden,s)
  self.assertIn('publisher.find_native_record(page',s);self.assertIn('publisher.verify(public,item',s)
  self.assertLess(s.index('url=publisher.verify'),s.index('native.checkpoint'))
  self.assertIn("'recovered_existing':True",s)
 def test_lox_native_alias_fallback_does_not_resubmit(self):
  s=(ROOT/'automation/publish_loxblog_posts.py').read_text()
  self.assertEqual(s.count('button.click()'),1)
  self.assertIn('native_record=find_native_record(page,title)',s)
  self.assertIn("finally:journal(e,'unconfirmed')",s)
if __name__=='__main__':unittest.main()
