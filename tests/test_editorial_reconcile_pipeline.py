import json,hashlib,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from reconcile_farsiblog_editorials import reconcile,save,load
class EditorialReconcileTests(unittest.TestCase):
 def fixture(self,root):
  fix={'key':'article-fixture','pid':12,'previous_title':'عنوان قبلی','title':'عنوان اصلاح‌شده','html':'<p>متن اصلاح‌شده</p>','live_verified':True}
  fix['body_sha256']=hashlib.sha256(fix['html'].encode()).hexdigest()
  save(root/'data/farsiblog/editorial-fixes-20261014.json',{'revision':'test','updates':[fix]})
  published={'key':fix['key'],'pid':12,'published':True,'title':fix['previous_title'],'published_at':'original','published_url':'https://example/old-link'}
  save(root/'data/farsiblog/backlink-queue.json',{'items':[published,{'key':'pending','status':'pending'}]})
  save(root/'state/farsiblog-backlink-progress.json',{'published':[dict(published)]})
  save(root/'artifacts/farsiblog-backlink-queue/items/article-fixture.json',{**published,'post':{'title':fix['previous_title'],'html':'old'}})
 def test_existing_only_idempotent_and_publication_time_preserved(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);self.fixture(root);self.assertEqual(reconcile(root),1);self.assertEqual(reconcile(root),0)
   q=load(root/'data/farsiblog/backlink-queue.json',{})
   self.assertEqual(q['items'][1],{'key':'pending','status':'pending'});self.assertEqual(q['items'][0]['published_at'],'original');self.assertEqual(q['items'][0]['published_url'],'https://example/old-link')
 def test_newer_edits_are_not_overwritten(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);self.fixture(root);p=root/'data/farsiblog/backlink-queue.json';q=load(p,{});q['items'][0]['title']='ویرایش جدید کاربر';save(p,q)
   with self.assertRaises(RuntimeError):reconcile(root)
if __name__=='__main__':unittest.main()
