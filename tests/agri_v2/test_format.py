import unittest
from automation.agri_v2.pipeline import normalize_article,SafeHTML
class FormatTests(unittest.TestCase):
 def normalize(self,body):return normalize_article({'content_html':body},{'sources':[{'url':'https://example.edu/source'}]})['content_html']
 def test_inert_wrappers_and_headings(self):
  body=self.normalize('<section class="article"><h1>Title</h1><div><p class="x">Text <b>bold</b></p><a href="https://example.edu/source" target="_blank">Source</a></div></section>')
  self.assertIn('<h2>Title</h2>',body);self.assertIn('<strong>bold</strong>',body);self.assertNotIn('class=',body)
  p=SafeHTML({'https://example.edu/source'});p.feed(body);self.assertTrue(p.cited)
 def test_active_html_rejected(self):
  for body in ['<script>x</script>','<img src="x">','<p onclick="x">bad</p>','<iframe>x</iframe>','<!DOCTYPE html>']:
   with self.assertRaises(ValueError):self.normalize(body)
 def test_unapproved_link_rejected(self):
  with self.assertRaises(ValueError):self.normalize('<a href="https://evil.invalid">x</a>')
 def test_text_escaped(self):self.assertEqual(self.normalize('<p>A &amp; B &lt; C</p>'),'<p>A &amp; B &lt; C</p>')
if __name__=='__main__':unittest.main()
