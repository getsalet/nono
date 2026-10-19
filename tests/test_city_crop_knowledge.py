import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import build_city_crop_knowledge as k

class KnowledgeTests(unittest.TestCase):
    def test_complete_destination_decisions_do_not_claim_complete_research(self):
        rows,s,sources,claims=k.build(ROOT)
        self.assertEqual(len(rows),645)
        self.assertEqual(s['approved_target_count'],8)
        self.assertEqual(sum(s['status_counts'].values()),645)
        self.assertEqual(len(sources),13)
        self.assertEqual(len(claims),27)
        self.assertEqual(s['completion'],'incomplete_local_cultivation_research')
        self.assertTrue(any(r['knowledge_status']=='not_adjudicated'for r in rows))
        for r in rows:
            if not r['approved_crops']:
                self.assertEqual(r['publication_decision'],'crop_free_until_approved')

    def test_scope_system_and_storage_are_not_silently_approved(self):
        rows,s,_,claims=k.build(ROOT)
        byplace={r['place_fa']:r for r in rows}
        for place in ('تیمورلو','زاهدان','دلگان','فامنین','فارسان','بروجن'):
            self.assertFalse(byplace[place]['approved_crops'],place)
        self.assertEqual(byplace['تیمورلو']['knowledge_status'],'context_not_cultivation')
        self.assertEqual(byplace['فامنین']['knowledge_status'],'historical_policy_caution')
        self.assertIn('kowsar-tomato-2026',s['unattached_claim_ids'])
        self.assertFalse(any('kowsar-tomato-2026'in r['claim_ids']for r in rows))

    def test_repeated_names_keep_different_target_keys(self):
        rows,_,_,_=k.build(ROOT)
        sardasht=[r for r in rows if r['place_fa']=='سردشت']
        self.assertEqual(len(sardasht),2)
        self.assertEqual(len({r['target_key']for r in sardasht}),2)
        self.assertTrue(all(r['geography_flags']for r in sardasht))

    def test_future_source_and_orphan_claim_fail_closed(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d)
            for path in ('data/blog-city-title-inventory.json','data/roya/backlink-queue.json',
                         'data/blog-city-crop-evidence.json','data/blog-city-title-matrix.json',
                         'data/city-crop-knowledge/sources.json','data/city-crop-knowledge/claims.json'):
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text((ROOT/path).read_text())
            p=root/'data/city-crop-knowledge/claims.json'
            original=json.loads(p.read_text());bad=copy.deepcopy(original)
            bad['claims'][0]['source_id']='missing'
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'Orphan'):k.build(root)
            p.write_text(json.dumps(original))
            p=root/'data/city-crop-knowledge/sources.json'
            bad=json.loads(p.read_text());bad['sources'][0]['source_date']='2999-01-01'
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'Future'):k.build(root)

    def test_source_claim_approval_consistency(self):
        rows,s,sources,claims=k.build(ROOT)
        approved=[r for r in rows if r['approved_crops']]
        self.assertEqual({r['place_fa']for r in approved},
                         {'طارم','بهار','اسدآباد','تاکستان','ارومیه','میاندوآب','آذرشهر','هوراند'})
        self.assertEqual(sum(c['source_id']=='mehr-6920740'for c in claims),3)
        self.assertEqual(sum(c['source_id']=='mehr-6905006'for c in claims),4)

if __name__=='__main__':unittest.main()