import unittest,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from content_originality import published_snapshot
class NativeHistoryUrls(unittest.TestCase):
 def test_verified_roz_custom_permalink(self):
  url='https://afp-pipe.rozblog.com/naghmeh-ta-yin-naghat-abyari-navar-tip-dpcsd'
  class Response:
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def geturl(self):return url
   def read(self):return ('<div class="post-content"><p>'+('راهنمای بررسی مسیر آب در مزرعه '*30)+'</p></div>').encode()
  with tempfile.TemporaryDirectory()as root,patch('content_originality.urllib.request.urlopen',return_value=Response()):
   self.assertIn('راهنمای بررسی',published_snapshot(root,'rozblog',{'published_url':url,'key':'verified-24'}))
 def test_wrong_host_never_loaded(self):
  with tempfile.TemporaryDirectory()as root,patch('content_originality.urllib.request.urlopen')as get:
   with self.assertRaises(RuntimeError):published_snapshot(root,'rozblog',{'published_url':'https://other.example/post/24','key':'x'})
   get.assert_not_called()
 def test_root_is_not_article(self):
  with tempfile.TemporaryDirectory()as root:
   with self.assertRaises(RuntimeError):published_snapshot(root,'rozblog',{'published_url':'https://afp-pipe.rozblog.com/','key':'x'})
if __name__=='__main__':unittest.main()
