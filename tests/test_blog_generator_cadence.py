"""Five-minute polling only; native writers and publication gates stay separate."""
import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OFFSETS={'roya-backlink-queue.yml':1,'roya-backlink-publish.yml':3,'farsiblog-content.yml':2,'rozblog-content.yml':3,'loxblog-content.yml':4,'blogsky-auto.yml':1,'niloblog-content.yml':2,'parsiblog-content.yml':4}
class GeneratorCadence(unittest.TestCase):
 def test_all_active_generation_and_publication_schedules_are_five_minutes(self):
  for filename,offset in OFFSETS.items():
   with self.subTest(workflow=filename):
    content=(ROOT/'.github/workflows'/filename).read_text()
    crons=re.findall(r"(?m)^    - cron: '([^']+)'$",content);self.assertEqual(len(crons),1)
    fields=crons[0].split();self.assertEqual(fields[1:],['*']*4)
    minutes=[int(x)for x in fields[0].split(',')];self.assertEqual(minutes,list(range(offset,60,5)))
    self.assertEqual([(minutes[(i+1)%len(minutes)]-m)%60 for i,m in enumerate(minutes)],[5]*12)
 def test_roya_generation_and_publication_keep_shared_serial_lock(self):
  for filename in ['roya-backlink-queue.yml','roya-backlink-publish.yml']:
   content=(ROOT/'.github/workflows'/filename).read_text();self.assertIn('group: roya-backlink-pipeline',content);self.assertIn('cancel-in-progress: false',content)
 def test_blogsky_native_writer_stays_serialized(self):
  content=(ROOT/'.github/workflows/blogsky-auto.yml').read_text();self.assertIn('group: blogsky-native-publication',content);self.assertIn('run: python automation/blogsky_auto_control.py',content)
 def test_existing_control_preflight_stays_present_for_each_blog(self):
  for filename in OFFSETS:
   content=(ROOT/'.github/workflows'/filename).read_text()
   self.assertTrue(any(x in content for x in ['check_blog_pipeline_control.py','blogsky_auto_control.py','pause_image_production','niloblog_pipeline.py']),filename)
if __name__=='__main__':unittest.main()
