import copy,re,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'automation'))
from blog_draft_structure import normalize
class StructureTests(unittest.TestCase):
 def fixture(self):
  item={'key':'city-a123','family':'tape20'}
  p={'slug':'nوار-tip-invalid','html':'<h2>موضوع مقاله</h2><p><a href="https://navar-abyari.ir/">نوار تیپ</a></p><h2>جمع‌بندی</h2><p>'+('مشخصات همان مدل و اطلاعات زمین را ثبت کنید. '*6)+'</p>'+''.join('<details><summary>پرسش؟</summary><p>پاسخ بررسی شود.</p></details>'for _ in range(3))}
  return item,p
 def test_slug_is_ascii_stable_unique_and_bounded(self):
  i,p=self.fixture();normalize(i,p,'farsiblog');a=p['slug'];self.assertRegex(a,r'^[a-z0-9][a-z0-9-]{2,59}$')
  _,q=self.fixture();normalize(i,q,'farsiblog');self.assertEqual(a,q['slug']);q['slug']='???';normalize({**i,'key':'other'},q,'farsiblog');self.assertNotEqual(a,q['slug'])
 def test_preserves_links_faqs_and_valid_metadata(self):
  i,p=self.fixture();p['slug']='valid-model-slug';before=p['html'];normalize(i,p,'farsiblog')
  self.assertEqual(p['slug'],'valid-model-slug');self.assertEqual(re.findall('<a.*?</a>',before),re.findall('<a.*?</a>',p['html']));self.assertEqual(before[before.index('<details'):],p['html'][p['html'].index('<details'):]);self.assertNotIn('<a',p['html'][p['html'].index('<h2>جمع'):p['html'].index('<details')])
 def test_idempotent_and_no_new_factual_claim(self):
  i,p=self.fixture();normalize(i,p,'rozblog');first=copy.deepcopy(p);self.assertEqual(normalize(i,p,'rozblog'),[]);self.assertEqual(p,first);self.assertIn('وب‌سایت اصلی AFP',p['html'])
 def test_never_invents_missing_short_conclusion_or_faq(self):
  for body in ['<p>بدنه</p>','<h2>جمع‌بندی</h2><p>کوتاه</p><details>پرسش</details>','<h2>بدنه</h2><details>پرسش</details>']:
   i,p=self.fixture();p.update(slug='valid-slug',html=body);normalize(i,p,'farsiblog');self.assertEqual(p['html'],body)
 def test_other_providers_are_unchanged(self):
  i,p=self.fixture();before=copy.deepcopy(p);self.assertEqual(normalize(i,p,'blogfa'),[]);self.assertEqual(p,before)
if __name__=='__main__':unittest.main()
