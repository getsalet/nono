import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from diagnose_hose_provider import error_summary,png_refs
import blog_reference_scene as scene
class DiagnosisTests(unittest.TestCase):
 def test_errors_never_persist_raw_message_or_untrusted_values(self):
  import json
  raw=b'{"error":{"message":"private_token_xyz upstream unavailable capacity","code":"secret-code"}}'
  summary=error_summary(raw,None)
  self.assertIn('upstream_capacity',summary['categories'])
  self.assertNotIn('private_token_xyz',json.dumps(summary));self.assertNotIn('secret-code',json.dumps(summary))
 def test_lossless_encoding_preserves_reference_pixels(self):
  import base64,io
  from PIL import Image,ImageChops
  ref=scene.references({'key':'x','family':'hose'})
  for a,b in zip(ref,png_refs(ref)):
   x=Image.open(io.BytesIO(base64.b64decode(a.split(',',1)[1]))).convert('RGB')
   y=Image.open(io.BytesIO(base64.b64decode(b.split(',',1)[1]))).convert('RGB')
   self.assertIsNone(ImageChops.difference(x,y).getbbox())
