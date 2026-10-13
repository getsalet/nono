import copy,json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'automation'))
import farsiblog_backlink_queue as f
from content_originality import reuse_errors,corpus
from roya_backlink_queue import has_numeric_price
class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.item=json.loads((ROOT/'data/farsiblog/backlink-queue.json').read_text())['items'][0];self.links=f.links_for(self.item)
        sections=[]
        for n in range(3):
            words=' '.join('بررسیآبیاری'+str(i+n*200)for i in range(200));sections.append('<h2>بخش بررسی تجهیزات</h2><p>'+words+'</p>')
        links=''.join('<p><a href="'+x['url']+'">'+x['anchor']+'</a></p>'for x in self.links)
        faq=''.join('<details><summary>پرسش کاربردی انتخاب تجهیزات چیست؟</summary><p>مشخصات مدل انتخابی و نیاز زمین را بررسی کنید.</p></details>'for _ in range(3))
        body='<p><img src="'+self.item['image_url']+'" alt="عکس واقعی نوار تیپ AFP"></p>'+''.join(sections)+'<ul><li>بررسی مشخصات محصول</li></ul>'+links+faq
        self.obj={'title':'چک‌لیست انتخاب تجهیزات آبیاری پیش از خرید','slug':'irrigation-selection-checklist','tags':['آبیاری'],'meta_description':'این راهنما به بررسی مشخصات تجهیزات آبیاری و آماده‌سازی اطلاعات مورد نیاز برای انتخاب متناسب با شرایط زمین کمک می‌کند.','html':body}
    def tearDown(self):self.tmp.cleanup()
    def qa(self,obj):return f.qa(self.item,obj,self.links,root=self.root)[0]
    def test_valid_fixture_not_publishable_artifact(self):self.assertEqual(self.qa(self.obj),[])
    def test_real_dimensions_not_price(self):
        self.assertFalse(has_numeric_price('قیمت نوار تیپ ۲۰ سانتی‌متری چقدر است؟'));self.assertTrue(has_numeric_price('قیمت هر رول ۵۰ هزار تومان است'))
    def test_links_and_script_fail(self):
        o=copy.deepcopy(self.obj);o['html']+='<script>alert(1)</script>';self.assertTrue(self.qa(o))
        o=copy.deepcopy(self.obj);o['html']=o['html'].replace(self.links[1]['url'],'https://example.com/');self.assertTrue(self.qa(o))
        o=copy.deepcopy(self.obj);o['html']+='<a href="https://navar-abyari.ir/">نوار تیپ</a>';self.assertTrue(self.qa(o))
    def test_no_duplicate_or_renamed_copy(self):
        r=[{'html':self.obj['html'],'label':'roya:old'}];self.assertTrue(reuse_errors(self.obj['html'],r));self.assertTrue(reuse_errors(self.obj['html'].replace('زمین','مزرعه'),r))
    def test_cross_blog_corpus_and_own_record_exclusion(self):
        p=self.root/'artifacts/roya-backlink-queue/items/old.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'key':'old','qa':{'passed':True},'post':self.obj}))
        self.assertTrue(self.qa(self.obj));self.assertEqual(len(corpus(self.root,'farsiblog',self.item['key'])),1)
    def test_missing_published_corpus_fails_closed(self):
        q=self.root/'data/roya/backlink-queue.json';q.parent.mkdir(parents=True);q.write_text(json.dumps({'items':[{'key':'missing','published':True}]}))
        with self.assertRaises(RuntimeError):self.qa(self.obj)
    def test_missing_api_key_does_not_write_fake_ready(self):
        original=(f.QUEUE,f.ART,f.STATE,f.BASE.AGNES_KEY,f.BASE.AGNES_KEYS)
        try:
            f.QUEUE=self.root/'q.json';f.ART=self.root/'artifacts';f.STATE=self.root/'state.json';f.QUEUE.write_text(json.dumps({'items':[self.item]}));f.BASE.AGNES_KEY='';f.BASE.AGNES_KEYS=[]
            from unittest.mock import patch
            with patch.dict(os.environ,{'FARSIBLOG_DRY_RUN':'0','FARSIBLOG_COUNT':'1'}):
                with self.assertRaises(RuntimeError):f.main()
            self.assertFalse((f.ART/'publish-queue.json').exists())
        finally:f.QUEUE,f.ART,f.STATE,f.BASE.AGNES_KEY,f.BASE.AGNES_KEYS=original
    def test_rolling_hourly_budget(self):
        import datetime
        current=datetime.datetime(2026,10,13,18,30,tzinfo=datetime.timezone.utc)
        state=self.root/'budget.json'
        state.write_text(json.dumps({'published':[{'at':'2026-10-13T17:00:00Z'},{'at':'2026-10-13T18:05:00Z'},{'at':'2026-10-13T18:10:00Z'}]}))
        self.assertEqual(f.remaining_publication_budget(state,current),1)
        state.write_text(json.dumps({'published':[{'at':'2026-10-13T18:05:00Z'}]*3}))
        self.assertEqual(f.remaining_publication_budget(state,current),0)
    def test_bad_hourly_history_fails_closed(self):
        import datetime
        state=self.root/'budget.json';state.write_text(json.dumps({'published':[{'at':'invalid'}]}))
        with self.assertRaises(RuntimeError):f.remaining_publication_budget(state,datetime.datetime.now(datetime.timezone.utc))
    def test_exhausted_budget_prevents_publication(self):
        import publish_farsiblog_posts as publisher
        from unittest.mock import patch
        with patch.object(publisher.native,'DO_PUBLISH',True),patch.object(publisher.native,'main')as publish,patch.object(publisher.generator,'remaining_publication_budget',return_value=0),patch.dict(os.environ,{'FARSIBLOG_USERNAME':'unit-test','FARSIBLOG_PASSWORD':'unit-test'}):
            self.assertEqual(publisher.main(),0);publish.assert_not_called()
if __name__=='__main__':unittest.main()
