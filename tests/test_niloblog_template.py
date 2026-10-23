"""Static safeguards for the independently installed Niloblog template."""
import re
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / 'templates/niloblog/afp-professional.html'

class NiloblogTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding='utf-8')

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
        self.assertNotIn('google-site-verification', self.html)
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

if __name__ == '__main__':
    unittest.main()
