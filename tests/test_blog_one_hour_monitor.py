import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from monitor_blog_generators_one_hour import probe_allowed,DURATION,MAX_PROBES,WORKFLOWS
class FiniteMonitorTests(unittest.TestCase):
 def allowed(self,**kw):
  d=dict(elapsed=600,remaining=3000,attempts=0,last_probe=0,cooldown=100,now=200,received=False,control={'pause_image_production':False,'enabled_families':['tape20']});d.update(kw);return probe_allowed(**d)
 def test_finite_window_and_five_generators(self):self.assertEqual(DURATION,3600);self.assertEqual(MAX_PROBES,5);self.assertEqual(len(WORKFLOWS),5)
 def test_cooldown_and_spacing(self):self.assertTrue(self.allowed());self.assertFalse(self.allowed(cooldown=300));self.assertFalse(self.allowed(elapsed=500))
 def test_budget_and_remaining_window(self):self.assertFalse(self.allowed(attempts=5));self.assertFalse(self.allowed(remaining=650))
 def test_candidate_and_pause_stop_probes(self):self.assertFalse(self.allowed(received=True));self.assertFalse(self.allowed(control={'pause_image_production':True,'enabled_families':['tape20']}))
 def test_ambiguous_or_changed_scope(self):self.assertFalse(self.allowed(control={}));self.assertFalse(self.allowed(control={'pause_image_production':False,'enabled_families':['tape20','hose']}))
