"""Capacity must be checked before buying new prose, not only before image API."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_stock as stock
import blog_generated_image as generated
import farsiblog_backlink_queue as f
class CapacityPreflightTests(unittest.TestCase):
 def test_full_blog_stock_prevents_source_and_text_calls(self):
  with tempfile.TemporaryDirectory()as directory,patch.dict(os.environ,{'GITHUB_ACTIONS':'false','FARSIBLOG_COUNT':'1','FARSIBLOG_DRY_RUN':'0','FARSIBLOG_TARGET':''}):
   root=Path(directory);art=root/'artifacts/farsiblog-backlink-queue';art.mkdir(parents=True)
   (root/'data').mkdir();(root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3}))
   queue=root/'data/farsiblog/backlink-queue.json';state=root/'state.json'
   for i in range(3):
    item={'key':'owned'+str(i),'family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز','summary':'این متن آموزشی مربوط به بررسی و نصب نوار تیپ در ردیف های پیاز و بررسی رطوبت خاک است'}}
    with self.assertRaises(stock.ImagePending):stock.request_image(item,'farsiblog',root)
   item={'key':'new-no-draft','family':'tape20','kind':'city','status':'pending','site_title':'نوار تیپ پیاز'}
   f.save(queue,{'items':[item]});post={'title':'نوار تیپ پیاز','slug':'onion-topic','html':'<p>این متن واقعی درباره نصب نوار تیپ در ردیف های پیاز و بررسی توزیع رطوبت در خاک است</p>'}
   with patch.multiple(f,ROOT=root,QUEUE=queue,ART=art,STATE=state,CITY_BLOG='farsiblog'),patch.object(f.BASE,'AGNES_KEY','offline-fixture'),patch.object(f,'remaining_publication_budget',return_value=3),patch.object(f,'links_for',return_value=[]),patch.object(f,'source_text',return_value='source')as source,patch.object(f,'prompt',return_value='prompt'),patch('city_backlink_policy.build_queue'),patch('city_backlink_policy.matrix_ready',return_value=True),patch('city_backlink_policy.matrix_title',return_value=post['title']),patch('city_backlink_policy.resolve_editorial_link_tokens'),patch('city_backlink_policy.prepare_image',side_effect=lambda item:stock.request_image(item,'farsiblog',root)),patch.object(f,'agnes',return_value=post)as text:
    self.assertEqual(f.main(),0);text.assert_not_called();source.assert_not_called()
   self.assertEqual(len(stock.rows(root)),3)
   self.assertEqual(json.loads((art/'generation-status.json').read_text())['status'],'waiting_image')

 def test_ready_asset_not_blocked_by_twelve_active_requests(self):
  from blog_image_stock_preflight import eligible
  current=[{'blog':blog,'key':blog+str(i),'status':'ready'if blog=='roya'and i==0 else'requested'}for blog in ['roya','farsiblog','rozblog','blogfa']for i in range(3)]
  with patch('blog_image_stock_preflight.enabled',return_value=True),patch('blog_image_stock_preflight.rows',return_value=current),patch('blog_image_stock_preflight.control',return_value={'target':12,'per_blog_limit':3}):
   self.assertEqual(eligible([{'key':'roya0'},{'key':'new'}],'roya',ROOT),[{'key':'roya0'}])
   self.assertEqual(eligible([{'key':'new'}],'loxblog',ROOT),[])
 def test_disabled_stock_preserves_legacy_selection(self):
  from blog_image_stock_preflight import eligible
  candidates=[{'key':'old'}]
  with patch('blog_image_stock_preflight.enabled',return_value=False):self.assertIs(eligible(candidates,'roya',ROOT),candidates)
