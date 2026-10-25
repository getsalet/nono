import base64,io,unittest
from unittest.mock import patch
from PIL import Image
from automation.agri_v2.client import image_bytes,ModelClient,CapabilityError
class ImageResponseTests(unittest.TestCase):
 def test_verified_base64_bytes(self):self.assertEqual(image_bytes({'data':[{'b64_json':base64.b64encode(b'fixture').decode()}]}),b'fixture')
 def test_unsafe_urls_and_private_hosts_rejected(self):
  for url in ['http://example.org/a','https://user:pass@example.org/a','https://example.org:444/a']:
   with self.assertRaises(CapabilityError):image_bytes({'data':[{'url':url}]})
  with patch('automation.agri_v2.client.socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
   with self.assertRaises(CapabilityError):image_bytes({'data':[{'url':'https://example.org/a'}]})
 def test_image_decode_and_label_end_to_end_without_network(self):
  out=io.BytesIO();Image.new('RGB',(1312,736),'green').save(out,'PNG');obj={'data':[{'b64_json':base64.b64encode(out.getvalue()).decode()}]}
  c=object.__new__(ModelClient);c.request=lambda *a,**kw:obj
  im=Image.open(io.BytesIO(c.image('fixture')));self.assertEqual(im.size,(1200,675));self.assertEqual(im.format,'WEBP')
if __name__=='__main__':unittest.main()
