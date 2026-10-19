import copy
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'automation'))
import blogsky_backlink_queue as adapter
import city_backlink_policy as policy
from export_blogsky_posts import export
from content_originality import check_corpus, PublishedBody


class BlogskyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('data/blogsky/generator-control.json', 'data/blog-city-title-matrix.json',
                     'data/blog-editorial-image-policy.json', 'templates/blogsky/afp-single-post.html'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        self.write('data/blog-generated-image-control.json', {'pause_image_production': False,
                   'enabled_families': ['tape20'], 'cancelled_families': ['hose']})
        self.source = {'key': 'official-city-source', 'family': 'tape20',
                       'city_fa': 'آزمایش', 'province_fa': 'آزمایش',
                       'site_title': 'نوار تیپ در آزمایش',
                       'target_url': 'https://navar-abyari.ir/tehran/test-city/',
                       'hub_url': 'https://navar-abyari.ir/tehran/',
                       'post': {'html': '<p>Do not copy source prose</p>'}, 'published': False}
        self.write('data/roya/backlink-queue.json', {'items': [self.source]})
        self.write('data/blog-site-article-targets.json', {'targets': [self.source]})

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False))

    def fixture(self):
        q = policy.build_queue('blogsky', self.root)
        item = q['items'][0]
        links = policy.links_for(item)
        body = '<p>' + item['assigned_title'] + '</p>'
        for n in range(3):
            body += '<h2>بررسی نیاز سامانه آبیاری</h2><p>' + ' '.join('بررسیآبیاری' + str(n * 200 + i) for i in range(200)) + '</p>'
        body += '<ul><li>مشخصات مدل را بررسی کنید</li></ul>'
        body += ''.join('<p><a href="' + x['url'] + '">' + x['anchor'] + '</a></p>' for x in links)
        body += ''.join('<details><summary>چطور بررسی کنیم؟</summary><p>برگه همان مدل را بررسی کنید.</p></details>' for _ in range(3))
        post = {'title': item['assigned_title'], 'slug': 'blogsky-city-test', 'tags': ['آبیاری'],
                'meta_description': 'این راهنمای آموزشی به بررسی اطلاعات و مشخصات تجهیزات آبیاری و آماده‌سازی پرسش‌های لازم پیش از انتخاب مدل متناسب با نیاز زمین کمک می‌کند.',
                'html': body}
        item.update(status='completed', title=post['title'], slug=post['slug'])
        self.write('data/blogsky/backlink-queue.json', q)
        record = {**item, 'blog': adapter.BLOG, 'post': post, 'qa': {'passed': True}}
        self.write('artifacts/blogsky-backlink-queue/items/' + item['key'] + '.json', record)
        return item, post, record

    def test_real_builder_only_city_targets_no_article_or_prose_copy(self):
        q = policy.build_queue('blogsky', self.root)
        self.assertEqual(len(q['items']), 1)
        row = q['items'][0]
        self.assertEqual(row['kind'], 'city')
        self.assertNotIn('post', row)
        self.assertNotIn('published', row)
        self.assertEqual(policy.build_queue('blogsky', self.root), q)

    def test_dry_run_is_default_read_only_no_provider_or_queue_write(self):
        with patch.dict(os.environ, {}, clear=True), patch('roya_backlink_queue.agnes', side_effect=AssertionError('No API')):
            self.assertEqual(adapter.main(self.root), 0)
        self.assertFalse((self.root / 'data/blogsky/backlink-queue.json').exists())
        self.assertFalse((self.root / 'artifacts').exists())

    def test_paused_control_stops_before_preview(self):
        self.write('data/blog-generated-image-control.json', {'pause_image_production': True})
        with patch.dict(os.environ, {}, clear=True), patch.object(adapter, 'preview', side_effect=AssertionError('No queue')):
            self.assertEqual(adapter.main(self.root), 0)

    def test_publish_flag_rejected_before_any_queue_write(self):
        with patch.dict(os.environ, {'BLOGSKY_PUBLISH': '1'}, clear=True):
            with self.assertRaises(RuntimeError):
                adapter.main(self.root)
        self.assertFalse((self.root / 'data/blogsky/backlink-queue.json').exists())

    def test_no_more_than_one_new_draft_and_bad_target_fails(self):
        for setting in ({'BLOGSKY_COUNT': '2'}, {'BLOGSKY_DRY_RUN': 'perhaps'}, {'BLOGSKY_TARGET': '../other'}):
            with patch.dict(os.environ, setting, clear=True), self.assertRaises(RuntimeError):
                adapter.main(self.root)
        with patch.dict(os.environ, {'BLOGSKY_TARGET': 'city-' + '0' * 16}, clear=True), self.assertRaises(RuntimeError):
            adapter.main(self.root)

    def test_adapter_import_and_engine_do_not_retarget_other_blog(self):
        import farsiblog_backlink_queue as shared
        previous = (shared.CITY_BLOG, shared.ART, shared.QUEUE, shared.STATE)
        with patch.dict(os.environ, {'FARSIBLOG_COUNT': '3', 'FARSIBLOG_PUBLISH': '1'}, clear=True):
            importlib.reload(adapter)
            with adapter.shared_engine(self.root) as engine:
                self.assertEqual(engine.CITY_BLOG, 'blogsky')
                self.assertEqual(engine.QUEUE, self.root / 'data/blogsky/backlink-queue.json')
                self.assertEqual(os.environ['FARSIBLOG_PUBLISH'], '0')
                self.assertEqual(os.environ['FARSIBLOG_COUNT'], '1')
            self.assertEqual(os.environ['FARSIBLOG_COUNT'], '3')
            self.assertEqual(os.environ['FARSIBLOG_PUBLISH'], '1')
        self.assertEqual((shared.CITY_BLOG, shared.ART, shared.QUEUE, shared.STATE), previous)

    def test_real_shared_engine_produces_city_draft_with_mocked_provider_no_network(self):
        item, post, _ = self.fixture()
        item.update(status='pending')
        self.write('data/blogsky/backlink-queue.json', {'items': [item]})
        (self.root / 'artifacts/blogsky-backlink-queue/items' / (item['key'] + '.json')).unlink()
        with patch.dict(os.environ, {'BLOGSKY_DRY_RUN': '0', 'BLOGSKY_COUNT': '1'}, clear=True):
            with adapter.shared_engine(self.root) as engine:
                @__import__('contextlib').contextmanager
                def configured(*args, **kwargs):
                    yield engine
                with patch.object(adapter, 'shared_engine', configured), patch.object(policy, 'ROOT', self.root), \
                     patch.object(engine, 'source_text', return_value='مشخصات مرجع برای بررسی'), \
                     patch.object(engine, 'agnes', return_value=copy.deepcopy(post)) as provider, \
                     patch.object(engine.BASE, 'AGNES_KEY', 'offline-fixture-not-a-credential'), \
                     patch('blog_source_image.read_page', return_value='<article><p>متن بدون تصویر</p></article>'), \
                     patch('urllib.request.urlopen', side_effect=AssertionError('No network in test')):
                    self.assertEqual(adapter.main(self.root), 0)
                    self.assertEqual(provider.call_count, 1)
        manifest = json.loads((self.root / 'artifacts/blogsky-backlink-queue/exports/index.json').read_text())
        self.assertEqual(manifest['count'], 1)
        self.assertFalse(manifest['native_publication_verified'])
        q = json.loads((self.root / 'data/blogsky/backlink-queue.json').read_text())
        self.assertEqual(q['items'][0]['status'], 'completed')
        self.assertFalse(q['items'][0].get('published'))

    def test_raw_full_qa_then_wrap_footer_not_counted_as_backlinks(self):
        item, post, record = self.fixture()
        self.assertEqual(policy.qa(item, post, policy.links_for(item), 'blogsky', self.root)[0], [])
        before = (self.root / 'data/blogsky/backlink-queue.json').read_bytes()
        result = export(self.root)
        self.assertEqual(result['count'], 1)
        row = result['items'][0]
        body = (self.root / row['body_file']).read_text()
        self.assertIn('class="afp-article-body">' + post['html'] + '</div>', body)
        self.assertNotIn('{{ARTICLE_HTML}}', body)
        self.assertEqual(len(row['contextual_links']), 2)
        self.assertGreater(body.count('<a '), 2)
        self.assertFalse(result['native_publication_verified'])
        self.assertEqual((self.root / 'data/blogsky/backlink-queue.json').read_bytes(), before)
        self.assertEqual(export(self.root)['items'], result['items'])

    def test_saved_pass_does_not_bypass_current_qa_and_stale_manifest_cleared(self):
        item, post, record = self.fixture()
        self.assertEqual(export(self.root)['count'], 1)
        record['post']['html'] += '<script>alert(1)</script>'
        self.write('artifacts/blogsky-backlink-queue/items/' + item['key'] + '.json', record)
        with self.assertRaises(RuntimeError):
            export(self.root)
        manifest = json.loads((self.root / 'artifacts/blogsky-backlink-queue/exports/index.json').read_text())
        self.assertEqual(manifest['status'], 'not_ready')
        self.assertEqual(manifest['count'], 0)

    def test_missing_checkpoint_and_malformed_template_block_export(self):
        item, _, _ = self.fixture()
        path = self.root / 'artifacts/blogsky-backlink-queue/items' / (item['key'] + '.json')
        path.unlink()
        with self.assertRaises(RuntimeError):
            export(self.root)
        (self.root / 'templates/blogsky/afp-single-post.html').write_text('{{ARTICLE_HTML}}{{ARTICLE_HTML}}')
        with self.assertRaises(RuntimeError):
            export(self.root)

    def test_held_hose_and_published_records_are_not_exported(self):
        item, _, record = self.fixture()
        q = {'items': [{**item, 'family': 'hose'}]}
        self.write('data/blogsky/backlink-queue.json', q)
        self.assertEqual(export(self.root)['count'], 0)
        q['items'][0] = {**item, 'published': True}
        self.write('data/blogsky/backlink-queue.json', q)
        self.assertEqual(export(self.root)['count'], 0)

    def test_foreign_target_or_hub_rejected(self):
        item, _, _ = self.fixture()
        for fields in ({'target_url': 'https://evil.example/city/'}, {'target_url': item['hub_url']}, {'city_fa': ''}):
            with self.assertRaises(RuntimeError):
                adapter.validate_target({**item, **fields})

    def test_two_contextual_links_and_three_faqs_remain_mandatory(self):
        item, post, _ = self.fixture()
        for extra in ('<p><a href="https://navar-abyari.ir/shop/">فروشگاه</a></p>', '<details><summary>پرسش</summary><p>پاسخ</p></details>'):
            candidate = {**post, 'html': post['html'] + extra}
            self.assertTrue(policy.qa(item, candidate, policy.links_for(item), 'blogsky', self.root)[0])

    def test_other_blogs_check_blogsky_corpus_and_footer_excluded(self):
        item, post, _ = self.fixture()
        self.assertTrue(check_corpus(self.root, 'rozblog', 'other', post['html']))
        self.assertFalse(check_corpus(self.root, 'blogsky', item['key'], post['html']))
        parsed = PublishedBody('afp-article-body')
        parsed.feed('<div><div class="afp-article-body">' + post['html'] + '</div><footer>FOOTER NOT ARTICLE</footer></div>')
        self.assertTrue(parsed.done)
        self.assertNotIn('FOOTER', ''.join(parsed.parts))

    def test_new_blog_uses_exact_source_images_not_generated_images(self):
        from blog_source_image import source_preferred, trusted_source
        from blog_editorial_image_policy import validate
        self.assertTrue(source_preferred({'family': 'tape20'}, 'blogsky', self.root))
        self.assertTrue(trusted_source({'family': 'tape20'}, 'blogsky', self.root))
        self.assertFalse(source_preferred({'family': 'hose'}, 'blogsky', self.root))
        cfg = json.loads((self.root / 'data/blog-editorial-image-policy.json').read_text())
        for invalid in (['unknown'], ['blogsky', 'blogsky'], 'blogsky', [False], [{}]):
            with self.assertRaises((RuntimeError, TypeError)):
                validate({**cfg, 'additional_blogs': invalid})

    def test_workflow_manual_dry_run_default_no_publish_or_login(self):
        workflow = (ROOT / '.github/workflows/blogsky-content.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('default: true', workflow)
        self.assertIn("BLOGSKY_PUBLISH: '0'", workflow)
        for forbidden in ('schedule:', 'workflow_run:', 'publish_blogsky_posts.py', 'BLOGSKY_PASSWORD', 'install_blog_browser'):
            self.assertNotIn(forbidden, workflow)


if __name__ == '__main__':
    unittest.main()
