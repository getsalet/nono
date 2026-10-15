"""Lexical cross-blog reuse guard; incomplete history never silently passes."""
import hashlib,html,json,re,unicodedata,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,quote,urlunsplit

def text(markup):
    s=unicodedata.normalize('NFKC',html.unescape(re.sub(r'<[^>]+>',' ',markup or ''))).replace('ي','ی').replace('ك','ک').replace('\u200c',' ')
    return ' '.join(re.findall(r'[\w\u0600-\u06ff]+',s.lower()))

def shingles(s):
    t=s.split();return {' '.join(t[i:i+5])for i in range(max(0,len(t)-4))}

def reuse_errors(markup,records):
    candidate=text(markup);a=shingles(candidate)
    paragraphs=[text(p)for p in re.findall(r'<p\b[^>]*>(.*?)</p>',markup or '',re.I|re.S)]
    for record in records:
        other=text(record['html']);b=shingles(other)
        if candidate and candidate==other:return ['duplicate content: '+record['label']]
        if min(len(a),len(b))<40:continue
        overlap=len(a&b)
        if overlap/max(1,len(a|b))>=.50 or overlap/max(1,min(len(a),len(b)))>=.70:return ['excessive text reuse: '+record['label']]
        if any(len(p.split())>=70 and p in other for p in paragraphs):return ['reused long paragraph: '+record['label']]
    return []

class PublishedBody(HTMLParser):
    """Extract only the actual .post-content block, without layout/advertising."""
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):super().__init__(convert_charrefs=True);self.depth=0;self.done=False;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if self.done:return
        if not self.depth:
            if 'post-content'in dict(attrs).get('class','').split():self.depth=1
            return
        self.parts.append(self.get_starttag_text())
        if tag not in self.VOID:self.depth+=1
    def handle_startendtag(self,tag,attrs):
        if self.depth and not self.done:self.parts.append(self.get_starttag_text())
    def handle_endtag(self,tag):
        if not self.depth or self.done:return
        if tag in self.VOID:return
        self.depth-=1
        if self.depth:self.parts.append('</'+tag+'>')
        else:self.done=True
    def handle_data(self,data):
        if self.depth and not self.done:self.parts.append(html.escape(data))

def published_snapshot(root,blog,item):
    url=item.get('published_url');host={'roya':'afp.royablog.ir','farsiblog':'afp.farsiblog.com','rozblog':'afp-pipe.rozblog.com','blogfa':'afp-pipe.blogfa.com','loxblog':'afp.lxb.ir'}[blog]
    parts=urlsplit(url or '')
    native_path=parts.path.startswith('/post/') or (blog in ('rozblog','loxblog') and parts.path not in ('','/'))
    # published_url is an already verified native checkpoint; Roz and LoxBlog use their own custom slugs.
    if parts.scheme!='https'or parts.hostname!=host or not native_path:
        raise RuntimeError('originality published history missing a verified public URL for '+blog)
    cache=Path(root)/'artifacts/content-originality'/blog/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if cache.exists():
        obj=json.loads(cache.read_text())
        if obj.get('url')==url and len(text(obj.get('html','')).split())>=100:return obj['html']
    safe=urlunsplit((parts.scheme,parts.netloc,quote(parts.path,safe='/%'),parts.query,parts.fragment))
    request=urllib.request.Request(safe,headers={'User-Agent':'AFP-originality-history-check/1.0'})
    try:
        with urllib.request.urlopen(request,timeout=45)as response:
            if urlsplit(response.geturl()).hostname!=host:raise RuntimeError('originality public history redirected to another host')
            parser=PublishedBody();parser.feed(response.read().decode('utf8','replace'))
    except Exception as exc:raise RuntimeError('originality cannot load published history for '+blog+': '+type(exc).__name__)from None
    body=''.join(parser.parts)
    if not parser.done or len(text(body).split())<100:raise RuntimeError('originality published article body incomplete for '+blog)
    cache.parent.mkdir(parents=True,exist_ok=True);cache.write_text(json.dumps({'key':item['key'],'url':url,'source':'actual public post, not failed replacement draft','html':body},ensure_ascii=False,indent=2))
    return body

def corpus(root,exclude_blog='',exclude_key=''):
    records=[]
    for blog in ('roya','farsiblog','rozblog','blogfa','loxblog'):
        for p in sorted((Path(root)/'artifacts'/f'{blog}-backlink-queue'/'items').glob('*.json')):
            obj=json.loads(p.read_text())
            if blog==exclude_blog and obj.get('key')==exclude_key:continue
            if obj.get('qa',{}).get('passed')and(obj.get('post')or{}).get('html'):records.append({'html':obj['post']['html'],'label':blog+':'+obj.get('key',p.stem)})
        q=Path(root)/'data'/blog/'backlink-queue.json'
        if q.exists():
            expected=[x for x in json.loads(q.read_text()).get('items',[])if(x.get('published')or x.get('status')=='completed')and not(blog==exclude_blog and x.get('key')==exclude_key)]
            keys={r['label'].split(':',1)[1]for r in records if r['label'].startswith(blog+':')}
            for item in expected:
                if item['key']in keys:continue
                if item.get('published'):
                    records.append({'html':published_snapshot(root,blog,item),'label':blog+':'+item['key']});keys.add(item['key'])
                else:raise RuntimeError('originality approved draft missing for '+blog+'; refusing unchecked content')
    return records

def check_corpus(root,blog,key,markup):return reuse_errors(markup,corpus(root,blog,key))
