import unittest,tempfile
from pathlib import Path
from automation.agri_v2.wordpress import WordPress,WPError
from automation.agri_v2.queue import atomic_json
class WPTests(unittest.TestCase):
 def test_origin_and_missing_secret(self):
  for e in [{},{'AFP_WP_BASE_URL':'http://navar-abyari.ir'},{'AFP_WP_BASE_URL':'https://evil.invalid'}]:
   with self.assertRaises(WPError):WordPress(e)
 def test_forbidden_route(self):
  w=WordPress({'AFP_WP_BASE_URL':'https://navar-abyari.ir','AFP_WP_USERNAME':'fixture','AFP_WP_APP_PASSWORD':'fixture'})
  with self.assertRaises(WPError):w.call('users/1','POST',{'roles':['administrator']})
 def test_author_capabilities(self):
  w=WordPress({'AFP_WP_BASE_URL':'https://navar-abyari.ir','AFP_WP_USERNAME':'fixture','AFP_WP_APP_PASSWORD':'fixture'});w.call=lambda *a:({'id':2,'roles':['subscriber'],'capabilities':{}},{})
  with self.assertRaises(WPError):w.preflight()
 def test_publication_needs_explicit_authorization(self):
  w=WordPress({'AFP_WP_BASE_URL':'https://navar-abyari.ir','AFP_WP_USERNAME':'fixture','AFP_WP_APP_PASSWORD':'fixture'})
  with self.assertRaises(WPError):w.publish('/nonexistent',{}, {},False)
 def test_empty_inventory_fails_closed(self):
  w=WordPress({'AFP_WP_BASE_URL':'https://navar-abyari.ir','AFP_WP_USERNAME':'fixture','AFP_WP_APP_PASSWORD':'fixture'});w.call=lambda *a:([],{'X-WP-TotalPages':'0'})
  with self.assertRaises(WPError):w.inventory()
if __name__=='__main__':unittest.main()
