"""Text failures must never consume image quota; publisher remains strict."""
import copy,inspect,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_draft_preflight as draft
import blog_image_stock as stock
import blog_generated_image as generated
import blog_image_gate as gate
import blog_reference_scene as scene
class DraftPreflightTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  env=patch.dict(os.environ,{'GITHUB_ACTIONS':'false'});env.start();self.addCleanup(env.stop)
  (self.root/'data').mkdir();(self.root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3,'text_preflight_required':True}))
  self.item={'key':'draft','family':'tape20','kind':'city','_image_article_context':{'title':'نوار تیپ گوجه‌فرنگی؛ بازدید اتصال‌ها','summary':'قیمت روز نوار تیپ و راهنمای خرید از کارخانه'}}
 def enqueue(self):
  with self.assertRaises(stock.ImagePending):stock.request_image(self.item,'loxblog',self.root)
  p=self.root/'data/loxblog/backlink-queue.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'items':[self.item]}))
 def test_missing_saved_draft_defers_without_provider(self):
  self.enqueue()
  with patch.object(generated,'prepare_now')as api:
   result=stock.worker_once(self.root)
  api.assert_not_called();row=stock.rows(self.root)[0]
  self.assertEqual(row['last_error'],'saved_draft_unavailable');self.assertEqual(row['attempts'],0)
 def test_invalid_text_frees_capacity_without_image_api(self):
  self.enqueue()
  with patch.object(draft,'check_saved',return_value=['Invalid links','Title/body mismatch']),patch.object(generated,'prepare_now')as api:
   stock.worker_once(self.root)
  api.assert_not_called();row=stock.rows(self.root)[0]
  self.assertEqual(row['status'],'needs_text_repair');self.assertEqual(row['attempts'],0)
  self.assertFalse(stock.awaiting(self.item,self.root));self.assertNotIn(row['status'],stock.ACTIVE)
 def test_changed_authoritative_text_cannot_use_old_request(self):
  request={'blog':'loxblog','item':self.item};p=self.root/'artifacts/loxblog-backlink-queue/items/draft.json';p.parent.mkdir(parents=True)
  p.write_text(json.dumps({'post':{'title':'موضوع دیگر','slug':'valid','html':'<p>متن جدید</p>'}}))
  self.assertIn('Saved draft changed',draft.check_saved(request,self.item,self.root)[0])
 def test_normalized_crop_and_introduction_mismatch(self):
  (self.root/'data/blog-city-title-matrix.json').write_text(json.dumps({'row_crops':['گوجه فرنگی']}))
  post={'title':self.item['_image_article_context']['title'],'html':'<p>قیمت روز نوار تیپ و خرید از کارخانه</p>'}
  errors=draft.subject_errors(self.item,post,self.root)
  self.assertEqual(len(errors),2)
 def test_topic_and_crop_present_are_not_rejected(self):
  (self.root/'data/blog-city-title-matrix.json').write_text(json.dumps({'row_crops':['گوجه فرنگی']}))
  post={'title':self.item['_image_article_context']['title'],'html':'<p>بازدید اتصال نوار تیپ در کشت گوجه فرنگی و بررسی نشتی</p>'}
  self.assertEqual(draft.subject_errors(self.item,post,self.root),[])
 def test_clean_does_not_mutate_saved_article(self):
  post={'html':'<p><img src="old"></p><p>متن</p>','image_url':'old'};before=copy.deepcopy(post)
  self.assertEqual(draft.clean(post)['html'],'<p>متن</p>');self.assertEqual(post,before)
 def test_default_publication_qa_stays_strict(self):
  import city_backlink_policy as city,roya_backlink_queue as roya
  self.assertTrue(inspect.signature(city.qa).parameters['require_image'].default)
  self.assertTrue(inspect.signature(roya.qa).parameters['require_image'].default)
 def test_bad_preflight_config_fails_closed(self):
  cfg=json.loads((self.root/stock.CONFIG).read_text());cfg['text_preflight_required']='true';(self.root/stock.CONFIG).write_text(json.dumps(cfg))
  with self.assertRaises(RuntimeError):stock.control(self.root)
 def test_both_producers_validate_before_preparing_image(self):
  import farsiblog_backlink_queue as f,roya_backlink_queue as r
  for module,image_call in ((f,'retry_transient(lambda:prepare_image(item))'),(r,'image_url = prepare_roya_image(item)')):
   source=inspect.getsource(module.main);self.assertLess(source.index("stage='text_validation'"),source.index(image_call))
 def test_detail_views_are_bounded_same_candidate(self):
  buf=io.BytesIO();Image.new('RGB',(1200,900),'brown').save(buf,'PNG')
  details=list(gate.candidate_details(buf.getvalue()));self.assertEqual(len(details),2)
  for label,data in details:
   self.assertIn('same full-frame image',label);image=Image.open(io.BytesIO(data));self.assertLessEqual(max(image.size),1024)
 def test_prompt_forbids_pipe_support_and_white_ribbon(self):
  prompt=scene.prompt(self.item,'loxblog')
  self.assertIn('visible strip of bare soil',prompt);self.assertIn('No white ribbon',prompt)
if __name__=='__main__':unittest.main()
