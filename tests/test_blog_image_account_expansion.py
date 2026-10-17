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
 def main_fixture(self,results,request=None):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
  p=root/a.REQUEST;p.parent.mkdir(parents=True);p.write_text(json.dumps(request or self.request()))
  config={'policy':router.POLICY,'enabled':True,'slots':['AGNES_API_KEY10','AGNES_API_KEY6','AGNES_API_KEY7','AGNES_API_KEY11']}
  saved={}
  def checkpoint(path,raw,*args):saved[path]=json.loads(raw)
  def git(args,*args2,**kw):
   if args[0]=='cat-file':return SimpleNamespace(returncode=0 if args[-1].split(':',1)[-1]in saved else 1,stdout=b'')
   return SimpleNamespace(returncode=0,stdout=json.dumps(config).encode())
  pool=SimpleNamespace(keys=['fixture-private-'+n for n in a.CANDIDATES],slots={'fixture-private-'+n:n for n in a.CANDIDATES})
  patches=[patch.object(a,'ROOT',root),patch.object(a,'shared_open'),patch.object(a.images,'git',side_effect=git),patch.object(a.images,'checkpoint_asset',side_effect=checkpoint),patch.object(a,'configured_keys',return_value={n:'fixture-private-'+n for n in (request or self.request())['slots']if n!=a.DUPLICATE}),patch.object(a,'text_probe',return_value={'status':'healthy','http_status':200}),patch.object(a,'image_probe',side_effect=results),patch('blog_image_queue.provider_slot',side_effect=lambda *args:contextlib.nullcontext())]
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
    self.assertEqual(a.main(),1);self.assertEqual(mocks[6].call_count,1);self.assertNotIn(router.CONFIG,saved);self.assertNotIn(a.LATEST,saved);self.assertIn(a.PROGRESS,saved)
 def test_global_stop_prevents_even_text_probe(self):
  root,saved,patches=self.main_fixture([])
  with contextlib.ExitStack()as stack:
   mocks=[stack.enter_context(p)for p in patches];mocks[1].side_effect=RuntimeError('Global stop')
   self.assertEqual(a.main(),1);self.assertEqual(mocks[5].call_count,0);self.assertEqual(mocks[6].call_count,0)
 def full_request(self):
  r=self.request();r.update(slots=list(a.ALL_SLOTS),max_image_requests=24);return r
 def test_full_scope_includes_every_slot_and_rejects_extra_budget(self):
  self.assertIn('b'*32,a.validate_request(self.full_request()))
  for change in ({'max_image_requests':25},{'slots':list(a.ALL_SLOTS)+['UNKNOWN']}):
   r=self.full_request();r.update(change)
   with self.assertRaises(RuntimeError):a.validate_request(r)
 def test_diagnostic_sees_previously_rejected_slots_without_changing_production_pool(self):
  names=list(a.ALL_SLOTS);env={'AGNES_API_KEY2':'fixture-two','AGNES_API_KEY16':'fixture-sixteen','AGNES_API_KEY8':'fixture-duplicate'}
  self.assertEqual(a.configured_keys(names,env),{'AGNES_API_KEY2':'fixture-two','AGNES_API_KEY16':'fixture-sixteen'})
  self.assertNotIn('AGNES_API_KEY8',a.configured_keys(names,env))
 def test_all_25_slots_reported_text_first_and_no_image_for_bad_text(self):
  failed={'status':'temporarily_unavailable','http_status':503,'provider_code':'image_queue_full'}
  root,saved,patches=self.main_fixture([failed]*11,self.full_request());events=[]
  def text(key):
   name=key.replace('fixture-private-','');events.append('text')
   if name in [f'AGNES_API_KEY{i}'for i in range(16,26)]:return {'status':'authentication_rejected','http_status':401}
   if name in ('AGNES_API_KEY2','AGNES_API_KEY12','AGNES_API_KEY13'):return {'status':'nonconforming_response','http_status':200}
   return {'status':'healthy','http_status':200}
  with contextlib.ExitStack()as stack:
   mocks=[stack.enter_context(p)for p in patches];mocks[5].side_effect=text
   def image(*args):events.append('image');return failed
   mocks[6].side_effect=image
   self.assertEqual(a.main(),0);self.assertEqual(mocks[5].call_count,24);self.assertEqual(mocks[6].call_count,11)
  report=saved[a.LATEST];self.assertEqual(len(report['keys']),25)
  self.assertEqual(events[:24],['text']*24);self.assertTrue(report['complete_text'])
  dup=next(r for r in report['keys']if r['secret_name']=='AGNES_API_KEY8');self.assertEqual(dup['duplicate_of'],'AGNES_API_KEY')
  self.assertNotIn(router.CONFIG,saved)
 def test_completed_prior_six_account_results_are_reused_not_reprobed(self):
  prior=self.report();prior.update(request_id='c'*32)
  prior['keys']=[{'secret_name':n,'text':{'status':'healthy','http_status':200},'image':{'status':'temporarily_unavailable','http_status':503}}for n in a.CANDIDATES]
  request=self.full_request();request['reuse_request_id']='c'*32
  self.assertEqual(len(a.reusable(prior,request,prior['connection'])),6)
  prior['status']='checking_images';self.assertEqual(a.reusable(prior,request,prior['connection']),{})
 def test_report_with_explicit_duplicate_can_still_admit_other_success(self):
  r=self.report();r['keys'].append({'secret_name':'AGNES_API_KEY8','duplicate_of':'AGNES_API_KEY','text':{'status':'skipped_duplicate'},'image':{'status':'skipped_duplicate'}})
  self.assertEqual(a.successful(r,r['connection']),['AGNES_API_KEY4'])
 def test_updated_single_slot_is_bounded_and_preserves_full_evidence(self):
  request=self.request();request.update(slots=['AGNES_API_KEY16'],max_image_requests=1,credential_updated_by_user=True)
  self.assertIn('b'*32,a.validate_request(request))
  for change in ({'credential_updated_by_user':False},{'max_image_requests':2},{'slots':['AGNES_API_KEY8']}):
   invalid={**request,**change}
   with self.assertRaises(RuntimeError):a.validate_request(invalid)
  root,saved,patches=self.main_fixture([self.image()],request)
  with contextlib.ExitStack()as stack:
   mocks=[stack.enter_context(p)for p in patches]
   self.assertEqual(a.main(),0);self.assertEqual(mocks[5].call_count,1);self.assertEqual(mocks[6].call_count,1)
  self.assertNotIn(a.LATEST,saved);self.assertNotIn(router.CONFIG,saved)
  self.assertEqual(saved[a.PROGRESS]['keys'][0]['secret_name'],'AGNES_API_KEY16')
  self.assertTrue(saved[a.PROGRESS]['complete_image'])
 def test_workflow_only_has_requested_accounts_and_keeps_secrets_out_of_test_step(self):
  source=(Path(__file__).resolve().parents[1]/'.github/workflows/blog-image-account-expansion.yml').read_text()
  self.assertNotIn('secrets.AGNES_API_KEY8',source)
  self.assertNotIn('secrets.',source.split('Probe all requested',1)[0])
  for n in a.CANDIDATES:self.assertIn('secrets.'+n+' }}',source)
  self.assertIn("BLOG_IMAGE_QUEUE_ENABLED: '1'",source)

if __name__=='__main__':unittest.main()
