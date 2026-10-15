import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from source_page_image import primary_image
BASE='https://navar-abyari.ir/'
PHOTO=BASE+'wp-content/uploads/own.webp'
RELATED=BASE+'wp-content/uploads/navar-article-generated/related.webp'
class PrimarySourceImageTests(unittest.TestCase):
 def test_declared_image_beats_earlier_recommendation(self):
  page='<img src="'+RELATED+'"><meta property="og:image" content="'+PHOTO+'">'
  self.assertEqual(primary_image(page,BASE),PHOTO)
 def test_own_article_image_not_related_card(self):
  page='<header><img src="'+RELATED+'"></header><main><aside><img src="'+RELATED+'"></aside><article><img src="'+PHOTO+'"></article></main>'
  self.assertEqual(primary_image(page,BASE),PHOTO)
 def test_related_images_alone_do_not_count(self):
  self.assertEqual(primary_image('<div class="related"><img src="'+RELATED+'"></div>',BASE),'')
 def test_foreign_or_lookalike_host_rejected(self):
  for url in ('https://other.example/wp-content/uploads/a.webp','https://navar-abyari.ir.evil.test/wp-content/uploads/a.webp'):
   self.assertEqual(primary_image('<meta property="og:image" content="'+url+'">',BASE),'')
 def test_entities_and_relative_source(self):
  self.assertEqual(primary_image('<main><img src="/wp-content/uploads/own.webp"></main>',BASE),PHOTO)
if __name__=='__main__':unittest.main()
