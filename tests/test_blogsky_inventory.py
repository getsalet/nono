import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
from blogsky_backlink_queue import preview
from blogsky_title_inventory import expand
from blog_city_priority import ordered

class BlogskyInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = preview(ROOT)

    def test_1500_blogsky_titles_only_real_645_tape_destinations(self):
        active=[x for x in self.queue['items'] if x['family']=='tape20']
        self.assertEqual(len(active),1500)
        self.assertEqual(len({x['key'] for x in active}),1500)
        titles=[x['title'] if x.get('published') else x['assigned_title'] for x in active]
        self.assertEqual(len(set(titles)),1500)
        self.assertEqual(len({x['target_url'] for x in active}),645)
        self.assertEqual(sum(bool(x.get('published')) for x in active),1)

    def test_variants_never_copy_drafts_or_publish_fields(self):
        variants=[x for x in self.queue['items'] if x.get('inventory_parent_key')]
        self.assertEqual(len(variants),855)
        for row in variants:
            self.assertEqual(row['status'],'pending')
            for key in ('post','published','pid','generated_at','published_url','image_review'):
                self.assertNotIn(key,row)

    def test_major_cities_are_first_and_expansion_is_idempotent(self):
        q=copy.deepcopy(self.queue)
        self.assertEqual(expand(q,ROOT),self.queue)
        pending=ordered([x for x in q['items'] if x['family']=='tape20' and not x.get('published')],ROOT)
        names=list(dict.fromkeys(x['city_fa'] for x in pending))
        cfg=json.loads((ROOT/'data/blog-city-priority.json').read_text())
        expected=[name for name in cfg['major_cities'] if name in names]
        self.assertEqual(names[:len(expected)],expected)
        before=json.loads((ROOT/'data/blogsky/backlink-queue.json').read_text())
        for row in before['items']:
            if row.get('published'):
                self.assertEqual(row,next(x for x in q['items'] if x['key']==row['key']))

if __name__=='__main__':unittest.main()
