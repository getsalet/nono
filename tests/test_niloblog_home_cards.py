"""Homepage-only six-card layout and progressive pagination safeguards."""
import unittest
from pathlib import Path
class HomepageCardsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=(Path(__file__).resolve().parents[1]/'templates/niloblog/afp-professional.html').read_text()
 def test_only_homepage_and_six_per_page(self):
  for token in ["dataset.view!=='home')return",'var pageSize=6','id="afp-home-cards"']:
   self.assertIn(token,self.html)
 def test_two_columns_mobile_one(self):
  self.assertIn('.home-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))',self.html)
  self.assertIn('.home-card-grid{grid-template-columns:minmax(0,1fr)',self.html)
 def test_image_box_is_non_shrinking(self):
  self.assertIn('.card-media{display:block;position:relative;flex-shrink:0;',self.html)
  self.assertIn('.card-media img{position:absolute;inset:0;',self.html)
 def test_excerpt_and_real_article_links(self):
  for token in ['text.length<=170','summary.textContent=text','read.href=url','media.href=url','body.hidden=true']:
   self.assertIn(token,self.html)
 def test_sitemap_pagination_and_recovery(self):
  for token in ["fetch('/sitemap.xml'","'#afp-page='+page","'hashchange'","activePage!==1","aria-current","تلاش دوباره","requestVersion"]:
   self.assertIn(token,self.html)
 def test_fetched_content_is_constrained(self):
  for token in ['u.origin===location.origin',"post.querySelectorAll('script,iframe,object,embed')",'/^on/i.test(a.name)','made.dataset.articleUrl!==url']:
   self.assertIn(token,self.html)
if __name__=='__main__':unittest.main()
