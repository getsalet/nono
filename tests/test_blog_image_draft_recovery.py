import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_image_draft_recovery import recover
class ImageDraftRecoveryTests(unittest.TestCase):
 def record(self):return {'status':'failed','failure_stage':'image','post':{'title':'عنوان','slug':'valid-draft','html':'<p><img src="old"></p><p>متن</p>','image_url':'old'}}
 def test_only_image_failures_recover_and_no_original_mutation(self):
  row=self.record();before=copy.deepcopy(row);post=recover(row)
  self.assertEqual(row,before);self.assertNotIn('<img',post['html']);self.assertNotIn('image_url',post)
 def test_failed_text_and_published_drafts_not_reused(self):
  for field,value in [('failure_stage','validation'),('failure_stage','source'),('status','published'),('status','completed')]:
   row=self.record();row[field]=value;self.assertIsNone(recover(row))
 def test_missing_or_malformed_draft_not_recovered(self):
  for value in [None,[],{}, {'title':'a','slug':'b','html':None}]:
   row=self.record();row['post']=value;self.assertIsNone(recover(row))
 def test_final_pipeline_quality_gates_still_present(self):
  import inspect,farsiblog_backlink_queue as f,roya_backlink_queue as r
  for module in [f,r]:
   source=inspect.getsource(module.main)
   self.assertIn('qa(item,',source);self.assertIn("stage='validation'",source)
  self.assertIn('prepare_image(item)',inspect.getsource(f.main));self.assertIn('prepare_roya_image(item)',inspect.getsource(r.main))
