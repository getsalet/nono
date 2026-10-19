import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blogsky_native as native
import publish_blogsky_posts as publisher
class NativeTests(unittest.TestCase):
 def fixture(self):
  post={'title':'عنوان آزمون','html':'<p>بدنه واقعی برای آزمون</p>'};links=[{'url':'https://navar-abyari.ir/','anchor':'نوار آبیاری'},{'url':'https://navar-abyari.ir/a/','anchor':'نوار تیپ شهر'}]
  result={'url':'https://afp-pipe.blogsky.com/1405/07/28/post-1/test-slug','title':post['title'],'html':post['html'],'details':3,'summaries':3,'links':links,'images':[{'src':'https://navar-abyari.ir/a.jpg','alt':'محصول'}],'layout':True,'footer':True,'mobileCall':True};return post,links,result
 def test_actual_observed_native_url_and_host(self):
  for url in ['https://afp-pipe.blogsky.com/1405/07/28/post-1/test','https://afp-pipe.blogsky.com/post/1/test/']:self.assertTrue(native.public_url(url))
  for url in ['https://evil.example/1405/07/28/post-1/test','https://afp-pipe.blogsky.com.evil.test/1405/07/28/post-1/test','https://afp-pipe.blogsky.com/','https://afp-pipe.blogsky.com/1405/07/28/post-1/test?preview=1','http://afp-pipe.blogsky.com/1405/07/28/post-1/test']:self.assertFalse(native.public_url(url))
 def test_full_public_acceptance(self):
  p,l,r=self.fixture();self.assertTrue(native.verify(r,p,l,'https://navar-abyari.ir/a.jpg'))
 def test_missing_content_links_faq_or_layout_never_verified(self):
  p,l,r=self.fixture()
  for key,val in [('title','wrong'),('html','<p>ناقص</p>'),('details',2),('summaries',2),('links',[]),('images',[]),('footer',False),('mobileCall',False),('layout',False)]:
   bad=copy.deepcopy(r);bad[key]=val
   with self.subTest(key=key),self.assertRaises(RuntimeError):native.verify(bad,p,l,'https://navar-abyari.ir/a.jpg')
 def test_uncertain_journal_blocks_every_target(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);path=root/'artifacts/blogsky-backlink-queue/native-publications/x.json';path.parent.mkdir(parents=True);path.write_text(json.dumps({'phase':'submitting'}))
   with self.assertRaises(RuntimeError):publisher.pending(root)
   path.write_text(json.dumps({'phase':'verified'}));publisher.pending(root)
 def test_published_target_is_idempotent_without_browser_or_export(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);p=root/'data/blogsky/backlink-queue.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'items':[{'key':'city-0123456789abcdef','published':True}]}))
   with patch('export_blogsky_posts.export',side_effect=AssertionError('Must not export')):self.assertIsNone(publisher.prepare('city-0123456789abcdef',root))
 def test_explicit_exact_key_required(self):
  for bad in ['', '../x','city-xyz']:
   with self.assertRaises(RuntimeError):publisher.prepare(bad)
 def test_invalid_native_mode_cannot_login(self):
  with patch.object(publisher,'gate'),patch.dict('os.environ',{'BLOGSKY_NATIVE_MODE':'bulk'}),patch.object(native,'login',side_effect=AssertionError('No login')):
   with self.assertRaises(RuntimeError):publisher.run(None,None)
 def test_stop_gate_precedes_browser(self):
  with tempfile.TemporaryDirectory() as temp:
   with self.assertRaises(RuntimeError):publisher.gate(Path(temp))
 def test_actual_date_route_is_accepted_for_originality_cache(self):
  from content_originality import published_snapshot
  import hashlib
  p,l,r=self.fixture();url=r['url']
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);p=root/'artifacts/content-originality/blogsky'/(hashlib.sha256(url.encode()).hexdigest()+'.json');p.parent.mkdir(parents=True);p.write_text(json.dumps({'url':url,'html':'<p>'+('متن '+ 'معتبر ')*110+'</p>'}))
   self.assertTrue(published_snapshot(root,'blogsky',{'published_url':url,'key':'x'}))
if __name__=='__main__':unittest.main()
