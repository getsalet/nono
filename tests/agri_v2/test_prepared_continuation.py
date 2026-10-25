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
