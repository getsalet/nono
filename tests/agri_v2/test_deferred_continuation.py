import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation.agri_v2 import curated_continuation as c
from automation.agri_v2.queue import atomic_json,load_json,DATA
from automation.agri_v2.client import ModelClient
class DeferredContinuationTests(unittest.TestCase):
 def test_only_transient_image_failure_can_resume(self):
  req=load_json(DATA/'curated-continuation-request.json')
  for kind,code,expected in [('image_provider',503,True),('image_provider',429,True),('image_provider',401,False),('image_provider',402,False),('text_provider',503,False),('image_quality',503,False)]:
   row={'status':'stopped_safely','failure':{'kind':kind,'http_status':code}}
   self.assertEqual(c.resumable(row,req),expected)
   row['recovery_resumes']=2;self.assertFalse(c.resumable(row,req))
 def test_cooldown_never_reserves_another_call(self):
  with patch.object(c,'authorized',return_value=True),patch.object(c,'circuit_open',return_value=True),patch.object(c,'BoundedClient') as client,patch.object(c,'atomic_json') as write:
   self.assertEqual(c.run()['status'],'provider_cooldown');client.assert_not_called();write.assert_not_called()
 def test_cumulative_counts_keep_entire_verified_pool(self):
  def init(obj,*a,**kw):obj.keys={'image':[('AGNES_API_KEY','redacted'),('AGNES_API_KEY2','redacted2')]}
  with tempfile.TemporaryDirectory() as tmp,patch.object(ModelClient,'__init__',init),patch.object(ModelClient,'request',return_value={}):
   path=Path(tmp)/'calls.json';atomic_json(path,{'image_calls_reserved':1,'visual_review_calls_reserved':0})
   x=c.BoundedClient({},call_limit=4,review_limit=2,accounting_path=path)
   self.assertEqual(len(x.keys['image']),2);self.assertEqual(x.reserved['image'],1)
   for _ in range(3):x.request('image','/',{},1)
   with self.assertRaises(c.CapabilityError):x.request('image','/',{},1)
   for _ in range(2):x.request('text','/',{},1)
   with self.assertRaises(c.CapabilityError):x.request('text','/',{},1)
   self.assertEqual(load_json(path)['image_calls_reserved'],4)
   y=c.BoundedClient({},call_limit=4,review_limit=2,accounting_path=path)
   with self.assertRaises(c.CapabilityError):y.request('image','/',{},1)
 def test_publication_and_quality_stops_never_resume(self):
  req=load_json(DATA/'curated-continuation-request.json')
  for status in ('publication_verified','reserved','publishing_after_three_current_quality_passes'):
   self.assertFalse(c.resumable({'status':status,'failure':{'kind':'image_provider','http_status':503}},req))
