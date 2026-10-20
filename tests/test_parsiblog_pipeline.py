import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import parsiblog_matrix as matrix
import parsiblog_policy as policy
import parsiblog_native as native
import parsiblog_pipeline as pipeline
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.inventory=matrix.build();cls.item=copy.deepcopy(next(x for x in cls.inventory['items']if not x['evidence']));cls.item['image_url']='https://navar-abyari.ir/wp-content/uploads/afp-drip-tape-roll-transparent.webp'
 def fixture(self):
  item=copy.deepcopy(self.item);links=policy.links_for(item)
  para='<p>'+('بررسی مشخصات محصول پیش از سفارش و ثبت اطلاعات زمین برای انتخاب آگاهانه ضروری است. '*43)+'</p>'
  body='<p><img src="'+item['image_url']+'" alt="نمای محصول آبیاری AFP"></p><h2>ثبت نیاز زمین</h2>'+para+'<h2>انتخاب مشخصات</h2><ul><li>ثبت نیاز واقعی زمین</li></ul><h2>جمع‌بندی</h2>'
  for x in links:body+='<p>برای بررسی دقیق‌تر <a href="'+x['url']+'">'+x['anchor']+'</a> را بخوانید.</p>'
  body+='<h2>پرسش‌های متداول</h2>'+''.join('<h3>چه اطلاعاتی لازم است؟</h3><p>نیاز زمین و مشخصات همان مدل باید بررسی شود.</p>'for _ in range(3))
  post={'title':item['assigned_title'],'slug':'parsiblog-city-choice','meta_description':'راهنمای انتخاب تجهیزات آبیاری و بررسی مشخصات محصول با توجه به اطلاعات واقعی زمین، پرسش‌های فنی و نکات ضروری پیش از ثبت سفارش.','tags':['آبیاری','راهنمای انتخاب'],'html':body};return item,post
 def test_inventory(self):
  rows=self.inventory['items'];self.assertEqual(len(rows),1000);self.assertEqual(len({x['assigned_title']for x in rows}),1000);self.assertTrue(all(12<=len(x['assigned_title'])<=65 for x in rows));self.assertEqual(self.inventory['crop_title_count'],8)
  self.assertTrue(all(not policy.title_errors(x,x['assigned_title'],matrix.ROOT)for x in rows))
 def test_three_links_and_native_faq(self):
  x,p=self.fixture();e,r=policy.qa(x,p,originality=False);self.assertEqual(e,[]);self.assertEqual(r['link_count'],3)
 def test_fourth_link_rejected(self):
  x,p=self.fixture();p['html']+='<p><a href="https://navar-abyari.ir/shop/">فروشگاه</a></p>';self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_links_in_faq_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace('<h3>چه اطلاعاتی لازم است؟','<a href="https://navar-abyari.ir/">پیوند</a><h3>چه اطلاعاتی لازم است؟',1);self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_stripped_faq_format_rejected(self):
  x,p=self.fixture();p['html']=p['html'].replace('<h3>چه اطلاعاتی لازم است؟</h3>','<details><summary>پرسش</summary></details>',1);self.assertTrue(policy.qa(x,p,originality=False)[0])
 def test_readback_changed_text_rejected(self):
  x,p=self.fixture();self.assertEqual(native.persisted_errors(x,p,p),[]);q=copy.deepcopy(p);q['html']=q['html'].replace('اطلاعات واقعی زمین','متن عوض شده');q['html']+='<p>بخش تازه</p>';self.assertTrue(native.persisted_errors(x,p,q))
 def test_readback_normalizes_letters(self):
  x,p=self.fixture();q=copy.deepcopy(p);q['html']=q['html'].replace('ی','ي').replace('ک','ك');q['title']=q['title'].replace('ی','ي');self.assertEqual(native.persisted_errors(x,p,q),[])
 def test_budget(self):
  self.assertEqual(pipeline.budget({'published':[]}),1);self.assertEqual(pipeline.budget({'published':[{'at':pipeline.stamp()}]}),0)
 def test_account_guard(self):
  class P:
   url='http://www.parsiblog.com/Notes.aspx'
   def wait_for_selector(self,*a,**k):pass
   def evaluate(self,*a,**k):return 'someoneelse'
  with self.assertRaises(native.NativeError):native.guard(P())
 def test_native_readback_parse(self):
  class P:
   def evaluate(self,*a):return 'native-edit-payload'
  with patch.object(native,'guard'),patch.object(native,'native_request',return_value='OK$#PBFalse$#PBعنوان$#PB<p>متن</p>$#PB12$#PBFalse$#PBTrue$#PBSub=آبیاری'):
   actual=native.read_post(P(),'12');self.assertEqual(actual['id'],'12');self.assertFalse(actual['published']);self.assertEqual(actual['title'],'عنوان')
if __name__=='__main__':unittest.main()
