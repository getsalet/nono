"""Offline media planning helper. NOT a publisher or enabled workflow.
The future adapter must hold a single-writer lock across load/reserve/save,
persist returned states atomically, and call acknowledge only after independent
public-page verification. An ambiguous publish result retains its reservation
until reconciled; never retry publication merely because a receipt was lost.
"""
import copy
import hashlib
from urllib.parse import urlsplit
BASE='https://navar-abyari.ir/wp-content/uploads/2026/09/drip-tape/'

def validate_catalog(catalog):
    assets=catalog.get('assets',[])
    if not assets or len({a['id'] for a in assets})!=len(assets):
        raise ValueError('Empty catalog or duplicate IDs')
    for a in assets:
        u=urlsplit(a['url'])
        if (not a['url'].startswith(BASE) or u.query or u.fragment or u.username
                or u.port or a['kind'] not in ('image','video')):
            raise ValueError('Unsafe media URL/type')
        if a.get('eligible_for_selection'):
            if not a.get('verified'): raise ValueError('Unverified asset')
            if a['kind']=='image' and not (a.get('format')=='WEBP' and a.get('public_sha256_verified')):
                raise ValueError('WebP public integrity verification required')
            if a['kind']=='video' and not a.get('metadata_verified'):
                raise ValueError('Video metadata not verified')
    if not any(a['kind']=='image' and a.get('eligible_for_selection') for a in assets):
        raise ValueError('No usable image')

def reserve(catalog,state,post_id,video_probability=0.0):
    """Return (new_state, selection). Same post is idempotent; no publishing."""
    validate_catalog(catalog)
    if not isinstance(post_id,str) or not post_id.strip(): raise ValueError('Post ID required')
    if not 0<=video_probability<=1: raise ValueError('Invalid video probability')
    s=copy.deepcopy(state or {'next_image':0,'published':{},'pending':None})
    if post_id in s['published']: return s,copy.deepcopy(s['published'][post_id]['selection'])
    if s.get('pending'):
        if s['pending']['post_id']!=post_id: raise ValueError('Reconcile pending post first')
        return s,copy.deepcopy(s['pending']['selection'])
    images=sorted((a for a in catalog['assets'] if a['kind']=='image' and a.get('eligible_for_selection')),key=lambda a:a['id'])
    videos=sorted((a for a in catalog['assets'] if a['kind']=='video' and a.get('eligible_for_selection')),key=lambda a:a['id'])
    h=hashlib.sha256(('niloblog-media-v1:'+post_id).encode()).digest()
    selection={'image_id':images[s['next_image']%len(images)]['id'],'video_id':None}
    if videos and int.from_bytes(h[:8],'big')/2**64<video_probability:
        selection['video_id']=videos[int.from_bytes(h[8:16],'big')%len(videos)]['id']
    s['pending']={'post_id':post_id,'selection':selection}
    return s,copy.deepcopy(selection)

def acknowledge(catalog,state,post_id,public_url,*,public_receipt_verified=False):
    """Adapter-only acknowledgement; this helper does NOT verify remote pages."""
    validate_catalog(catalog)
    u=urlsplit(public_url)
    if not public_receipt_verified or u.scheme!='https' or u.hostname!='afp.niloblog.com' or u.username or u.port or u.path in ('','/'):
        raise ValueError('Independently verified public post receipt required')
    s=copy.deepcopy(state)
    if post_id in s['published']: return s
    if not s.get('pending') or s['pending']['post_id']!=post_id: raise ValueError('No matching reservation')
    s['published'][post_id]={'selection':s['pending']['selection'],'receipt':public_url}
    s['pending']=None;s['next_image']+=1
    return s
