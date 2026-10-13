import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import roya_backlink_queue as r
import city_backlink_policy as c
class RoyaMatrixTests(unittest.TestCase):
 def item(self,key='fixture',family='tape20',city='آزمایش'):
  return {'key':key,'family':family,'city_fa':city,'province_fa':'استان آزمایش','status':'pending','site_title':'نوار تیپ در آزمایش'}
 def test_three_blogs_and_products(self):
  m=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for blog in ('royablog','farsiblog','rozblog'):
   for family in ('tape20','hose'):
    self.assertTrue(m['templates'][blog][family]);self.assertTrue(m['article_templates'][blog][family])
 def test_crop_city_and_blog_angle_present(self):
  m=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for blog in ('royablog','farsiblog','rozblog'):
   for family in ('tape20','hose'):
    title=c.matrix_title(self.item(family=family),blog)
    self.assertIn('آزمایش',title);self.assertEqual(sum(crop in title for crop in m['row_crops']),1);self.assertLessEqual(len(title),65)
  titles={c.matrix_title(self.item(),b)for b in ('royablog','farsiblog','rozblog')};self.assertEqual(len(titles),3)
 def test_distinct_titles_preserve_posts(self):
  old={**self.item('old'),'status':'published','published':True,'title':'عنوان قبلی بدون تغییر'}
  q={'items':[old,self.item('one'),self.item('two')]};before=copy.deepcopy(old)
  r.assign_roya_titles(q)
  self.assertEqual(old,before);self.assertNotEqual(q['items'][1]['assigned_title'],q['items'][2]['assigned_title'])
  before=copy.deepcopy(q);r.assign_roya_titles(q);self.assertEqual(q,before)
 def test_prompt_uses_exact_title_and_independent_angle(self):
  q={'items':[self.item()]};r.assign_roya_titles(q);p=r.build_prompt(q['items'][0],[])
  self.assertIn(q['items'][0]['assigned_title'],p);self.assertIn('برنامه‌ریزی آبیاری',p);self.assertIn('بازنویسی سطحی نکن',p)
 def test_hubs_and_hoses_have_titles(self):
  for f in ('hub','hose'):
   q={'items':[self.item(f,f)]};r.assign_roya_titles(q);self.assertLessEqual(len(q['items'][0]['assigned_title']),65)
 def test_long_city_never_truncated(self):
  q={'items':[self.item(city='نام بسیار بسیار بسیار بسیار بسیار بسیار بسیار بسیار بسیار طولانی شهر')]};r.assign_roya_titles(q)
  self.assertEqual(q['items'][0]['status'],'needs_title_review');self.assertNotIn('assigned_title',q['items'][0])
 def test_all_pending_source_titles_fit(self):
  q=json.loads((ROOT/'data/roya/backlink-queue.json').read_text());old=copy.deepcopy([x for x in q['items'] if x.get('published')or x.get('status')not in ('pending','failed','needs_title_review')]);r.assign_roya_titles(q)
  self.assertEqual(old,[x for x in q['items'] if x.get('published')or x.get('status')not in ('pending','failed','needs_title_review')])
  review=[x for x in q['items'] if x.get('status')=='needs_title_review'];self.assertEqual(review,[])
  titles=[x['assigned_title']for x in q['items'] if x.get('assigned_title')];self.assertEqual(len(titles),len(set(titles)))
if __name__=='__main__':unittest.main()
