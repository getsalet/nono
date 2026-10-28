import contextlib,copy,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_restore as restore
import validate_blog_image_pairs as audit
class PairValidationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.cfg=json.loads((restore.ROOT/restore.CONFIG).read_text());self.cfg['enabled']=False;self.request={'policy':restore.POLICY,'request_id':'a'*32,'max_image_requests':14}
  for name,v in [(restore.CONFIG,self.cfg),(audit.REQUEST,self.request)]:
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
  self.names=[n for p in self.cfg['key_pairs'].values()for n in p];self.bindings={n:'fixture-'+n for n in self.names}
  self.good={'status':'image_healthy','http_status':200,'width':1024,'height':768,'image_sha256':'b'*64}
 def run_audit(self,result=None,bindings=None):
  saved=[]
  with patch.object(audit,'ROOT',self.root),patch('blog_generated_image.git',return_value=SimpleNamespace(returncode=1)),patch('blog_generated_image.checkpoint_asset',side_effect=lambda p,raw,*a:saved.append((p,json.loads(raw)))),patch('blog_image_account_expansion.shared_open'),patch('blog_image_account_expansion.configured_keys',return_value=bindings if bindings is not None else self.bindings),patch('blog_image_queue.provider_slot',side_effect=lambda *a:contextlib.nullcontext()),patch('audit_usable_agnes_keys.image_probe',return_value=result or self.good)as probe,patch('blog_image_backpressure.defer')as defer,patch('blog_image_key_router.state',return_value={'policy':'audited-image-key-pool-v1','keys':{}}):
   code=audit.main()
  report=json.loads((self.root/restore.EVIDENCE).read_text())if (self.root/restore.EVIDENCE).exists()else None
  return code,report,probe.call_count,saved,defer
 def test_fourteen_bounded_calls_no_automatic_activation_or_post(self):
  code,v,calls,saved,_=self.run_audit()
  self.assertEqual(code,0);self.assertEqual(calls,14);self.assertTrue(v['all_pairs_ready']);self.assertFalse(v['production_activated']);self.assertEqual(v['post_submissions'],0)
  self.assertEqual(v['keys'][0]['image']['status'],'image_healthy');self.assertNotIn('fixture-',json.dumps(saved));self.assertFalse(restore.load(self.root)['enabled'])
 def test_missing_and_duplicate_slots_are_not_promoted(self):
  bindings=copy.deepcopy(self.bindings);del bindings[self.names[0]];bindings[self.names[-1]]=bindings[self.names[-2]]
  code,v,calls,*_=self.run_audit(bindings=bindings)
  self.assertEqual(code,2);self.assertEqual(calls,12);self.assertFalse(v['all_pairs_ready']);self.assertEqual(v['keys'][0]['image']['status'],'not_configured');self.assertIn('duplicate_of',v['keys'][-1])
 def test_shared_billing_stops_after_one_call(self):
  code,v,calls,saved,_=self.run_audit({'status':'billing_required','http_status':402})
  self.assertEqual(code,2);self.assertEqual(calls,1);self.assertEqual(v['status'],'stopped_shared_limit');self.assertTrue(any(x.get('shared_block')=='billing_required'for _,x in saved))
 def test_shared_rate_limit_and_queue_full_do_not_probe_next_account(self):
  for result,status in [({'status':'rate_limited','http_status':429},'stopped_shared_limit'),({'status':'temporarily_unavailable','http_status':503,'provider_code':'image_queue_full'},'deferred_provider_queue')]:
   # Different temporary root per request; same request must never be repeated.
   ledger=self.root/'data/blog-image-pair-validation/requests'/('a'*32+'.json')
   if ledger.exists():ledger.unlink()
   code,v,calls,_,defer=self.run_audit(result)
   self.assertEqual(code,2);self.assertEqual(calls,1);self.assertEqual(v['status'],status);defer.assert_called_once()
 def test_reserved_request_is_never_repeated(self):
  p=self.root/'data/blog-image-pair-validation/requests'/('a'*32+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
  code,v,calls,*_=self.run_audit()
  self.assertEqual(code,0);self.assertEqual(calls,0);self.assertIsNone(v)
if __name__=='__main__':unittest.main()
