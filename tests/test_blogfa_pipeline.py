import unittest,json,sys,subprocess,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
from blog_post_excerpt import native_split
from blogfa_native import active
class BlogfaContracts(unittest.TestCase):
 def test_native_excerpt_preserves_full(self):
  body='<p><img src="x" alt="محصول"></p><p>'+('مقدمه واقعی برای مخاطب مزرعه ' * 8)+'</p><h2>راهنما</h2><p>'+('متن کامل درباره بررسی مسیر آب ' * 40)+'</p><details><summary>پرسش</summary><p>پاسخ</p></details>'
  a,b=native_split(body);self.assertEqual(a+b,body);self.assertNotIn('<details',a);self.assertNotIn('<img',b)
 def test_blogfa_extended_replaces_summary(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text();self.assertIn("full=post['html']",s)
 def test_independent_titles(self):
  m=json.loads((ROOT/'data/blog-city-title-matrix.json').read_text())
  for table in ('templates','article_templates'):
   for family,pool in m[table]['blogfa'].items():
    self.assertGreaterEqual(len(pool),4)
    for other in ('rozblog','farsiblog'):self.assertFalse(set(pool)&set(m[table][other][family]))
 def test_template_native_summary_and_pager(self):
  t=(ROOT/'templates/blogfa/afp-professional.html').read_text()
  for s in ('<-PostContent->','<BlogExtendedPost>','<BlogNextAndPreviousBlock>','google-site-verification','prefers-reduced-motion', 'lang="fa"'):self.assertIn(s,t)
  for s in ('<BlogComment>','line-clamp'):self.assertNotIn(s,t)
  # Image sizing is allowed; article text itself must never be clipped.
  self.assertNotRegex(t,r'(?:\.post-content|\.post-card)\s*\{[^}]*max-height:')
 def test_retirement_removes_schedule_and_blocks_jobs(self):
  w=(ROOT/'.github/workflows/blogfa-content.yml').read_text();self.assertNotIn('schedule:',w);self.assertNotIn('  push:',w);self.assertEqual(w.count('if: ${{ false }}'),2);self.assertIn('always()',w)
 def test_readonly_diagnosis_uses_bounded_inputs_not_cross_blog_images(self):
  w=(ROOT/'.github/workflows/blogfa-content.yml').read_text()
  d=w.split('- name: Checkout read-only Blogfa diagnostic inputs',1)[1].split('- uses: actions/checkout@v4',1)[0]
  self.assertIn("env.BLOGFA_LOGIN_DIAGNOSTIC == '1'",d)
  self.assertIn('fetch-depth: 1',d);self.assertIn('sparse-checkout-cone-mode: false',d)
  for path in ('/automation/','/data/','/state/blogfa-backlink-progress.json','/artifacts/blogfa-backlink-queue/'):self.assertIn(path,d)
  self.assertNotIn('/artifacts/\n',d)
  self.assertIn("if: env.BLOGFA_LOGIN_DIAGNOSTIC != '1'\n        with: {fetch-depth: 0, ref: main}",w)
 def test_uncertain_submit_blocks(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text();self.assertIn("('submitting','unconfirmed')",s);self.assertEqual(s.count("page.locator('#btnPublish').click()"),1);self.assertIn('assert_no_native_match(page',s)
 def test_serialization_js_preserves_regex_boundary(self):
  tree=ast.parse((ROOT/'automation/publish_blogfa_posts.py').read_text())
  scripts=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)and 'faqs:'in n.value]
  self.assertEqual(len(scripts),1);self.assertNotIn(chr(8),scripts[0]);self.assertIn(r'/<details\b/g',scripts[0])
 def test_native_settings_tabs_open_before_controls(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text()
  self.assertLess(s.index("page.locator('#tab3').click()"),s.index("page.locator('#cmbCommentType').select_option"))
  self.assertLess(s.index("page.locator('#tab4').click()"),s.index("page.locator('#chkSticky').uncheck"))
  self.assertIn('e.filter.disable()',s);self.assertNotIn('e.filter=new CKEDITOR.filter',s)
 def test_new_route_does_not_include_edit_links(self):
  class Loc:
   def evaluate_all(self,js):return ['http://afp-pipe.blogfa.com/','https://www.blogfa.com/Desktop/Post.aspx?action=new&r=one','https://www.blogfa.com/Desktop/Post.aspx?action=edit&id=1','https://www.blogfa.com/Desktop/Archive.aspx','https://www.blogfa.com/Desktop/Options.aspx']
  class Page:
   url='https://www.blogfa.com/Desktop/Home.aspx'
   def locator(self,s):return Loc()
  self.assertIn('action=new',active(Page())['new'])
 def test_fresh_native_create_route_after_archive(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text();self.assertIn("fresh=active(page)",s);self.assertIn("page.goto(fresh['new']",s)
 def test_native_login_wrong_destination(self):
  class Loc:
   def evaluate_all(self,js):return ['https://another.blogfa.com/']
  class Page:
   url='https://www.blogfa.com/Desktop/Home.aspx'
   def locator(self,s):return Loc()
  with self.assertRaises(RuntimeError):active(Page())
 def test_budget_blogfa_supported(self):
  s=(ROOT/'automation/check_blog_run_budget.py').read_text();self.assertIn("'blogfa'",s);self.assertIn('prefix=blog.upper()',s)
 def test_native_bootstrap_uses_canonical_return_route(self):
  s=(ROOT/'automation/blogfa_native.py').read_text();self.assertIn("page.goto(PANEL+'/Desktop/Home.aspx',wait_until='load'",s)
 def test_editor_waits_for_initial_server_session_refresh(self):
  s=(ROOT/'automation/blogfa_native.py').read_text();self.assertIn('httpreq.readyState===4&&httpreq.status===200',s)
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text();self.assertLess(s.index('wait_editor_ready(page)'),s.index("page.locator('#txtPostTitle').fill"))
 def test_authenticated_native_page_never_visits_public_blog(self):
  s=(ROOT/'automation/publish_blogfa_posts.py').read_text()
  self.assertIn("public=browser.new_page()",s)
  self.assertNotIn('scan_public(page)',s[s.index('def main():'):])
  self.assertIn('verify(public,item,record)',s)
 def test_native_browser_engine_is_real_not_impersonated(self):
  from unittest.mock import patch,Mock
  from blogfa_native import launch_browser
  pw=Mock()
  with patch.dict('os.environ',{'BLOGFA_BROWSER':'firefox'}):launch_browser(pw)
  pw.firefox.launch.assert_called_once_with();pw.chromium.launch.assert_not_called()
  with patch.dict('os.environ',{'BLOGFA_BROWSER':'unsupported'}):
   with self.assertRaises(RuntimeError):launch_browser(pw)
 def test_blogfa_uses_explicit_real_browser_install_and_engine(self):
  w=(ROOT/'.github/workflows/blogfa-content.yml').read_text();self.assertIn('BLOGFA_BROWSER: chromium',w);self.assertIn('install_blog_browser.sh "$BLOGFA_BROWSER"',w)
class DuplicateDashboardRoutes(unittest.TestCase):
 def test_unique_sidebar_beats_shortcut_with_different_nonce(self):
  links=[('❯نوشته جدید','https://www.blogfa.com/Desktop/Post.aspx?action=new&r=sidebar'),('نوشته جدید','https://www.blogfa.com/Desktop/Post.aspx?action=new&r=shortcut'),('❯نوشته‌های پیشین','https://www.blogfa.com/Desktop/Archive.aspx?t=sidebar'),('نوشته های پیشین','https://www.blogfa.com/Desktop/Archive.aspx?t=shortcut'),('❯تنظیمات و دیگر امکانات','https://www.blogfa.com/Desktop/Options.aspx'),('مشاهده وبلاگ','https://afp-pipe.blogfa.com/')]
  class Loc:
   def __init__(self,rows):self.rows=rows
   def evaluate_all(self,js):return [u for _,u in self.rows]
   def count(self):return len(self.rows)
   def get_attribute(self,k):return self.rows[0][1]
  class Page:
   url='https://www.blogfa.com/Desktop/Home.aspx'
   def locator(self,s):return Loc(links)
   def get_by_role(self,role,name):return Loc([(l,u)for l,u in links if name.search(l)])
  result=active(Page());self.assertTrue(result['new'].endswith('r=sidebar'));self.assertTrue(result['archive'].endswith('t=sidebar'))
if __name__=='__main__':unittest.main()
