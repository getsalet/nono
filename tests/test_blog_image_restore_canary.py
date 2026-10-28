import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import blog_image_restore_canary as canary
class CanaryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.key='nilo-'+'a'*16
  self.state={'intent':None,'published':[{'key':self.key,'url':'https://afp.niloblog.com/p/42/guide'}]}
  self.item={'key':self.key,'status':'published','receipt':{'public_post_verified':True,'url':self.state['published'][0]['url']},'post':{'title':'راهنمای نوار تیپ','html':'<p>مقاله واقعی</p><img src="https://old/image.webp"><video><source src="old"></video>'}}
  self.write()
 def write(self):
  for p,v in [('data/niloblog/runtime-state.json',self.state),('artifacts/niloblog/items/'+self.key+'.json',self.item)]:
   p=self.root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
 def test_public_article_context_is_copy_only_not_article_edit(self):
  before=copy.deepcopy(self.item);item,post=canary.source(self.root)
  self.assertEqual(item['family'],'tape20');self.assertNotIn('<img',post['html']);self.assertNotIn('<video',post['html']);self.assertEqual(json.loads((self.root/'artifacts/niloblog/items'/f'{self.key}.json').read_text()),before)
 def test_uncertain_native_write_is_not_touched(self):
  self.state['intent']={'key':'pending'};self.write()
  with self.assertRaises(RuntimeError):canary.source(self.root)
 def test_unverified_article_not_used(self):
  self.item['receipt']['public_post_verified']=False;self.write()
  with self.assertRaises(RuntimeError):canary.source(self.root)
 def test_empty_inventory_not_fabricated(self):
  self.state['published']=[];self.write()
  with self.assertRaises(RuntimeError):canary.source(self.root)
 def test_missing_pair_proof_blocks_before_any_local_rollout_or_provider(self):
  p=self.root/canary.EVIDENCE;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'status':'completed','all_pairs_ready':False}))
  with patch.object(canary,'ROOT',self.root),patch('blog_image_restore.prepare')as generate,self.assertRaises(RuntimeError):canary.main()
  generate.assert_not_called()
 def test_no_native_post_writer_or_automatic_activation(self):
  import inspect
  s=inspect.getsource(canary.main)
  self.assertNotIn('submit_once(',s);self.assertNotIn('publish(',s);self.assertIn('p.write_bytes(raw)',s);self.assertIn("'production_activated':False",s)
if __name__=='__main__':unittest.main()
