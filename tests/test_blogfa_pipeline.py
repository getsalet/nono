import unittest,json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
from blog_post_excerpt import native_split
from blogfa_native import active
class BlogfaContracts(unittest.TestCase):
 def test_native_excerpt_preserves_full(self):
  body='<p><img src="x" alt="محصول"></p><p>'+('مقدمه واقعی برای مخاطب مزرعه ' * 8)+'</p><h2>راهنما</h2><p>'+('متن کامل درباره بررسی مسیر آب ' * 40)+'</p><details><summary>پرسش</summary><p>پاسخ</p></details>'
  a,b=native_split(body);self.assertEqual(a+b,body);self.assertNotIn('<details',a);self.assertNotIn('<img',b)
 def test_independent_titles(self):
  m=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for table in ('templates','article_templates'):
   for family,pool in m[table]['blogfa'].items():
    self.assertGreaterEqual(len(pool),4)
    for other in ('rozblog','farsiblog'):self.assertFalse(set(pool)&set(m[table][other][family]))
 def test_template_native_summary_and_pager(self):
  t=(ROOT/'templates/blogfa/afp-professional.html').read_text()
  for s in ('<-PostContent->','<BlogExtendedPost>','<BlogNextAndPreviousBlock>','google-site-verification','prefers-reduced-motion', 'lang="fa"'):self.assertIn(s,t)
  for s in ('<BlogComment>','line-clamp','max-height:'):self.assertNotIn(s,t)
 def test_schedule_requires_opt_in(self):
  w=(ROOT/'.github/workflows/blogfa-content.yml').read_text();self.assertIn("vars.BLOGFA_AUTOMATION_ENABLED == '1'",w);self.assertIn('cancel-in-progress: false',w);self.assertIn('always()',w)
 def test_uncertain_submit_blocks(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text();self.assertIn("('submitting','unconfirmed')",s);self.assertEqual(s.count("page.locator('#btnPublish').click()"),1);self.assertIn('assert_no_native_match(page',s)
 def test_native_login_wrong_destination(self):
  class Loc:
   def evaluate_all(self,js):return ['https://another.blogfa.com/']
  class Page:
   url='https://www.blogfa.com/Desktop/Home.aspx'
   def locator(self,s):return Loc()
  with self.assertRaises(RuntimeError):active(Page())
 def test_budget_blogfa_supported(self):
  s=(ROOT/'automation/check_blog_run_budget.py').read_text();self.assertIn("'blogfa'",s);self.assertIn('prefix=blog.upper()',s)
if __name__=='__main__':unittest.main()
