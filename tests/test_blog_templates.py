import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RozPaginationTemplateTests(unittest.TestCase):
 def setUp(self):self.template=(ROOT/'templates/rozblog/afp-main.html').read_text()
 def test_native_server_pager_preserved(self):
  self.assertIn('<RB:Blog_Page_Block>',self.template)
  self.assertIn('[Blog_Page]',self.template)
  self.assertEqual(self.template.count('<ROZBLOG>'),1)
 def test_all_listing_pages_use_previews(self):
  self.assertIn("const isList=isHome||/^\\/pages\\/\\d+\\/?$/.test(location.pathname)",self.template)
  self.assertIn('if(isList){posts.forEach',self.template)
  self.assertIn("classList.toggle('is-list',isList",self.template)
 def test_single_article_guard_preserved(self):
  self.assertIn('const single=!isHome&&posts.length===1&&!!samePath',self.template)
  self.assertIn('if(single){',self.template)
  self.assertIn('(isHome?home:origin+location.pathname)',self.template)
