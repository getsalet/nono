#!/usr/bin/env python3
"""Persist operator-observed native/public proof. Never connects to a blog."""
import hashlib,json
from pathlib import Path
import publish_loxblog_posts as p
ROOT=Path(__file__).resolve().parent.parent
proof=json.loads((ROOT/'data/loxblog-post56-observed-proof.json').read_text())
key='city-2c396c586e4fb71a'
assert proof['key']==key and proof['pid']==56 and proof['url']=='https://afp.lxb.ir/post/56'
assert proof['passed'] and proof['native_status_published'] and proof['native_title_verified']
assert proof['full_body_links_image_faqs_verified'] and proof['used_existing_user_browser_session']
assert proof['new_submissions']==0 and proof['mode']=='existing_post_only'
entry={'key':key,'item_file':key+'.json'}
item=p.state.load(p.state.resolve_item(entry),{})
assert item['post']['title']==proof['title']
assert hashlib.sha256(json.dumps(item['post'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()==proof['approved_post_sha256']
journal=p.engine.load(p.engine.ART/'submission-attempts.json',{})
phase=journal.get(key,{}).get('phase')
assert phase in ('submitting','unconfirmed','verified'), phase
if phase!='verified':
 row={k:proof[k] for k in ('key','title','pid','url','at')}
 row.update(verified=True,recovered_existing=True,verification_source='user_authenticated_browser_native_and_public')
 p.state.checkpoint(entry,item,row)
 p.journal(entry,'verified')
p.engine.save(p.engine.ART/'existing-receipt-recovery.json',proof)
assert not any(x['key']==key for x in p.state.load(p.state.PUBLISH_QUEUE,{}).get('items',[]))
print('Existing post 56 receipt verified; no browser, credentials, or post submission used.')
