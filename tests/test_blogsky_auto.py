import copy
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import blogsky_auto_control as auto
import publish_blogsky_posts as publisher
import blogsky_native as native

class AutomaticBlogskyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.write('data/blogsky/native-publication-control.json',auto.AUTOMATIC)
        self.write('data/blog-generated-image-control.json',{'pause_image_production':False,'enabled_families':['tape20'],'cancelled_families':['hose']})
    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
    def test_configuration_requires_exact_automatic_authorization(self):
        self.assertTrue(auto.preflight(self.root))
        for cfg in (auto.MANUAL,{**auto.AUTOMATIC,'max_count_per_run':2},{**auto.AUTOMATIC,'enabled':False},{**auto.AUTOMATIC,'min_interval_minutes':1}):
            self.write('data/blogsky/native-publication-control.json',cfg)
            with self.assertRaises(RuntimeError):auto.preflight(self.root)
    def test_global_stop_or_unconfirmed_submit_blocks_automatic_generation(self):
        self.write('data/blog-generated-image-control.json',{'pause_image_production':True})
        with self.assertRaises(RuntimeError):auto.preflight(self.root)
        self.write('data/blog-generated-image-control.json',{'pause_image_production':False})
        self.write('artifacts/blogsky-backlink-queue/native-publications/key.json',{'phase':'submitted_unverified'})
        with self.assertRaises(RuntimeError):auto.preflight(self.root)
    def test_at_most_one_verified_post_per_twenty_minutes(self):
        now=dt.datetime.now(dt.timezone.utc)
        self.write('state/blogsky-backlink-progress.json',{'published':[{'at':(now-dt.timedelta(minutes=19,seconds=59)).isoformat()}]})
        self.assertFalse(auto.interval_open(self.root,now))
        self.write('state/blogsky-backlink-progress.json',{'published':[{'at':(now-dt.timedelta(minutes=20)).isoformat()}]})
        self.assertTrue(auto.interval_open(self.root,now))
        self.write('state/blogsky-backlink-progress.json',{'published':[{'at':(now+dt.timedelta(minutes=1)).isoformat()}]})
        self.assertFalse(auto.interval_open(self.root,now))
        for stamp in ('bad','2026-01-01T00:00:00'):
            self.write('state/blogsky-backlink-progress.json',{'published':[{'at':stamp}]})
            with self.assertRaises(RuntimeError):auto.interval_open(self.root,now)
    def test_only_completed_unpublished_enabled_family_in_priority_order(self):
        row={'kind':'city','family':'tape20','status':'completed'}
        self.write('data/blogsky/backlink-queue.json',{'items':[
            {**row,'key':'pending','status':'pending'},
            {**row,'key':'held','family':'hose'},
            {**row,'key':'already','published':True},
            {**row,'key':'second','city_fa':'رشت'},
            {**row,'key':'first','city_fa':'تهران'}]})
        cfg=json.loads((ROOT/'data/blog-city-priority.json').read_text());self.write('data/blog-city-priority.json',cfg)
        self.assertEqual(auto.select_target(self.root),'first')
    def test_no_ready_post_never_logs_in(self):
        with patch.dict(os.environ,{'BLOGSKY_NATIVE_MODE':'auto-one'}),patch.object(native,'login',side_effect=AssertionError('No login')):
            self.assertEqual(publisher.run(None,None,self.root),0)
    def test_automatic_intent_requires_remote_durability_before_submit(self):
        receipt=self.root/'artifacts/blogsky-backlink-queue/native-publications/key.json'
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}),self.assertRaises(RuntimeError):publisher.durable_automatic_intent(self.root,receipt,{'phase':'submitting'})
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'true'}),patch('checkpoint_blogsky_native.persist',return_value='durable') as persist:
            publisher.durable_automatic_intent(self.root,receipt,{'phase':'submitting'})
            persist.assert_called_once_with(self.root,[str(receipt.relative_to(self.root))],'Checkpoint Blogsky automatic submit intent [skip ci]')
            self.assertEqual(json.loads(receipt.read_text())['phase'],'submitting')
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'true'}),patch('checkpoint_blogsky_native.persist',side_effect=RuntimeError('safe failure')),self.assertRaises(RuntimeError):publisher.durable_automatic_intent(self.root,receipt,{'phase':'submitting'})
    def test_workflow_requires_qa_and_serializes_native_publication(self):
        text=(ROOT/'.github/workflows/blogsky-auto.yml').read_text()
        for required in ("cron: '*/20 * * * *'",'needs.generate.result',"count: '1'",'blogsky-native-publication','BLOGSKY_NATIVE_MODE: auto-one','if: always()'):
            self.assertIn(required,text)
    def test_export_adapter_stays_separate_and_does_not_bypass_native_gate(self):
        from blogsky_backlink_queue import control
        self.assertFalse(control(ROOT)['publication_enabled'])

if __name__=='__main__':unittest.main()
