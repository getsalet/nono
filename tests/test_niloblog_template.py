"""Static safeguards for the independently installed Niloblog template."""
import re
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / 'templates/niloblog/afp-professional.html'

class NiloblogTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding='utf-8')

    def test_google_verification_is_once_in_head(self):
        from bs4 import BeautifulSoup
        doc=BeautifulSoup(self.html,'html.parser')
        tags=doc.find_all('meta',attrs={'name':'google-site-verification'})
        self.assertEqual(len(tags),1)
        self.assertIsNotNone(tags[0].find_parent('head'))
        self.assertEqual(tags[0].get('content'),'mfvTYyYIDjhZyWQxwHLs9MwtTAeaMDnBkHeU3te-ts8')

    def test_preserves_native_rendering(self):
        for tag in ['<NILOOBLOG>', '</NILOOBLOG>', '<-PostContent->', '<-PostLink->', '<-PostTitle->', '<BlogExtendedPost>', '<BlogLastPosts>', '<-PostSchema->', '<-BlogCustomHtml->']:
            self.assertIn(tag, self.html)

    def test_viewport_allows_zoom(self):
        self.assertIn('width=device-width,initial-scale=1', self.html)
        self.assertNotIn('user-scalable=0', self.html)
        self.assertNotIn('maximum-scale=1', self.html)

    def test_menu_accessibility_and_close(self):
        for value in ['aria-controls="site-nav"', 'aria-expanded="false"', "e.key==='Escape'", 'closeMenu()', '.nav{order:3}', '.actions{order:2}']:
            self.assertIn(value, self.html)

    def test_fluid_layout_and_contained_tables(self):
        self.assertIn('minmax(0,1fr) 320px', self.html)
        self.assertIn('.table-scroll{overflow-x:auto;', self.html)
        for width in ['360px', '600px', '900px', '1150px', '1800px']:
            self.assertIn(width, self.html)

    def test_font_has_cross_origin_compatible_source(self):
        self.assertIn('cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/', self.html)
        self.assertNotIn('6973vazir.woff2', self.html)

    def test_no_fake_sample_post_or_tracking_code(self):
        self.assertNotIn('این متن فقط برای آزمون', self.html)
        self.assertNotIn('googletagmanager', self.html)
        # The real user-authorized verification token is checked separately above.
        self.assertNotIn('G-XXXXXXXXXX', self.html)
        self.assertIn('میزبانی و انتشار با نیلوبلاگ', self.html)

    def test_real_brand_destinations(self):
        self.assertIn('tel:+989134922013', self.html)
        self.assertIn('mailto:sqroms@gmail.com', self.html)
        self.assertIn('https://navar-abyari.ir/shop/', self.html)
        self.assertIn('https://navar-abyari.ir/blog/', self.html)
        self.assertNotIn('آبیاری-قطره‌ای-در-کشت-سیر-راهنمای-جامع/', self.html)

    def test_system_theme_and_reduced_motion(self):
        self.assertIn('prefers-color-scheme:dark', self.html)
        self.assertIn('prefers-reduced-motion:reduce', self.html)
        self.assertIn('font-display:swap', self.html)

    def test_article_layout_compact_and_readable(self):
        for token in ['data-afp-template="article-layout-v2"', 'html[data-view=detail] .post{padding:28px;', 'max-width:760px', 'padding:20px 16px 32px', 'min-width:1600px']:
            self.assertIn(token, self.html)
        self.assertNotIn('inner', self.html)

    def test_wide_article_index_is_native_content_only(self):
        self.assertIn("querySelectorAll('.post-body h2')", self.html)
        self.assertIn("link.textContent=section.textContent", self.html)
        self.assertIn("index.setAttribute('aria-label','در این راهنما')", self.html)
        self.assertIn("reading.className='post-reading'", self.html)
        self.assertIn('.article-index{display:none}', self.html)

    def test_hamburger_has_fixed_touch_target(self):
        self.assertIn('.actions>#menu-toggle{display:grid;width:46px;height:46px}', self.html)

    def test_mobile_backtop_does_not_overlay_article_text(self):
        self.assertIn('.backtop{position:static;margin:0 16px 16px auto}', self.html)
        self.assertIn('text-wrap:balance', self.html)

if __name__ == '__main__':
    unittest.main()
