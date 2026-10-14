import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BlogCommentsDisabledTests(unittest.TestCase):
 def test_roya_and_farsi_have_no_comments_output(self):
  for blog in ('royablog','farsiblog'):
   text=(ROOT/'templates'/blog/'afp-main.html').read_text()
   for token in ('<fb:post_comments>','<fb:last_comments>','[#post_comment_form#]','[#post_comment_link#]'):
    self.assertNotIn(token,text)
 def test_roz_has_no_comments_output(self):
  text=(ROOT/'templates/rozblog/afp-main.html').read_text()
  for token in ('<RB:Comment_Block>','<RB:Post_Comment_Block>','[Comment_Form]','[Post_Comment_Url]'):
   self.assertNotIn(token,text)
 def test_shared_roya_farsi_publisher_disables_comments(self):
  text=(ROOT/'automation/publish_roya_posts.py').read_text()
  self.assertIn('comments.checked=false;',text)
  self.assertIn("Comment control missing",text)
 def test_roz_publisher_disables_comments(self):
  text=(ROOT/'automation/publish_rozblog_posts.py').read_text()
  self.assertIn("page.locator('select[name=pcm]').select_option('2')",text)
