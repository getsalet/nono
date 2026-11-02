import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'automation'))
import roya_backlink_queue as r


class LinkDedupeTest(unittest.TestCase):
    def test_unwraps_only_repeated_destination(self):
        obj = {'html': '<p><a href="https://a.ir/x">A</a> و <a href="https://a.ir/x/">باز A</a> <a href="https://b.ir">B</a></p>'}
        out = r.dedupe_repeated_links(obj)['html']
        self.assertEqual(out.count('<a '), 2)
        self.assertIn('باز A', out)

    def test_recovery_only_for_link_only_failures(self):
        item = {'key': 'k', 'status': 'failed'}
        post = {'title': 't', 'slug': 's', 'html': '<a href="https://a.ir">x</a><a href="https://a.ir">y</a>'}
        rec = {'key': 'k', 'status': 'failed', 'post': post,
               'qa': {'passed': False, 'errors': ['6 links > 5', 'each destination URL may be linked at most once']}}
        self.assertIsNotNone(r.link_dedupe_draft(rec, item, {}))
        rec['qa']['errors'].append('banned claim: x')
        self.assertIsNone(r.link_dedupe_draft(rec, item, {}))
        rec['qa']['errors'].pop(); item['link_dedupe_recovery'] = r.LINK_DEDUPE_POLICY
        self.assertIsNone(r.link_dedupe_draft(rec, item, {}))


if __name__ == '__main__':
    unittest.main()
