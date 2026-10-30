import io,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_package_labels as p
class ExactCaptionTests(unittest.TestCase):
 def good(self):return {'english_text':'Drip Irrigation Tape','persian_text':'آبگسترفراپاریان','english_legible':True,'persian_legible':True}
 def test_literal_owner_names(self):self.assertEqual(p.exact_errors(self.good()),[])
 def test_normal_spacing_is_not_a_spelling_error(self):
  v=self.good();v['persian_text']='آب گستر فراپاریان';self.assertEqual(p.exact_errors(v),[])
 def test_guessed_malformed_or_unreadable_is_rejected(self):
  for field,value in [('english_text','Drip Irrigaton Tape'),('persian_text','آبگسترفراباریان'),('persian_text',''),('persian_legible',False),('english_legible',1)]:
   v=self.good();v[field]=value
   with self.subTest(field=field,value=value):self.assertTrue(p.exact_errors(v))
 def test_reader_prompt_does_not_disclose_answers(self):
  im=io.BytesIO();Image.new('RGB',(800,600),'white').save(im,'PNG')
  response={'choices':[{'message':{'content':'{}'}}]}
  with patch.object(p.roya.BASE._key_pool,'next',return_value='fixture'),patch.object(p.roya.BASE,'fetch_json',return_value=response)as fetch:p.inspect(im.getvalue())
  prompt=fetch.call_args.args[2]['messages'][0]['content'][0]['text']
  self.assertNotIn(p.ENGLISH,prompt);self.assertNotIn(p.PERSIAN,prompt);self.assertIn('without translating, guessing',prompt)
 def test_uncertain_geometry_does_not_paint(self):
  with self.assertRaises(RuntimeError):p.safe_geometry({'package_count':1,'geometry_confidence':.8},(1200,900))
 def test_persian_requires_joined_shaping(self):
  with patch.object(p.features,'check',return_value=False):
   with self.assertRaisesRegex(RuntimeError,'shaping'):p.typeset(b'',{})
 def test_projective_map_is_identity_for_rectangle(self):
  c=p.inverse_coefficients([(0,0),(200,0),(200,30),(0,30)],200,30)
  for actual,wanted in zip(c,(1,0,0,0,1,0,0,0)):self.assertAlmostEqual(actual,wanted)
if __name__=='__main__':unittest.main()
