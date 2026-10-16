import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_generated_image as g
import monitor_blog_generators_one_hour as m
class TapeRestartTests(unittest.TestCase):
 def test_cancelled_hose_never_assembles_prompt_or_calls_provider(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text(json.dumps({'cancelled_families':['hose'],'enabled_families':['hose','tape20']}))
   with patch.object(g.roya,'ROOT',root),patch('blog_reference_scene.prompt')as prompt,patch.object(g.roya.BASE._key_pool,'fetch_json')as fetch:
    self.assertFalse(g.family_enabled({'family':'hose'}))
    self.assertTrue(g.family_enabled({'family':'tape20'}))
    with self.assertRaisesRegex(RuntimeError,'cancelled'):g.generate({'family':'hose'},'loxblog')
    prompt.assert_not_called();fetch.assert_not_called()
 def snapshot(self):
  return {'release_control':{'enabled':True,'pause_image_production':False,'enabled_families':['tape20'],'cancelled_families':['hose'],'blogs':list(m.WORKFLOWS),'activation_dispatch_mode':'sequential_by_hour_monitor'},'provider_cooldown':{'retry_at_epoch':0},'blogs':{b:{'runs':[{'status':'completed','created_at':'2026-01-01T00:00:00Z'}]}for b in m.WORKFLOWS}}
 def test_active_workflow_or_shared_cooldown_blocks_dispatch(self):
  current=self.snapshot();current['provider_cooldown']['retry_at_epoch']=10**12
  with patch.object(m.urllib.request,'urlopen')as request:
   self.assertIsNone(m.dispatch_next(current,[]));current['provider_cooldown']['retry_at_epoch']=0
   current['blogs']['roya']['runs'][0]['status']='queued'
   self.assertIsNone(m.dispatch_next(current,[]));request.assert_not_called()
 def test_uncertain_or_not_yet_visible_dispatch_never_repeated(self):
  with patch.object(m.urllib.request,'urlopen')as request:
   for status in [None,403,204]:
    self.assertIsNone(m.dispatch_next(self.snapshot(),[{'blog':'roya','http_status':status,'requested_at':'2099-01-01T00:00:00Z'}]))
   request.assert_not_called()
 def test_single_guarded_tape_dispatch(self):
  with patch.object(m.urllib.request,'urlopen')as request,patch.object(g,'rollout_enabled',return_value=True),patch.dict('os.environ',{'GH_TOKEN':'offline-fixture'}):
   request.return_value.__enter__.return_value.status=204
   result=m.dispatch_next(self.snapshot(),[])
   payload=json.loads(request.call_args.args[0].data)
   self.assertEqual(result['blog'],'roya');self.assertEqual(result['http_status'],204)
   self.assertEqual(payload['inputs'],{'count':'1','dry_run':'0','target':''})
   self.assertNotIn('verify_hose_full_references',__import__('inspect').getsource(m.main))
 def test_hose_diagnostics_stop_before_any_api(self):
  import diagnose_hose_provider,inspect_hose_provider_error,probe_blog_image_transport,verify_hose_full_references
  for module in [diagnose_hose_provider,inspect_hose_provider_error,probe_blog_image_transport,verify_hose_full_references]:
   with patch.object(g,'family_cancelled',return_value=True),patch('urllib.request.urlopen')as request:
    self.assertEqual(module.main(),0);request.assert_not_called()
