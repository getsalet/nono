"""Enroll evidence-safe Blogsky title variants; never generate or publish content."""
import hashlib
import json
from pathlib import Path

CONTROL = 'data/blogsky/title-inventory-control.json'

def expand(queue, root):
    root = Path(root)
    path = root / CONTROL
    if not path.exists():
        return queue
    cfg = json.loads(path.read_text())
    if cfg.get('enabled') is not True:
        return queue
    if cfg.get('total_titles') != 1500 or cfg.get('family') != 'tape20':
        raise RuntimeError('Invalid Blogsky title inventory control')
    from city_backlink_policy import title_candidates
    from blog_city_editorial import title_errors
    from blog_generated_image import family_enabled
    from blog_city_priority import ordered
    rows = queue['items']
    active = [r for r in rows if r.get('kind') == 'city' and r.get('family') == 'tape20' and family_enabled(r, root)]
    goal = cfg['total_titles']
    if len(active) > goal:
        raise RuntimeError('Inventory already exceeds requested count; never delete records')
    bases = ordered([r for r in active if not r.get('inventory_parent_key')], root)
    used = {r.get('title') if r.get('published') else r.get('assigned_title') for r in active}
    used.discard(None)
    keys = {r['key'] for r in rows}
    additions = []
    # Breadth-first variants. Keep existing work untouched and distinct technical
    # questions per destination; no invented city or crop and no prose cloning.
    for variant in range(1, 17):
        for base in bases:
            if len(active) + len(additions) >= goal:
                break
            key = 'city-' + hashlib.sha256((base['key'] + '|blogsky-title-' + str(variant)).encode()).hexdigest()[:16]
            if key in keys:
                continue
            item = {k: base.get(k, '') for k in ('city_fa','province_fa','family','target_url','hub_url','site_title','source_key','reference_url','topic')}
            item.update(key=key, kind='city', status='pending', inventory_parent_key=base['key'], inventory_variant=variant)
            title = next((t for t in title_candidates(item, 'blogsky', root) if t not in used and not title_errors(item, t, root)), None)
            if not title:
                continue
            item.update(assigned_title=title, angle='پاسخ مستقل و مستند به مسئله فنی همین عنوان: ' + title.split('؛')[-1].strip())
            additions.append(item)
            keys.add(key)
            used.add(title)
        if len(active) + len(additions) >= goal:
            break
    if len(active) + len(additions) != goal:
        raise RuntimeError('Insufficient distinct safe titles; no padding allowed')
    rows.extend(additions)
    queue['title_inventory_policy'] = 'blogsky-1500-evidence-safe-v1'
    return queue
