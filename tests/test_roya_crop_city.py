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
