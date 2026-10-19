#!/usr/bin/env python3
"""Build a finite, reviewable TITLE inventory, never 1,500 auto-published posts.
Only exact tape city destinations already in Roya are eligible. Crop-free rows
are explicitly identified; crop titles require exact reviewed geographic scope.
"""
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter
from city_backlink_policy import title_candidates
from blog_city_editorial import approved_crop_records, crop_names, title_errors, matching_evidence
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
    rows=[];used=set();pairs=set();per_blog=Counter()
    quotas={blog:count//len(BLOGS)+(i<count%len(BLOGS))for i,blog in enumerate(BLOGS)}
    def offer(item,blog):
        if len(rows)>=count or per_blog[blog]>=quotas[blog] or (blog,item['key']) in pairs:return
        title=next((t for t in title_candidates(item,blog,root)
                    if t not in used and not title_errors(item,t,root)),None)
        if title is None:return
        crops=crop_names(title,root);evidence=matching_evidence(item,title,root)
        scope='county' if crops and any(row['scope']=='county'for row in evidence) else 'municipality'
        row={'id':'title-'+hashlib.sha256((blog+'|'+item['key']+'|'+title).encode()).hexdigest()[:16],
             'blog':blog,'target_key':item['key'],'title':title,'crop':crops[0] if crops else None,
             'locality_status':('approved_'+scope+'_crop') if crops else 'city_only_no_crop_claim',
             'status':'title_candidate_not_generated'}
        if crops:row['evidence_ids']=[x['id']for x in evidence if x.get('id')]
        rows.append(row);used.add(title);pairs.add((blog,item['key']));per_blog[blog]+=1
    # First make reviewed crop targets available in every active blog. This is
    # at most one title per destination/blog, not padding one crop to 1,500 rows.
    verified=[item for item in targets if approved_crop_records(item,root)]
    for item in verified:
        for blog in BLOGS:offer(item,blog)
    # Then breadth-first over actual targets, preserving important-city order,
    # distinct blog angles, and equal quotas. No new target is invented.
    for turn in range(len(BLOGS)):
        for index,item in enumerate(targets):
            offer(item,BLOGS[(index+turn)%len(BLOGS)])
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
