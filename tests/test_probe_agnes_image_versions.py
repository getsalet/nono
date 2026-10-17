import base64,contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import probe_agnes_image_versions as p
class VersionTests(unittest.TestCase):
 def request(self):return {'policy':p.POLICY,'request_id':'c'*32,'models':list(p.MODELS),'slot':p.SLOT,'max_requests':2,'minimum_interval_seconds':60}
 def test_bounded_explicit_alternatives_only(self):
  p.validate(self.request())
  for change in ({'max_requests':3},{'minimum_interval_seconds':0},{'models':['guessed-model']},{'slot':'AGNES_API_KEY16'}):
   with self.assertRaises(RuntimeError):p.validate({**self.request(),**change})
 def test_inputs_identical_except_model(self):
  prompt,refs=p.material();left=p.payload(p.MODELS[0],prompt,refs);right=p.payload(p.MODELS[1],prompt,refs)
  self.assertNotEqual(left.pop('model'),right.pop('model'));self.assertEqual(left,right);self.assertIn('extra_body',left);self.assertNotIn('response_format',left)
 def test_decode_has_exact_phone_and_valid_bytes(self):
  b=io.BytesIO();Image.new('RGB',(1024,768),(100,100,100)).save(b,'PNG')
  raw,meta=p.decode({'data':[{'b64_json':base64.b64encode(b.getvalue()).decode()}]})
  self.assertEqual(meta['watermark'],'AFP | 09134922013');self.assertEqual(Image.open(io.BytesIO(raw)).size,(1024,768))
 def run_fixture(self,results,stop=False):
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);q=root/p.REQUEST;q.parent.mkdir(parents=True);q.write_text(json.dumps(self.request()));saved={}
   def git(args,*a,**kw):return SimpleNamespace(returncode=1 if args[0]=='cat-file'else 0,stdout=b'')
   def save(path,raw,*a):saved[path]=raw;return 'https://example.com/safe/'+path
   with patch.object(p,'ROOT',root),patch.object(p.images,'git',side_effect=git),patch.object(p.images,'checkpoint_asset',side_effect=save),patch.dict('os.environ',{p.SLOT:'fixture-private-value'}),patch('blog_image_account_expansion.shared_open',side_effect=RuntimeError()if stop else None),patch('blog_image_key_router.available_at',return_value=0),patch('blog_image_queue.provider_slot',side_effect=lambda *a:contextlib.nullcontext()),patch.object(p,'probe',side_effect=results)as probe:
    code=p.main()
   report=json.loads(saved[p.validate(self.request())]);self.assertNotIn('fixture-private-value',json.dumps(report));return report,probe.call_count,code
 def test_two_attempts_no_retry_and_no_production_change(self):
  report,calls,code=self.run_fixture([({'status':'temporarily_unavailable','http_status':503},None)]*2)
  self.assertEqual(calls,2);self.assertEqual(code,0);self.assertFalse(report['production_model_changed']);self.assertEqual(report['post_submissions'],0)
 def test_rate_or_billing_stops_without_other_model_request(self):
  for code in (401,402,429):
   report,calls,_=self.run_fixture([({'status':'blocked','http_status':code},None)])
   self.assertEqual(calls,1);self.assertEqual(report['status'],'stopped_auth_quota_or_rate_limit')
 def test_pause_blocks_requests(self):
  _,calls,_=self.run_fixture([],True);self.assertEqual(calls,0)
if __name__=='__main__':unittest.main()
