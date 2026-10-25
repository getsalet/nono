import unittest
from automation.agri_v2.prepared_continuation import run
class PreparedContinuationTests(unittest.TestCase):
 def test_unbounded_or_wrong_topic_never_runs(self):
  for req in ({},{'prepared_topic':'wrong','max_image_calls':2,'max_visual_reviews':2,'max_text_generation_calls':0},{'prepared_topic':'agri-5419edf5b44f','max_image_calls':3,'max_visual_reviews':2,'max_text_generation_calls':0}):
   with self.assertRaises(ValueError):run(req)
 def test_exact_prepared_article_passes_original_checks(self):
  from automation.agri_v2.queue import DATA,load_json,get_topic
  from automation.agri_v2.pipeline import validate_article,validate_for_publication
  ident='agri-5419edf5b44f';a=load_json(DATA/'prepared-articles'/f'{ident}.json');b=load_json(DATA/'briefs'/f'{ident}.json')
  validate_article(a,get_topic('new',ident),b);validate_for_publication(a)

class RecoveryTests(unittest.TestCase):
 def test_shared_cooldown_blocks_before_wp_or_model(self):
  import tempfile
  from pathlib import Path
  from unittest.mock import patch
  from automation.agri_v2 import prepared_continuation as c
  from automation.agri_v2.queue import atomic_json
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'config.json',{'publication_enabled':True,'automatic_generation':True})
   atomic_json(out/'prepared-continuations'/c.ID/'receipt.json',{'status':'stopped_safely','image_calls':1,'visual_reviews':0,'failure':{'kind':'image_provider','category':'provider_unavailable'}})
   req={'prepared_topic':c.TOPIC,'max_image_calls':2,'max_visual_reviews':2,'max_text_generation_calls':0,'max_recovery_cycles':1,'max_total_image_calls':3}
   with patch.object(c,'DATA',data),patch.object(c,'OUT',out),patch.object(c,'authorized',return_value=True),patch('automation.agri_v2.recovery.circuit_open',return_value=True),patch('automation.agri_v2.wordpress.WordPress') as wp:
    self.assertEqual(c.run(req,allow_recovery=True)['status'],'provider_cooldown');wp.assert_not_called()
 def test_exhausted_recovery_does_not_block_other_topics(self):
  import tempfile
  from pathlib import Path
  from unittest.mock import patch
  from automation.agri_v2 import prepared_continuation as c
  from automation.agri_v2.queue import atomic_json
  with tempfile.TemporaryDirectory() as t:
   data=Path(t)/'data';out=Path(t)/'out';atomic_json(data/'production-start-request.json',{'prepared_topic':c.TOPIC})
   atomic_json(out/'prepared-continuations'/c.ID/'receipt.json',{'status':'stopped_safely','recovery_cycles':1})
   with patch.object(c,'DATA',data),patch.object(c,'OUT',out),patch.object(c,'run') as run:
    self.assertIsNone(c.scheduled_resume());run.assert_not_called()
