"""Explicit generation outcome; a green cooldown/idle run is not publication."""
import datetime,json,math,os
from pathlib import Path
BLOG_NAMES={'roya':'رویا','farsiblog':'فارسی‌بلاگ','rozblog':'روزبلاگ','blogfa':'بلاگفا','loxblog':'لوکس‌بلاگ'}
def outcome(completed,failed,retry_at=None,waiting=None):
 if completed:return 'partial_success' if failed else 'produced'
 if failed:return 'failed'
 if waiting:return 'waiting_image'
 if retry_at is not None:return 'waiting_provider'
 return 'idle'
def write(root,blog,completed,failed,retry_at=None,waiting=None):
 if blog not in BLOG_NAMES:raise ValueError('Known blog required')
 if retry_at is not None and (isinstance(retry_at,bool)or not isinstance(retry_at,(int,float))or not math.isfinite(retry_at)):raise ValueError('Valid cooldown timestamp required')
 status=outcome(completed,failed,retry_at,waiting)
 record={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blog':blog,'status':status,'completed_this_run':len(completed),'failed_this_run':len(failed),'waiting_image_this_run':len(waiting or []),'retry_at':datetime.datetime.fromtimestamp(retry_at,datetime.timezone.utc).isoformat() if retry_at is not None else None,'publication_verified_by_this_report':False,'note':'Generation outcome only. Waiting/idle success is not successful image generation or verified publication.'}
 path=Path(root)/'artifacts'/f'{blog}-backlink-queue/generation-status.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,ensure_ascii=False,indent=2))
 summary=os.getenv('GITHUB_STEP_SUMMARY')
 if summary:
  with open(summary,'a')as f:f.write(f'\n## {blog} generation: {status}\n\nCompleted this run: {len(completed)}. Failed this run: {len(failed)}. Retry after: {record["retry_at"] or "not set"}.\n\nWaiting or idle is not successful generation or verified publication.\n')
 return record
