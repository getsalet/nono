"""Explicit versioned scheduler approval; never bypasses native/content/budget gates."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ACTIVE=('farsiblog','rozblog','loxblog')
def enabled(blog,root=ROOT):
 from check_blog_pipeline_control import decision
 if blog not in ACTIVE or not decision(blog,root)['proceed']:return False
 try:
  c=json.loads((Path(root)/'data/blog-automation-control.json').read_text())
  return c.get('policy')=='explicit-blog-scheduler-v1' and c.get('enabled',{}).get(blog)is True
 except (OSError,ValueError,TypeError,AttributeError):return False
