#!/usr/bin/env python3
"""Build/query a source-deduplicated research registry. Never auto-approve claims.

Research coverage is NOT cultivation coverage. Pending targets stay crop-free.
Run without options to write coverage.csv and summary.json; --lookup prints the
matching destinations and their source-linked claims. --batch emits a resumable
province-grouped research worklist, not a claim that searches have been executed.
"""
import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from blog_city_editorial import approved_crop_records, norm

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    'current_field_evidence': 'شاهد جاری؛ فقط محدوده تأییدشده',
    'historical_only': 'فقط شاهد تاریخی؛ نیازمند منبع تازه',
    'scope_or_system_review': 'شاهد محدود؛ نیازمند بررسی محدوده یا نوع کشت',
    'historical_policy_caution': 'هشدار برنامه کشت تاریخی؛ وضعیت فعلی نامعلوم',
    'context_not_cultivation': 'شاهد انبار یا زمینه خبر؛ نه شاهد کشت',
    'reviewed_source_needs_refresh': 'شاهد قبلی نیازمند بازبینی تازگی یا مجوز است',
    'not_adjudicated': 'هنوز شاهد محلی داوری‌شده ثبت نشده',
}

def read(root, path):
    return json.loads((Path(root)/path).read_text())

def build(root=ROOT, today=None):
    root = Path(root)
    today = today or dt.datetime.now(dt.timezone.utc).date()
    targets = read(root, 'data/blog-city-title-inventory.json')['targets']
    sources = read(root, 'data/city-crop-knowledge/sources.json')['sources']
    claims = read(root, 'data/city-crop-knowledge/claims.json')['claims']
    source_map = {s['id']:s for s in sources}
    if len(source_map)!=len(sources) or len({c['id'] for c in claims})!=len(claims):
        raise ValueError('Duplicate source/claim ID')
    if len({s['url'] for s in sources})!=len(sources):
        raise ValueError('Same source must be reused, not duplicated per county')
    for c in claims:
        if c['source_id'] not in source_map:
            raise ValueError('Orphan claim: '+c['id'])
    for s in sources:
        date = dt.date.fromisoformat(s['source_date'])
        reviewed = dt.date.fromisoformat(s['reviewed_at'][:10])
        if date>today or reviewed>today:
            raise ValueError('Future source/review date')
        if not s.get('reviewed_excerpt'):
            raise ValueError('Source has no reviewed excerpt')
        if s.get('main_text_loaded') and len(s.get('extraction_sha256',''))!=64:
            raise ValueError('Loaded article needs extraction hash')
    approved = read(root,'data/blog-city-crop-evidence.json')['approved_records']
    claim_map={c['id']:c for c in claims}
    for a in approved:
        c=claim_map.get(a.get('knowledge_claim_id',a['id']))
        if not c or c['review_status']!='reviewed_current':
            raise ValueError('Production approval has no reviewed current claim')
        s=source_map[c['source_id']]
        if (not s.get('main_text_loaded') or c['claim_kind']!='cultivation_report'
                or c['production_system']!='field'
                or c['geographic_scope'] not in ('county','municipality')
                or c['crop']!=a['crop'] or c['province_route']!=a['province_route']
                or norm(c['place_fa'])!=norm(a['city_fa'])
                or s['url']!=a['source_url'] or s['source_date']!=a['source_date']
                or s['reviewed_excerpt']!=a['source_excerpt']
                or s['extraction_sha256']!=a['source_text_sha256']):
            raise ValueError('Production approval diverges from source/claim')
    counts=Counter(norm(t['city_fa']) for t in targets)
    # These are REVIEW flags, not an authoritative administrative gazetteer.
    suspicious={'مرکزی','خراسان رضوی','مازندران','چهارمحال و بختیاری',
                'داران فریدن','خداجوخراجو','قلعه','مشگین','هفتکل','هفتگل',
                'مأمونیه','مامونیه','نایین','نائین'}
    rows=[]
    attached=set()
    for t in targets:
        route=urlsplit(t['hub_url']).path.strip('/').split('/')[0]
        matched=[c for c in claims if c['province_route']==route and
                 (norm(c['place_fa'])==norm(t['city_fa']) or
                  any(norm(p)==norm(t['city_fa']) for p in c.get('related_target_places',[])))]
        attached.update(c['id']for c in matched)
        records=approved_crop_records({**t,'kind':'city','family':'tape20'},root)
        status='not_adjudicated'
        if matched:
            statuses={c['review_status']for c in matched}
            if 'reviewed_current' in statuses:status='reviewed_source_needs_refresh'
            if 'historical_cultivation' in statuses:status='historical_only'
            if 'not_cultivation_evidence' in statuses:status='context_not_cultivation'
            if statuses & {'reviewed_current_limited_scope','reviewed_current_limited_system'}:
                status='scope_or_system_review'
            if 'historical_policy_caution' in statuses:status='historical_policy_caution'
        if records:status='current_field_evidence'
        flags=[]
        if counts[norm(t['city_fa'])]>1:flags.append('homonym_keep_province_and_exact_url')
        if t['city_fa'] in suspicious:flags.append('administrative_or_spelling_review_no_auto_merge')
        rows.append(dict(target_key=t['key'],place_fa=t['city_fa'],province_route=route,
                         knowledge_status=status,publication_decision=(
                             'explicit_approved_scope_only' if records else 'crop_free_until_approved'),
                         approved_crops=list(dict.fromkeys(r['crop']for r in records)),
                         claim_ids=[c['id']for c in matched],geography_flags=flags,
                         next_action=('recheck_source_before_generation' if records else
                                      'resolve_geography_then_load_local_source' if flags else
                                      'load_current_local_main_text_or_county_statistics')))
    # Independent coverage check against the actual source queue, not summaries.
    queue=read(root,'data/roya/backlink-queue.json')['items']
    actual={x['target_url'] for x in queue if x.get('family')=='tape20'
            and x.get('target_url') and x.get('target_url')!=x.get('hub_url')}
    if {t['target_url']for t in targets}!=actual:
        raise ValueError('Destination inventory differs from actual source queue')
    if len(rows)!=len({r['target_key']for r in rows}):
        raise ValueError('Destination duplication')
    summary=dict(schema='afp-city-crop-knowledge-summary-v1',as_of=today.isoformat(),
                 target_count=len(rows),source_count=len(sources),claim_count=len(claims),
                 approved_target_count=sum(bool(r['approved_crops'])for r in rows),
                 status_counts=dict(Counter(r['knowledge_status']for r in rows)),
                 geography_review_target_count=sum(bool(r['geography_flags'])for r in rows),
                 unattached_claim_ids=[c['id']for c in claims if c['id']not in attached],
                 completion='incomplete_local_cultivation_research',
                 caution='All destinations have a publishing decision. This does NOT mean all destinations were searched or cultivation has been adjudicated. No evidence is not evidence of no cultivation.',
                 status_labels_fa=LABELS)
    return rows,summary,source_map,claims

def export(root=ROOT):
    rows,summary,_,_=build(root)
    out=Path(root)/'data/city-crop-knowledge'
    with (out/'coverage.csv').open('w',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        for r in rows:
            writer.writerow({k:' | '.join(v)if isinstance(v,list)else v for k,v in r.items()})
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    plan=read(root,'data/blog-city-crop-review-plan.json')
    bykey={r['target_key']:r for r in rows}
    for t in plan['targets']:
        r=bykey[t['target_key']]
        t['status']='approved_explicit_county_crop' if r['approved_crops'] else 'needs_loaded_local_crop_source'
        t['approved_crops']=r['approved_crops']
    plan['knowledge_coverage']='data/city-crop-knowledge/coverage.csv'
    (Path(root)/'data/blog-city-crop-review-plan.json').write_text(
        json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--lookup',help='Place, crop, or province route')
    p.add_argument('--batch',type=int,help='Maximum pending destinations to return')
    p.add_argument('--offset',type=int,default=0,help='Resume offset in province-grouped worklist')
    p.add_argument('--expected-plan-sha256',help='Required with nonzero offset; prevents skipping jobs after registry changes')
    args=p.parse_args()
    if args.offset<0 or (args.batch is not None and args.batch<1):p.error('Positive batch/nonnegative offset required')
    if args.lookup is not None or args.batch is not None:
        rows,summary,sources,claims=build(args.root)
        if args.lookup is not None:
            query=norm(args.lookup)
            selected=[c for c in claims if any(query in norm(c[k]) for k in ('place_fa','crop','province_route'))]
            claim_ids={c['id']for c in selected}
            output=dict(destinations=[r for r in rows if query in norm(r['place_fa'])or
                                     query in norm(r['province_route'])or bool(set(r['claim_ids'])&claim_ids)],
                        claims=selected,sources=[sources[sid]for sid in sorted({c['source_id']for c in selected})])
        else:
            provinces={urlsplit(t['hub_url']).path.strip('/').split('/')[0]:t['province_fa']
                       for t in read(args.root,'data/blog-city-title-inventory.json')['targets']}
            pending=sorted([r for r in rows if not r['approved_crops']],
                           key=lambda r:(r['province_route'],bool(r['geography_flags']),r['target_key']))
            digest=hashlib.sha256(json.dumps(pending,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            if args.offset and not args.expected_plan_sha256:
                p.error('Resume requires --expected-plan-sha256 from the previous batch')
            if args.expected_plan_sha256 and digest!=args.expected_plan_sha256:
                p.error('Research plan changed. Restart at offset 0; do not silently skip targets.')
            batch=pending[args.offset:args.offset+args.batch]
            groups=defaultdict(list)
            for r in batch:
                groups[r['province_route']].append(dict(
                    target_key=r['target_key'],place_fa=r['place_fa'],
                    state='queued_not_executed',
                    query=f"{r['place_fa']} {provinces[r['province_route']]} جهاد کشاورزی کشت صیفی",
                    geography_flags=r['geography_flags']))
            output=dict(plan_sha256=digest,offset=args.offset,next_offset=args.offset+len(batch),
                        remaining_after_batch=max(0,len(pending)-args.offset-len(batch)),
                        province_batches=dict(groups),
                        instructions='Discover multi-county articles first; load each canonical article once; extract explicit named localities only; review each claim. Worklist execution never constitutes approval.')
        print(json.dumps(output,ensure_ascii=False,indent=2))
    else:
        print(json.dumps(export(args.root),ensure_ascii=False))

if __name__=='__main__':main()