import sys,unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
from content_originality import PublishedBody
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
class HeaderTests(unittest.TestCase):
 def setUp(self):self.template=(ROOT/'templates/blogsky/afp-single-post.html').read_text()
 def test_header_is_once_and_outside_contextual_article(self):
  self.assertEqual(self.template.count('class="afp-post-header"'),1)
  self.assertLess(self.template.index('class="afp-post-header"'),self.template.index('class="afp-article-body"'))
  self.assertEqual(self.template.count('{{ARTICLE_HTML}}'),1)
 def test_raw_article_is_unchanged_by_wrapper(self):
  article='<p>مقاله اصلی <a href="https://navar-abyari.ir/">نوار آبیاری</a></p>'+''.join('<details><summary>سؤال</summary><p>پاسخ معتبر</p></details>' for _ in range(3))
  parser=PublishedBody('afp-article-body');parser.feed(self.template.replace('{{ARTICLE_HTML}}',article));self.assertTrue(parser.done);self.assertEqual(''.join(parser.parts),article)
 def test_hiding_native_header_is_scoped_to_single_post_marker(self):
  self.assertIn('body:has(#afp-post) .main-container>.sticky-nav,body:has(#afp-post) .main-container>.parallax-container{display:none!important}',self.template)
  self.assertNotIn('.main-container>.parallax-container{display:none}',self.template)
  self.assertIn('padding-top:176px!important',self.template);self.assertIn('padding-top:168px!important',self.template)
 def test_native_mobile_menu_and_source_logo_no_new_script(self):
  tags=Tags();tags.feed(self.template)
  self.assertFalse(any(t=='script' for t,_ in tags.tags))
  self.assertEqual(len([a for t,a in tags.tags if t=='details' and a.get('class')=='afp-header-menu']),1)
  self.assertTrue(any(t=='img' and 'afp-drip-tape.png' in a.get('src','') and a.get('alt') for t,a in tags.tags))
  self.assertIn('max-width:none!important;padding:8px 16px',self.template)
 def test_header_contact_and_store_are_real_destinations(self):
  header=self.template.split('<header class="afp-post-header"',1)[1].split('</header>',1)[0]
  self.assertIn('href="tel:+989134922013"',header);self.assertIn('href="https://navar-abyari.ir/shop/"',header)
  self.assertIn('aria-label="مسیر راهنما"',header);self.assertIn('min-height:44px',self.template)
if __name__=='__main__':unittest.main()
