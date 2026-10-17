"""Offline regression: retry saved transient failures only, never republish."""
import datetime,json,sys,tempfile,unittest,copy,re
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import roya_backlink_queue as r
from blog_image_draft_recovery import capacity_retry_due
class RoyaCapacityRecoveryTests(unittest.TestCase):
 def row(self):return {'key':'city/test','province':'test','family':'tape20','status':'failed','failure_stage':'image','last_error':'agnes error: Image provider queue full; generation deferred until 2026-10-16T22:01:12Z'}
 def saved(self,row):return {**row,'post':{'title':'نوار تیپ','slug':'tape-test','html':'<p>پیش نویس ذخیره شده برای بررسی</p>'}}
 def test_capacity_timer_and_malformed_timer(self):
  row=self.row();now=datetime.datetime(2026,10,16,tzinfo=datetime.timezone.utc)
  self.assertTrue(capacity_retry_due(row,now))
  for value in ['2026-10-17T00:00:00Z','bad',12,'2026-10-15T00:00:00']:
   self.assertFalse(capacity_retry_due({**row,'next_retry_at':value},now))
  self.assertTrue(capacity_retry_due({**row,'next_retry_at':'2026-10-15T00:00:00Z'},now))
 def test_mutex_deferral_uses_its_actual_exception_message(self):
  from blog_image_queue import ImageQueueBusy
  self.assertTrue(capacity_retry_due({**self.row(),'last_error':'agnes error: '+str(ImageQueueBusy())}))
 def test_content_visual_auth_and_published_never_auto_retry(self):
  for fields in [{'last_error':'Product image rejected: geometry'},{'last_error':'Agnes/provider HTTP 401; raw response withheld'},{'last_error':'unapproved Latin words'},{'failure_stage':'validation'},{'status':'published'},{'published':True}]:
   self.assertFalse(capacity_retry_due({**self.row(),**fields}))
 def test_only_saved_due_capacity_failure_is_automatically_selected(self):
  with tempfile.TemporaryDirectory()as d:
   rows=[self.row(),{**self.row(),'key':'no-draft'},{**self.row(),'key':'future','next_retry_at':'2099-01-01T00:00:00Z'},{**self.row(),'key':'visual','last_error':'Product image rejected: geometry'}]
   for row in rows:
    if row['key']!='no-draft':r.save_json(Path(d)/(re.sub(r'[^A-Za-z0-9._-]+','_',row['key'])+'.json'),self.saved(row))
   with patch.multiple(r,ROOT=Path(d),ITEMS=Path(d),RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=True):
    self.assertEqual([x['key']for x in r.pick({'items':rows},{},3)],['city/test'])
 def test_explicit_target_cannot_reselect_published_or_completed(self):
  for status in ['published','completed','processing']:
   row={**self.row(),'status':status}
   with patch.multiple(r,RETRY_FAILED=True,ONLY=row['key']),patch('blog_generated_image.family_enabled',return_value=True):
    self.assertEqual(r.pick({'items':[row]},{},1),[])
 def test_cancelled_hose_stays_filtered(self):
  row={**self.row(),'family':'hose','status':'pending'}
  with patch.multiple(r,RETRY_FAILED=False,ONLY=''),patch('blog_generated_image.family_enabled',return_value=False):self.assertEqual(r.pick({'items':[row]},{},1),[])
 def test_workflow_retains_visual_reviews_in_both_recovery_channels(self):
  s=(ROOT/'.github/workflows/roya-backlink-queue.yml').read_text()
  self.assertIn('            artifacts/blog-image-reviews',s)
  self.assertIn('if [ -d artifacts/blog-image-reviews ]; then git add -f artifacts/blog-image-reviews; fi',s)
 def test_retry_timer_saved_before_record_and_all_quality_gates_retained(self):
  import inspect
  s=inspect.getsource(r.main)
  self.assertLess(s.index("item['next_retry_at']=datetime"),s.index('record = dict(item)'))
  self.assertIn('recover(load_json',s);self.assertIn('errors, info = qa(item, obj, links)',s)
  self.assertIn('image_url = prepare_roya_image(item)',s)
