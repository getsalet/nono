"""Automatic Blogsky admission: 20-minute interval plus two posts per rolling hour."""
import datetime
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANUAL={'enabled':True,'mode':'manual_one_post','max_count_per_run':1,'schedule_enabled':False}
AUTOMATIC={'enabled':True,'mode':'automatic_one_post','max_count_per_run':1,'schedule_enabled':True,'min_interval_minutes':20}

def configuration(root=ROOT):
    return json.loads((Path(root)/'data/blogsky/native-publication-control.json').read_text())

def interval_open(root=ROOT,current=None):
    current=current or datetime.datetime.now(datetime.timezone.utc)
    if current.tzinfo is None:raise RuntimeError('Timezone-aware publication clock required')
    path=Path(root)/'state/blogsky-backlink-progress.json'
    state=json.loads(path.read_text()) if path.exists() else {}
    for row in state.get('published',[]):
        try:
            at=datetime.datetime.fromisoformat(row['at'].replace('Z','+00:00'))
            if at.tzinfo is None:raise ValueError()
        except (KeyError,ValueError,TypeError,AttributeError):
            raise RuntimeError('Invalid publication history; reconcile before automatic publishing') from None
        if at>current-datetime.timedelta(minutes=AUTOMATIC['min_interval_minutes']):return False
    from farsiblog_backlink_queue import remaining_publication_budget
    return remaining_publication_budget(path,current)>0

def preflight(root=ROOT):
    from publish_blogsky_posts import gate,pending
    gate(root)
    if configuration(root)!=AUTOMATIC:raise RuntimeError('Automatic publication is not enabled')
    pending(root)
    return interval_open(root)

def select_target(root=ROOT):
    from blog_city_priority import ordered
    from blog_generated_image import family_enabled
    if not preflight(root):return None
    path=Path(root)/'data/blogsky/backlink-queue.json'
    queue=json.loads(path.read_text()) if path.exists() else {'items':[]}
    rows=[x for x in queue['items'] if x.get('status')=='completed' and not x.get('published') and x.get('kind')=='city' and family_enabled(x,root)]
    rows=ordered(rows,root)
    return rows[0]['key'] if rows else None

def main():
    allowed=preflight()
    print('Blogsky automatic admission: '+('allowed; generation and QA still required' if allowed else '20-minute interval idle; no generation or publication'))
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('proceed='+('1' if allowed else '0')+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
