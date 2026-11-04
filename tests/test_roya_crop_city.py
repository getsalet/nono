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
    assert [x['key'] for x in out] == ['a', 'cropcity-x']
    assert out[1]['kind'] == 'article' and out[1]['city_fa'] == ''
    assert title_candidates(out[1], 'royablog', ROOT) == [topic['matrix_title']]


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
