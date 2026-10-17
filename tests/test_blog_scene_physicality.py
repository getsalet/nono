"""Fail closed on package-as-hardware and stale positive AI reviews; no API calls."""
import copy,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_gate as gate
import blog_generated_image as generated
import blog_reference_scene as scene
import blog_image_watermark as watermark
import roya_backlink_queue as roya

class ScenePhysicalityTests(unittest.TestCase):
 def setUp(self):
  self.item={'key':'physicality','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'بازرسی اتصالات نوار تیپ','summary':'بازرسی اتصال واقعی نوار تیپ به لوله فرعی و آب بندی آن'}}
  self.verdict={'pass':True,'score':95,'observed_family':'tape20','expected_product_visible':True,'wrong_product_present':False,'fake_text_or_logo':False,'implausible_geometry':False,'people_present':False,'topic_match':True,'product_integrated':True,'product_fully_in_frame':True,'product_count_match':True,'technical_evidence_match':True,'observed_product_count':1,'collage_or_split_layout':False,'crop_contradiction':False,**{f:True for f in gate.SCENE_FLAGS}}
  buf=io.BytesIO();watermark.apply(Image.new('RGB',(1200,900),'brown')).save(buf,'WEBP');self.raw=buf.getvalue();self.digest=hashlib.sha256(self.raw).hexdigest()
 def test_normal_grounded_package_passes_explicit_conditions(self):
  self.assertEqual(gate.generated_scene_errors({'scene_guard_version':gate.SCENE_GUARD,'verdict':self.verdict},'tape20'),[])
 def test_every_physical_role_flag_is_required_even_high_score(self):
  for flag in gate.SCENE_FLAGS:
   for bad in (False,None,'true',1):
    with self.subTest(flag=flag,bad=bad):
     record={'scene_guard_version':gate.SCENE_GUARD,'verdict':{**self.verdict,flag:bad}}
     self.assertTrue(gate.generated_scene_errors(record,'tape20'))
 def test_old_cached_positive_review_is_reinspected(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);folder=root/'artifacts/blog-image-reviews';folder.mkdir(parents=True)
   old={'policy':gate.POLICY,'review_model':roya.BASE.AGNES_MODEL,'sha256':self.digest,'family':'tape20','topic_sha256':scene.topic_hash(self.item),'verdict':self.verdict}
   (folder/('tape20-'+self.digest+'.json')).write_text(json.dumps(old))
   reply={'choices':[{'message':{'content':json.dumps(self.verdict)}}]}
   with patch.object(generated,'family_enabled',return_value=True),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',return_value=reply)as api:
    record=gate.review(copy.deepcopy(self.item),'generated://roya/'+'a'*32,root,_candidate=self.raw)
   self.assertEqual(api.call_count,1);self.assertEqual(record['scene_guard_version'],gate.SCENE_GUARD)
   prompt=api.call_args.args[2]['messages'][0]['content'][0]['text']
   self.assertIn('carton encircling a rigid pipe',prompt)
 def test_carton_as_coupling_is_rejected_despite_positive_overall_pass(self):
  v={**self.verdict,'packaging_not_used_as_hardware':False}
  reply={'choices':[{'message':{'content':json.dumps(v)}}]}
  with tempfile.TemporaryDirectory()as d,patch.object(generated,'family_enabled',return_value=True),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',return_value=reply):
   with self.assertRaisesRegex(RuntimeError,'packaging_not_used_as_hardware'):
    gate.review(copy.deepcopy(self.item),'generated://roya/'+'a'*32,Path(d),_candidate=self.raw)
 def test_publication_rechecks_direct_rejection_despite_positive_ai_cache(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-visual-review.json').write_text(json.dumps({'rejected_sha256':[self.digest]}))
   item={**self.item,'image_generation':{'policy':generated.POLICY},'image_review':{'sha256':self.digest,'scene_guard_version':gate.SCENE_GUARD,'verdict':self.verdict}}
   with patch.object(generated,'family_enabled',return_value=True):errors=gate.generated_record_errors(item,'roya',root)
   self.assertTrue(any('Direct visual inspection rejected' in e for e in errors))
 def test_stale_scene_review_cannot_pass_structured_publication(self):
  item={**self.item,'image_generation':{'policy':generated.POLICY},'image_review':{'verdict':self.verdict}}
  with patch.object(generated,'family_enabled',return_value=True):errors=gate.generated_record_errors(item,'roya')
  self.assertIn('Current physical scene review required',errors)
 def test_nonexception_validation_failure_updates_saved_stage(self):
  import inspect,farsiblog_backlink_queue as f
  source=inspect.getsource(f.main)
  self.assertIn("if errors:\n            item['failure_stage']=stage",source)
  self.assertIn("else:failed.append(item['key'])",source)

 def test_no_named_crop_never_injects_okra_rule(self):
  item=copy.deepcopy(self.item);item['_image_article_context']={'title':'تفاوت نوار تیپ بغل دوخت و پلاکدار؛ راهنمای مستندسازی','summary':'بررسی درز کناری نوار و محل قطره چکان داخلی در نمونه های واقعی برای مستندسازی پیش از انتخاب انجام می شود.'}
  reply={'choices':[{'message':{'content':json.dumps(self.verdict)}}]}
  with tempfile.TemporaryDirectory()as d,patch.object(generated,'family_enabled',return_value=True),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',return_value=reply)as api:
   gate.review(item,'generated://roya/'+'b'*32,Path(d),_candidate=self.raw)
  instruction=api.call_args.args[2]['messages'][0]['content'][0]['text']
  self.assertIn('No crop species is assigned',instruction);self.assertNotIn('For okra require',instruction)
  self.assertIn('welded edge seam',instruction)
 def test_okra_botany_guard_remains_for_actual_okra_article(self):
  item=copy.deepcopy(self.item);item['_image_article_context']['title']='نوار تیپ بامیه؛ بازبینی اتصال'
  reply={'choices':[{'message':{'content':json.dumps(self.verdict)}}]}
  with tempfile.TemporaryDirectory()as d,patch.object(generated,'family_enabled',return_value=True),patch.object(gate,'fetch',return_value=(self.raw,(1200,900),'WEBP')),patch.object(roya.BASE,'next_agnes_key',return_value='fixture'),patch.object(roya.BASE,'fetch_json',return_value=reply)as api:
   gate.review(item,'generated://roya/'+'c'*32,Path(d),_candidate=self.raw)
  self.assertIn('For okra require',api.call_args.args[2]['messages'][0]['content'][0]['text'])

 def test_line_under_carton_is_blocked_even_with_high_aggregate_score(self):
  verdict={**self.verdict,'pass':True,'score':99,'package_soil_gap_visible':False}
  errors=gate.generated_scene_errors({'scene_guard_version':gate.SCENE_GUARD,'verdict':verdict},'tape20')
  self.assertTrue(any('package_soil_gap_visible'in e for e in errors))
 def test_new_layout_has_separate_off_axis_soil_island(self):
  prompt=scene.prompt(self.item,'roya')
  self.assertIn('LOWER-LEFT',prompt);self.assertIn('RIGHT half',prompt)
  self.assertIn('one carton diameter',prompt);self.assertIn('No line behind the carton',prompt)

if __name__=='__main__':unittest.main()
