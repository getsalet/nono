import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from parsiblog_text import render_city_token,post_language_errors
class CityRenderTests(unittest.TestCase):
 def test_matrix_spelling_rendered_in_visible_fields_only(self):
  post={'title':'عنوان دقیق گهرو','slug':'gahro-AFP_CITY','meta_description':'بررسی در AFP_CITY','tags':['AFP_CITY','آبیاری'], 'html':'<p>در AFP_CITY نیاز زمین را ثبت کنید؛ <strong>AFP_CITY</strong>.</p><a href="https://x/AFP_CITY">مطالعه</a>'}
  self.assertEqual(render_city_token({'city_fa':'گهرو'},post),4)
  self.assertEqual(post['title'],'عنوان دقیق گهرو');self.assertEqual(post['slug'],'gahro-AFP_CITY');self.assertIn('https://x/AFP_CITY',post['html']);self.assertIn('<strong>گهرو</strong>',post['html']);self.assertEqual(post_language_errors(post),[])
 def test_no_guessing_of_corrupt_word_or_unknown_placeholder(self):
  post={'html':'<p>گهro و AFP_CITY_OTHER و xAFP_CITY</p>'};before=copy.deepcopy(post)
  self.assertEqual(render_city_token({'city_fa':'گهرو'},post),0);self.assertEqual(post,before);self.assertTrue(post_language_errors(post))
 def test_no_token_is_byte_for_byte_noop(self):
  post={'html':'<p>گهرو<br/>متن فارسی</p>','title':'عنوان','slug':'gahro'};before=copy.deepcopy(post)
  self.assertEqual(render_city_token({'city_fa':'گهرو'},post),0);self.assertEqual(post,before)
 def test_idempotent_and_does_not_invent_claims(self):
  post={'html':'<p>برای AFP_CITY باید اطلاعات همان زمین بررسی شود.</p>'}
  self.assertEqual(render_city_token({'city_fa':'گهرو'},post),1);before=copy.deepcopy(post)
  self.assertEqual(render_city_token({'city_fa':'گهرو'},post),0);self.assertEqual(post,before)
 def test_invalid_locality_fails_closed(self):
  for city in ('','gahro','گهro','<script>','گهرو\nشهر'):
   with self.subTest(city=city),self.assertRaises(ValueError):render_city_token({'city_fa':city},{'html':'<p>AFP_CITY</p>'})
 def test_language_gate_still_rejects_unresolved_token(self):
  self.assertTrue(post_language_errors({'html':'<p>AFP_CITY</p>'}))
 def test_generator_renders_before_qa_and_independent_review(self):
  import inspect,parsiblog_pipeline as p
  code=inspect.getsource(p.generate);self.assertLess(code.index('render_city_token(item,obj)'),code.index('errors,report=qa('));self.assertLess(code.index('render_city_token(item,obj)'),code.index('review=agnes('))
if __name__=='__main__':unittest.main()
