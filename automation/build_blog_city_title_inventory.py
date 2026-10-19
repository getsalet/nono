#!/usr/bin/env python3
"""Build a finite, reviewable TITLE inventory, never 1,500 auto-published posts.
Only exact tape city destinations already in Roya are eligible. Crop-free rows
are explicitly identified; a production crop title requires municipal evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter
from city_backlink_policy import title_candidates
from blog_city_editorial import approved_crops, crop_names, title_errors
from blog_city_priority import ordered

ROOT=Path(__file__).resolve().parents[1]
BLOGS=('royablog','farsiblog','rozblog','loxblog','blogsky')

def build(root=ROOT, count=1500):
    root=Path(root)
    if type(count) is not int or count<1:raise ValueError('Positive title count required')
    raw=json.loads((root/'data/roya/backlink-queue.json').read_text())
    targets=[];seen=set()
    for source in ordered(raw['items'],root):
        if (source.get('family')!='tape20' or not source.get('city_fa') or not source.get('target_url')
                or source.get('target_url')==source.get('hub_url') or source['target_url'] in seen):continue
        seen.add(source['target_url'])
        key='city-'+hashlib.sha256(source['key'].encode()).hexdigest()[:16]
        targets.append({**source,'key':key,'kind':'city'})
    rows=[];used=set();pairs=set()
    # Breadth first: cover every available target before adding another angle.
    for turn in range(len(BLOGS)):
        for index,item in enumerate(targets):
            blog=BLOGS[(index+turn)%len(BLOGS)]
            if (blog,item['key']) in pairs:continue
            candidates=title_candidates(item,blog,root)
            title=next((t for t in candidates if t not in used and not title_errors(item,t,root)),None)
            if title is None:continue
            crops=crop_names(title,root)
            rows.append({'id':'title-'+hashlib.sha256((blog+'|'+item['key']+'|'+title).encode()).hexdigest()[:16],
                         'blog':blog,'target_key':item['key'],'title':title,
                         'crop':crops[0] if crops else None,
                         'locality_status':'approved_municipality_crop' if crops else 'city_only_no_crop_claim',
                         'status':'title_candidate_not_generated'})
            used.add(title);pairs.add((blog,item['key']))
            if len(rows)==count:break
        if len(rows)==count:break
    if len(rows)!=count:raise RuntimeError('Insufficient unique evidence-safe titles; do not pad, duplicate or invent crop claims')
    selected={row['target_key'] for row in rows}
    table=[{'key':t['key'],'city_fa':t['city_fa'],'province_fa':t.get('province_fa',''),
            'hub_url':t.get('hub_url',''),'target_url':t['target_url']}for t in targets if t['key']in selected]
    # Independent checks against the raw source, not just derived summary fields.
    official={x.get('target_url')for x in raw['items']if x.get('family')=='tape20' and x.get('target_url')!=x.get('hub_url')}
    assert len(rows)==len({x['id']for x in rows})==len({x['title']for x in rows})==count
    assert len(table)==len(selected) and all(t['target_url'] in official for t in table)
    assert all(12<=len(t['title'])<=65 for t in rows)
    result={'schema':'afp-city-title-inventory-v1','requested_count':count,'count':len(rows),
            'note':'Titles, not articles or publication approvals. No unverified crop is attached to a city. Crop confirmation remains incomplete; source images and final article QA are required at generation/export/publication.',
            'summary':{'unique_city_targets':len(table),'crop_verified_titles':sum(x['crop'] is not None for x in rows),
                       'crop_free_titles':sum(x['crop'] is None for x in rows)},
            'targets':table,'titles':rows}
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count',type=int,default=1500)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=build(args.root,args.count)
    output=args.output or args.root/'data/blog-city-title-inventory.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps(result['summary'],ensure_ascii=False))

if __name__=='__main__':main()
