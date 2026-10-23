import copy,importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('nm',R/'automation/niloblog_media.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MediaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.c=json.loads((R/'data/niloblog/media-catalog.json').read_text())
 def test_integrity(self): m.validate_catalog(self.c)
 def test_round_robin(self):
  s=None; ids=[]
  for i in range(38):
   s,a=m.reserve(self.c,s,str(i));ids.append(a['image_id']);s=m.acknowledge(self.c,s,str(i),f'https://afp.niloblog.com/p/{i}',public_receipt_verified=True)
  self.assertEqual(len(set(ids[:37])),37);self.assertEqual(ids[0],ids[37])
 def test_retry_stable(self):
  s,a=m.reserve(self.c,None,'p');s2,a2=m.reserve(self.c,s,'p');self.assertEqual((s,a),(s2,a2));self.assertEqual(s['next_image'],0)
 def test_pending_blocks_next(self):
  s,_=m.reserve(self.c,None,'p')
  with self.assertRaises(ValueError): m.reserve(self.c,s,'q')
 def test_receipt_required(self):
  s,_=m.reserve(self.c,None,'p')
  with self.assertRaises(ValueError): m.acknowledge(self.c,s,'p','https://afp.niloblog.com/p/1')
  self.assertEqual(s['next_image'],0)
 def test_acked_retry_does_not_advance(self):
  s,a=m.reserve(self.c,None,'p');s=m.acknowledge(self.c,s,'p','https://afp.niloblog.com/p/1',public_receipt_verified=True);s2,a2=m.reserve(self.c,s,'p');self.assertEqual(s,s2);self.assertEqual(a,a2)
 def test_video_rate_endpoints(self):
  self.assertIsNone(m.reserve(self.c,None,'p',0)[1]['video_id']);self.assertIsNotNone(m.reserve(self.c,None,'p',1)[1]['video_id'])
 def test_unsafe_media_rejected(self):
  c=copy.deepcopy(self.c);c['assets'][0]['url']='https://evil.example/a.webp'
  with self.assertRaises(ValueError):m.validate_catalog(c)
 def test_unverified_image_rejected(self):
  c=copy.deepcopy(self.c);next(a for a in c['assets'] if a['kind']=='image')['public_sha256_verified']=False
  with self.assertRaises(ValueError):m.validate_catalog(c)
if __name__=='__main__':unittest.main()
