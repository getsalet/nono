"""Offline pool routing: no actual credentials, API requests or quota probing."""
import copy,json,os,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_key_router as router
from blog_image_backpressure import ImageProviderBusy
class ImageKeyRouterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  # Deterministic offline evidence; live audit results must not redefine fixtures.
  self.names=['AGNES_API_KEY10','AGNES_API_KEY6','AGNES_API_KEY7','AGNES_API_KEY11']
  from blog_image_connection import settings
  import datetime
  stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
  fixtures={router.CONFIG:{'enabled':True,'policy':router.POLICY,'slots':self.names},
   'data/agnes-usable-key-audit/latest.json':{'complete_text':True,'complete_image':True,'finished_at':stamp,'connection':settings('https://apihub.agnes-ai.com/v1'),'keys':[{'secret_name':n,'text':{'status':'healthy','http_status':200},'image':{'http_status':503,'provider_code':'image_queue_full'}}for n in self.names]},
   'data/agnes-image-key-health/latest.json':{'complete':True,'tested_at':stamp,'endpoint':'https://apihub.agnes-ai.com/v1/images/generations','model':'agnes-image-2.5-flash','keys':[{'secret_name':n,'status':'image_healthy','http_status':200}for n in self.names]}}
  for name,value in fixtures.items():
   q=self.root/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(value))
  self.pool=SimpleNamespace(keys=['private-fixture-'+n for n in self.names],slots={'private-fixture-'+n:n for n in self.names})
  self.lease=SimpleNamespace(retain=False);self.commits=[]
  self.env=patch.dict(os.environ,{'GITHUB_ACTIONS':'false'});self.env.start();self.addCleanup(self.env.stop)
 def checkpoint(self,path,raw,root):self.commits.append((path,json.loads(raw)))
 def run_route(self,operation,item=None):
  return router.generate(item if item is not None else {},'farsiblog',self.root,self.pool,operation,self.checkpoint,self.lease)
 def test_four_real_image_proofs_only_no_text_only_keys(self):self.assertEqual(router.evidence(self.root),self.names)
 def test_round_robin_and_before_request_reservation(self):
  chosen=[]
  def op(item,blog,slots,max_attempts):
   chosen.extend(slots);self.assertEqual(max_attempts,1)
   self.assertEqual(router.state(self.root)['keys'][slots[0]]['status'],'reserved')
   return b'validated_image_fixture'
  for _ in range(5):self.run_route(op)
  self.assertEqual(chosen,self.names+[self.names[0]])
  self.assertNotIn('private-fixture',json.dumps(self.commits))
 def busy(self,item,blog,slots,max_attempts):
  item.setdefault('_image_provider_attempts',[]).append({'http_status':503,'provider_code':'image_queue_full'})
  raise ImageProviderBusy(time.time()+300)
 def test_queue_retry_after_is_never_shortened(self):
  start=time.time();provider_retry=start+1200
  def busy_long(item,*args,**kw):
   item['_image_provider_attempts']=[{'http_status':503,'provider_code':'image_queue_full'}]
   raise ImageProviderBusy(provider_retry)
  with self.assertRaises(ImageProviderBusy):self.run_route(busy_long)
  self.assertGreaterEqual(router.state(self.root)['keys'][self.names[0]]['retry_at_epoch'],provider_retry)
 def test_slow_request_still_gets_full_post_response_backoff(self):
  clock=[time.time()]
  def slow(item,*args,**kw):
   clock[0]+=600
   item['_image_provider_attempts']=[{'http_status':503,'provider_code':'image_queue_full'}]
   raise ImageProviderBusy(clock[0]+300)
  with patch.object(router.time,'time',side_effect=lambda:clock[0]),self.assertRaises(ImageProviderBusy):self.run_route(slow)
  self.assertGreaterEqual(router.state(self.root)['keys'][self.names[0]]['retry_at_epoch'],clock[0]+300)
 def test_live_canary_preflight_uses_the_same_pool_as_production(self):
  source=(ROOT/'.github/workflows/blog-tape-live-canary.yml').read_text()
  self.assertIn("IMAGE_KEY_POOL_ENABLED: '1'",source)
  # Production routing must not leak into the offline legacy-route fixtures.
  job=source.split('    steps:',1)[0]
  self.assertNotIn('IMAGE_KEY_POOL_ENABLED',job)
  dispatch=source.split('      - name: Dispatch at most one',1)[1]
  self.assertIn("IMAGE_KEY_POOL_ENABLED: '1'",dispatch)
 def test_single_key_capacity_failure_does_not_disable_other_keys(self):
  with self.assertRaises(ImageProviderBusy)as exc:self.run_route(self.busy)
  self.assertTrue(exc.exception.key_scoped);self.assertTrue(exc.exception.shared_cooldown_attempted)
  state=router.state(self.root);self.assertGreater(state['keys'][self.names[0]]['retry_at_epoch'],time.time())
  called=[];self.run_route(lambda *a,**kw:called.extend(kw['slots'])or b'ok')
  self.assertEqual(called,[self.names[1]])
 def test_all_key_capacity_failures_wait_without_fifth_request(self):
  for _ in self.names:
   with self.assertRaises(ImageProviderBusy):self.run_route(self.busy)
  with patch('builtins.print'),self.assertRaises(ImageProviderBusy):self.run_route(lambda *a,**kw:self.fail('No request before earliest per-key retry'))
  self.assertGreater(router.available_at(self.root),time.time())
 def error(self,code):
  def operation(item,*args,**kw):
   item.setdefault('_image_provider_attempts',[]).append({'http_status':code,'retry_after_seconds':120})
   raise RuntimeError('Image provider HTTP '+str(code)+'; raw response withheld')
  return operation
 def test_rate_limit_stops_entire_pool_no_credential_rotation(self):
  with self.assertRaises(ImageProviderBusy):self.run_route(self.error(429))
  with self.assertRaises(ImageProviderBusy):self.run_route(lambda *a,**kw:self.fail('Rate limit must block other credentials'))
  self.assertEqual(self.commits[-1][1]['reason'],'provider_rate_limited')
 def test_billing_stops_entire_pool_for_review(self):
  with self.assertRaises(RuntimeError):self.run_route(self.error(402))
  with self.assertRaisesRegex(RuntimeError,'billing/quota'):self.run_route(lambda *a,**kw:self.fail('No billing bypass'))
 def test_auth_and_permission_disable_only_the_rejected_slot(self):
  for code in [401,403]:
   with self.assertRaises(RuntimeError):self.run_route(self.error(code))
  s=router.state(self.root);self.assertEqual(s['keys'][self.names[0]]['status'],'authentication_rejected');self.assertEqual(s['keys'][self.names[1]]['status'],'image_scope_denied')
 def test_unknown_and_text_only_credentials_never_selected(self):
  self.pool=SimpleNamespace(keys=['private-fixture-text'],slots={'private-fixture-text':'AGNES_API_KEY4'})
  with self.assertRaisesRegex(RuntimeError,'not configured'):self.run_route(lambda *a,**kw:self.fail('No text-only fallback'))
 def test_checkpoint_failure_retains_lease_and_stops_before_api(self):
  def fail(*a):raise OSError('private-error')
  with self.assertRaisesRegex(RuntimeError,'lease retained'):
   router.generate({},'farsiblog',self.root,self.pool,lambda *a,**kw:self.fail('No request before durable reservation'),fail,self.lease)
  self.assertTrue(self.lease.retain)
 def test_corrupt_state_fails_closed(self):
  p=self.root/router.CACHE;p.parent.mkdir(parents=True);p.write_text('not json')
  with self.assertRaisesRegex(RuntimeError,'unreadable'):self.run_route(lambda *a,**kw:self.fail('No request with unreadable state'))
 def test_nan_and_boolean_cooldown_fail_closed(self):
  p=self.root/router.STATE;p.parent.mkdir(parents=True,exist_ok=True)
  for value in [float('nan'),True,-1]:
   p.write_text(json.dumps({'policy':router.POLICY,'keys':{self.names[0]:{'retry_at_epoch':value}}}))
   with self.assertRaises(RuntimeError):router.state(self.root)
 def test_explicit_quota_error_blocks_other_credentials_even_on_403(self):
  def quota(item,*args,**kw):
   item['_image_provider_attempts']=[{'http_status':403,'provider_code':'insufficient_quota'}]
   raise RuntimeError('Image provider HTTP 403; raw response withheld')
  with self.assertRaises(RuntimeError):self.run_route(quota)
  with self.assertRaisesRegex(RuntimeError,'billing/quota'):router.available_at(self.root)
 def test_long_rate_limit_retry_after_is_not_shortened_for_rotation(self):
  from agnes_key_pool import AgnesProviderError
  self.assertEqual(AgnesProviderError(429,retry_after='600').rate_limit_retry_after_seconds,600)
  def limited(item,*args,**kw):
   item['_image_provider_attempts']=[{'http_status':429,'retry_after_seconds':600}]
   raise RuntimeError('Image provider HTTP 429; raw response withheld')
  start=time.time()
  with self.assertRaises(ImageProviderBusy):self.run_route(limited)
  self.assertGreaterEqual(router.state(self.root)['shared_retry_at_epoch'],start+600)
 def test_provider_auth_exhaustion_still_records_401_for_router(self):
  import blog_generated_image as images
  item={'key':'auth-router','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز','summary':'این متن فقط برای آزمون کنترل احراز هویت و ثبت درست خطای کلید در مسیر تولید تصویر نوار تیپ است'}}
  with patch.object(images.roya.BASE._key_pool,'keys',['fixture-private']),patch.object(images.roya.BASE._key_pool,'slots',{'fixture-private':'AGNES_API_KEY10'}),patch.object(images.roya.BASE._key_pool,'fetch_json',side_effect=RuntimeError('No active credentials in the requested Agnes capability pool')):
   with self.assertRaisesRegex(RuntimeError,'HTTP 401'):images._generate(item,'farsiblog',slots=['AGNES_API_KEY10'],max_attempts=1)
  self.assertEqual(item['_image_provider_attempts'][-1]['http_status'],401)
 def test_stale_latest_audit_needs_explicit_refresh(self):
  path=self.root/'data/agnes-usable-key-audit/latest.json';data=json.loads(path.read_text());data['finished_at']='2020-01-01T00:00:00+00:00';path.write_text(json.dumps(data))
  with self.assertRaisesRegex(RuntimeError,'expired'):router.evidence(self.root)
 def test_incomplete_latest_audit_never_promotes_text_keys(self):
  path=self.root/'data/agnes-usable-key-audit/latest.json';data=json.loads(path.read_text());data['complete_image']=False;path.write_text(json.dumps(data))
  with self.assertRaisesRegex(RuntimeError,'complete image key audit'):router.evidence(self.root)
 def test_five_workflows_enable_router_with_global_queue(self):
  for name in ['roya-backlink-queue.yml','farsiblog-content.yml','rozblog-content.yml','blogfa-content.yml','loxblog-content.yml']:
   s=(ROOT/'.github/workflows'/name).read_text();self.assertIn("IMAGE_KEY_POOL_ENABLED: '1'",s);self.assertIn("BLOG_IMAGE_QUEUE_ENABLED: '1'",s)
 def test_preflight_respects_all_key_cooldowns_and_legacy_global_stop(self):
  from blog_image_backpressure import require_open,STATE
  with patch.dict(os.environ,{'IMAGE_KEY_POOL_ENABLED':'1'}):
   (self.root/STATE).write_text(json.dumps({'retry_at_epoch':time.time()+600}))
   with self.assertRaises(ImageProviderBusy):require_open(self.root)
 def test_production_wrapper_routes_inside_lease_and_avoids_legacy_defer_for_local_busy(self):
  import inspect,blog_generated_image as images
  source=inspect.getsource(images.generate)
  self.assertLess(source.index('with provider_slot('),source.index('raw=route_image('))
  self.assertIn("getattr(busy,'key_scoped',False):raise",source)
 def prefer_health(self):
  path=self.root/router.CONFIG;cfg=json.loads(path.read_text());cfg['prefer_recent_success_seconds']=21600;path.write_text(json.dumps(cfg))
 def health_state(self,**overrides):
  now=time.time();rows={self.names[0]:{'status':'temporary_failure','retry_at_epoch':0,'failures':7,'http_status':503},self.names[2]:{'status':'image_healthy','http_status':200,'retry_at_epoch':0,'last_success_at_epoch':now-60}}
  rows[self.names[2]].update(overrides)
  (self.root/router.STATE).write_text(json.dumps({'policy':router.POLICY,'cursor':0,'keys':rows}))
 def test_recent_real_success_precedes_failed_half_open_account(self):
  self.prefer_health();self.health_state();chosen=[]
  self.run_route(lambda *a,**kw:chosen.extend(kw['slots'])or b'ok')
  self.assertEqual(chosen,[self.names[2]])
 def test_healthy_priority_never_shortens_key_cooldown(self):
  self.prefer_health();self.health_state(retry_at_epoch=time.time()+600);chosen=[]
  self.run_route(lambda *a,**kw:chosen.extend(kw['slots'])or b'ok')
  self.assertNotEqual(chosen,[self.names[2]])
 def test_stale_success_does_not_override_rotation(self):
  self.prefer_health();self.health_state(last_success_at_epoch=time.time()-21601);chosen=[]
  p=self.root/router.STATE;s=json.loads(p.read_text());s['keys'][self.names[0]]['failures']=0;p.write_text(json.dumps(s))
  self.run_route(lambda *a,**kw:chosen.extend(kw['slots'])or b'ok')
  self.assertEqual(chosen,[self.names[0]])
 def test_health_preference_cannot_bypass_shared_rate_limit(self):
  self.prefer_health();self.health_state()
  p=self.root/router.STATE;value=json.loads(p.read_text());value['shared_retry_at_epoch']=time.time()+600;p.write_text(json.dumps(value))
  with self.assertRaises(ImageProviderBusy):self.run_route(lambda *a,**kw:self.fail('Shared stop must win'))
 def test_invalid_health_window_fails_closed(self):
  self.prefer_health();p=self.root/router.CONFIG;cfg=json.loads(p.read_text());cfg['prefer_recent_success_seconds']=True;p.write_text(json.dumps(cfg))
  with self.assertRaisesRegex(RuntimeError,'routing window'):self.run_route(lambda *a,**kw:self.fail('Bad config cannot request'))

 def test_transient_failure_keeps_prior_success_but_not_healthy_status(self):
  self.prefer_health();self.health_state();before=router.state(self.root)['keys'][self.names[2]]['last_success_at_epoch']
  with self.assertRaises(ImageProviderBusy):self.run_route(self.busy)
  row=router.state(self.root)['keys'][self.names[2]]
  self.assertEqual(row['last_success_at_epoch'],before);self.assertEqual(row['status'],'temporary_failure');self.assertEqual(row['http_status'],503)
 def test_all_unhealthy_accounts_prefer_fewer_failures_not_blind_cursor(self):
  self.prefer_health();now=time.time();s={'policy':router.POLICY,'cursor':0,'keys':{n:{'status':'temporary_failure','http_status':503,'retry_at_epoch':0,'failures':7 if i<2 else 1}for i,n in enumerate(self.names)}}
  (self.root/router.STATE).write_text(json.dumps(s));chosen=[]
  self.run_route(lambda *a,**kw:chosen.extend(kw['slots'])or b'ok');self.assertEqual(chosen,[self.names[2]])
 def test_proven_recovery_must_still_wait_for_its_retry_after(self):
  self.prefer_health();now=time.time();rows={n:{'status':'temporary_failure','http_status':503,'retry_at_epoch':0,'failures':7}for n in self.names}
  rows[self.names[2]].update(last_success_at_epoch=now-60,failures=1,retry_at_epoch=now+600)
  (self.root/router.STATE).write_text(json.dumps({'policy':router.POLICY,'cursor':0,'keys':rows}));chosen=[]
  self.run_route(lambda *a,**kw:chosen.extend(kw['slots'])or b'ok');self.assertNotIn(self.names[2],chosen)
 def test_proven_recovery_does_not_rotate_around_a_shared_rate_stop(self):
  self.prefer_health();now=time.time();s={'policy':router.POLICY,'shared_retry_at_epoch':now+600,'keys':{self.names[2]:{'status':'temporary_failure','failures':1,'last_success_at_epoch':now-60,'retry_at_epoch':0,'http_status':503}}}
  (self.root/router.STATE).write_text(json.dumps(s))
  with self.assertRaises(ImageProviderBusy):self.run_route(lambda *a,**kw:self.fail('Shared rate stop must win'))

if __name__=='__main__':unittest.main()
