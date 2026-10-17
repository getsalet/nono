import datetime,io,json,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_generation_status as status
import roya_backlink_queue as r
class GenerationStatusTests(unittest.TestCase):
 def test_real_failures_are_not_hidden(self):
  self.assertEqual(status.outcome([],['failed'],time.time()+60),'failed')
  self.assertEqual(status.outcome(['ok'],['failed']),'partial_success')
  self.assertEqual(status.outcome(['ok'],[]),'produced')
 def test_idle_and_waiting_explicitly_not_generation(self):
  self.assertEqual(status.outcome([],[]),'idle');self.assertEqual(status.outcome([],[],time.time()+60),'waiting_provider')
  with tempfile.TemporaryDirectory()as d,patch.dict(os.environ,{'GITHUB_STEP_SUMMARY':d+'/summary'}):
   row=status.write(Path(d),'rozblog',[],[],time.time()+60)
   self.assertFalse(row['publication_verified_by_this_report']);self.assertEqual(row['completed_this_run'],0)
   self.assertIn('not successful generation',(Path(d)/'summary').read_text())
 def test_roya_existing_cooldown_returns_idle_success_without_any_api(self):
  from blog_image_backpressure import ImageProviderBusy
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);art=root/'artifacts/roya-backlink-queue';art.mkdir(parents=True)
   queue=root/'queue.json';state=root/'state.json';row={'key':'pending','status':'pending','family':'tape20','province':'test'}
   r.save_json(queue,{'items':[row]});r.save_json(state,{})
   with patch.multiple(r,ROOT=root,QUEUE_PATH=queue,STATE_PATH=state,LINKS_PATH=root/'links.json',ITEMS=art/'items',PUBLISH_QUEUE=art/'publish-queue.json',STATUS_MD=art/'status.md',DRY_RUN=False),patch.object(r.BASE,'AGNES_KEY','offline-fixture'),patch.object(r,'assign_roya_titles'),patch.object(r,'pick',return_value=[row]),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open',side_effect=ImageProviderBusy(time.time()+600)),patch.object(r,'agnes')as text,patch.object(r,'prepare_roya_image')as image:
    self.assertEqual(r.main(),0);text.assert_not_called();image.assert_not_called()
   self.assertEqual(json.loads((art/'generation-status.json').read_text())['status'],'waiting_provider')
   self.assertEqual(json.loads(queue.read_text())['items'][0]['status'],'pending')
 def test_actual_capacity_failure_after_attempt_stays_failed(self):
  from blog_image_backpressure import ImageProviderBusy
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);art=root/'artifacts/roya-backlink-queue';art.mkdir(parents=True)
   queue=root/'queue.json';state=root/'state.json';row={'key':'pending','status':'pending','family':'tape20','province':'test','assigned_title':'نوار تیپ پیاز'}
   r.save_json(queue,{'items':[row]});r.save_json(state,{})
   post={'title':'نوار تیپ پیاز','slug':'test','html':'<p>متن پیش نویس کافی برای نگهداری و تلاش مجدد پس از خطای موقت تصویر</p>'}
   with patch.multiple(r,ROOT=root,QUEUE_PATH=queue,STATE_PATH=state,LINKS_PATH=root/'links.json',ITEMS=art/'items',PUBLISH_QUEUE=art/'publish-queue.json',STATUS_MD=art/'status.md',DRY_RUN=False,ATTEMPTS=1),patch.object(r.BASE,'AGNES_KEY','offline-fixture'),patch.object(r,'assign_roya_titles'),patch.object(r,'pick',return_value=[row]),patch.object(r,'approved_links',return_value=[]),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open'),patch.object(r,'agnes',return_value=post),patch.object(r,'prepare_roya_image',side_effect=ImageProviderBusy(time.time()+600)):
    self.assertEqual(r.main(),1)
   result=json.loads((art/'generation-status.json').read_text())
   self.assertEqual(result['status'],'failed');self.assertEqual(result['failed_this_run'],1)
 def test_both_generators_track_attempted_failures_and_preflight_waiting(self):
  import inspect,farsiblog_backlink_queue as f
  for module in [r,f]:
   source=inspect.getsource(module.main);self.assertIn('blocked_until=busy.retry_at',source);self.assertIn('write_generation_status',source)
   self.assertIn("failed.append(item['key'])",source)
if __name__=='__main__':unittest.main()
