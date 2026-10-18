"""A successful native submission must not lose its receipt to unstaged QA files."""
import inspect,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import publish_roya_posts as p
class RoyaPublicationReceiptTests(unittest.TestCase):
 def test_workflow_keeps_qa_changes_and_recovery_artifact_before_push(self):
  s=(ROOT/'.github/workflows/roya-backlink-publish.yml').read_text()
  self.assertIn("IMAGE_REVIEW_MODEL: ${{ vars.AGNES_MODEL || 'agnes-3.0-flash' }}",s)
  self.assertLess(s.index('name: Preserve native publication receipts'),s.index('name: Commit per-post publication checkpoints'))
  self.assertIn('artifacts/blog-image-reviews artifacts/content-originality',s)
  self.assertIn('for attempt in 1 2 3',s);self.assertIn('Unexpected unstaged changes',s)
  self.assertNotIn('git push --force',s);self.assertNotIn('git add -A',s)
 def test_existing_native_title_is_checked_before_any_form_submission(self):
  s=inspect.getsource(p.publish)
  self.assertLess(s.index('existing=scan_panel(page)'),s.index('if not pid:'))
  self.assertLess(s.index('if not pid:'),s.index('page.goto(ADD_URL'))
  self.assertIn('recovered=bool(pid)',s);self.assertIn("'recovered_existing':recovered",s)
 def test_reconciled_existing_receipt_preserves_uncertainty_about_creation_time(self):
  for recovered in (True,False):
   with tempfile.TemporaryDirectory()as d:
    root=Path(d);art=root/'artifacts';entry={'key':'owner','item_file':'items/owner.json'}
    files={'QUEUE':root/'queue.json','ART':art,'STATE':root/'state.json','PUBLISH_QUEUE':art/'publish-queue.json','LOG':art/'publish-log.jsonl'}
    for name,obj in [('QUEUE',{'items':[{'key':'owner'}]}),('PUBLISH_QUEUE',{'items':[entry]})]:
     files[name].parent.mkdir(parents=True,exist_ok=True);files[name].write_text(json.dumps(obj))
    with patch.multiple(p,**files):
     p.checkpoint(entry,{'key':'owner'},{'key':'owner','pid':215,'url':'https://afp.royablog.ir/post/215/topic/','at':'2026-10-18T04:45:00Z','recovered_existing':recovered})
    state=json.loads(files['STATE'].read_text());self.assertIs(state['published'][0]['recovered_existing'],recovered)
    self.assertEqual(json.loads(files['PUBLISH_QUEUE'].read_text())['count'],0)
if __name__=='__main__':unittest.main()
