import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'automation'))
import build_blogsky_title_matrix as subject

class BlogskyTitleMatrixTests(unittest.TestCase):
    def setUp(self):
        self.value = subject.build(ROOT)

    def test_matches_generator_titles_and_never_includes_held_family(self):
        from city_backlink_policy import matrix_title
        from blog_generated_image import family_enabled
        queue = subject.preview(ROOT)
        by_key = {r['key']: r for r in self.value['titles']}
        self.assertEqual(set(by_key), {i['key'] for i in queue['items'] if family_enabled(i, ROOT)})
        for item in queue['items']:
            if item['key'] in by_key and not item.get('published'):
                self.assertEqual(by_key[item['key']]['title'], matrix_title(item, 'blogsky', ROOT))

    def test_unique_titles_scoped_evidence_and_exact_destinations(self):
        from blog_city_editorial import title_errors
        rows = self.value['titles']
        queue = {i['key']: i for i in subject.preview(ROOT)['items']}
        self.assertEqual(len(rows), len({r['title'] for r in rows}))
        self.assertEqual(len(rows), len({r['key'] for r in rows}))
        for row in rows:
            self.assertEqual(row['target_url'], queue[row['key']]['target_url'])
            if row['state'] != 'published_locked':
                self.assertFalse(title_errors(queue[row['key']], row['title'], ROOT))

    def test_reproducible_and_no_input_mutation(self):
        before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                  for name in subject.INPUTS if (ROOT / name).exists()}
        again = subject.build(ROOT)
        self.assertEqual(self.value, again)
        self.assertEqual(before, again['input_sha256'])
        for name, digest in before.items():
            self.assertEqual(digest, hashlib.sha256((ROOT / name).read_bytes()).hexdigest())

if __name__ == '__main__':
    unittest.main()
