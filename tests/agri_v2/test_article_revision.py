import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from automation.agri_v2.article_revision import checked_candidate
class RevisionTests(unittest.TestCase):
 def test_valid_article_has_no_extra_call(self):
  with tempfile.TemporaryDirectory() as d,patch('automation.agri_v2.pipeline.normalize_article',side_effect=lambda a,b:a),patch('automation.agri_v2.pipeline.validate_article'),patch('automation.agri_v2.pipeline.validate_for_publication'):
   client=Mock();self.assertEqual(checked_candidate({'ok':True},{},{},Path(d),client),{'ok':True});client.text.assert_not_called()
 def test_one_revision_then_resume_without_second_call(self):
  with tempfile.TemporaryDirectory() as d,patch('automation.agri_v2.pipeline.normalize_article',side_effect=lambda a,b:a),patch('automation.agri_v2.pipeline.validate_for_publication'),patch('automation.agri_v2.pipeline.validate_article') as validate:
   def check(a,*args):
    if not a.get('ok'):raise ValueError('Draft must cite approved sources inline')
   validate.side_effect=check;client=Mock();client.text.return_value={'ok':True}
   for _ in range(2):self.assertEqual(checked_candidate({}, {}, {},Path(d),client),{'ok':True})
   client.text.assert_called_once()
 def test_invalid_revision_never_repeats(self):
  with tempfile.TemporaryDirectory() as d,patch('automation.agri_v2.pipeline.normalize_article',side_effect=lambda a,b:a),patch('automation.agri_v2.pipeline.validate_article',side_effect=ValueError('Draft must cite approved sources inline')):
   client=Mock();client.text.return_value={}
   for _ in range(2):
    with self.assertRaises(ValueError):checked_candidate({},{},{},Path(d),client)
   client.text.assert_called_once()
 def test_unrelated_safety_failure_not_repaired(self):
  with tempfile.TemporaryDirectory() as d,patch('automation.agri_v2.pipeline.normalize_article',side_effect=ValueError('Active model HTML attribute')):
   client=Mock()
   with self.assertRaises(ValueError):checked_candidate({},{},{},Path(d),client)
   client.text.assert_not_called()
