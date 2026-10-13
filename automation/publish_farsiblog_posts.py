#!/usr/bin/env python3
"""Native-form FarsiBlog publication with per-post checkpoints and revalidation."""
import os,sys
from pathlib import Path
from urllib.parse import unquote,urlsplit
import publish_roya_posts as native
import farsiblog_backlink_queue as generator
native.QUEUE=generator.QUEUE;native.ART=generator.ART;native.PUBLISH_QUEUE=native.ART/'publish-queue.json';native.STATE=generator.STATE;native.LOG=native.ART/'publish-log.jsonl';native.EXPORT=native.ART/'publish'
native.PANEL='https://www.farsiblog.com';native.BLOG=generator.BLOG;native.POSTS_URL=native.PANEL+'/User/Posts/';native.ADD_URL=native.PANEL+'/User/AddPost/'
native.LIMIT=max(1,min(3,int(os.getenv('FARSIBLOG_PUBLISH_LIMIT','1'))));native.DO_PUBLISH=os.getenv('FARSIBLOG_PUBLISH','0')=='1';native.DELAY=10

def active_blog(page):
    urls=page.locator('a[href]').evaluate_all('a=>a.map(x=>x.href).filter(x=>x.includes(".farsiblog.com")&&!x.includes("www.farsiblog.com"))')
    if 'afp.farsiblog.com'not in {urlsplit(x).hostname for x in urls}:raise RuntimeError('FarsiBlog active blog is not AFP; refusing another destination')
def login(page):
    page.goto(native.PANEL+'/UserPanel/afp/',wait_until='domcontentloaded',timeout=60000)
    if '/SignIn/'in page.url:
        u=os.getenv('FARSIBLOG_USERNAME','');p=os.getenv('FARSIBLOG_PASSWORD','')
        if not u or not p:raise RuntimeError('FarsiBlog login secrets required')
        page.fill('#username',u);page.fill('#password',p)
        for label in ('مرا به خاطر بسپار','Remember me','Keep me signed in'):
            c=page.get_by_label(label,exact=True)
            if c.count()and c.first.is_visible():c.first.check()
        try:
            with page.expect_navigation(wait_until='domcontentloaded',timeout=30000):page.click('#login')
        except Exception as exc:
            from playwright.sync_api import TimeoutError
            if not isinstance(exc,TimeoutError):raise
        page.goto(native.PANEL+'/UserPanel/afp/',wait_until='domcontentloaded',timeout=60000)
        if '/SignIn/'in page.url:raise RuntimeError('FarsiBlog sign-in failed; check secrets, no blind resubmission')
    page.goto(native.POSTS_URL,wait_until='domcontentloaded',timeout=60000);active_blog(page);page.wait_for_selector('table.poststable',timeout=30000)
    print('FarsiBlog protected post table and AFP blog verified',flush=True)
old_scan=native.scan_panel;old_verify=native.verify_live

def scan(page):
    found=old_scan(page);active_blog(page)
    for entry in native.load(native.PUBLISH_QUEUE,{'items':[]})['items']:
        item=native.load(native.resolve_item(entry),{});errors,_=generator.qa(item,item['post'],generator.links_for(item))
        if errors:raise RuntimeError('Publication revalidation failed: '+'; '.join(errors[:3]))
    return found

def verify(page,item,pid):
    url=old_verify(page,item,pid)
    if urlsplit(page.url).hostname!='afp.farsiblog.com':raise RuntimeError('Wrong public blog')
    article=page.locator('article.post-card').first
    if not article.count():raise RuntimeError('Published article block missing')
    links={unquote(x).rstrip('/')for x in article.locator('.post-content a[href]').evaluate_all('a=>a.map(x=>x.href)')}
    if any(unquote(x['url']).rstrip('/')not in links for x in generator.links_for(item)):raise RuntimeError('Published contextual link missing')
    if article.locator('.post-content details').count()!=3:raise RuntimeError('Published FAQ did not persist')
    return url
native.login=login;native.scan_panel=scan;native.verify_live=verify

def main():
    if native.DO_PUBLISH and not os.getenv('AGENT_BROWSER_CDP')and not(os.getenv('FARSIBLOG_USERNAME')and os.getenv('FARSIBLOG_PASSWORD')):raise RuntimeError('Set FARSIBLOG_USERNAME and FARSIBLOG_PASSWORD repository secrets')
    # The generic publisher guard uses these names; map only in process memory.
    os.environ['ROYA_USERNAME']=os.getenv('FARSIBLOG_USERNAME','');os.environ['ROYA_PASSWORD']=os.getenv('FARSIBLOG_PASSWORD','')
    return native.main()
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:print('FarsiBlog publication stopped: '+str(exc),file=sys.stderr);sys.exit(1)
