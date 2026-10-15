import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_reference_scene import prompt,scene_plan
class TopicSceneContractTests(unittest.TestCase):
 def item(self,title,family='tape20'):
  return {'key':'actual-topic-fixture','family':family,'site_title':'لوله نخی'if family=='hose'else'نوار تیپ','_image_article_context':{'title':title,'summary':'این متن واقعی مقاله درباره آبیاری و تجهیزات است. کارشناس باید فشار و فیلتر را هم بررسی کند و در بازدید دوره‌ای نشانه‌های مشکل را ثبت کند.'}}
 def test_positive_whitelist_does_not_prime_human_subject(self):
  text=prompt(self.item('نوار تیپ بامیه؛ مراقبت حین بهره‌برداری'),'loxblog')
  self.assertIn('okra',text);self.assertIn('in-service monitoring',text)
  for word in ('farmer','worker','people','hands','body parts','engineer'):
   self.assertNotIn(word,text.lower())
  self.assertIn('vacant and motionless',text);self.assertLess(len(text),3200)
 def test_title_crop_and_connection_topic_win_over_generic_body(self):
  plan=scene_plan(self.item('لوله نخی ذرت؛ پایش اتصال‌ها','hose'),'roya')
  self.assertEqual(plan['crop'],'maize');self.assertEqual(plan['topic'],'connection inspection')
 def test_spacing_and_pressure_have_distinct_physical_evidence(self):
  a=scene_plan(self.item('نوار تیپ پیاز؛ فاصله خطوط'),'roya');b=scene_plan(self.item('نوار تیپ پیاز؛ کنترل فشار'),'roya')
  self.assertNotEqual(a['evidence'],b['evidence']);self.assertIn('gauge',b['evidence'])
 def test_rejection_text_cannot_seed_wrong_crop_or_person(self):
  item=self.item('نوار تیپ بامیه؛ مراقبت');a=prompt(item,'roya');item['_image_qa_feedback']='wrong sunflower with farmer'
  self.assertEqual(a,prompt(item,'roya'))

class PreferredImagePoolTests(unittest.TestCase):
 def test_preferred_audited_image_slots_are_not_rotated_into_unrelated_slots(self):
  import base64,io
  from PIL import Image
  from unittest.mock import patch
  import blog_generated_image as g
  item=TopicSceneContractTests().item('نوار تیپ پیاز؛ فاصله خطوط')
  buf=io.BytesIO();Image.new('RGB',(1024,768),'green').save(buf,'PNG');reply={'data':[{'b64_json':base64.b64encode(buf.getvalue()).decode()}]}
  pool=g.roya.BASE._key_pool
  with patch.dict('os.environ',{'AGNES_IMAGE_PREFERRED_KEY_SLOTS':'AGNES_API_KEY14,AGNES_API_KEY15'}),patch.object(g,'capability_slots',return_value=['AGNES_API_KEY3','AGNES_API_KEY14','AGNES_API_KEY15']),patch.object(pool,'keys',['k3','k14','k15']),patch.object(pool,'slots',{'k3':'AGNES_API_KEY3','k14':'AGNES_API_KEY14','k15':'AGNES_API_KEY15'}),patch.object(pool,'fetch_json',return_value=reply)as fetch:
   g.generate(item,'roya')
   self.assertEqual(set(fetch.call_args.kwargs['allowed_keys']),{'k14','k15'})
