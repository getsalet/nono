import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'automation'))
import build_roya_queue as b
import roya_backlink_queue as r
from city_backlink_policy import title_candidates

ROOT = Path(__file__).resolve().parents[1]


def test_matrix_retires_unpublished_and_keeps_published(tmp_path):
    (tmp_path / 'data/roya').mkdir(parents=True)
    topic = dict(key='cropcity-x', source_key='gsc-1', target_url='https://navar-abyari.ir/%D8%A7/',
                 site_title='میزان برداشت جو در هکتار', topic='میزان برداشت جو در هکتار', audience_city='همدان',
                 audience_province='همدان', matrix_title='میزان برداشت جو در هکتار؛ راهنمای کشاورزان همدان')
    (tmp_path / 'data/roya/crop-city-topics.json').write_text(json.dumps(dict(
        policy='roya-crop-city-gsc-v1', enabled=True, retire_unpublished_legacy=True, topics=[topic])))
    items = [dict(key='a', published=True, title='t'), dict(key='b', status='failed'), dict(key='c', status='pending')]
    out = b.append_crop_city_topics(items, {}, tmp_path)
    assert [x['key'] for x in out] == ['a', 'b', 'c', 'cropcity-x'] and out[1]['status'] == out[2]['status'] == 'retired'
    assert out[3]['kind'] == 'article' and out[3]['city_fa'] == ''
    assert title_candidates(out[3], 'royablog', ROOT) == [topic['matrix_title']]


def test_committed_matrix_is_unique_and_bounded():
    d = json.loads((ROOT / 'data/roya/crop-city-topics.json').read_text())
    titles = [t['matrix_title'] for t in d['topics']]
    assert len(titles) == len(set(titles)) and all(len(t) <= 65 and t2 in t for t, t2 in
                                                   ((x['matrix_title'], x['audience_city']) for x in d['topics']))


def test_prompt_and_qa_forbid_local_claims():
    item = dict(key='cropcity-x', kind='article', family='tape20', target_url='https://navar-abyari.ir/%D8%A7/',
                site_title='میزان برداشت جو در هکتار', topic='میزان برداشت جو در هکتار', city_fa='', province_fa='',
                audience_city='همدان', assigned_title='میزان برداشت جو در هکتار؛ راهنمای کشاورزان همدان')
    links = [{'url': item['target_url'], 'anchor': item['site_title'], 'role': 'city'},
             {'url': 'https://navar-abyari.ir/', 'anchor': 'نوار تیپ', 'role': 'home'}]
    prompt = r.build_prompt(item, links)
    assert 'کشاورزان همدان' in prompt and 'ادعا نکن' in prompt
    bad = {'title': item['assigned_title'], 'html': '<p>همدان قطب تولید جو است.</p>'}
    errs = r.qa(item, bad, links, ROOT, require_image=False)[0]
    assert 'Unverified local crop/production claim about audience city' in errs


def test_city_keyword_templates_expand_per_city():
    tpl = json.loads((ROOT / 'data/roya/crop-city-topics.json').read_text())['city_templates']
    city = dict(key='k', family='tape20', city_fa='همدان', province_fa='همدان', published=True,
                target_url='https://navar-abyari.ir/hamedan/x/', hub_url='https://navar-abyari.ir/hamedan/',
                site_title='نوار تیپ همدان')
    out = b.append_city_keyword_topics([city], {}, tpl, set(), set())
    titles = [x['matrix_title'] for x in out[1:]]
    assert 'قیمت نوار تیپ در همدان' in titles and any(t.startswith('روش کشت ') and t.endswith('با نوار آبیاری در همدان') for t in titles) and any(t.startswith('کشت گلخانه‌ای') for t in titles)
    for x in out[1:]:
        if x['kind'] == 'city':
            assert x['target_url'] == city['target_url']
        else:
            assert x['audience_city'] == 'همدان' and x['target_url'].startswith('https://navar-abyari.ir/')


def test_commercial_cap_preserves_published_and_retires_only_excess():
    import hashlib
    tpl = json.loads((ROOT / 'data/roya/crop-city-topics.json').read_text())['city_templates']
    def row(template, city='همدان', **kwargs):
        title = template.format(city=city)
        return dict(key='citykw-' + hashlib.sha256(title.encode()).hexdigest()[:16],
                    city_fa=city, status='pending', attempts=0, **kwargs)
    rows = [row(t) for t in tpl['commercial'] + tpl['retired_commercial']]
    rows[-1].update(status='published', published=True, pid=123, title='اصل منتشرشده')
    rows[3]['attempts'] = 2
    b.retire_excess_commercial(rows, tpl)
    assert rows[-1]['status'] == 'published' and rows[-1]['pid'] == 123
    assert rows[0]['status'] == 'pending' and rows[0]['matrix_title'] == 'قیمت نوار تیپ در همدان'
    assert all(x['status'] == 'retired' for x in rows[1:-1])
    assert rows[3]['attempts'] == 2
    before = json.dumps(rows, sort_keys=True)
    b.retire_excess_commercial(rows, tpl)
    assert json.dumps(rows, sort_keys=True) == before


def test_commercial_cap_does_not_modify_existing_or_inflight_selected():
    import hashlib
    tpl = json.loads((ROOT / 'data/roya/crop-city-topics.json').read_text())['city_templates']
    city='تهران'
    def row(t, status):
        return dict(key='citykw-'+hashlib.sha256(t.format(city=city).encode()).hexdigest()[:16],
                    city_fa=city, status=status, generated_at='2026-01-01', assigned_title='عنوان قبلی')
    rows=[row(t,'published' if i in (2,3,4) else 'pending') for i,t in enumerate(tpl['commercial']+tpl['retired_commercial'])]
    unrelated={'key':'citykw-method', 'kind':'article', 'status':'pending', 'city_fa':city}
    rows.append(unrelated)
    b.retire_excess_commercial(rows, tpl)
    assert sum(x['status']=='published' for x in rows)==3
    assert sum(x['status']=='pending' for x in rows[:-1])==0
    assert unrelated['status']=='pending'


def test_publisher_skips_excess_ready_artifact_before_preflight(tmp_path, monkeypatch):
    import hashlib
    import publish_roya_posts as pub
    import blog_image_runtime_control
    cfg = json.loads((ROOT / 'data/roya/crop-city-topics.json').read_text())
    folder = tmp_path / 'data/roya'; folder.mkdir(parents=True)
    (folder / 'crop-city-topics.json').write_text(json.dumps(cfg))
    city='همدان'; tpl=cfg['city_templates']
    def key(t): return 'citykw-'+hashlib.sha256(t.format(city=city).encode()).hexdigest()[:16]
    rows=[dict(key=key(t), city_fa=city, status='pending') for t in tpl['commercial']+tpl['retired_commercial']]
    queue=tmp_path/'queue.json';queue.write_text(json.dumps({'items':rows}))
    pq=tmp_path/'publish.json';pq.write_text(json.dumps({'items':[{'key':rows[2]['key'], 'item_file':'missing.json'}]}))
    monkeypatch.setattr(pub, 'ROOT', tmp_path);monkeypatch.setattr(pub, 'QUEUE', queue)
    monkeypatch.setattr(pub, 'PUBLISH_QUEUE', pq);monkeypatch.setattr(pub, 'STATE', tmp_path/'state.json')
    monkeypatch.setattr(pub, 'DO_PUBLISH', False)
    monkeypatch.setattr(blog_image_runtime_control, 'publication_paused', lambda root: False)
    assert pub.main() == 0
    assert json.loads(pq.read_text())['items'][0]['key'] == rows[2]['key']
