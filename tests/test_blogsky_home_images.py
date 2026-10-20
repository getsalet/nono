import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import sync_blogsky_home_images as images
class HomeImageTests(unittest.TestCase):
 def row(self):return {'url':'https://afp-pipe.blogsky.com/1405/07/28/post-3/exact-slug','image':'https://navar-abyari.ir/wp-content/uploads/exact.jpg'}
 def body(self):return '<style id="afp-page-style">.hero{color:teal}</style><div id="afp-home"><h1>unchanged</h1></div>'
 def test_only_marked_css_changes_and_patch_is_idempotent(self):
  body=self.body();css=images.cover_css([self.row()]);after=images.patch_body(body,css)
  self.assertEqual(images.without_mapping(after),body);self.assertEqual(images.patch_body(after,css),after)
  other={**self.row(),'image':'https://navar-abyari.ir/wp-content/uploads/new.jpg'};next_body=images.patch_body(after,images.cover_css([other]));self.assertNotIn('exact.jpg',next_body);self.assertEqual(images.without_mapping(next_body),body)
 def test_maps_exact_path_and_article_image_not_brand_logo(self):
  css=images.cover_css([self.row()]);self.assertIn('a[href="/1405/07/28/post-3/exact-slug"]',css);self.assertIn('background-size:cover',css);self.assertNotIn('afp-drip-tape.png',css)
 def test_reject_foreign_urls_duplicates_and_css_injection(self):
  for bad in [{**self.row(),'url':'https://evil.test/post-3/x'},{**self.row(),'image':'javascript:alert(1)'},{**self.row(),'image':'https://navar-abyari.ir.evil.test/wp-content/uploads/a.jpg'}]:
   with self.assertRaises(RuntimeError):images.cover_css([bad])
  with self.assertRaises(RuntimeError):images.cover_css([self.row(),self.row()])
  with self.assertRaises(RuntimeError):images.cover_css([])
  row={**self.row(),'image':'https://navar-abyari.ir/wp-content/uploads/a\"b.jpg'};self.assertIn('a%22b.jpg',images.cover_css([row]))
 def test_reject_ambiguous_boundaries_and_wrong_homepage(self):
  with self.assertRaises(RuntimeError):images.patch_body('<div>wrong page</div>','css')
  with self.assertRaises(RuntimeError):images.without_mapping(images.START+'x'+images.START+images.END)
 def test_only_editor_cdata_noops_are_ignored_in_preservation_check(self):
  before=self.body();after=images.patch_body(before,images.cover_css([self.row()])).replace('>.hero','>/*<![CDATA[*/\n.hero').replace('</style>','/*]]>*/</style>')
  self.assertEqual(images.preserved_body(before),images.preserved_body(after))
  self.assertNotEqual(images.preserved_body(before),images.preserved_body(after.replace('unchanged','changed')))
 def test_sync_is_hooked_after_publication_and_before_checkpoint(self):
  workflow=(ROOT/'.github/workflows/blogsky-auto.yml').read_text();self.assertLess(workflow.index('run: python automation/publish_blogsky_posts.py'),workflow.index('run: python automation/sync_blogsky_home_images.py'));self.assertLess(workflow.index('run: python automation/sync_blogsky_home_images.py'),workflow.index('run: python automation/checkpoint_blogsky_native.py'))
 def test_current_article_samples_all_receive_exact_image_css(self):
  template=(ROOT/'templates/blogsky/afp-home.html').read_text();rows=[{**self.row(),'url':f'https://afp-pipe.blogsky.com/1405/07/28/post-{n}/article-{n}'} for n in range(1,7)];css=images.cover_css(rows);self.assertEqual(css.count('background-image:'),6);self.assertEqual(images.without_mapping(images.patch_body(template,css)),images.without_mapping(template))
if __name__=='__main__':unittest.main()
