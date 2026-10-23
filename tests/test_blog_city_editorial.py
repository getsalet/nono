import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import blog_city_editorial as e
import city_backlink_policy as c
import roya_backlink_queue as r
from build_blog_city_title_inventory import build

class CityEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.write('data/blog-city-title-matrix.json', json.loads((ROOT/'data/blog-city-title-matrix.json').read_text()))
        self.item={'key':'city-fixture','kind':'city','family':'tape20','city_fa':'تهران','province_fa':'تهران',
                   'hub_url':'https://navar-abyari.ir/tehran/','target_url':'https://navar-abyari.ir/tehran/city/',
                   'site_title':'نوار تیپ تهران','status':'pending'}
        today=dt.datetime.now(dt.timezone.utc).date().isoformat()
        self.approval={'approved':True,'city_fa':'تهران','target_url':self.item['target_url'],
            'province_route':'tehran','scope':'municipality','production_system':'field','crop':'گوجه‌فرنگی',
            'source_url':'https://example.org/municipal-report','source_excerpt':'Synthetic test evidence, NOT a real approval',
            'source_date':today,'reviewed_at':today,'review_note':'offline test fixture only'}
    def tearDown(self):self.temp.cleanup()
    def write(self,path,data):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False))
    def registry(self,record):self.write('data/blog-city-crop-evidence.json',{'policy':e.POLICY,'approved_records':[record]})
    def test_missing_registry_never_randomly_assigns_crop(self):
        for blog in ('royablog',*c.BLOGS):
            for t in c.title_candidates(self.item,blog,self.root):
                self.assertEqual(e.crop_names(t,self.root),[])
    def test_exact_verified_city_crop_used_not_global_lottery(self):
        self.registry(self.approval)
        titles=c.title_candidates(self.item,'blogsky',self.root)
        self.assertTrue(titles);self.assertTrue(all(e.crop_names(t,self.root)==['گوجه‌فرنگی'] for t in titles))
    def test_province_county_homonym_url_system_staleness_not_city_evidence(self):
        for change in ({'scope':'province'},{'scope':'county'},{'production_system':'greenhouse'},
                       {'province_route':'isfahan'},{'target_url':'https://navar-abyari.ir/other/'},
                       {'city_fa':'فلاورجان'},{'source_date':'2010-01-01'},{'source_date':'2999-01-01'},
                       {'approved':False},{'approved':'true'},{'review_note':''},{'source_url':'http://example.org/'},
                       {'reviewed_at':'invalid'}):
            self.registry({**self.approval,**change})
            self.assertEqual(e.approved_crops(self.item,self.root),[],change)
    def test_county_evidence_only_produces_explicit_same_county_titles(self):
        self.registry({**self.approval,'scope':'county','county_fa':'تهران'})
        titles=c.title_candidates(self.item,'blogsky',self.root)
        self.assertTrue(titles)
        self.assertTrue(all('در شهرستان تهران' in t for t in titles))
        self.assertTrue(all(not e.title_errors(self.item,t,self.root)for t in titles))
        self.assertTrue(e.title_errors(self.item,'نوار تیپ گوجه‌فرنگی در تهران؛ بررسی نیازها',self.root))
        self.registry({**self.approval,'scope':'county','county_fa':'ورامین'})
        self.assertEqual(e.approved_crops(self.item,self.root),[])
    def test_county_crop_binding_does_not_cross_product_with_city_evidence(self):
        self.write('data/blog-city-crop-evidence.json',{'policy':e.POLICY,'approved_records':[
            self.approval,{**self.approval,'scope':'county','county_fa':'تهران','crop':'سیب‌زمینی'}]})
        titles=c.title_candidates(self.item,'blogsky',self.root)
        self.assertTrue(any('گوجه‌فرنگی در تهران' in t for t in titles))
        self.assertTrue(any('سیب‌زمینی در شهرستان تهران' in t for t in titles))
        self.assertFalse(any('گوجه‌فرنگی در شهرستان تهران' in t or 'سیب‌زمینی در تهران' in t for t in titles))
    def test_county_intro_and_evidence_prompt_retain_scope_not_third_link(self):
        self.registry({**self.approval,'scope':'county','county_fa':'تهران'})
        title=c.title_candidates(self.item,'blogsky',self.root)[0]
        post={'title':title,'html':self.valid_body()}
        self.assertTrue(e.editorial_errors(self.item,post,c.links_for(self.item),self.root))
        post['html']='<p>اگر در شهرستان تهران گوجه‌فرنگی می‌کارید، اطلاعات واقعی زمین را برای بررسی مدل ثبت کنید.</p>'+post['html']
        self.assertEqual(e.editorial_errors(self.item,post,c.links_for(self.item),self.root),[])
        prompt=e.evidence_prompt(self.item,title,self.root)
        self.assertIn('شهرستان تهران',prompt);self.assertIn('لینک سوم اضافه نکن',prompt)
    def test_current_approved_targets_cover_all_five_active_blogs_without_padding(self):
        data=build(ROOT);verified=[row for row in data['titles']if row['crop']]
        targets=data['targets']
        expected=5*sum(bool(e.approved_crop_records({**t,'kind':'city','family':'tape20'},ROOT))for t in targets)
        self.assertEqual(len(verified),expected)
        self.assertGreaterEqual(len(verified),10)
        self.assertEqual({row['locality_status']for row in verified},{'approved_county_crop'})
        self.assertEqual({row['blog']for row in verified},{'royablog','farsiblog','rozblog','loxblog','blogsky'})
        self.assertTrue(all(row.get('evidence_ids')for row in verified))
    def test_historical_research_record_is_not_approval(self):
        self.write('data/blog-city-crop-evidence.json',{'policy':e.POLICY,'research_records':[self.approval]})
        self.assertEqual(e.approved_crops(self.item,self.root),[])
    def test_old_saved_crop_title_rejected_even_if_qa_passed_before(self):
        self.assertTrue(e.title_errors(self.item,'نوار تیپ پنبه در تهران؛ برگه نیازسنجی',self.root))
        self.assertEqual(e.title_errors(self.item,'نوار تیپ در تهران؛ بررسی مسیر',self.root),[])
    def test_crop_detection_not_substring_in_masir(self):
        self.assertEqual(e.crop_names('نوار تیپ در تهران؛ بررسی مسیر',self.root),[])
        self.assertEqual(e.crop_names('نوار تیپ گوجه فرنگی در تهران',self.root),['گوجه‌فرنگی'])
        self.assertEqual(e.crop_names('پیاز؛ بررسی مسیر',self.root),['پیاز'])
    def test_roya_published_frozen_but_stale_completed_reopened(self):
        old={**self.item,'published':True,'title':'نوار تیپ پنبه در تهران','status':'published'}
        stale={**self.item,'key':'draft','status':'completed','title':'نوار تیپ پنبه در تهران'}
        before=copy.deepcopy(old);q={'items':[old,stale]};r.assign_roya_titles(q,self.root)
        self.assertEqual(old,before);self.assertEqual(stale['status'],'failed')
        self.assertEqual(e.crop_names(stale['assigned_title'],self.root),[])
    def test_shared_builder_reopens_bad_draft_without_touching_published(self):
        import hashlib
        source={**self.item,'key':'source'}
        self.write('data/roya/backlink-queue.json',{'items':[source]})
        key='city-'+hashlib.sha256(b'source').hexdigest()[:16]
        stale={**self.item,'key':key,'status':'completed','title':'نوار تیپ پنبه در تهران'}
        self.write('data/blogsky/backlink-queue.json',{'items':[stale]})
        q=c.build_queue('blogsky',self.root);self.assertEqual(q['items'][0]['status'],'failed')
    def test_new_crop_evidence_reopens_neutral_completed_draft_instead_of_blocking_backlog(self):
        import hashlib
        self.registry({**self.approval,'scope':'county','county_fa':'تهران'})
        source={**self.item,'key':'source'}
        self.write('data/roya/backlink-queue.json',{'items':[source]})
        key='city-'+hashlib.sha256(b'source').hexdigest()[:16]
        stale={**self.item,'key':key,'status':'completed','title':'نوار تیپ در تهران؛ ثبت پرسش‌های فنی',
               'assigned_title':'نوار تیپ در تهران؛ ثبت پرسش‌های فنی'}
        self.write('data/blogsky/backlink-queue.json',{'items':[stale]})
        q=c.build_queue('blogsky',self.root);row=q['items'][0]
        self.assertEqual(row['status'],'failed');self.assertIn('شهرستان تهران',row['assigned_title'])
        self.assertEqual(row['title'],stale['title'])  # Never relabel old prose as a new article.
    def valid_body(self):
        return ('<h2>جمع‌بندی</h2><p>برای تصمیم نهایی ابتدا اطلاعات واقعی زمین و مسیر آب را ثبت کنید و مشخصات همان مدل را بررسی کنید. سپس راهنمای شهری و توضیحات تجهیزات را در وب‌سایت اصلی AFP مطالعه کنید تا پرسش‌های لازم را برای مشاوره آماده داشته باشید.</p>'+
                '<h2>سوالات متداول</h2>'+''.join('<details><summary>چه اطلاعاتی لازم است؟</summary><p>مشخصات واقعی مسیر را برای بررسی مدل آماده کنید.</p></details>'for _ in range(3)))
    def test_conclusion_and_final_faq_contract(self):
        links=c.links_for(self.item);post={'title':'نوار تیپ در تهران؛ بررسی مسیر','html':self.valid_body()}
        self.assertEqual(e.editorial_errors(self.item,post,links,self.root),[])
        for body in (post['html'].replace('جمع‌بندی','نتیجه'),post['html']+'<p>مطلب دیگری</p>',
                     post['html'].replace('<p>مشخصات واقعی','مشخصات واقعی'),
                     post['html'].replace('وب‌سایت اصلی AFP','این برگه'),
                     post['html'].replace('برای تصمیم نهایی ابتدا اطلاعات واقعی زمین و مسیر آب را ثبت کنید و مشخصات همان مدل را بررسی کنید. سپس راهنمای شهری و توضیحات تجهیزات را در وب‌سایت اصلی AFP مطالعه کنید تا پرسش‌های لازم را برای مشاوره آماده داشته باشید.','مشخصات را در وب‌سایت AFP بررسی کنید.')):
            self.assertTrue(e.editorial_errors(self.item,{**post,'html':body},links,self.root))
    def test_primary_keyword_anchor_for_both_engines(self):
        self.assertIn(c.links_for(self.item)[1]['anchor'],('نوار تیپ','نوار آبیاری'))
        lib={'families':{'tape20':{'anchor':'نوار تیپ'}},'home':{'url':'https://navar-abyari.ir/'}}
        self.assertIn(r.approved_links(self.item,lib)[1]['anchor'],('نوار تیپ','نوار آبیاری'))
    def test_inventory_has_1500_unique_titles_real_targets_and_no_false_crop_approval(self):
        data=build(ROOT)
        source=json.loads((ROOT/'data/roya/backlink-queue.json').read_text())
        expected=len({x['target_url']for x in source['items']if x.get('family')=='tape20' and x.get('kind')!='article' and x.get('city_fa') and x.get('target_url')!=x.get('hub_url')})
        self.assertEqual(data['count'],1500);self.assertEqual(data['summary']['unique_city_targets'],min(expected,1500))
        target={t['key']:t for t in data['targets']}
        for row in data['titles']:
            if row['crop']:
                item={**target[row['target_key']],'family':'tape20','kind':'city'}
                self.assertTrue(e.matching_evidence(item,row['title'],ROOT))
                self.assertFalse(e.title_errors(item,row['title'],ROOT))
        self.assertEqual(len({x['title']for x in data['titles']}),1500)
        self.assertNotIn('blogfa',{x['blog']for x in data['titles']})
        self.assertTrue(all(len(x['title'])<=65 for x in data['titles']))
        committed=json.loads((ROOT/'data/blog-city-title-inventory.json').read_text());self.assertEqual(data,committed)

if __name__=='__main__':unittest.main()
