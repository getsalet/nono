"""A repeatedly deferred oldest article must not starve the other blogs."""
import json,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_stock as stock
import blog_generated_image as generated
class StockFairnessTests(unittest.TestCase):
 def test_never_attempted_request_precedes_old_deferred_request(self):
  with tempfile.TemporaryDirectory()as directory,patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}):
   root=Path(directory);(root/'data').mkdir();(root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3}))
   items=[]
   for key in ['old-repeated','fresh-waiting']:
    item={'key':key,'family':'tape20','site_title':'نوار تیپ پیاز','_image_article_context':{'title':'آبیاری پیاز با نوار تیپ','summary':'این متن واقعی آموزشی درباره بررسی خطوط نوار تیپ در ردیف های پیاز و توزیع رطوبت خاک است'}}
    items.append(item)
    with self.assertRaises(stock.ImagePending):stock.request_image(item,'roya',root)
   pending=stock.rows(root)
   old=next(r for r in pending if r['key']=='old-repeated');old.update(attempts=2,started_at=time.time(),retry_at=0);stock.persist(root,old)
   source=root/'data/roya/backlink-queue.json';source.parent.mkdir(parents=True);source.write_text(json.dumps({'items':items}))
   seen=[]
   def approved(item,*args,**kwargs):seen.append(item['key']);item['image_review']={'sha256':'a'*64};return 'immutable-approved'
   with patch.object(generated,'rollout_enabled',return_value=True),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open'),patch.object(generated,'prepare_now',side_effect=approved):
    result=stock.worker_once(root)
   self.assertEqual(seen,['fresh-waiting']);self.assertEqual(result['status'],'ready')
