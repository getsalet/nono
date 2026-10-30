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
class AutomaticRealSceneTests(unittest.TestCase):
 ROOT=Path(__file__).resolve().parents[1]
 def test_four_real_scene_geometries_without_article_coordinates(self):
  paths=['41029742464/case-2-candidate-v2.webp','41031355848/case-2-finish-edit.webp','41030647254/case-1-finish-edit.webp','41037090356/case-3-native.webp']
  for path in paths:
   with self.subTest(path=path):
    raw=(self.ROOT/'artifacts/blog-image-calibration'/path).read_bytes();g=p.detect_geometry(raw)
    image,proof=p.typeset(raw,g);original=Image.open(io.BytesIO(raw)).convert('RGB')
    self.assertEqual(proof['captions']['english']['text'],p.ENGLISH);self.assertEqual(proof['captions']['persian']['text'],p.PERSIAN)
    self.assertEqual(image.crop((800,800,1200,900)).tobytes(),original.crop((800,800,1200,900)).tobytes())
    for box_ in g['afp_glyph_bboxes']+[g['symbol_bbox']]:
     x0,y0,x1,y1=[round(v*(image.width if i%2==0 else image.height)/1000)for i,v in enumerate(box_)]
     for y in range(y0,y1):
      for x in range(x0,x1):
       rgb=original.getpixel((x,y))
       if rgb[2]>rgb[0]*1.3 and rgb[2]>70 and rgb[0]<140:self.assertEqual(rgb,image.getpixel((x,y)))
 def test_ambiguous_or_absent_brand_is_not_guessed(self):
  raw=io.BytesIO();Image.new('RGB',(1200,900),'white').save(raw,'PNG')
  with self.assertRaisesRegex(RuntimeError,'recognized'):p.detect_geometry(raw.getvalue())

class CaptionFoundationTests(unittest.TestCase):
 def test_opt_in_is_tape_only_and_boolean(self):
  import tempfile,json
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();cfg=root/'data/blog-image-acceptance-policy.json'
   self.assertFalse(p.enabled(root,'tape20'))
   cfg.write_text(json.dumps({'require_exact_package_labels':True}));self.assertTrue(p.enabled(root,'tape20'));self.assertFalse(p.enabled(root,'hose'))
   cfg.write_text(json.dumps({'require_exact_package_labels':1}))
   with self.assertRaises(RuntimeError):p.enabled(root,'tape20')
 def test_hash_bound_readback_never_accepts_score_alone(self):
  r={'exact_labels_required':True,'sha256':'a'*64,'verdict':{'score':99}}
  self.assertTrue(p.record_errors(r))
  r['package_label_review']={'policy':p.POLICY,'sha256':'a'*64,'reading':ExactCaptionTests().good()};self.assertEqual(p.record_errors(r),[])
  r['sha256']='b'*64;self.assertTrue(p.record_errors(r))
 def test_cache_render_once_and_bind_bytes(self):
  import tempfile
  raw=(AutomaticRealSceneTests.ROOT/'artifacts/blog-image-calibration/41029742464/case-2-candidate-v2.webp').read_bytes()
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'candidate.webp';path.write_bytes(raw)
   with patch.object(p,'typeset',wraps=p.typeset)as render:
    first,proof=p.prepare_cached(path);second,_=p.prepare_cached(path)
   self.assertEqual(first,second);self.assertEqual(render.call_count,1)
   self.assertEqual(proof['sha256'],__import__('hashlib').sha256(second).hexdigest())
 def test_layout_failure_is_bounded_quality_rejection(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'candidate.webp';path.write_bytes(b'fixture')
   with patch.object(p,'detect_geometry',side_effect=RuntimeError('Caption anchors not uniquely recognized')):
    with self.assertRaisesRegex(RuntimeError,'^Product image rejected:'):p.prepare_cached(path)
   self.assertEqual(path.read_bytes(),b'fixture')
 def test_runtime_failure_preserves_candidate_without_regeneration(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'candidate.webp';path.write_bytes(b'fixture')
   with patch.object(p,'detect_geometry',side_effect=RuntimeError('Verified caption font unavailable')):
    with self.assertRaisesRegex(RuntimeError,'^Verified caption font'):p.prepare_cached(path)
   self.assertEqual(path.read_bytes(),b'fixture')
