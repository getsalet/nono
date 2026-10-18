"""User-authorized practical >=90 acceptance, with real evidence and no new image API."""
import copy,hashlib,io,json,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_gate as gate
import blog_generated_image as generated
import blog_image_stock as stock
import blog_image_watermark as watermark
import blog_reference_scene as scene
import roya_backlink_queue as roya
class PracticalScore90Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.env=patch.dict('os.environ',{'GITHUB_ACTIONS':'false'});self.env.start();self.addCleanup(self.env.stop)
  (self.root/'data').mkdir()
  self.cfg={'mode':gate.PRACTICAL_MODE,'minimum_score':90,'reconsider_candidates':{}}
  self.write_config()
  self.item={'key':'real-owner','family':'tape20','_image_article_context':{'title':'نوار تیپ سیب زمینی؛ نگهداری','summary':'این مقاله درباره بررسی نوار تیپ در مزرعه سیب زمینی و رطوبت خاک کنار ریشه ها و پایش دوره ای نصب است.'}}
  b=io.BytesIO();watermark.apply(Image.new('RGB',(1200,900),'brown')).save(b,'WEBP');self.raw=b.getvalue();self.digest=hashlib.sha256(self.raw).hexdigest()
  self.v={'pass':False,'score':95,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_count_match':True,'technical_evidence_match':True,'packaging_not_used_as_hardware':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False,'product_role_plausible':False,'irrigation_geometry_plausible':True,'package_soil_gap_visible':False,'product_fully_in_frame':True}
 def write_config(self):(self.root/gate.ACCEPTANCE_CONFIG).write_text(json.dumps(self.cfg))
 def record(self):
  return {'policy':gate.POLICY,'review_model':roya.BASE.AGNES_MODEL,'sha256':self.digest,'family':'tape20','scene_guard_version':gate.SCENE_GUARD,'topic_sha256':scene.topic_hash(self.item),'article_owner':'rozblog|'+self.item['key'],'width':1200,'height':900,'verdict':copy.deepcopy(self.v),'focused_physical_review':{'clear_soil_gap':False,'line_touches_or_crosses_package':False,'extra_loose_product_coil':False,'package_has_protruding_strip':True}}
 def save_record(self,record=None):
  p=self.root/'artifacts/blog-image-reviews'/('tape20-'+self.digest+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(record or self.record()));return p
 def practical_record(self,verdict=None):return {**self.record(),'acceptance_mode':gate.PRACTICAL_MODE,'verdict':verdict or self.v}
 def test_90_and_95_accept_with_minor_physical_warnings(self):
  for score in (90,95,100):
   v={**self.v,'score':score};self.assertEqual(gate.generated_scene_errors(self.practical_record(v),'tape20'),[])
 def test_under_90_or_nonfinite_or_out_of_range_scores_reject(self):
  for score in (89.99,70,None,True,'NaN','Infinity',101):
   self.assertTrue(gate.generated_scene_errors(self.practical_record({**self.v,'score':score}),'tape20'))
 def test_core_defects_still_reject_even_score_99(self):
  for k,value in [('observed_family','hose'),('expected_product_visible',False),('wrong_product_present',True),('fake_text_or_logo',True),('implausible_geometry',True),('people_present',True),('topic_match',False),('product_integrated',False),('product_count_match',False),('technical_evidence_match',False),('packaging_not_used_as_hardware',False),('collage_or_split_layout',True),('crop_contradiction',True),('observed_product_count',2)]:
   with self.subTest(field=k):self.assertTrue(gate.generated_scene_errors(self.practical_record({**self.v,'score':99,k:value}),'tape20'))
 def test_missing_core_boolean_is_not_implicitly_approved(self):
  for k in ('topic_match','expected_product_visible','people_present','technical_evidence_match'):
   v={**self.v};v.pop(k);self.assertTrue(gate.generated_scene_errors(self.practical_record(v),'tape20'))
 def test_existing_actual_review_reconsidered_without_inventing_score_or_api(self):
  p=self.save_record();before=json.loads(p.read_text())
  with patch.object(roya.BASE,'fetch_json',side_effect=AssertionError('No model calls for valid saved evidence')):
   result=gate.review(self.item,'generated://rozblog/'+'a'*32,self.root,_candidate=self.raw)
  self.assertEqual(result['verdict'],before['verdict']);self.assertEqual(result['verdict']['score'],95)
  self.assertEqual(result['acceptance_mode'],gate.PRACTICAL_MODE);self.assertTrue(result['acceptance_warnings'])
  self.assertEqual(gate.validate_record(self.item),[])
 def test_direct_severe_veto_still_blocks_score95(self):
  self.save_record();(self.root/'data/blog-generated-image-visual-review.json').write_text(json.dumps({'rejected_sha256':[self.digest]}))
  with self.assertRaisesRegex(RuntimeError,'direct visual inspection rejected'):gate.review(self.item,'generated://rozblog/'+'a'*32,self.root,_candidate=self.raw)
 def test_mismatched_owner_cannot_reuse_high_score(self):
  record=self.record();record['article_owner']='roya|someone-else';self.save_record(record)
  with self.assertRaisesRegex(RuntimeError,'another blog/article'):gate.review(self.item,'generated://rozblog/'+'a'*32,self.root,_candidate=self.raw)
 def test_missing_watermark_still_rejects_score95(self):
  self.save_record();b=io.BytesIO();Image.new('RGB',(1200,900),'brown').save(b,'WEBP')
  with self.assertRaisesRegex(RuntimeError,'watermark'):gate.review(self.item,'generated://rozblog/'+'a'*32,self.root,_candidate=b.getvalue())
 def test_practical_new_review_uses_one_call_and_no_focused_veto(self):
  v={**self.v,'pass':True};reply={'choices':[{'message':{'content':json.dumps(v)}}]}
  with patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',return_value=reply)as api,patch.object(gate,'focused_physical_check',side_effect=AssertionError('No extra veto for minor details')):
   record=gate.review(self.item,'generated://rozblog/'+'a'*32,self.root,_candidate=self.raw)
  self.assertEqual(api.call_count,1);self.assertEqual(record['verdict']['score'],95)
  self.assertIn('ADVISORY',api.call_args.args[2]['messages'][0]['content'][0]['text'])
 def install_saved_candidate(self):
  asset=generated.identity(self.item,'rozblog');self.cfg['reconsider_candidates'][asset]={'blog':'rozblog','key':self.item['key'],'sha256':self.digest};self.write_config()
  p=self.root/'artifacts/rozblog-backlink-queue/generated-images/rejected'/f'{asset}-{self.digest[:12]}.webp';p.parent.mkdir(parents=True);p.write_bytes(self.raw);self.save_record();return asset,p
 def test_only_explicit_exact_saved_bytes_can_be_reused(self):
  asset,p=self.install_saved_candidate();self.assertEqual(generated.reconsider_candidate(self.item,'rozblog',self.root),p)
  p.write_bytes(b'changed')
  with self.assertRaisesRegex(RuntimeError,'missing or changed'):generated.reconsider_candidate(self.item,'rozblog',self.root)
 def test_authorized_saved_recheck_prioritized_and_bypasses_only_image_cooldown(self):
  asset,p=self.install_saved_candidate();(self.root/stock.CONFIG).write_text(json.dumps({'enabled':True,'target':12,'per_blog_limit':3}))
  row={'policy':stock.POLICY,'asset_id':asset,'blog':'rozblog','key':self.item['key'],'status':'requested','created_at':time.time(),'attempts':2,'visual_rejections':2,'retry_at':time.time()+1800,'item':copy.deepcopy(self.item)};stock.persist(self.root,row)
  source=self.root/'data/rozblog/backlink-queue.json';source.parent.mkdir(parents=True);source.write_text(json.dumps({'items':[self.item]}))
  url='https://raw.githubusercontent.com/getsalet/nono/'+'a'*40+'/assets/blog-generated/rozblog/'+asset+'.webp'
  with patch.object(generated,'rollout_enabled',return_value=True),patch('blog_image_runtime_control.generation_paused',return_value=False),patch('blog_image_backpressure.require_open',side_effect=AssertionError('No image provider needed')),patch.object(generated,'existing_asset',return_value=None),patch.object(generated,'checkpoint_asset',return_value=url),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(generated,'generate',side_effect=AssertionError('No new image API')),patch.object(roya.BASE,'fetch_json',side_effect=AssertionError('Use original actual review')):
   result=stock.worker_once(self.root)
  self.assertEqual(result['status'],'ready');saved=stock.rows(self.root)[0];self.assertEqual(saved['visual_rejections'],2);self.assertEqual(saved['attempts'],3)
 def test_invalid_policy_fails_closed(self):
  self.cfg['minimum_score']=70;self.write_config()
  with self.assertRaises(RuntimeError):gate.acceptance_mode(self.root)
if __name__=='__main__':unittest.main()
