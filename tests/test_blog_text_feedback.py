import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_text_feedback import language_feedback,rejected_text_seed
import farsiblog_backlink_queue as f
class TextFeedbackTests(unittest.TestCase):
 def test_visible_mixed_tokens_and_foreign_words_reported(self):
  post={'title':'راهنمای بهرهبردارi','meta_description':'فرایند проверь','tags':['آبیarی'],'html':'<p>انتخaب و unknown</p>'}
  tokens={x['invalid_visible_token']for x in language_feedback(post)}
  self.assertTrue({'بهرهبردارi','проверь','آبیarی','انتخaب','unknown'}<=tokens)
 def test_approved_units_urls_slugs_and_attributes_not_flagged(self):
  post={'title':'نوار AFP','slug':'latin-slug','html':'<p>PE UV ISO cm mm <a href="https://example.test/english">پیوند</a></p><img src="https://x/image.webp" alt="محصول AFP">'}
  self.assertEqual(language_feedback(post),[])
 def test_allowed_mark_inside_mixed_word_is_not_hidden(self):
  self.assertTrue(language_feedback({'html':'<p>نوارAFP</p>'}))
 def test_image_alt_is_visible_feedback_and_post_is_unchanged(self):
  post={'html':'<img src="https://x/ok" alt="انتخaب">'};before=copy.deepcopy(post)
  self.assertEqual(language_feedback(post)[0]['field'],'image_alt');self.assertEqual(post,before)
 def test_feedback_is_bounded(self):
  out=language_feedback({'html':'<p>'+' '.join('foreign'+str(i)for i in range(30))+'</p>'});self.assertEqual(len(out),8)
 def test_rejected_seed_preserves_reason_and_is_a_copy(self):
  old={'key':'k','status':'failed','failure_stage':'text_validation','post':{'title':'عنوان','html':'<p>متن ردشده</p>'},'qa':{'passed':False,'errors':['unapproved Latin words']}}
  post,errors=rejected_text_seed(old,{'key':'k'});post['html']='changed';self.assertEqual(old['post']['html'],'<p>متن ردشده</p>');self.assertEqual(errors,['unapproved Latin words'])
 def test_published_wrong_identity_and_other_failure_stages_not_seeded(self):
  old={'key':'k','status':'failed','failure_stage':'text_validation','post':{'title':'عنوان','html':'<p>متن</p>'}}
  for change in [{'published':True},{'key':'other'},{'status':'completed'},{'failure_stage':'image'},{'post':None}]:
   with self.subTest(change=change):self.assertIsNone(rejected_text_seed({**old,**change},{'key':'k'}))
 def test_repair_prompt_contains_specific_tokens_without_mutation(self):
  item={'kind':'legacy','topic':'آبیاری','angle':'بررسی','family':'tape','reference_url':'https://navar-abyari.ir/'}
  post={'html':'<p>انتخaب محصول</p>','slug':'valid-slug'};before=copy.deepcopy(post)
  text=f.repair_request(item,[],'منبع',post,['unapproved Latin words']);self.assertIn('invalid_visible_token',text);self.assertIn('انتخaب',text);self.assertEqual(post,before)
if __name__=='__main__':unittest.main()
