import datetime,hashlib,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import Mock
from automation.agri_v2.source_loading import load_documents,MAX_WORKERS
from automation.agri_v2.research import source_host
from automation.agri_v2.cycle import fresh_inventory
from automation.agri_v2.queue import utcnow,atomic_json

def doc(u):
 text='verified extension evidence '*40
 return dict(url=u,text=text,sha256=hashlib.sha256(text.encode()).hexdigest(),fetched_at=utcnow())
def ago(hours):return (datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(hours=hours)).isoformat()
class SpeedIOTests(unittest.TestCase):
 def test_parallel_order_dedup_and_worker_bound(self):
  with tempfile.TemporaryDirectory() as d:
   urls=[f'https://extension.msu.edu/{i}' for i in range(8)];barrier=threading.Barrier(MAX_WORKERS);calls=[];lock=threading.Lock()
   def fetch(u):
    with lock:calls.append(u)
    barrier.wait(timeout=3)
    return doc(u)
   result=load_documents(urls+[urls[0]],fetch,Path(d),source_host)
   self.assertEqual([r['url'] for r in result],urls[:6]);self.assertEqual(len(calls),6)
 def test_cache_reuses_original_timestamp_without_fetch(self):
  with tempfile.TemporaryDirectory() as d:
   u='https://extension.msu.edu/beans';f=Mock(side_effect=doc)
   a=load_documents([u,u],f,Path(d),source_host);b=load_documents([u],f,Path(d),source_host)
   self.assertEqual(a,b);f.assert_called_once_with(u)
 def test_stale_corrupt_future_and_wrong_url_are_refetched(self):
  for change in ({'fetched_at':ago(7)},{'sha256':'0'*64},{'fetched_at':ago(-1)},{'url':'https://extension.msu.edu/other'}):
   with self.subTest(change=change),tempfile.TemporaryDirectory() as d:
    u='https://extension.msu.edu/beans';old=doc(u);old.update(change)
    atomic_json(Path(d)/'source-cache'/(hashlib.sha256(u.encode()).hexdigest()+'.json'),old)
    f=Mock(side_effect=doc);load_documents([u],f,Path(d),source_host);f.assert_called_once()
 def test_failures_not_cached_or_retried(self):
  with tempfile.TemporaryDirectory() as d:
   f=Mock(side_effect=RuntimeError('network'));u='https://extension.msu.edu/beans'
   self.assertEqual(load_documents([u],f,Path(d),source_host),[])
   self.assertEqual(load_documents([u],f,Path(d),source_host),[]);self.assertEqual(f.call_count,2)
 def test_unsafe_url_never_fetches(self):
  with tempfile.TemporaryDirectory() as d:
   f=Mock();self.assertEqual(load_documents(['https://localhost/private'],f,Path(d),source_host),[]);f.assert_not_called()
 def test_immediate_research_inventory_is_reused(self):
  wp=Mock();s=dict(source_generated_at=utcnow(),scope='all published',records=[{'id':1}])
  self.assertIs(fresh_inventory(wp,s),s);wp.inventory.assert_not_called()
 def test_stale_future_or_empty_inventory_refetches(self):
  for date,records in [(ago(1),[{'id':1}]),(ago(-1),[{'id':1}]),(utcnow(),[])]:
   wp=Mock();fresh_inventory(wp,dict(source_generated_at=date,scope='all published',records=records));wp.inventory.assert_called_once()
