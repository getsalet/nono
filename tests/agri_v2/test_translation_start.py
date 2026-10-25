import unittest
from automation.agri_v2.translation_start import run
class TranslationStartTests(unittest.TestCase):
 def test_wrong_topic_or_extra_calls_rejected_before_network(self):
  for req in ({},{'multilingual_source_topic':'agri-a4f1fee1e3ee','max_translation_calls':5,'max_new_source_posts':0,'max_new_image_calls':0},{'multilingual_source_topic':'wrong','max_translation_calls':4,'max_new_source_posts':0,'max_new_image_calls':0}):
   with self.assertRaises(ValueError):run(req)
