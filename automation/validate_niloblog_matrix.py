"""Fail-closed structural validation; never enables generation/publication."""
import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

def normalize(text):
    text=unicodedata.normalize('NFKC',text).replace('ي','ی').replace('ك','ک')
    return re.sub(r'[\s\u200c\u200f\u200e؛،؟!:.]+','',text)

def validate(matrix,catalog,evidence=None):
    errors=[]
    def require(test,message):
        if not test: errors.append(message)
    rows=matrix.get('titles',[])
    require(matrix.get('provider')=='niloblog','wrong provider')
    require(matrix.get('count')==len(rows)==1000,'expected exactly 1000 titles')
    require(matrix.get('publication_enabled') is False,'planning matrix must not enable publication')
    require(len({r.get('id') for r in rows})==len(rows),'duplicate ids')
    require(len({normalize(r.get('title','')) for r in rows})==len(rows),'duplicate normalized titles')
    contract=matrix.get('editorial_contract',{})
    require(contract.get('link_budget')==[2,3],'body link budget must be 2..3')
    require(contract.get('image_status')=='awaiting_user_image_url','image must await user URL')
    require(contract.get('image_generation_enabled') is False,'image generation must stay disabled')
    require(contract.get('seo',{}).get('article_target_words')==[600,900],'article length profile missing')
    require(contract.get('seo',{}).get('title_hard_max_chars')==78,'short title cap missing')
    targets={r['key']:r for r in catalog.get('targets',[])}
    for key,target in targets.items():
        u=urlparse(target.get('target_url',''))
        require(u.scheme=='https' and u.hostname in ('navar-abyari.ir','www.navar-abyari.ir'),f'unsafe target: {key}')
    for key,plan in matrix.get('link_plans',{}).items():
        links=plan.get('required_links',[])
        require(len(links)==2,f'exactly two required links: {key}')
        refs=[x.get('target_ref') for x in links]
        third=plan.get('optional_third_link',{}).get('target_ref')
        require(len(set(refs+[third]))==3,f'duplicate link destination: {key}')
        require(all(ref in targets for ref in refs+[third]),f'unknown link reference: {key}')
        if refs and refs[0] in targets:require(targets[refs[0]].get('kind')=='article',f'first link is not article: {key}')
        if len(links)==2:require(links[1].get('anchor_keyword') in ['نوار تیپ','نوار آبیاری'],f'missing keyword link: {key}')
        require(plan.get('max_links')==3,f'link cap missing: {key}')
        require(bool(plan.get('optional_third_link',{}).get('condition')),f'third link needs condition: {key}')
    approved={r['id']:r for r in (evidence or {}).get('approved_records',[]) if r.get('approved') is True}
    for row in rows:
        rid=row.get('id','?');loc=matrix.get('localities',{}).get(row.get('locality_ref'),{})
        title=row.get('title','')
        require(bool(loc),f'unknown locality: {rid}')
        require(loc.get('city_fa','__missing__') in title and loc.get('crop','__missing__') in title,f'missing place/crop: {rid}')
        require('آبیاری قطره‌ای' in title or 'نوار تیپ' in title,f'missing irrigation context: {rid}')
        require(len(title)<=78,f'excessively long title: {rid}')
        require(row.get('angle_ref') in matrix.get('angles',{}),f'unknown angle: {rid}')
        require(row.get('link_plan_ref') in matrix.get('link_plans',{}),f'unknown link plan: {rid}')
        require(row.get('review_state') in ['editorial_review_required','local_crop_evidence_required'],f'row not held for review: {rid}')
        if loc.get('scope')=='county':require('شهرستان '+loc.get('city_fa','') in title,f'county scope lost: {rid}')
        if loc.get('evidence_status')=='user_example_only_not_verified':
            require(row.get('review_state')=='local_crop_evidence_required',f'unverified locality unlocked: {rid}')
        elif evidence is not None:
            ev=approved.get(loc.get('evidence_ref'),{})
            require(ev.get('city_fa')==loc.get('city_fa') and ev.get('crop')==loc.get('crop') and ev.get('scope')==loc.get('scope'),f'current evidence mismatch: {rid}')
            require(ev.get('source_url')==loc.get('source_url'),f'provenance mismatch: {rid}')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));ap.add_argument('--evidence');args=ap.parse_args();root=Path(args.root)
    matrix=json.loads((root/'data/niloblog/title-matrix.json').read_text());catalog=json.loads((root/'data/niloblog/article-targets.json').read_text())
    ep=Path(args.evidence) if args.evidence else root/'data/blog-city-crop-evidence.json'
    if not ep.exists():raise SystemExit('Shared locality evidence is required; validation failed closed.')
    errors=validate(matrix,catalog,json.loads(ep.read_text()))
    if errors:
        print(json.dumps({'status':'failed','errors':errors[:30]},ensure_ascii=False));raise SystemExit(1)
    print(json.dumps({'status':'ok','title_count':len(matrix['titles']),'publication_enabled':False,'image_status':'awaiting_user_image_url'},ensure_ascii=False))
if __name__=='__main__':main()
