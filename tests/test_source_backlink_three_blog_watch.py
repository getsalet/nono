import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import monitor_source_backlink_three_blogs as m
class MonitorTests(unittest.TestCase):
 def test_only_requested_three_blogs(self):
  self.assertEqual(set(m.BLOGS),{'farsiblog','rozblog','loxblog'});self.assertNotIn('blogfa',json.dumps(m.BLOGS));self.assertNotIn('roya',json.dumps(m.BLOGS))
 def test_read_only_http_and_no_token_to_public_site(self):
  response=Mock();response.status=200;response.read.return_value=b'{}';context=Mock();context.__enter__=Mock(return_value=response);context.__exit__=Mock(return_value=False)
  with patch.dict(os.environ,{'GH_TOKEN':'offline-fixture'}),patch.object(m.urllib.request,'urlopen',return_value=context)as transport:
   m.read('https://afp.farsiblog.com/');req=transport.call_args.args[0];self.assertEqual(req.method,'GET');self.assertNotIn('Authorization',req.headers)
   m.read('https://api.github.com/repos/getsalet/nono',True);self.assertEqual(transport.call_args.args[0].method,'GET')
   with self.assertRaises(ValueError):m.read('https://evil.example/',True)
 def test_exact_image_and_backlink_in_published_html_without_image_fetch(self):
  item={'target_url':'https://navar-abyari.ir/post/','image_url':'https://navar-abyari.ir/wp-content/uploads/own.jpg','image_source':{'policy':'trusted-existing-source-no-recheck-v1','visual_review_performed':False}}
  body='<img src="'+item['image_url']+'"><a href="'+item['target_url']+'">source</a>'
  with patch.object(m,'read',return_value=(200,body))as read:
   result=m.verify_post('farsiblog',item,{'url':'https://afp.farsiblog.com/post/1/'});self.assertTrue(result['original_source_image_tag_present']);self.assertTrue(result['source_backlink_present']);read.assert_called_once()
  with patch.object(m,'read')as read:result=m.verify_post('farsiblog',item,{'url':'https://evil.example/'});read.assert_not_called();self.assertIn('unverified',result)
 def test_missing_image_not_misreported_as_present(self):
  with patch.object(m,'read',return_value=(200,'<p>text</p>')):
   result=m.verify_post('loxblog',{}, {'url':'https://afp.lxb.ir/post/1/'})
  self.assertFalse(result['any_image_tag_present']);self.assertFalse(result['original_source_image_tag_present'])
 def test_report_does_not_claim_hour_complete_at_start(self):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);m.write_report(root,[{'at':'now','blogs':[]}],'start',1.0,False);self.assertFalse(json.loads((root/'status.json').read_text())['one_hour_completed'])
 def test_hour_duration_and_read_only_workflow_are_fixed(self):
  text=(ROOT/'automation/monitor_source_backlink_three_blogs.py').read_text();self.assertIn('end=clock+3600',text);self.assertNotIn('/dispatches',text)
  workflow=(ROOT/'.github/workflows/source-backlink-three-blog-watch.yml').read_text();self.assertIn('contents: read',workflow);self.assertIn('actions: read',workflow);self.assertNotIn('secrets.',workflow)
