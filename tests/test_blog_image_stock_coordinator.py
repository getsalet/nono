"""Coordinator cannot publish, call an image provider, or bypass its stop gates."""
import copy,datetime as dt,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_stock_coordinator as c
class CoordinatorTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,18,16,tzinfo=dt.timezone.utc).timestamp()
  self.cfg=json.loads((ROOT/c.CONFIG).read_text())
  self.control={'enabled':True,'pause_image_production':False,'blogs':sorted(c.BLOGS),'retired_blogs':['blogfa'],'enabled_families':['tape20']}
  self.key_config={'policy':'audited-image-key-pool-v1','enabled':True,'slots':['AGNES_API_KEY10','AGNES_API_KEY7','AGNES_API_KEY11','AGNES_API_KEY3']}
  self.pool={'policy':'audited-image-key-pool-v1','keys':{s:{'status':'image_healthy','retry_at_epoch':0}for s in self.key_config['slots']}}
  self.provider={'retry_at_epoch':0}
  self.audit={'finished_at':dt.datetime.fromtimestamp(self.now-3600,dt.timezone.utc).isoformat(),'complete_text':True,'complete_image':True,'connection':{'endpoint':'https://apihub.agnes-ai.com/v1/images/generations','model':'agnes-image-2.5-flash'}}
  self.stock=[{'blog':'roya','status':'requested','retry_at':0,'item':{'family':'tape20'}}]
 def snapshot(self):return copy.deepcopy({'cfg':self.cfg,'control':self.control,'key_config':self.key_config,'provider':self.provider,'pool':self.pool,'stock':self.stock,'audit':self.audit})
 def plan(self,**kwargs):return c.plan(**(self.snapshot()|{'runs':[],'now':self.now}|kwargs))
 def old_run(self,seconds=600,status='completed'):
  return {'created_at':dt.datetime.fromtimestamp(self.now-seconds,dt.timezone.utc).isoformat(),'status':status}
 def test_due_work_dispatches_only_the_existing_worker(self):self.assertTrue(self.plan()['dispatch'])
 def test_paused_disabled_or_retired_production_never_dispatches(self):
  for field,value in [('enabled',False),('pause_image_production',True)]:
   control=self.control|{field:value};r=self.plan(control=control);self.assertFalse(r['dispatch']);self.assertTrue(r['stop'])
  self.assertFalse(self.plan(cfg=self.cfg|{'enabled':False})['dispatch'])
  self.assertFalse(self.plan(stock=[{'blog':'blogfa','status':'requested','item':{'family':'tape20'}}])['dispatch'])
 def test_hose_ready_and_text_repair_rows_do_not_trigger_provider_work(self):
  for update in ({'status':'ready'},{'status':'consumed'},{'status':'needs_text_repair'},{'item':{'family':'hose'}}):self.assertFalse(self.plan(stock=[self.stock[0]|update])['dispatch'])
 def test_active_worker_blocks_a_second_dispatch(self):
  for status in c.ACTIVE:self.assertEqual(self.plan(runs=[self.old_run(status=status)])['reason'],'worker_already_active')
 def test_minimum_spacing_uses_both_run_history_and_local_dispatch_reservation(self):
  self.assertEqual(self.plan(runs=[self.old_run(299)])['reason'],'minimum_dispatch_spacing')
  self.assertFalse(self.plan(last_dispatch=self.now-100)['dispatch'])
  self.assertTrue(self.plan(runs=[self.old_run(300)])['dispatch'])
 def test_rolling_budget_counts_all_workflow_events_and_session_budget_is_bounded(self):
  self.assertEqual(self.plan(runs=[self.old_run(301+i*100)for i in range(12)])['reason'],'rolling_worker_run_budget')
  self.assertEqual(self.plan(dispatches=12)['reason'],'session_dispatch_budget')
 def test_long_run_history_is_usable_when_it_covers_the_whole_hour(self):
  self.assertTrue(self.plan(runs=[self.old_run(4000+i)for i in range(100)])['dispatch'])
  with self.assertRaises(ValueError):self.plan(runs=[self.old_run(301+i)for i in range(100)])
 def test_global_rate_limit_and_all_key_cooldowns_are_honored(self):
  self.assertEqual(self.plan(provider={'retry_at_epoch':self.now+300})['reason'],'provider_cooldown')
  pool=copy.deepcopy(self.pool);pool['shared_retry_at_epoch']=self.now+600
  self.assertEqual(self.plan(pool=pool)['retry_at'],self.now+600)
  pool=copy.deepcopy(self.pool)
  for row in pool['keys'].values():row['retry_at_epoch']=self.now+1200
  self.assertEqual(self.plan(pool=pool)['retry_at'],self.now+1200)
 def test_billing_and_disabled_routes_stop_instead_of_rotating(self):
  pool=self.pool|{'shared_block':'billing_required'};self.assertTrue(self.plan(pool=pool)['stop'])
  pool=copy.deepcopy(self.pool)
  for row in pool['keys'].values():row['status']='authentication_rejected'
  self.assertEqual(self.plan(pool=pool)['reason'],'all_audited_routes_disabled')
 def test_article_retry_and_audit_expiry_do_not_generate_a_request(self):
  self.assertEqual(self.plan(stock=[self.stock[0]|{'retry_at':self.now+1800}])['reason'],'article_retry_cooldown')
  audit=self.audit|{'finished_at':dt.datetime.fromtimestamp(self.now-73*3600,dt.timezone.utc).isoformat()}
  self.assertEqual(self.plan(audit=audit)['reason'],'image_capability_audit_expired')
 def test_no_unverified_six_or_duplicate_eight_slots_or_expanded_budgets(self):
  for slots in (['AGNES_API_KEY6'],['AGNES_API_KEY8'],['AGNES_API_KEY10']*2):
   with self.assertRaises(ValueError):self.plan(key_config=self.key_config|{'slots':slots})
  with self.assertRaises(ValueError):self.plan(cfg=self.cfg|{'max_worker_runs_per_hour':100})
 def test_malformed_times_and_ambiguous_history_fail_closed(self):
  for value in (True,-1,float('nan'),'0'):
   with self.assertRaises(ValueError):self.plan(provider={'retry_at_epoch':value})
  with self.assertRaises(ValueError):self.plan(runs=[{'created_at':'2026-10-18T16:00:00','status':'completed'}])
 def test_dispatch_timeout_stops_and_cannot_issue_a_blind_second_request(self):
  client=Mock();client.runs.return_value=[];client.dispatch.side_effect=TimeoutError()
  snap=self.snapshot()|{'ref':'a'*40}
  with tempfile.TemporaryDirectory()as d:
   self.assertEqual(c.run(Path(d),clock=lambda:self.now,sleep=Mock(),client=client,loader=lambda root:copy.deepcopy(snap)),0)
   report=json.loads((Path(d)/'artifacts/blog-image-coordinator/latest.json').read_text())
  client.dispatch.assert_called_once();self.assertEqual(report['events'][-1]['reason'],'dispatch_outcome_unverified')
 def test_successful_dispatch_still_rechecks_pause_before_any_next_request(self):
  client=Mock();client.runs.return_value=[];client.dispatch.return_value={'http_status':204};count=[0]
  def load(root):
   count[0]+=1;snap=self.snapshot()|{'ref':'a'*40}
   if count[0]>2:snap['control']['pause_image_production']=True
   return snap
  with tempfile.TemporaryDirectory()as d:
   c.run(Path(d),clock=lambda:self.now,sleep=Mock(),client=client,loader=load)
  client.dispatch.assert_called_once()
 def test_failed_worker_is_not_blindly_redispatched(self):
  row=self.old_run()|{'conclusion':'failure'}
  self.assertEqual(self.plan(runs=[row])['reason'],'worker_failure_requires_review')
  self.assertTrue(self.plan(runs=[row])['stop'])
 def test_accepted_but_unobserved_dispatch_cannot_be_duplicated(self):
  r=self.plan(last_dispatch=self.now-100);self.assertFalse(r['dispatch']);self.assertFalse(r['stop'])
  r=self.plan(last_dispatch=self.now-301);self.assertFalse(r['dispatch']);self.assertTrue(r['stop'])
 def test_workflow_has_finite_timeout_no_image_secrets_and_its_own_lock(self):
  s=(ROOT/'.github/workflows/blog-image-stock-coordinator.yml').read_text()
  self.assertIn('timeout-minutes: 65',s);self.assertIn('group: afp-bounded-image-stock-coordinator',s)
  self.assertIn('actions: write',s);self.assertNotIn('secrets.',s)
  self.assertNotIn('publish_',s);self.assertNotIn('cancel-in-progress: true',s)
  worker=(ROOT/'.github/workflows/blog-image-stock.yml').read_text()
  self.assertIn('Process at most one article-owned image',worker)
if __name__=='__main__':unittest.main()
