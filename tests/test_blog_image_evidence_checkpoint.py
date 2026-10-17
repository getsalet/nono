"""Never persist an unchanged stale local review over newer remote evidence."""
import json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import blog_image_stock as stock
import blog_generated_image as generated
class EvidenceCheckpointTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.asset='a'*32
  self.review=self.root/'artifacts/blog-image-reviews/tape20-old.json';self.review.parent.mkdir(parents=True);self.review.write_text('{"verdict":"older local"}')
 def test_unchanged_local_review_cannot_overwrite_newer_remote(self):
  before=stock.evidence_snapshot(self.root,'roya',self.asset)
  with patch.object(stock,'hosted',return_value=True),patch.object(stock.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=b'{"verdict":"newer remote"}'))as remote,patch.object(generated,'checkpoint_asset')as commit:
   stock.checkpoint_evidence(self.root,'roya',self.asset,before)
  commit.assert_not_called();remote.assert_not_called()
 def test_new_review_is_checkpointed(self):
  before=stock.evidence_snapshot(self.root,'roya',self.asset);new=self.review.parent/'tape20-new.json';new.write_text('{"new":true}')
  with patch.object(stock,'hosted',return_value=True),patch.object(stock.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout=b'')),patch.object(generated,'checkpoint_asset')as commit:
   stock.checkpoint_evidence(self.root,'roya',self.asset,before)
  self.assertEqual(commit.call_count,1);self.assertEqual(commit.call_args.args[0],str(new.relative_to(self.root)))
 def test_actually_updated_local_review_is_checkpointed(self):
  before=stock.evidence_snapshot(self.root,'roya',self.asset);self.review.write_text('{"verdict":"new locally reviewed"}')
  with patch.object(stock,'hosted',return_value=True),patch.object(stock.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=b'old')),patch.object(generated,'checkpoint_asset')as commit:
   stock.checkpoint_evidence(self.root,'roya',self.asset,before)
  self.assertEqual(commit.call_count,1)
 def test_already_identical_remote_is_not_rewritten(self):
  before=stock.evidence_snapshot(self.root,'roya',self.asset);self.review.write_text('{"updated":true}')
  with patch.object(stock,'hosted',return_value=True),patch.object(stock.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout=self.review.read_bytes())),patch.object(generated,'checkpoint_asset')as commit:
   stock.checkpoint_evidence(self.root,'roya',self.asset,before)
  commit.assert_not_called()
 def test_missing_baseline_fails_closed_when_hosted(self):
  with patch.object(stock,'hosted',return_value=True),patch.object(generated,'checkpoint_asset')as commit:
   with self.assertRaisesRegex(RuntimeError,'baseline required'):stock.checkpoint_evidence(self.root,'roya',self.asset)
  commit.assert_not_called()
 def test_current_asset_image_saved_without_other_article_cache(self):
  before=stock.evidence_snapshot(self.root,'roya',self.asset);folder=self.root/'artifacts/roya-backlink-queue/generated-images';folder.mkdir(parents=True)
  (folder/(self.asset+'.webp')).write_bytes(b'candidate-fixture');(folder/('b'*32+'.webp')).write_bytes(b'other-article-fixture')
  with patch.object(stock,'hosted',return_value=True),patch.object(stock.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout=b'')),patch.object(generated,'checkpoint_asset')as commit:
   stock.checkpoint_evidence(self.root,'roya',self.asset,before)
  self.assertEqual(commit.call_count,1);self.assertTrue(commit.call_args.args[0].endswith(self.asset+'.webp'))
if __name__=='__main__':unittest.main()
