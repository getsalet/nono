import io,json,sys,unittest,urllib.error,base64
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import audit_usable_agnes_keys as a
from agnes_key_pool import AgnesKeyPool
class UsableKeysTests(unittest.TestCase):
 def test_priority_and_duplicates(self):
  p=AgnesKeyPool({'AGNES_API_KEY':'fixture-a','AGNES_API_KEY8':'fixture-a','AGNES_API_KEY6':'fixture-six','AGNES_API_KEY7':'fixture-seven','AGNES_API_KEY11':'fixture-eleven'},report_path='/absent')
  self.assertEqual([p.slots[k]for k in a.selected(p)],['AGNES_API_KEY6','AGNES_API_KEY7','AGNES_API_KEY11','AGNES_API_KEY'])
 def test_text_requires_correct_completion_not_just_200(self):
  with patch.object(a.urllib.request,'urlopen',return_value=io.BytesIO(b'{"choices":[{"message":{"content":"wrong"}}]}')):
   self.assertEqual(a.text_probe('private-fixture')['status'],'nonconforming_response')
 def test_secret_and_raw_error_not_in_report(self):
  error=urllib.error.HTTPError('https://example.test',401,'private-fixture',{},io.BytesIO(b'PRIVATE_RESPONSE'))
  with patch.object(a.urllib.request,'urlopen',side_effect=error):row=a.text_probe('private-fixture')
  self.assertNotIn('private',json.dumps(row));self.assertNotIn('PRIVATE_RESPONSE',json.dumps(row));self.assertEqual(row['http_status'],401)
 def item(self):return {'key':'fixture','family':'tape20','site_title':'نوار تیپ','_image_article_context':{'title':'نوار تیپ پیاز','summary':'بررسی فاصله خطوط نوار تیپ و نصب درست آن در ردیف پیاز برای آزمون تصویر'}}
 def config(self):return {'endpoint':'https://example.test/images/generations','model':'agnes-image-2.5-flash','size':'1024x768'}
 def test_http_200_without_image_never_healthy(self):
  with patch.object(a.urllib.request,'urlopen',return_value=io.BytesIO(b'{"data":[]}')):row=a.image_probe('private-fixture',self.item(),self.config())
  self.assertEqual(row['status'],'no_usable_image')
 def test_real_valid_bytes_not_visual_approval(self):
  b=io.BytesIO();Image.new('RGB',(1024,768),'white').save(b,'PNG')
  data={'data':[{'b64_json':base64.b64encode(b.getvalue()).decode()}]}
  with patch.object(a.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(data).encode()))as api:row=a.image_probe('private-fixture',self.item(),self.config())
  self.assertEqual(row['status'],'image_healthy');self.assertFalse(row['visual_publication_approved']);self.assertEqual(api.call_count,1)
 def test_queue_full_is_redacted_not_auth_failure(self):
  body=b'{"error":{"message":"Image queue is full PRIVATE_RESPONSE"}}'
  error=urllib.error.HTTPError('https://example.test',503,'private-fixture',{},io.BytesIO(body))
  with patch.object(a.urllib.request,'urlopen',side_effect=error)as api:row=a.image_probe('private-fixture',self.item(),self.config())
  self.assertEqual(row['provider_code'],'image_queue_full');self.assertEqual(api.call_count,1);self.assertNotIn('PRIVATE_RESPONSE',json.dumps(row))
 def test_image_comparison_is_exclusive_spaced_and_never_publishes(self):
  import inspect
  s=inspect.getsource(a.main)
  self.assertIn("provider_slot('keyaudit',token)",s);self.assertIn('60-(time.monotonic()-last_start)',s)
  self.assertIn("get('http_status')==429",s);self.assertIn('require_open(ROOT)',s)
  self.assertNotIn('publish(',s);self.assertNotIn('images.prepare',s)
if __name__=='__main__':unittest.main()
