import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class BlogskyHomeCardsTests(unittest.TestCase):
    def test_uses_live_native_widget_not_inline_script_or_frozen_post_list(self):
        html = (ROOT / 'templates/blogsky/afp-home.html').read_text()
        self.assertIn('Live native Blogsky recent-post cards', html)
        self.assertIn('.sidebar>.menu:has(>.head>a[href="/posts"])', html)
        self.assertNotIn('<script', html.lower())
        self.assertNotIn('afp-live-post-cards', html)
        self.assertNotIn('class="afp-post-card"', html)
        self.assertNotIn('حداکثر ۶', html)
        self.assertNotIn('۶ یادداشت اخیر', html)
        self.assertNotIn('هنوز مقاله‌ای در این وبلاگ منتشر نشده', html)

    def test_six_per_page_and_native_archive_navigation(self):
        value = json.loads((ROOT / 'data/blogsky/home-display.json').read_text())
        self.assertEqual(value['latest_card_count'], 6)
        self.assertEqual(value['native_posts_per_page'], 6)
        self.assertEqual(value['native_archive_per_page'], 6)
        self.assertFalse(value['client_script_required'])
        self.assertEqual(value['archive_url'], 'https://afp-pipe.blogsky.com/posts')
        html = (ROOT / 'templates/blogsky/afp-home.html').read_text()
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))', html)
        self.assertIn('grid-template-columns:minmax(0,1fr)', html)
        self.assertIn('مطالب قدیمی‌تر و صفحه‌بندی', html)
        self.assertIn('id="guides"', html)

if __name__ == '__main__':
    unittest.main()
