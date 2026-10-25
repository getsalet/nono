import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2.slug_repair import publication_slug,repair_brief
from automation.agri_v2.queue import atomic_json,load_json
from test_research import TOPIC,fixtures
from automation.agri_v2.research import build_brief
class SlugRepairTests(unittest.TestCase):
 def test_valid_slug_unchanged(self):self.assertEqual(publication_slug(TOPIC,'bean-harvest'),'bean-harvest')
 def test_invalid_formats_get_stable_topic_id(self):
  for value in ['kاهش-تلفات','/path','a'*101,None,{},'Upper Case']:
   self.assertEqual(publication_slug(TOPIC,value),TOPIC['id'])
 def test_format_does_not_bypass_review(self):
  d,c,r,i=fixtures();c['slug']='فارسی';r['safe_qualitative']=False
  with self.assertRaises(ValueError):build_brief(TOPIC,d,c,r,i)
 def test_evidence_repair_preserves_attempts_and_original_bytes(self):
  import hashlib
  d,c,r,i=fixtures();c['slug']='فارسی'
  for row in d:row['sha256']=hashlib.sha256(row['text'].encode()).hexdigest()
  with tempfile.TemporaryDirectory() as tmp:
   data=Path(tmp)/'data';out=Path(tmp)/'out';base=out/'research-evidence'/TOPIC['id'];sp=out/'research'/f"{TOPIC['id']}.json"
   atomic_json(sp,{'status':'needs_review','reason':'invalid_research_slug','attempts':1})
   for name,val in [('sources',{'documents':d}),('candidate-raw',c),('review',{'review':r})]:atomic_json(base/(name+'.json'),val)
   before={p:p.read_bytes() for p in base.iterdir()}
   with patch('automation.agri_v2.slug_repair.get_topic',return_value=TOPIC):repair_brief(TOPIC['id'],i,data,out)
   self.assertEqual(load_json(sp)['attempts'],1)
   for p,b in before.items():self.assertEqual(p.read_bytes(),b)
   self.assertEqual(load_json(data/'briefs'/f"{TOPIC['id']}.json")['slug'],TOPIC['id'])
