"""Cheap preflight: respect explicit user pause before text/image API work."""
import json
from pathlib import Path
def generation_paused(root):
 path=Path(root)/'data/blog-generated-image-control.json'
 if not path.exists():return False
 try:control=json.loads(path.read_text())
 except (OSError,ValueError):raise RuntimeError('Image production control unreadable; no unchecked generation')from None
 if not isinstance(control,dict):raise RuntimeError('Image production control invalid; no unchecked generation')
 return control.get('pause_image_production')is True
