"""Sparse admission must preserve exactly the read-only gate's dependencies."""
import json,sys,tempfile,unittest,shutil,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import check_blog_ready_image_handoff as h
class AdmissionCheckoutTests(unittest.TestCase):
 def test_only_admission_checkout_is_sparse(self):
  for b,w in [('roya','roya-backlink-queue'),('farsiblog','farsiblog-content'),('rozblog','rozblog-content'),('loxblog','loxblog-content')]:
   s=(ROOT/'.github/workflows'/f'{w}.yml').read_text();admission=s.split('  image_handoff:',1)[1].split('\n  tests:',1)[0].split('\n  queue:',1)[0]
   self.assertIn('sparse-checkout-cone-mode: false',admission)
   expected=['/automation/','/data/','/state/',f'/artifacts/{b}-backlink-queue/items/',f'/assets/blog-generated/{b}/']
   block=admission.split('sparse-checkout: |\n',1)[1].split('      - uses:',1)[0]
   self.assertEqual([x.strip()for x in block.splitlines()if x.strip()],expected)
   self.assertEqual(s.count('sparse-checkout-cone-mode: false'),3 if b=='loxblog'else 1)
   # Existing production checkpoint rebase/history and gates remain intact.
   self.assertIn('fetch-depth: 0',s);self.assertIn('git pull --rebase origin main',s)
 def test_ready_draft_survives_exact_sparse_manifest_for_every_blog(self):
  for b in ('roya','farsiblog','rozblog','loxblog'):
   with self.subTest(blog=b),tempfile.TemporaryDirectory()as td:
    full=Path(td)/'full';sparse=Path(td)/'sparse';asset='a'*32;key='city-test';raw=b'owned-image';digest=hashlib.sha256(raw).hexdigest();post={'title':'عنوان','slug':'slug','meta_description':'شرح','html':'<p>متن مقاله</p>'};ctx={'title':'عنوان','meta_description':'شرح','summary':'متن مقاله'}
    data={'data/blog-generated-image-control.json':{'pause_image_production':False},f'data/{b}/backlink-queue.json':{'items':[{'key':key,'family':'tape20','status':'failed','_image_stock_request':asset,'_image_article_context':ctx}]},'data/blog-image-stock/requests/'+asset+'.json':{'blog':b,'status':'ready','asset_id':asset,'key':key,'review_sha256':digest,'ready_at':10,'item':{'_image_article_context':ctx}},f'artifacts/{b}-backlink-queue/items/{key}.json':{'status':'failed','failure_stage':'image','post':post}}
    for p,v in data.items():q=full/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v))
    p=full/f'assets/blog-generated/{b}/{asset}.webp';p.parent.mkdir(parents=True);p.write_bytes(raw)
    q=full/'artifacts/legacy-export/private.sql';q.parent.mkdir(parents=True);q.write_text('excluded')
    for prefix in ('automation','data','state',f'artifacts/{b}-backlink-queue/items',f'assets/blog-generated/{b}'):
     if (full/prefix).exists():shutil.copytree(full/prefix,sparse/prefix,dirs_exist_ok=True)
    self.assertFalse((sparse/'artifacts/legacy-export').exists());self.assertEqual(h.select(b,full),key);self.assertEqual(h.select(b,sparse),key)
    # A missing owned asset still fails closed, even with sparse checkout.
    (sparse/f'assets/blog-generated/{b}/{asset}.webp').unlink();self.assertIsNone(h.select(b,sparse))
if __name__=='__main__':unittest.main()
