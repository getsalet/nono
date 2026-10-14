import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RoyaNativeCardFallbackTests(unittest.TestCase):
 def setUp(self):self.template=(ROOT/'templates/royablog/afp-main.html').read_text()
 def test_styles_emitted_only_in_native_page_block(self):
  block=re.search(r'<fb:blog_page>(.*?)</fb:blog_page>',self.template,re.S).group(1)
  self.assertIn('id="afp-roya-native-card-fallback"',block)
  self.assertIn('class="afp-list-header"',block)
  self.assertLess(self.template.index('<fb:blog_page>'),self.template.index('<fb:royablog>'))
 def test_text_is_bounded_without_javascript(self):
  self.assertIn('max-height:8em!important;overflow:hidden!important',self.template)
  self.assertIn('#main-content .post-content :is(h1,h2,h3,h4,img,figure,details,table,ul,ol,iframe,video)',self.template)
 def test_full_article_link_not_conditional_on_split_body(self):
  self.assertIn('class="btn btn-outline btn-sm afp-native-read-more"',self.template)
  self.assertNotIn('<fb:post_short><a class="btn btn-outline btn-sm"',self.template)
 def test_enhancement_reuses_native_header(self):
  self.assertIn("main.querySelector(':scope > .afp-list-header')||document.createElement('header')",self.template)
  self.assertIn('main.append(pager);const topPager=pager.cloneNode(true)',self.template)
