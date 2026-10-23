"""Bounded GET-only archive navigation. No login, form or submission code."""
import time
from urllib.parse import urlsplit
HOST="afp.lxb.ir"

def read_archive_page(page,url):
 # Retry only a read-only navigation, never a credential request or native save.
 # Exhaustion still blocks publication: an incomplete archive is not dedup proof.
 for attempt in range(3):
  try:
   response=page.goto(url,wait_until='domcontentloaded',timeout=60000)
  except Exception as exc:
   if attempt==2:raise RuntimeError('Public archive unavailable after bounded read retries; refuse partial dedup')from exc
   time.sleep(2*(attempt+1));continue
  if urlsplit(page.url).hostname!=HOST:raise RuntimeError('Public archive changed host; refuse partial dedup')
  if response and response.status<400:return response
  status=response.status if response else None
  if status is not None and status not in (408,429)and status<500:raise RuntimeError('Public archive unavailable; refuse partial dedup')
  if attempt==2:raise RuntimeError('Public archive unavailable after bounded read retries; refuse partial dedup')
  time.sleep(2*(attempt+1))
 raise RuntimeError('Public archive unavailable; refuse partial dedup')

