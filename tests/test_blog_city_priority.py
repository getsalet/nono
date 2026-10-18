"""Editorial priority must change ordering, never article identity or progress."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_city_priority as p
class CityPriorityTests(unittest.TestCase):
 def row(self,city,key=None,**extra):return {'key':key or city,'city_fa':city,'family':'tape20','kind':'city','status':'pending','province':'tehran',**extra}
 def test_major_then_capital_then_county_then_other_then_generic(self):
  rows=[self.row('روستاشهر'),self.row('',kind='article'),self.row('ورامین'),self.row('ساری'),self.row('اصفهان'),self.row('تهران')]
  ordered=p.ordered(rows,ROOT)
  self.assertEqual([x['city_fa']for x in ordered],['تهران','اصفهان','ساری','ورامین','روستاشهر',''])
 def test_arabic_letters_spaces_and_halfspace_do_not_lose_priority(self):
  self.assertEqual(p.normalize('بندر عباس'),p.normalize('بندرعباس'))
  self.assertEqual(p.normalize('خرم\u200cآباد'),p.normalize('خرم آباد'))
  self.assertEqual(p.normalize('اراك'),p.normalize('اراک'))
 def test_frozen_rows_and_all_record_fields_remain_identical(self):
  rows=[self.row('کوچک'),self.row('قدیمی',published=True,status='published',pid=8),self.row('تهران'),self.row('صف تصویر',_image_stock_request='old'),self.row('اصفهان'),self.row('نوشته شده',generated_at='timestamp')]
  q={'items':copy.deepcopy(rows)};p.prioritize_queue(q,ROOT)
  for i in (1,3,5):self.assertEqual(q['items'][i],rows[i])
  self.assertEqual({x['key']:x for x in q['items']},{x['key']:x for x in rows})
  self.assertEqual([q['items'][i]['city_fa']for i in (0,2,4)],['تهران','اصفهان','کوچک'])
  before=copy.deepcopy(q);p.prioritize_queue(q,ROOT);self.assertEqual(before,q)
 def test_missing_policy_preserves_legacy_order(self):
  with tempfile.TemporaryDirectory()as d:
   rows=[self.row('کوچک'),self.row('تهران')];self.assertEqual(p.ordered(rows,d),rows)
 def test_priority_does_not_change_image_identity(self):
  import blog_generated_image as g
  item=self.row('تهران',_image_article_context={'title':'نوار تیپ تهران','summary':'متن واقعی مقاله درباره انتخاب و نصب خطوط آبیاری و بررسی نیازهای مزرعه و رطوبت خاک است.'})
  before=g.identity(item,'roya');q={'items':[item]};p.prioritize_queue(q,ROOT);self.assertEqual(g.identity(item,'roya'),before)
 def test_runtime_roya_rotation_cannot_put_small_town_before_major(self):
  import roya_backlink_queue as r
  rows=[self.row('کوچک',province='zahedan'),self.row('تهران')]
  with patch.multiple(r,ONLY='',RETRY_FAILED=True,ROOT=ROOT),patch('blog_generated_image.family_enabled',return_value=True),patch('blog_image_stock.awaiting',return_value=False),patch('blog_image_stock_preflight.eligible',side_effect=lambda xs,*a:xs):
   self.assertEqual(r.pick({'items':rows},{'rotation':900},1)[0]['city_fa'],'تهران')
 def test_build_queue_keeps_existing_valid_assigned_title(self):
  import city_backlink_policy as c
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);m={'approved':True,'approval_note':'fixture','templates':{'farsiblog':{'tape20':['عنوان نخست درباره {city}','عنوان انتخابی درباره {city}']}}}
   c.write(root/'data/blog-city-title-matrix.json',m)
   item=self.row('تهران',assigned_title='عنوان انتخابی درباره تهران',site_title='نوار تیپ',source_key='old',angle='')
   c.write(root/'data/farsiblog/backlink-queue.json',{'items':[item]});c.write(root/'data/roya/backlink-queue.json',{'items':[]})
   self.assertEqual(c.build_queue('farsiblog',root)['items'][0]['assigned_title'],item['assigned_title'])
 def test_pipeline_wiring_is_after_eligibility_and_preserves_explicit_targets(self):
  s=(ROOT/'automation/farsiblog_backlink_queue.py').read_text()
  self.assertLess(s.index('candidates=eligible('),s.index('if city_priority_enabled(ROOT)'))
  self.assertIn("if target:candidates=[x for x in candidates if x['key']==target]",s)
class AtomicPriorityIntegrityTests(unittest.TestCase):
 def test_atomic_check_rejects_changed_article_fields(self):
  from apply_blog_city_priority import unchanged_records
  before={'items':[{'key':'one','city_fa':'تهران','status':'pending'}]};after=copy.deepcopy(before);after['items'][0]['status']='published'
  with self.assertRaises(RuntimeError):unchanged_records(before,after)
 def test_atomic_check_rejects_moved_published_record(self):
  from apply_blog_city_priority import unchanged_records
  before={'items':[{'key':'done','published':True},{'key':'future','status':'pending'}]};after={'items':list(reversed(before['items']))}
  with self.assertRaises(RuntimeError):unchanged_records(before,after)
 def test_migration_never_force_pushes_or_uses_provider_credentials(self):
  src=(ROOT/'automation/apply_blog_city_priority.py').read_text()
  self.assertNotIn('--force',src);self.assertNotIn('IMAGE_API_KEY',src);self.assertNotIn('urllib',src)
  self.assertIn("before=json.loads(git(['show',parent+':'+path]).stdout)",src)
if __name__=='__main__':unittest.main()
