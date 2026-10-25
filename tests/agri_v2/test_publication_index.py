import tempfile,unittest
from pathlib import Path
from automation.agri_v2.publication_index import verified_publications
from automation.agri_v2.queue import atomic_json
class PublicationIndexTests(unittest.TestCase):
 def put(self,out,topic,post,date,**kw):
  folder=out/'new'/topic
  atomic_json(folder/'article.json',{'title':'عنوان '+topic})
  row={'post_id':post,'url':'https://navar-abyari.ir/post-'+str(post)+'/','status':'published','public_verified':True,'public_http_status':200,'published_at':date,'verified_at':date};row.update(kw);atomic_json(folder/'wordpress-receipt.json',row)
 def test_newest_verified_receipt_first_not_file_order(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);self.put(out,'b',1,'2026-10-25T03:00:00Z');self.put(out,'a',2,'2026-10-25T05:00:00+03:00');rows=verified_publications(out);self.assertEqual([r['post_id'] for r in rows],[1,2])
 def test_draft_failed_and_unverified_never_displayed(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)
   for i,kw in enumerate([{'public_verified':False},{'status':'draft'},{'public_http_status':404},{'url':'https://evil.example/a'},{'verified_at':'bad'}]):self.put(out,str(i),i+1,'2026-10-25T03:00:00Z',**kw)
   self.assertEqual(verified_publications(out),[])
 def test_later_failed_run_does_not_erase_last_publication(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);self.put(out,'good',1,'2026-10-25T03:00:00Z');atomic_json(out/'latest-cycle-error.json',{'status':'failed'});self.assertEqual(verified_publications(out)[0]['post_id'],1)
