import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_reference_scene import prompt,scene_plan
class TopicSceneContractTests(unittest.TestCase):
 def item(self,title,family='tape20'):
  return {'key':'actual-topic-fixture','family':family,'site_title':'لوله نخی'if family=='hose'else'نوار تیپ','_image_article_context':{'title':title,'summary':'این متن واقعی مقاله درباره آبیاری و تجهیزات است. کارشناس باید فشار و فیلتر را هم بررسی کند و در بازدید دوره‌ای نشانه‌های مشکل را ثبت کند.'}}
 def test_concise_recipe_keeps_single_topic_and_actual_context(self):
  item=self.item('لوله نخی ذرت؛ پایش اتصال‌ها','hose');text=prompt(item,'loxblog')
  self.assertLess(len(text),2000)
  self.assertIn('compression union installed inline',text)
  self.assertIn('exactly two',text)
  self.assertIn('no people',text)
  self.assertNotIn('three sibling images',text)
  self.assertEqual(scene_plan(item,'loxblog')['intent'],'connection')
 def test_actual_summary_is_present_and_changes_the_prompt(self):
  item=self.item('نوار تیپ بامیه؛ مراقبت حین بهره‌برداری');a=prompt(item,'roya')
  self.assertIn(item['_image_article_context']['summary'],a)
  item['_image_article_context']['summary']='موضوع این مقاله بررسی یکنواختی رطوبت در ناحیه ریشه و فاصله خطوط کشت است و به شرایط دیگری نمی‌پردازد.'
  self.assertNotEqual(a,prompt(item,'roya'))
 def test_reference_scale_and_no_unconditional_hose_coupling(self):
  item=self.item('لوله نخی ذرت؛ عملکرد آبیاری','hose');text=prompt(item,'roya')
  self.assertIn('12 to 15 percent',text)
  self.assertNotIn('The installed coupling is a distinct fixed detail',text)
 def test_reference_qa_correction_is_not_discarded(self):
  item=self.item('نوار تیپ پیاز؛ انتخاب');a=prompt(item,'roya');item['_image_qa_feedback']='Place the complete product farther inside the frame.'
  self.assertNotEqual(a,prompt(item,'roya'));self.assertIn(item['_image_qa_feedback'],prompt(item,'roya'))

class PreferredImagePoolTests(unittest.TestCase):
 def test_preferred_audited_image_slots_are_not_rotated_into_unrelated_slots(self):
  import base64,io
  from PIL import Image
  from unittest.mock import patch
  import blog_generated_image as g
  item=TopicSceneContractTests().item('نوار تیپ پیاز؛ فاصله خطوط')
  buf=io.BytesIO();Image.new('RGB',(1024,768),'green').save(buf,'PNG');reply={'data':[{'b64_json':base64.b64encode(buf.getvalue()).decode()}]}
  pool=g.roya.BASE._key_pool
  with patch.dict('os.environ',{'IMAGE_API_KEY':'','AGNES_IMAGE_PREFERRED_KEY_SLOTS':'AGNES_API_KEY14,AGNES_API_KEY15'}),patch.object(g,'capability_slots',return_value=['AGNES_API_KEY3','AGNES_API_KEY14','AGNES_API_KEY15']),patch.object(pool,'keys',['k3','k14','k15']),patch.object(pool,'slots',{'k3':'AGNES_API_KEY3','k14':'AGNES_API_KEY14','k15':'AGNES_API_KEY15'}),patch.object(pool,'fetch_json',return_value=reply)as fetch:
   g.generate(item,'roya')
   self.assertEqual(set(fetch.call_args.kwargs['allowed_keys']),{'k14','k15'})

class SafeProviderDiagnosticsTests(unittest.TestCase):
 def test_only_known_nonsecret_error_codes_are_exposed(self):
  import json
  from agnes_key_pool import AgnesProviderError
  error=AgnesProviderError(503,json.dumps({'error':{'code':'service_unavailable','type':'server_error','message':'private response body'}}).encode())
  self.assertEqual(error.provider_code,'service_unavailable');self.assertEqual(error.provider_type,'server_error')
  self.assertNotIn('private',str(error));self.assertIn('503',str(error))
 def test_unknown_codes_and_messages_never_escape(self):
  from agnes_key_pool import AgnesProviderError
  error=AgnesProviderError(503,b'{"error":{"code":"secret-shaped-value","type":"untrusted-type","message":"private"}}')
  self.assertIsNone(error.provider_code);self.assertIsNone(error.provider_type)
