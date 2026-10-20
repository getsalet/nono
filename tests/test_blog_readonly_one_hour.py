import base64
import copy
import inspect
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import observe_blog_generators_one_hour as subject

class ReadOnlyHourTests(unittest.TestCase):
    def test_scope_and_fixed_finite_window(self):
        self.assertEqual(subject.DURATION,3600);self.assertEqual(subject.INTERVAL,300)
        self.assertEqual(set(subject.BLOGS),{'roya','farsiblog','rozblog','loxblog','blogsky'})
        self.assertNotIn('blogfa',subject.BLOGS)
    def test_script_has_no_activation_or_native_submit_path(self):
        source=inspect.getsource(subject)
        for forbidden in ('dispatch_next(',"'/dispatches'",'publish_blogsky_posts','IMAGE_API_KEY','AGNES_API_KEY','native.login(',"locator('#publish')"):
            self.assertNotIn(forbidden,source)
        workflow=(ROOT/'.github/workflows/blog-readonly-one-hour.yml').read_text()
        self.assertIn('actions: read',workflow);self.assertNotIn('actions: write',workflow);self.assertNotIn('secrets.',workflow)
    def test_exact_immutable_commit_and_large_blob_are_required(self):
        sha='a'*40
        with patch.object(subject,'api',side_effect=[{'sha':sha,'content':''},{'encoding':'base64','content':base64.b64encode(b'{"items":[]}').decode()}]) as api:
            self.assertEqual(subject.repo_json('data/x.json','b'*40),{'items':[]})
            self.assertEqual(api.call_args_list[0].args[0],'/contents/data/x.json?ref='+'b'*40)
            self.assertEqual(api.call_args_list[1].args[0],'/git/blobs/'+sha)
        with self.assertRaises(ValueError):subject.repo_json('data/x.json','main')
    def sample(self,keys):
        return {'blogs':{blog:{'published_keys':keys,'generated_keys':keys,'ready_count':0}for blog in subject.BLOGS}}
    def test_queue_change_is_not_claimed_as_public_verification(self):
        result=subject.summary([self.sample(['old']),self.sample(['old','new'])])
        for row in result.values():
            self.assertEqual(row['new_published_queue_flags'],1)
            self.assertFalse(row['new_public_posts_independently_verified_by_monitor'])
        self.assertIsNone(subject.summary([{'blogs':{}},self.sample(['new'])])['blogsky']['new_published_queue_flags'])
    def test_old_failure_is_not_counted_as_new_but_running_to_failed_is(self):
        first=self.sample(['old'])
        for row in first['blogs'].values():row['workflows']={'fixture.yml':{'runs':[{'id':1,'conclusion':'failure'},{'id':2,'conclusion':None}]}}
        last=copy.deepcopy(first)
        for row in last['blogs'].values():row['workflows']['fixture.yml']['runs'][1]['conclusion']='failure'
        for row in subject.summary([first,last]).values():self.assertEqual(row['new_failed_run_ids'],['2'])

    def test_observation_waits_full_requested_window_and_checkpoints_progress(self):
        clock=[0.0];saved=[]
        def sleep(seconds):clock[0]+=seconds
        report=subject.observe(read=lambda:self.sample(['one']),persist=lambda r:saved.append(copy.deepcopy(r)),clock=lambda:clock[0],sleep=sleep,duration=2,interval=1)
        self.assertEqual(report['status'],'completed');self.assertGreaterEqual(report['elapsed_seconds'],2)
        self.assertEqual(len(report['samples']),3);self.assertEqual(report['native_submissions'],0);self.assertEqual(report['workflow_dispatches'],0)
        self.assertEqual(saved[0]['status'],'monitoring');self.assertEqual(saved[-1]['status'],'completed')
    def test_partial_failure_is_recorded_not_reported_healthy(self):
        clock=[0.0]
        report=subject.observe(read=lambda:(_ for _ in ()).throw(RuntimeError()),persist=lambda r:None,clock=lambda:clock[0],sleep=lambda n:clock.__setitem__(0,clock[0]+n),duration=1,interval=1)
        self.assertIn('read_error_type',report['samples'][0]);self.assertIsNone(report['summary']['roya']['new_published_queue_flags'])

if __name__=='__main__':unittest.main()
