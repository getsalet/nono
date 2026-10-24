import unittest
from automation.agri_v2.pipeline import normalize_article,SafeHTML,validate_for_publication
from automation.agri_v2.wordpress import illustrated_content
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
 def test_publication_language_and_boilerplate(self):
  for text in ['ضرر 损失', 'این مقاله یک پیش‌نویس است', 'ترکی مستقیم']:
   with self.assertRaises(ValueError):validate_for_publication({'content_html':'<p>'+text+'</p>'})
 def test_figures_outside_lists(self):
  content='<p>intro</p><h2>one</h2><ul><li>x</li></ul><h2>two</h2><p>end</p>'
  media=[{'url':'https://example.org/'+str(i)} for i in range(3)]
  result=illustrated_content(content,media,'لوبیا')
  self.assertEqual(result.count('<figure '),2);self.assertIn('</ul><figure ',result);self.assertNotIn('<li><figure',result)
if __name__=='__main__':unittest.main()
