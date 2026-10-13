"""Lexical cross-blog reuse guard; not a guarantee of semantic originality."""
import html,json,re,unicodedata
from pathlib import Path

def text(markup):
    s=unicodedata.normalize('NFKC',html.unescape(re.sub(r'<[^>]+>',' ',markup or ''))).replace('ي','ی').replace('ك','ک').replace('\u200c',' ')
    return ' '.join(re.findall(r'[\w\u0600-\u06ff]+',s.lower()))

def shingles(s):
    t=s.split();return {' '.join(t[i:i+5]) for i in range(max(0,len(t)-4))}

def reuse_errors(markup,records):
    candidate=text(markup);a=shingles(candidate)
    paragraphs=[text(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>',markup or '',re.I|re.S)]
    for record in records:
        other=text(record['html']);b=shingles(other)
        if candidate and candidate==other:return ['duplicate content: '+record['label']]
        if min(len(a),len(b))<40:continue
        overlap=len(a&b)
        if overlap/max(1,len(a|b))>=.50 or overlap/max(1,min(len(a),len(b)))>=.70:return ['excessive text reuse: '+record['label']]
        if any(len(p.split())>=70 and p in other for p in paragraphs):return ['reused long paragraph: '+record['label']]
    return []

def corpus(root,exclude_blog='',exclude_key=''):
    records=[]
    for blog in ('roya','farsiblog'):
        for p in sorted((Path(root)/'artifacts'/f'{blog}-backlink-queue'/'items').glob('*.json')):
            obj=json.loads(p.read_text());
            if blog==exclude_blog and obj.get('key')==exclude_key:continue
            if obj.get('qa',{}).get('passed') and (obj.get('post')or{}).get('html'):records.append({'html':obj['post']['html'],'label':blog+':'+obj.get('key',p.stem)})
        q=Path(root)/'data'/blog/'backlink-queue.json'
        if q.exists():
            expected=[x for x in json.loads(q.read_text()).get('items',[]) if (x.get('published')or x.get('status')=='completed') and not(blog==exclude_blog and x.get('key')==exclude_key)]
            keys={r['label'].split(':',1)[1] for r in records if r['label'].startswith(blog+':')}
            if any(x['key'] not in keys for x in expected):raise RuntimeError('originality corpus incomplete for '+blog)
    return records

def check_corpus(root,blog,key,markup):return reuse_errors(markup,corpus(root,blog,key))
