import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import editorial_repair as e
from automation.agri_v2.research import validate_evidence
from automation.agri_v2.queue import DATA,OUT,load_json,atomic_json,get_topic
class EditorialRepairTests(unittest.TestCase):
 def test_curated_request_is_grounded_in_actual_retained_sources(self):
  r=load_json(DATA/'editorial-repair-request.json');e.validate_request(r);docs=load_json(OUT/'research-evidence'/r['topic_id']/'sources.json')['documents'];self.assertEqual(len(validate_evidence(get_topic('new',r['topic_id']),r['candidate'],docs)),6)
 def test_no_publication_authorization_for_review_job(self):
  r=load_json(DATA/'editorial-repair-request.json');r['max_new_posts']=1
  with self.assertRaises(ValueError):e.validate_request(r)
 def test_repeated_request_does_not_repeat_paid_review(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);request=load_json(DATA/'editorial-repair-request.json');atomic_json(root/'data/editorial-repair-request.json',request);atomic_json(root/'out/editorial-repairs'/e.ID/'receipt.json',{'status':'reserved'})
   with patch.object(e,'DATA',root/'data'),patch.object(e,'OUT',root/'out'),patch.object(e,'ModelClient') as client:
    self.assertEqual(e.run()['status'],'already_reserved');client.assert_not_called()
if __name__=='__main__':unittest.main()
