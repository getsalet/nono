import copy,unittest
from automation.agri_v2.revise import restore_owned_post
from automation.agri_v2.wordpress import WPError
class RestoreTests(unittest.TestCase):
 def setUp(self):
  self.post={'id':5,'author':2,'status':'trash','content':{'raw':'<!-- marker -->'}}
  self.req={'post_id':5,'restore_same_post_authorized':True}
  class Fake:
   user_id=2
   def __init__(self):self.calls=[];self.conflicts=[]
   def call(self,path,method='GET',data=None):
    self.calls.append((path,method,data))
    if method=='GET':return self.conflicts,{}
    return {'id':5,'author':2,'status':'draft','content':{'raw':'<!-- marker -->'}},{}
  self.wp=Fake()
 def test_authorized_restore_is_same_post_draft_not_publish(self):
  p=restore_owned_post(self.wp,self.post,self.req,'<!-- marker -->','canonical-slug');self.assertEqual(p['status'],'draft');self.assertEqual(self.wp.calls[-1],('posts/5','POST',{'status':'draft','slug':'canonical-slug'}))
 def test_no_permission_no_write(self):
  with self.assertRaises(WPError):restore_owned_post(self.wp,self.post,{'post_id':5},'<!-- marker -->','canonical-slug')
  self.assertEqual(self.wp.calls,[])
 def test_ownership_marker_and_post_id_required(self):
  for k,v in [('author',99),('id',6),('content',{'raw':'other'})]:
   p=copy.deepcopy(self.post);p[k]=v
   with self.assertRaises(WPError):restore_owned_post(self.wp,p,self.req,'<!-- marker -->','canonical-slug')
  self.assertEqual(self.wp.calls,[])
 def test_slug_conflict_blocks_restore(self):
  self.wp.conflicts=[{'id':99}]
  with self.assertRaises(WPError):restore_owned_post(self.wp,self.post,self.req,'<!-- marker -->','canonical-slug')
  self.assertEqual(len(self.wp.calls),1)
 def test_published_post_is_not_restored(self):
  self.post['status']='publish';p=restore_owned_post(self.wp,self.post,self.req,'<!-- marker -->','canonical-slug');self.assertEqual(p['status'],'publish');self.assertEqual(self.wp.calls,[])
if __name__=='__main__':unittest.main()
