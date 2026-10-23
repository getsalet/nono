"""Regression tests for the disabled Niloblog planning matrix."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('niloblog_matrix_validator',ROOT/'automation/validate_niloblog_matrix.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class NiloblogMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/'data/niloblog/title-matrix.json').read_text());cls.c=json.loads((ROOT/'data/niloblog/article-targets.json').read_text());cls.config=json.loads((ROOT/'data/niloblog/integration-plan.json').read_text())
    def test_short_title_cap(self):
        self.assertLessEqual(max(len(r['title']) for r in self.m['titles']),78)
        m=copy.deepcopy(self.m);m['titles'][0]['title']+=' آبیاری'*30;self.assertTrue(mod.validate(m,self.c))
    def test_article_length_profile(self):
        self.assertEqual(self.m['editorial_contract']['seo']['article_target_words'],[600,900])
        self.assertTrue(self.m['editorial_contract']['seo']['no_padding_to_hit_minimum'])
    def test_valid_matrix(self):self.assertEqual(mod.validate(self.m,self.c),[])
    def test_exactly_one_thousand_unique_titles(self):self.assertEqual(len({mod.normalize(r['title']) for r in self.m['titles']}),1000)
    def test_duplicate_rejected(self):
        m=copy.deepcopy(self.m);m['titles'][1]['title']=m['titles'][0]['title'];self.assertTrue(mod.validate(m,self.c))
    def test_publication_not_enabled(self):
        self.assertFalse(self.m['publication_enabled']);control=json.loads((ROOT/'data/niloblog/runtime-control.json').read_text());self.assertEqual(bool(self.config.get('runtime_enabled')),bool(control['enabled']));self.assertEqual(control['rolling_hourly_limit'],2);self.assertTrue(control['publication_authorized_by_user']);m=copy.deepcopy(self.m);m['publication_enabled']=True;self.assertTrue(mod.validate(m,self.c))
    def test_unverified_example_cannot_be_unlocked(self):
        m=copy.deepcopy(self.m);m['titles'][0]['review_state']='editorial_review_required';self.assertTrue(mod.validate(m,self.c))
    def test_link_budget_and_keyword(self):
        m=copy.deepcopy(self.m);next(iter(m['link_plans'].values()))['max_links']=4;self.assertTrue(mod.validate(m,self.c));self.assertEqual(self.m['editorial_contract']['link_budget'],[2,3])
    def test_county_scope_not_silently_city_scope(self):
        m=copy.deepcopy(self.m);r=next(x for x in m['titles'] if 'شهرستان' in x['title']);r['title']=r['title'].replace('شهرستان ','');self.assertTrue(mod.validate(m,self.c))
    def test_credential_names_only(self):
        self.assertEqual(self.config['credential_secret_names'],{'username':'NILOBLOG_USERNAME','password':'NILOBLOG_PASSWORD'});self.assertIsInstance(self.config['credentials_verified'],bool);self.assertFalse(self.config['credential_values_stored'])
    def test_verified_media_does_not_enable_generator(self):
        self.assertIn(self.config['image_status'],('catalog_verified_adapter_pending','37_webp_host_verified_native_canary_blocked','catalog_webp_verified_first_native_receipt_verified'));self.assertFalse(self.config['image_generation_enabled']);
        if self.config['media_policy']['runtime_integration_enabled']:
            self.assertTrue(self.config['media_policy']['native_media_rendering_tested']);receipts=list((ROOT/'artifacts/niloblog/receipts').glob('*.json'));self.assertTrue(receipts);self.assertTrue(any(json.loads(p.read_text()).get('image_decoded') for p in receipts))
    def test_destinations_are_https_main_site(self):
        c=copy.deepcopy(self.c);c['targets'][0]['target_url']='https://example.org/';self.assertTrue(mod.validate(self.m,c))
if __name__=='__main__':unittest.main()
