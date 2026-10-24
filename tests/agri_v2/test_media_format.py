import base64,io,unittest
from PIL import Image,ImageChops
from automation.agri_v2.media_policy import reference_images,add_phone_watermark,image_prompt,PHONE_LABEL
from automation.agri_v2.article_format import faq_html
from automation.agri_v2.wordpress import illustrated_content
class MediaFormatTests(unittest.TestCase):
 def test_reference_and_identity(self):
  raw=base64.b64decode(reference_images()[0].split(',',1)[1]);im=Image.open(io.BytesIO(raw));self.assertEqual(im.size,(1200,675))
  self.assertEqual(PHONE_LABEL,'AFP | 09134922013')
  for i in (1,2,3):self.assertIn('drip-tape carton',image_prompt({'crop':'لوبیا','title':'برداشت لوبیا'},i))
 def test_phone_applied_bottom_right_only(self):
  source=Image.new('RGB',(1200,675),'white');out=add_phone_watermark(source)
  self.assertEqual(out.getpixel((10,10)),(255,255,255));self.assertIsNotNone(ImageChops.difference(source,out).crop((700,580,1200,675)).getbbox())
 def test_three_standard_faqs_and_escape(self):
  faq=[{'question':'پرسش درباره کشت چیست؟','answer':'این پاسخ آزمایشی قالب است و توصیه علمی نیست. <script>x</script>'} for _ in range(3)]
  h=faq_html(faq);self.assertEqual(h.count('<details '),3);self.assertEqual(h.count('<summary '),3);self.assertIn('faq-section',h);self.assertNotIn('<script>',h)
  with self.assertRaises(ValueError):faq_html(faq[:2])
 def test_no_visible_repeated_caption(self):
  s=illustrated_content('<p>x</p><h2>a</h2><p>b</p>',[{'url':'https://example.org/a'}]*3,'لوبیا')
  self.assertNotIn('figcaption',s);self.assertNotIn('نه تصویر مستند',s)
if __name__=='__main__':unittest.main()
