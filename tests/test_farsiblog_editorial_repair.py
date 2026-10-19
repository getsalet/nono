import copy,json,re,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import farsiblog_editorial_repair as repair
import test_blog_editorial_image_policy as fixtures
class EditorialRepairTests(unittest.TestCase):
 write=fixtures.EditorialImagePolicyTests.write
 qa=fixtures.EditorialImagePolicyTests.qa
 def setUp(self):
  fixtures.EditorialImagePolicyTests.setUp(self)
  # Move the already-approved second link into a self-contained FAQ sentence.
  second='<a href="'+self.links[1]['url']+'">'+self.links[1]['anchor']+'</a>'
  self.post['html']=self.post['html'].replace('<p>'+second+'</p>','')
  faq='<p>مشخصات مدل را بررسی کنید.</p>'
  rest='برای انتخاب تجهیزات، شرایط زمین و مشخصات مدل را با دقت بررسی کنید. نیاز هر مزرعه با شرایط واقعی آن تعیین می‌شود.'
  self.post['html']=self.post['html'].replace(faq,'<p>'+rest+' برای بررسی اطلاعات می‌توانید به '+second+' مراجعه کنید.</p>',1)
  self.record={**self.item,'status':'failed','failure_stage':'text_validation','post':self.post,'qa':{'passed':False,'errors':['No promotional links in FAQs']}}
 def test_relocates_same_sentence_preserves_two_links_and_full_qa(self):
  self.assertEqual(self.qa(),['No promotional links in FAQs'])
  corrected=repair.relocate(self.post,self.links);self.assertIsNotNone(corrected);self.assertEqual(self.qa(post=corrected),[])
  self.assertEqual(re.findall(r'<a\b[^>]*>.*?</a>',self.post['html']),re.findall(r'<a\b[^>]*>.*?</a>',corrected['html']))
  self.assertNotIn('<a', ''.join(re.findall(r'<details\b.*?</details>',corrected['html'],re.S)))
  self.assertLess(corrected['html'].index('برای بررسی اطلاعات'),corrected['html'].index('<details'))
  self.assertIn('<a',self.post['html'].split('<details',1)[1])
 def test_no_synthetic_new_sentences_or_claims(self):
  corrected=repair.relocate(self.post,self.links)
  def words(p):return sorted(re.sub('<[^>]*>',' ',p['html']).split())
  self.assertEqual(words(self.post),words(corrected))
 def test_unapproved_duplicate_and_foreign_links_are_not_repaired(self):
  for changed in (self.post['html'].replace(self.links[1]['url'],'https://evil.example/'),self.post['html']+'<a href="https://evil.example/">x</a>',self.post['html'].replace(self.links[1]['anchor'],'لنگر متفاوت')):
   self.assertIsNone(repair.relocate({**self.post,'html':changed},self.links))
 def test_short_remaining_answer_or_complex_markup_refused(self):
  for changed in (re.sub(r'<p>برای انتخاب تجهیزات.*?برای بررسی اطلاعات','<p>برای بررسی اطلاعات',self.post['html']),self.post['html'].replace('برای بررسی اطلاعات','<strong>برای بررسی اطلاعات</strong>')):
   self.assertIsNone(repair.relocate({**self.post,'html':changed},self.links))
 def test_recovery_requires_exact_failed_record_and_full_text_qa(self):
  self.assertIsNotNone(repair.recover_saved(self.record,self.item,self.links,'farsiblog',self.root))
  for item in ({**self.item,'published':True},{**self.item,'family':'hose'},{**self.item,'key':'different'},{**self.item,'faq_link_recovery_policy':repair.POLICY}):self.assertIsNone(repair.recover_saved(self.record,item,self.links,'farsiblog',self.root))
  for record in ({**self.record,'qa':{'errors':['unapproved Latin words']}},{**self.record,'failure_stage':'source'},{**self.record,'post':{**self.post,'slug':'NOT VALID'}}):self.assertIsNone(repair.recover_saved(record,self.item,self.links,'farsiblog',self.root))
  self.assertIsNone(repair.recover_saved(self.record,self.item,self.links,'rozblog',self.root))
 def test_valid_article_and_unknown_error_not_mutated(self):
  nofaq={**self.post,'html':self.post['html'].replace('برای بررسی اطلاعات','این اطلاعات')};original=copy.deepcopy(nofaq);self.assertIsNone(repair.relocate(nofaq,self.links));self.assertEqual(nofaq,original)

 def test_candidate_selection_is_local_but_production_recovery_requires_full_qa(self):
  with patch('blog_draft_preflight.check',side_effect=RuntimeError('missing corpus')):
   self.assertIsNotNone(repair.recover_saved(self.record,self.item,self.links,'farsiblog',self.root,validate=False))
   with self.assertRaises(RuntimeError):repair.recover_saved(self.record,self.item,self.links,'farsiblog',self.root)
 def test_main_recovers_this_saved_draft_once_without_new_text_or_image_generation(self):
  import os
  import farsiblog_backlink_queue as f
  import blog_editorial_image_policy as policy
  import blog_source_image as source
  self.cfg.update(source_image_preferred=True,source_image_review_required=False);self.write(policy.CONFIG,self.cfg)
  self.write('data/farsiblog/backlink-queue.json',{'items':[self.item]});self.write('artifacts/farsiblog-backlink-queue/items/'+self.item['key']+'.json',self.record)
  with patch.object(f,'ROOT',self.root),patch.object(f,'CITY_BLOG','farsiblog'),patch('city_backlink_policy.ROOT',self.root),patch.object(f,'ART',self.root/'artifacts/farsiblog-backlink-queue'),patch.object(f,'QUEUE',self.root/'data/farsiblog/backlink-queue.json'),patch.object(f,'STATE',self.root/'state/farsiblog-backlink-progress.json'),patch('city_backlink_policy.build_queue'),patch.object(f.BASE,'AGNES_KEY','offline-fixture'),patch.object(f,'agnes',side_effect=AssertionError('No new text API')),patch.object(f,'source_text',side_effect=AssertionError('Reuse saved draft')),patch('blog_generated_image.prepare_now',side_effect=AssertionError('No image generation')),patch('blog_generated_image.family_enabled',return_value=True),patch.object(source,'read_page',return_value='<article><img src="https://navar-abyari.ir/wp-content/uploads/actual.webp"></article>'),patch.dict(os.environ,{'FARSIBLOG_COUNT':'1','FARSIBLOG_TARGET':self.item['key'],'FARSIBLOG_DRY_RUN':'0','BLOG_READY_IMAGE_HANDOFF':'0','GITHUB_STEP_SUMMARY':''}):
   self.assertEqual(f.main(),0)
  result=json.loads((self.root/'artifacts/farsiblog-backlink-queue/items'/ (self.item['key']+'.json')).read_text())
  self.assertTrue(result['qa']['passed'],result['qa']);self.assertEqual(result['faq_link_recovery_policy'],repair.POLICY);self.assertEqual(result['status'],'completed');self.assertEqual(result['image_source']['policy'],source.TRUSTED)
