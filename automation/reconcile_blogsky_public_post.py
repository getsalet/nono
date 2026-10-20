#!/usr/bin/env python3
"""Explicit read-only public verification of one uncertain Blogsky submission.
Never log in, fill a form, submit, delete a journal, or regenerate content.
"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def reconcile(page,key,url,root=ROOT):
    from publish_blogsky_posts import KEY,gate,read,checkpoint
    from city_backlink_policy import links_for,qa
    from blogsky_native import public_url,public_readback,verify
    gate(root)
    if not KEY.fullmatch(key) or not public_url(url):raise RuntimeError('Exact existing key and observed public URL required')
    queue=read(root/'data/blogsky/backlink-queue.json',{'items':[]})
    rows=[x for x in queue['items'] if x['key']==key]
    record=read(root/f'artifacts/blogsky-backlink-queue/items/{key}.json',{})
    journal=read(root/f'artifacts/blogsky-backlink-queue/native-publications/{key}.json',{})
    if len(rows)!=1 or journal.get('key')!=key or journal.get('phase') not in ('submitting','submitted_unverified','verified'):
        raise RuntimeError('Existing uncertain or verified native journal required')
    item={**record,**rows[0]};post=record.get('post',{})
    if record.get('key')!=key or record.get('target_url')!=rows[0].get('target_url') or journal.get('title')!=post.get('title') or not url.endswith('/'+post.get('slug','!')):
        raise RuntimeError('Public reconciliation binding mismatch')
    errors,_=qa(item,post,links_for(item),'blogsky',root)
    if errors:raise RuntimeError('Public reconciliation raw QA failed')
    page.goto(url,wait_until='domcontentloaded',timeout=60000)
    result=public_readback(page);verify(result,post,links_for(item),item.get('image_url'))
    if rows[0].get('published'):
        if rows[0].get('published_url')!=url or journal.get('phase')!='verified':raise RuntimeError('Conflicting published checkpoint')
        return False
    checkpoint(root,queue,item,post,result,journal)
    return True

def main():
    if len(sys.argv)!=3:raise RuntimeError('Exact key and observed URL required')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page()
            changed=reconcile(page,sys.argv[1],sys.argv[2])
        finally:browser.close()
    print('Existing public Blogsky article verified and checkpointed: '+str(changed)+'; submissions: 0')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Read-only Blogsky reconciliation stopped: '+type(exc).__name__+'; no submission or retry.',file=sys.stderr)
        raise SystemExit(1)
