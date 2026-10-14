import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RoyaPaginatedCardTests(unittest.TestCase):
 def setUp(self):self.template=(ROOT/'templates/royablog/afp-main.html').read_text()
 def test_native_server_pagination_retained(self):
  for token in ('<fb:blog_page>','<fb:page_item>','[#page_link#]','[#page_num#]'):
   self.assertIn(token,self.template)
  self.assertIn("main.querySelector(':scope > .pagination')",self.template)
  self.assertIn("pager.cloneNode(true)",self.template)
 def test_responsive_card_grid(self):
  self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',self.template)
  self.assertIn('@media(max-width:700px)',self.template)
  self.assertIn('body.afp-card-list .home-intro{display:none!important}',self.template)
 def test_full_article_route_is_not_truncated(self):
  self.assertIn("route[1]==='post'&&Number(route[2])>0",self.template)
  self.assertIn('if(single||!posts.length)return;',self.template)
  self.assertIn('const samePath=',self.template)
 def test_native_template_sanitizer_safe_script(self):
  script=re.search(r'<script id="afp-roya-list-cards-script">(.*?)</script>',self.template,re.S).group(1)
  self.assertNotIn(chr(92),script)
  self.assertIn("path.endsWith('/')",script)
