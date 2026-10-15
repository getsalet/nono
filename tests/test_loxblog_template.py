import re, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
THEME=ROOT/'templates'/'loxblog'

class NativeLoxBlogThemeTests(unittest.TestCase):
 def read(self,name):return (THEME/(name+'.html')).read_text()
 def test_native_metadata_only(self):
  h=self.read('header')
  self.assertEqual(h.count('[LX:Head]'),1)
  tags=re.findall(r'<meta\s+name="google-site-verification"\s+content="([^"]+)"',h)
  self.assertEqual(set(tags),{'-BhLoljNdO2asCo1OjpTRZDWkhzl0RbWJCgrz-lCDqc','eA1pNGMD3C_odFB00bTqnmOZD9y2qY83hOGrfN2BVuI'})
  self.assertEqual(len(tags),len(set(tags)))
  self.assertIn('-BhLoljNdO2asCo1OjpTRZDWkhzl0RbWJCgrz-lCDqc',h)
  self.assertNotIn('canonical',h) # owned by LX:Head, not duplicated client-side
 def test_no_legacy_syntax(self):
  for f in THEME.glob('*.html'):
   s=f.read_text();self.assertNotRegex(s,r'<-\w+->|<BLOGFA>|<BlogExtendedPost>')
 def test_native_summary_and_pagination(self):
  s=self.read('index');self.assertEqual(s.count('<LOXBLOG>'),1)
  self.assertIn('[Post_Content]',s)
  self.assertIn('<LX:Post_More_Block>',s)
  self.assertIn('<LX:Blog_Page_Block>',s)
  self.assertIn('[Blog_Page]',s)
 def test_no_fake_summary_clipping(self):
  h=self.read('header')
  self.assertNotIn('line-clamp',h)
  self.assertNotRegex(h,r'\.post-(?:content|excerpt)[^{]*\{[^}]*overflow\s*:\s*hidden')
 def test_single_post_native_body(self):
  s=self.read('article');self.assertEqual(s.count('<h1'),1)
  self.assertIn('[Post_Content]',s)
  self.assertIn('article-route',s)
  self.assertNotIn('<LX:Post_Image>',s) # native body already carries its approved image
 def test_comments_not_inserted(self):
  for f in THEME.glob('*.html'):
   s=f.read_text();self.assertNotIn('Post_Comment',s);self.assertNotIn('Comment_Form',s)
 def test_logo_navigation_and_footer(self):
  h=self.read('header');f=self.read('footer')
  self.assertIn('afp-drip-tape.png',h);self.assertIn('afp-drip-tape.png',f)
  self.assertIn('<details class="nav-products afp-mega">',h)
  self.assertIn('tel:09134922013',f)
  self.assertIn('[LX:Blog_Xml_Link]',f)
  self.assertIn('https://loxblog.com/',f)
 def test_shared_fragments(self):
  for name in ('index','article','category','page','404','offline'):
   s=self.read(name)
   self.assertTrue(s.startswith('[LX:Header]'))
   self.assertTrue(s.endswith('[LX:Footer]'))

if __name__=='__main__':unittest.main()
