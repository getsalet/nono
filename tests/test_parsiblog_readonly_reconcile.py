"""Regression: receipt recovery must not become a new publication path."""
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import parsiblog_pipeline as pipeline
import parsiblog_native as native
KEY='pb-14653c02e6d410ca88e8'
class ReadOnlyReconciliationTests(unittest.TestCase):
 def run_case(self, *, published=True, changed=False, native_id='8027971', approved=True, public_failure=False):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);data=root/'data/parsiblog';art=root/'artifacts/parsiblog-backlink-queue';state=root/'state/parsiblog-progress.json'
   data.mkdir(parents=True);(art/'items').mkdir(parents=True);state.parent.mkdir()
   (root/'data/blog-generated-image-control.json').write_text(json.dumps({'pause_image_production':False}))
   (data/'control.json').write_text(json.dumps({'enabled':True,'max_verified_posts_per_rolling_hour':2}))
   (data/'title-matrix.json').write_text(json.dumps({'approved':True,'count':1000,'items':[{'key':KEY,'assigned_title':'بررسی مسیر','target_url':'https://navar-abyari.ir/a','family':'tape20'}]}))
   body='<p><img src="https://navar-abyari.ir/a.webp"></p><h2>بررسی</h2><p>برگه بازدید： ردیف ۱۲</p>'+''.join('<a href="https://navar-abyari.ir/'+x+'">راهنما</a>'for x in ['a','b','c'])
   item={'key':KEY,'target_url':'https://navar-abyari.ir/a','image_url':'https://navar-abyari.ir/a.webp','post':{'title':'بررسی مسیر','html':body},'qa':{'passed':approved}}
   (art/'items'/(KEY+'.json')).write_text(json.dumps(item))
   saved={'status':'submitting_publish','id':native_id,'native_phase':'acknowledged','at':'2026-10-25T11:42:27Z'}
   state.write_text(json.dumps({'items':{KEY:saved},'published':[]}))
   actual={'id':'8027971','title':'بررسی مسیر','html':body.replace('：',':').replace('۱۲','12'),'published':published}
   if changed:actual['html']+='<p>متن تغییر کرده</p>'
   pw=MagicMock();context=pw.__enter__.return_value.chromium.connect_over_cdp.return_value.contexts[0]
   with patch.object(pipeline,'ROOT',root),patch.object(pipeline,'DATA',data),patch.object(pipeline,'ART',art),patch.object(pipeline,'STATE',state),patch.dict(os.environ,{'AGENT_BROWSER_CDP':'test'}),patch('blog_generated_image.family_enabled',return_value=True),patch('playwright.sync_api.sync_playwright',return_value=pw),patch.object(native,'login'),patch.object(native,'read_post',return_value=actual),patch.object(native,'save_post') as write,patch.object(native,'verify_public',side_effect=RuntimeError('Public mismatch')if public_failure else None,return_value='http://afp.parsiblog.com/Posts/36/') as verify,patch.object(pipeline,'generate') as generate,patch.object(pipeline,'qa',return_value=([],{'passed':True})):
    if published and not changed and native_id and approved and not public_failure:
     self.assertEqual(pipeline.main(['--mode','reconcile','--target',KEY]),0)
     result=json.loads(state.read_text());self.assertEqual(result['items'][KEY]['status'],'published');self.assertEqual(len(result['published']),1)
     receipt=json.loads((art/'latest-receipt.json').read_text());self.assertFalse(receipt['publication_attempted']);verify.assert_called_once()
    else:
     with self.assertRaises((native.NativeError,RuntimeError)):pipeline.main(['--mode','reconcile','--target',KEY])
     result=json.loads(state.read_text());self.assertEqual(result['published'],[]);self.assertEqual(result['items'][KEY]['status'],'submitting_publish')
    write.assert_not_called();generate.assert_not_called();self.assertFalse(pipeline.RUN['native_write_attempted'])
 def test_existing_public_colon_and_digit_glyphs_recover_without_write(self):self.run_case()
 def test_private_draft_never_published(self):self.run_case(published=False)
 def test_changed_words_block_recovery(self):self.run_case(changed=True)
 def test_missing_recorded_id_never_creates_post(self):self.run_case(native_id=None)
 def test_unapproved_body_never_generated_or_submitted(self):self.run_case(approved=False)
 def test_failed_public_verification_retains_uncertainty(self):self.run_case(public_failure=True)
 def test_missing_target_rejected_before_browser(self):
  with tempfile.TemporaryDirectory()as tmp,patch.object(pipeline,'ART',Path(tmp)),patch.object(pipeline,'load',side_effect=[{}, {'max_verified_posts_per_rolling_hour':2},{'pause_image_production':False}]),patch.object(native,'login')as login:
   with self.assertRaisesRegex(RuntimeError,'one explicit target'):pipeline.main(['--mode','reconcile'])
   login.assert_not_called()
if __name__=='__main__':unittest.main()
