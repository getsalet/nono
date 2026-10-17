"""Distinct-account admission is bounded, replay-safe, and image-proven only."""
import contextlib,copy,datetime,json,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_account_expansion as a
import blog_image_key_router as router
from blog_image_connection import settings

class AccountExpansionTests(unittest.TestCase):
 def image(self):return {'status':'image_healthy','http_status':200,'width':1152,'height':864,'image_sha256':'a'*64,'visual_publication_approved':False}
 def report(self):
  return {'policy':a.POLICY,'status':'completed','post_submissions':0,'connection':settings('https://apihub.agnes-ai.com/v1'),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'keys':[{'secret_name':'AGNES_API_KEY4','text':{'status':'healthy','http_status':200},'image':self.image()}]}
 def test_only_actual_image_bytes_proof_admits_a_slot(self):
  r=self.report();self.assertEqual(a.successful(r,r['connection']),['AGNES_API_KEY4'])
  for image in ({'status':'temporarily_unavailable','http_status':503,'provider_code':'image_queue_full'},{'status':'no_usable_image','http_status':200},{**self.image(),'image_sha256':''},{**self.image(),'width':True},{**self.image(),'height':1200}):
   r['keys'][0]['image']=image;self.assertEqual(a.successful(r,r['connection']),[])
 def test_text_only_or_failed_text_cannot_promote(self):
  r=self.report();r['keys'][0]['text']={'status':'nonconforming_response','http_status':200};self.assertEqual(a.successful(r,r['connection']),[])
 def test_expired_future_partial_or_wrong_connection_evidence_is_rejected(self):
  for change in ({'finished_at':'2020-01-01T00:00:00Z'},{'finished_at':'2099-01-01T00:00:00Z'},{'status':'stopped_quota_or_rate_limit'},{'post_submissions':1},{'connection':{}}):
   r=self.report();r.update(change);self.assertEqual(a.successful(r,settings('https://apihub.agnes-ai.com/v1')),[])
 def test_duplicate_rows_or_slot8_never_admitted(self):
  r=self.report();r['keys']*=2;self.assertEqual(a.successful(r,r['connection']),[])
  r=self.report();r['keys'][0]['secret_name']='AGNES_API_KEY8';self.assertEqual(a.successful(r,r['connection']),[])
 def test_router_consumes_expansion_without_replacing_old_audit(self):
  root=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory()as d,patch.dict('os.environ',{'GITHUB_ACTIONS':'false'}):
   out=Path(d)
   for path in (router.CONFIG,'data/agnes-usable-key-audit/latest.json','data/agnes-image-key-health/latest.json'):
    p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((root/path).read_bytes())
   cfg=json.loads((out/router.CONFIG).read_text());cfg['slots'].append('AGNES_API_KEY4');(out/router.CONFIG).write_text(json.dumps(cfg))
   self.assertNotIn('AGNES_API_KEY4',router.evidence(out))
   p=out/a.LATEST;p.parent.mkdir(parents=True);p.write_text(json.dumps(self.report()))
   self.assertIn('AGNES_API_KEY4',router.evidence(out))
   r=self.report();r['keys'][0]['image']={'status':'temporarily_unavailable','http_status':503};p.write_text(json.dumps(r));self.assertNotIn('AGNES_API_KEY4',router.evidence(out))
 def request(self):return {'policy':a.POLICY,'request_id':'b'*32,'slots':list(a.CANDIDATES),'max_image_requests':6,'minimum_interval_seconds':60,'account_ownership_confirmed_by_user':True}
 def test_request_cannot_expand_budget_or_include_slot8(self):
  self.assertIn('b'*32,a.validate_request(self.request()))
  for change in ({'max_image_requests':7},{'minimum_interval_seconds':0},{'slots':['AGNES_API_KEY8']},{'account_ownership_confirmed_by_user':False}):
   r=self.request();r.update(change)
   with self.assertRaises(RuntimeError):a.validate_request(r)
 def main_fixture(self,results):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
  p=root/a.REQUEST;p.parent.mkdir(parents=True);p.write_text(json.dumps(self.request()))
  config={'policy':router.POLICY,'enabled':True,'slots':['AGNES_API_KEY10','AGNES_API_KEY6','AGNES_API_KEY7','AGNES_API_KEY11']}
  saved={}
  def checkpoint(path,raw,*args):saved[path]=json.loads(raw)
  def git(args,*args2,**kw):
   if args[0]=='cat-file':return SimpleNamespace(returncode=0 if args[-1].split(':',1)[-1]in saved else 1,stdout=b'')
   return SimpleNamespace(returncode=0,stdout=json.dumps(config).encode())
  pool=SimpleNamespace(keys=['fixture-private-'+n for n in a.CANDIDATES],slots={'fixture-private-'+n:n for n in a.CANDIDATES})
  patches=[patch.object(a,'ROOT',root),patch.object(a,'shared_open'),patch.object(a.images,'git',side_effect=git),patch.object(a.images,'checkpoint_asset',side_effect=checkpoint),patch.object(a.images.roya.BASE,'_key_pool',pool),patch.object(a,'text_probe',return_value={'status':'healthy','http_status':200}),patch.object(a,'image_probe',side_effect=results),patch('blog_image_queue.provider_slot',side_effect=lambda *args:contextlib.nullcontext())]
  return root,saved,patches
 def test_one_pass_six_requests_promotes_only_success_and_rerun_is_noop(self):
  root,saved,patches=self.main_fixture([self.image()]+[{'status':'temporarily_unavailable','http_status':503,'provider_code':'image_queue_full'}]*5)
  with contextlib.ExitStack()as stack:
   mocks=[stack.enter_context(p)for p in patches]
   self.assertEqual(a.main(),0);self.assertEqual(mocks[6].call_count,6)
   self.assertEqual(saved[a.LATEST]['promoted_slots'],['AGNES_API_KEY'])
   self.assertEqual(saved[router.CONFIG]['slots'][-1],'AGNES_API_KEY')
   self.assertEqual(a.main(),0);self.assertEqual(mocks[6].call_count,6)
  self.assertNotIn('fixture-private',json.dumps(saved));self.assertEqual(saved[a.LATEST]['post_submissions'],0)
 def test_rate_limit_or_billing_stops_comparison_without_other_account_probe(self):
  for code in (402,429):
   root,saved,patches=self.main_fixture([{'status':'rate_limited','http_status':code}])
   with contextlib.ExitStack()as stack:
    mocks=[stack.enter_context(p)for p in patches]
    self.assertEqual(a.main(),1);self.assertEqual(mocks[6].call_count,1);self.assertNotIn(router.CONFIG,saved)
 def test_global_stop_prevents_even_text_probe(self):
  root,saved,patches=self.main_fixture([])
  with contextlib.ExitStack()as stack:
   mocks=[stack.enter_context(p)for p in patches];mocks[1].side_effect=RuntimeError('Global stop')
   self.assertEqual(a.main(),1);self.assertEqual(mocks[5].call_count,0);self.assertEqual(mocks[6].call_count,0)
 def test_workflow_only_has_requested_accounts_and_keeps_secrets_out_of_test_step(self):
  source=(Path(__file__).resolve().parents[1]/'.github/workflows/blog-image-account-expansion.yml').read_text()
  self.assertNotIn('secrets.AGNES_API_KEY8',source)
  self.assertNotIn('secrets.',source.split('Probe at most six',1)[0])
  for n in a.CANDIDATES:self.assertIn('secrets.'+n+' }}',source)
  self.assertIn("BLOG_IMAGE_QUEUE_ENABLED: '1'",source)

if __name__=='__main__':unittest.main()
