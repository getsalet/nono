#!/usr/bin/env python3
"""Publish QA-approved Roya posts, checkpointing every verified native-form save.

GitHub Actions uses ROYA_USERNAME/ROYA_PASSWORD repository secrets. A one-time
interactive run may attach to AGENT_BROWSER_CDP; it never closes that browser.
Ready-file paths are resolved within this checkout rather than a previous runner.
"""
import json, os, re, sys, time
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT/'data/roya/backlink-queue.json'
ART = ROOT/'artifacts/roya-backlink-queue'
PUBLISH_QUEUE = ART/'publish-queue.json'
STATE = ROOT/'state/roya-backlink-progress.json'
LOG = ART/'publish-log.jsonl'
EXPORT = ART/'publish'
PANEL = os.getenv('ROYA_PANEL_URL','https://www.royablog.ir').rstrip('/')
BLOG = os.getenv('ROYA_BLOG_URL','https://afp.royablog.ir').rstrip('/')
POSTS_URL = PANEL+'/User/Posts/'
ADD_URL = PANEL+'/User/AddPost/'
LIMIT = max(1,int(os.getenv('ROYA_PUBLISH_LIMIT','30')))
DO_PUBLISH = os.getenv('ROYA_PUBLISH','0') == '1'
DELAY = max(0,float(os.getenv('ROYA_DELAY_SECONDS','10')))
def now(): return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def load(path,default):
    p=Path(path)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default

def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding='utf-8');tmp.replace(path)

def resolve_item(entry):
    return ART/'items'/Path(entry.get('item_file','')).name

def export_post(item):
    EXPORT.mkdir(parents=True,exist_ok=True)
    safe=re.sub(r'[^A-Za-z0-9._-]+','_',item['key'])
    post=item['post'];(EXPORT/(safe+'.html')).write_text(post['html'],encoding='utf-8')
    save(EXPORT/(safe+'.json'),{'key':item['key'],**post})

def checkpoint(entry,item,row):
    queue=load(QUEUE,{'items':[]})
    updates={'published':True,'published_url':row['url'],'published_at':row['at'],'pid':row['pid'],'status':'published'}
    for record in queue['items']:
        if record['key']==entry['key']:record.update(updates)
    save(QUEUE,queue);item.update(updates);save(resolve_item(entry),item)
    state=load(STATE,{})
    rows={r['key']:r for r in state.get('published',[])}
    rows[entry['key']]={k:row[k] for k in ('key','pid','url','at')}
    state['published']=list(rows.values());state['last_publish_run']=now();state['updated_at']=now();save(STATE,state)
    pq=load(PUBLISH_QUEUE,{'items':[]});pq['items']=[e for e in pq['items'] if e['key']!=entry['key']];pq['count']=len(pq['items']);save(PUBLISH_QUEUE,pq)
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')

def scan_panel(page):
    found={};pending=[POSTS_URL];seen=set()
    while pending:
        url=pending.pop(0)
        if url in seen:continue
        if len(seen)>=100:raise RuntimeError('Panel pagination limit exceeded')
        seen.add(url);page.goto(url,wait_until='domcontentloaded',timeout=90000)
        if '/SignIn/' in page.url:raise RuntimeError('Roya login session is not active')
        page.wait_for_selector('table.poststable',timeout=30000)
        rows=page.eval_on_selector_all('table.poststable tbody tr',r"""rows=>rows.map(r=>({title:(r.querySelector('.tdtitle')?.innerText||'').trim(),pid:(r.querySelector('a.actionedit')?.href||'').match(/EditPosts\/(\d+)/)?.[1]}))""")
        for r in rows:
            if r['pid'] and r['title']:found[r['title']]=int(r['pid'])
        links=page.eval_on_selector_all('a[href]','a=>a.map(e=>e.href)')
        for link in links:
            if urlsplit(link).netloc==urlsplit(PANEL).netloc and urlsplit(link).path.rstrip('/')=='/User/Posts' and link not in seen and link not in pending:pending.append(link)
    return found

def login(page):
    page.goto(POSTS_URL,wait_until='domcontentloaded',timeout=90000)
    if '/SignIn/' not in page.url:return
    user,password=os.getenv('ROYA_USERNAME',''),os.getenv('ROYA_PASSWORD','')
    if not user or not password:raise RuntimeError('ROYA_USERNAME and ROYA_PASSWORD repository secrets are required')
    page.fill('#username',user);page.fill('#password',password)
    # Remember-me, when this particular site visibly offers it.
    for label in ('مرا به خاطر بسپار','Remember me','Keep me signed in'):
        cb=page.get_by_label(label,exact=True)
        if cb.count() and cb.first.is_visible():cb.first.check()
    # Do not wait for every ad/third-party resource to finish loading.
    # Submit once, then verify access to the protected post table.
    navigation_error = False
    try:
        with page.expect_navigation(wait_until='domcontentloaded', timeout=30000):
            page.click('#login')
    except Exception as exc:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        if not isinstance(exc, PlaywrightTimeoutError):
            raise
        navigation_error = True
    if '/SignIn/' in page.url:
        # Classify visible feedback without logging page text or credentials.
        text = page.inner_text('body')
        if any(s in text for s in ('نام كاربري وارد شده معتبر', 'نام کاربری وارد شده معتبر')):
            raise RuntimeError('Roya login: username rejected by site format validation; check ROYA_USERNAME')
        if any(s in text for s in ('نام کاربری وارد نشده', 'رمز ورود وارد نشده')):
            raise RuntimeError('Roya login: site reports an empty login field')
        if any(s in text for s in ('اشتباه', 'نادرست', 'نامعتبر', 'صحیح نمی', 'معتبر نمی', 'معتبر نمي')):
            raise RuntimeError('Roya login: site rejected supplied credentials; check repository login secrets')
        if navigation_error:
            raise RuntimeError('Roya login: form did not navigate within 30 seconds; no second submission attempted')
        raise RuntimeError('Roya login: submitted form returned to SignIn without an authenticated session')
    page.goto(POSTS_URL,wait_until='domcontentloaded',timeout=90000)
    if '/SignIn/' in page.url:
        raise RuntimeError('Roya login: protected posts page redirected to SignIn')
    page.wait_for_selector('table.poststable',timeout=30000)
    print('Unattended Roya login verified against protected posts table',flush=True)

def verify_live(page,item,pid):
    post=item['post'];slug=(post.get('slug') or '').strip('-')[:60]
    url=f'{BLOG}/post/{pid}/{slug}/' if slug else f'{BLOG}/post/{pid}/'
    response=page.goto(url,wait_until='domcontentloaded',timeout=90000)
    if not response or response.status>=400:raise RuntimeError('Published URL returned an error')
    content=page.content()
    if post['title'].strip()[:25] not in page.inner_text('body'):raise RuntimeError('Published page title did not verify')
    # Verify the city backlink, not a success response alone.
    target=item.get('target_url')
    if target and target not in page.eval_on_selector_all('a[href]','a=>a.map(e=>e.href)'):
        from urllib.parse import unquote
        links=page.eval_on_selector_all('a[href]','a=>a.map(e=>e.href)')
        if unquote(target) not in [unquote(v) for v in links]:raise RuntimeError('City backlink did not verify')
    return url

def publish(todo):
    from playwright.sync_api import sync_playwright
    attached=bool(os.getenv('AGENT_BROWSER_CDP'));completed=0
    with sync_playwright() as pw:
        if attached:
            browser=pw.chromium.connect_over_cdp(os.environ['AGENT_BROWSER_CDP']);ctx=browser.contexts[0]
        else:
            browser=pw.chromium.launch(args=['--no-sandbox']);ctx=browser.new_context(locale='fa-IR',viewport={'width':1440,'height':900})
        page=ctx.new_page();page.on('dialog',lambda d:d.accept())
        try:
            login(page);existing=scan_panel(page)
            for n,entry in enumerate(todo,1):
                item=load(resolve_item(entry),{});post=item['post'];title=post['title'].strip();pid=existing.get(title)
                recovered=bool(pid)
                if not pid:
                    page.goto(ADD_URL,wait_until='domcontentloaded',timeout=90000)
                    if '/SignIn/' in page.url:raise RuntimeError('Roya login expired; refusing a blind retry')
                    page.wait_for_selector('#ptitle',timeout=30000)
                    page.wait_for_function("()=>window.tinymce && tinymce.get('pshort') && tinymce.get('pshort').parser && tinymce.get('pshort').getBody()",timeout=45000)
                    page.fill('#ptitle',title);page.fill('#plink',(post.get('slug') or '')[:60].strip('-'))
                    page.evaluate("""post=>{
                      const tags=(post.tags||[]).join(',');for(const id of ['keyword','kw']){const e=document.getElementById(id);if(e)e.value=tags;}
                      const pub=document.querySelector('input[name=ppublic][value="1"]');if(!pub)throw Error('Publish option missing');pub.checked=true;
                      if(window.tinymce&&tinymce.get('pshort')){tinymce.get('pshort').setContent(post.html);tinymce.triggerSave();}
                      else document.querySelector('#pshort').value=post.html;
                    }""",post)
                    # Native form submit is the only endpoint confirmed to persist posts.
                    with page.expect_navigation(timeout=90000):
                        page.evaluate("()=>window.jQuery?window.jQuery('.npost').submit():document.querySelector('form.npost').submit()")
                    if '/User/Posts/' not in page.url:page.goto(POSTS_URL,wait_until='domcontentloaded',timeout=90000)
                    page.wait_for_selector('table.poststable',timeout=30000)
                    pid=page.evaluate(r"""title=>{const row=[...document.querySelectorAll('table.poststable tbody tr')].find(r=>(r.querySelector('.tdtitle')?.innerText||'').trim()===title);return(row?.querySelector('a.actionedit')?.href||'').match(/EditPosts\/(\d+)/)?.[1]||null;}""",title)
                    if not pid:pid=scan_panel(page).get(title)
                    if not pid:raise RuntimeError('Post was not found after native submit; stop and reconcile before any retry')
                    pid=int(pid);existing[title]=pid
                url=verify_live(page,item,pid)
                row={'key':entry['key'],'title':title,'pid':pid,'url':url,'at':now(),'verified':True,'recovered_existing':recovered}
                checkpoint(entry,item,row);completed+=1;print(f'[{n}/{len(todo)}] verified {item.get("city_fa","")} pid={pid} -> {url}',flush=True)
                if n<len(todo) and DELAY:time.sleep(DELAY)
        finally:
            page.close()
            if not attached:browser.close()
    return completed

def main():
    if os.getenv('ROYA_DRAFT','0')=='1':raise RuntimeError('This queue publisher is configured for public publication, not drafts')
    pq=load(PUBLISH_QUEUE,{'items':[]});queue=load(QUEUE,{'items':[]});state=load(STATE,{})
    known={i['key'] for i in queue['items'] if i.get('published')}
    known.update(r['key'] for r in state.get('published',[]))
    todo=[]
    for e in pq['items']:
        if e['key'] in known:continue
        p=resolve_item(e)
        if not p.exists():raise RuntimeError('Ready artifact missing: '+p.name)
        i=load(p,{});post=i.get('post',{})
        if i.get('key')!=e['key'] or not post.get('title') or not post.get('html'):raise RuntimeError('Ready artifact is incomplete')
        if not i.get('qa',{}).get('passed',False):raise RuntimeError('Ready artifact has not passed QA: '+e['key'])
        todo.append(e)
    todo=todo[:LIMIT]
    if not todo:
        if DO_PUBLISH and os.getenv('ROYA_VERIFY_LOGIN','0') == '1':
            publish([]);print('Unattended Roya login verified; nothing ready to publish')
        else:print('nothing ready to publish')
        return 0
    for e in todo:export_post(load(resolve_item(e),{}))
    if not DO_PUBLISH:print(f'exported {len(todo)} posts; publication disabled explicitly');return 0
    if not os.getenv('AGENT_BROWSER_CDP') and not(os.getenv('ROYA_USERNAME') and os.getenv('ROYA_PASSWORD')):
        raise RuntimeError('ROYA_USERNAME and ROYA_PASSWORD secrets are missing; publication cannot run unattended')
    count=publish(todo);print(f'published and verified {count}; remaining {load(PUBLISH_QUEUE,{"count":0})["count"]}',flush=True);return 0
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:print('PUBLISH FAILED: '+str(exc),file=sys.stderr,flush=True);sys.exit(1)
