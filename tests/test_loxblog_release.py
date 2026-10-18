import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from check_loxblog_release import evaluate
class InJobReleaseTests(unittest.TestCase):
 def setUp(self):self.release={'enabled':True,'verified_post_ids':[1,2],'acceptance_run':'https://github.com/getsalet/nono/actions/runs/38763868939'}
 def test_approved_schedule_is_not_lost_to_cross_job_outputs(self):self.assertTrue(evaluate(self.release,'schedule')['proceed'])
 def test_repository_pause_still_blocks_scheduled_work(self):self.assertFalse(evaluate(self.release,'schedule','0')['proceed'])
 def test_versioned_disabled_or_invalid_evidence_blocks_schedules(self):
  for release in ({},{**self.release,'enabled':False},{**self.release,'verified_post_ids':[1]},{**self.release,'verified_post_ids':[True,2]},{**self.release,'acceptance_run':'https://wrong.example/1'}):self.assertFalse(evaluate(release,'schedule')['proceed'])
 def test_stock_workflow_wakeup_requires_existing_release_and_respects_pause(self):
  self.assertTrue(evaluate(self.release,'workflow_run')['proceed'])
  self.assertFalse(evaluate(self.release,'workflow_run','0')['proceed'])
  self.assertFalse(evaluate({},'workflow_run')['proceed'])
 def test_push_cannot_publish_and_manual_behavior_is_preserved(self):
  self.assertFalse(evaluate(self.release,'push')['proceed']);self.assertTrue(evaluate({},'workflow_dispatch','0')['proceed'])
 def test_every_costly_or_checkpoint_step_is_guarded(self):
  import re
  source=(Path(__file__).resolve().parents[1]/'.github/workflows/loxblog-content.yml').read_text()
  tail=source[source.index('      - name: Check rolling publication budget before costly steps'):]
  for step in re.split(r'(?=^      - )',tail,flags=re.M):
   if step.strip():self.assertIn("steps.release.outputs.proceed == '1'",step)
if __name__=='__main__':unittest.main()
