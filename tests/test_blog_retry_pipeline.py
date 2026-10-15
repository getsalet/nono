import copy,datetime,json,os,sys,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import farsiblog_backlink_queue as e
import city_backlink_policy as c
class RetryTests(unittest.TestCase):
 def test_cooldown_and_capped_backoff(self):
  clock=datetime.datetime(2026,10,13,tzinfo=datetime.timezone.utc)
  row={'attempts':1};e.defer_item(row,clock)
  self.assertFalse(e.retry_due(row,clock));self.assertTrue(e.retry_due(row,clock+datetime.timedelta(hours=1)))
  row['attempts']=100;e.defer_item(row,clock)
  self.assertTrue(e.retry_due(row,clock+datetime.timedelta(hours=24)))
 def test_transient_retries_but_not_authentication_failure(self):
  with patch.object(e.time,'sleep'),patch('builtins.print'):
   calls=[]
   def operation():
    calls.append(1)
    if len(calls)<3:raise TimeoutError()
    return 'ok'
   self.assertEqual(e.retry_transient(operation),'ok');self.assertEqual(len(calls),3)
   with self.assertRaises(urllib.error.HTTPError):e.retry_transient(lambda:(_ for _ in ()).throw(urllib.error.HTTPError('https://example.org',401,'unauthorized',{},None)))
 def test_rejected_item_does_not_block_next_topic(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);queue=root/'queue.json';art=root/'art';state=root/'state.json'
   items=[{'key':k,'kind':'city','family':'tape20','status':'pending','site_title':'نوار تیپ','image_url':'https://navar-abyari.ir/wp-content/uploads/test.webp','image_alt':'نوار تیپ','image_width':600,'image_height':400}for k in ('bad','good')]
   e.save(queue,{'items':items})
   def image(row):
    if row['key']=='bad':raise RuntimeError('Product image rejected: wrong family')
   post={'title':'راهنمای انتخاب نوار تیپ','slug':'test-good','html':'<p>متن آزمایشی</p>'}
   with patch('blog_image_runtime_control.generation_paused',return_value=False),patch.multiple(e,QUEUE=queue,ART=art,STATE=state),patch.dict(os.environ,{'FARSIBLOG_COUNT':'1','FARSIBLOG_DRY_RUN':'0','FARSIBLOG_TARGET':''}),patch.object(e.BASE,'AGNES_KEY','test-only-not-a-secret'),patch.object(c,'matrix_ready',return_value=True),patch.object(c,'build_queue'),patch.object(c,'prepare_image',side_effect=image),patch.object(e,'source_text',return_value='fixture'),patch.object(e,'links_for',return_value=[]),patch.object(e,'prompt',return_value='fixture'),patch.object(e,'agnes',return_value=post),patch.object(e,'qa',return_value=([],{'words':600})):
    self.assertEqual(e.main(),0)
   result=e.load(queue,{})['items'];self.assertEqual(result[0]['status'],'failed');self.assertIn('next_retry_at',result[0]);self.assertEqual(result[1]['status'],'completed')
if __name__=='__main__':unittest.main()
