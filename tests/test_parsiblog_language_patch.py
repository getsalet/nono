import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from parsiblog_text import apply_language_patch,language_patch_prompt,post_language_errors
class LanguagePatchTests(unittest.TestCase):
 def setUp(self):
  self.post={'title':'عنوان دقیق فارسی','slug':'city-ili','meta_description':'راهنمای فارسی','tags':['آبیاری'],'html':'<p>این مورد или آن مورد را بررسی کنید.</p><a href="https://x/или">منبع</a>'}
  self.patch={'edits':[{'field':'body','old':'или','new':'یا'}]}
 def test_only_exact_visible_bad_token_changes(self):
  before=copy.deepcopy(self.post);out,audit=apply_language_patch(self.post,self.patch)
  self.assertEqual(self.post,before);self.assertEqual(out['html'],'<p>این مورد یا آن مورد را بررسی کنید.</p><a href="https://x/или">منبع</a>');self.assertEqual(out['title'],before['title']);self.assertEqual(out['slug'],before['slug']);self.assertEqual(audit['edits'][0]['count'],1);self.assertNotEqual(audit['before_sha256'],audit['after_sha256']);self.assertFalse(post_language_errors(out))
 def test_valid_persian_words_cannot_be_edited(self):
  bad={'edits':[{'field':'body','old':'بررسی','new':'تأیید'}]}
  with self.assertRaises(ValueError):apply_language_patch(self.post,bad)
 def test_urls_are_not_patch_targets(self):
  bad={'edits':[{'field':'href','old':'https://x/или','new':'منبع'}]}
  with self.assertRaises(ValueError):apply_language_patch(self.post,bad)
 def test_no_markup_foreign_digits_or_long_rewrite(self):
  for value in ('или','گهro','<p>یا</p>','یا\nو','۲۰ بار','یا '*5,'','یا&و'):
   patch=copy.deepcopy(self.patch);patch['edits'][0]['new']=value
   with self.subTest(value=value),self.assertRaises(ValueError):apply_language_patch(self.post,patch)
 def test_unknown_duplicate_empty_and_extra_keys_rejected(self):
  for patch in ({'edits':[]},{'edits':self.patch['edits']*2},{'edits':self.patch['edits'],'html':'new'},{'edits':[{'field':'body','old':'нет','new':'نه'}]}):
   with self.subTest(patch=patch),self.assertRaises(ValueError):apply_language_patch(self.post,patch)
 def test_partial_patch_does_not_hide_remaining_language_error(self):
  self.post['html']+='<p>متن для باقی است.</p>';out,_=apply_language_patch(self.post,self.patch);self.assertTrue(post_language_errors(out))
 def test_comments_and_other_nonvisible_nodes_not_edited(self):
  self.post['html']+='<!-- или --><script>или</script><style>или</style>'
  out,audit=apply_language_patch(self.post,self.patch)
  self.assertIn('<!-- или -->',out['html']);self.assertIn('<script>или</script>',out['html']);self.assertIn('<style>или</style>',out['html']);self.assertEqual(audit['edits'][0]['count'],1)
 def test_brand_name_is_not_a_persian_language_replacement(self):
  bad=copy.deepcopy(self.patch);bad['edits'][0]['new']='برای AFP'
  with self.assertRaises(ValueError):apply_language_patch(self.post,bad)
 def test_prompt_requests_patch_not_article_rewrite(self):
  prompt=language_patch_prompt(self.post);self.assertIn('field',prompt);self.assertIn('حداکثر چهار',prompt);self.assertIn('نه بازنویسی',prompt)
 def test_patch_budget_inside_existing_loop_before_qa_and_review(self):
  import inspect,parsiblog_pipeline as p
  code=inspect.getsource(p.generate);self.assertIn('for attempt in range(3)',code);self.assertLess(code.index('apply_language_patch(obj,edits)'),code.index('errors,report=qa('));self.assertLess(code.index('apply_language_patch(obj,edits)'),code.index('review=agnes('));self.assertIn("errors==['Unexpected foreign-language text in Persian article']",code)
if __name__=='__main__':unittest.main()
