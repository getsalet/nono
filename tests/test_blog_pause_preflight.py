import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
import farsiblog_backlink_queue as shared
import roya_backlink_queue as roya
from blog_image_runtime_control import generation_paused
class PausePreflightTests(unittest.TestCase):
 def test_paused_five_blog_generation_stops_before_any_content_api_or_queue_write(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text(json.dumps({'pause_image_production':True,'enabled':False}))
   self.assertTrue(generation_paused(root))
   for engine in (shared,roya):
    with self.subTest(engine=engine.__name__),patch.object(engine,'ROOT',root),patch.object(engine,'agnes')as ai,patch.object(engine,'source_text',create=True)as source,patch('city_backlink_policy.build_queue')as queue:
     self.assertEqual(engine.main(),0);ai.assert_not_called();source.assert_not_called();queue.assert_not_called()
 def test_corrupt_control_fails_closed(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text('broken')
   with self.assertRaises(RuntimeError):generation_paused(root)
 def test_unpaused_or_absent_control_is_not_reported_as_paused(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);self.assertFalse(generation_paused(root));(root/'data').mkdir();(root/'data/blog-generated-image-control.json').write_text('{"pause_image_production":false}')
   self.assertFalse(generation_paused(root))
