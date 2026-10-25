"""Lifetime-bounded recovery of staged work after transient provider failure.
Original cycle counters and output bytes are never reset. Quality/auth/quota
failures do not receive an automatic recovery allowance.
"""
from .queue import load_json,atomic_json,utcnow
MAX_RECOVERY_CYCLES=4
TRANSIENT={'provider_unavailable','network_or_timeout','rate_limited'}

def eligible(folder):
 state_path=folder/'state.json'
 if not state_path.exists() or not (folder/'article.json').exists():return False
 state=load_json(state_path);failure=state.get('failure',{})
 staged=(state.get('status')=='draft_created' and (folder/'wordpress-draft-payload.json').exists() and all((folder/f'image-{n}.webp').exists() for n in (1,2)))
 if not staged and state.get('status')!='incomplete':return False
 if not staged and failure.get('kind') not in {'image_provider','text_provider','image_admission'}:return False
 if not staged and failure.get('category') not in TRANSIENT|{'admission_deferred'}:return False
 rp=folder/'production-recovery.json';row=load_json(rp) if rp.exists() else {}
 return row.get('cycles_started',0)<MAX_RECOVERY_CYCLES

def reserve(folder):
 if not eligible(folder):raise ValueError('Staged provider recovery is not eligible')
 rp=folder/'production-recovery.json';row=load_json(rp) if rp.exists() else {'cycles_started':0,'history':[]}
 row['cycles_started']+=1
 row.update(status='reserved',reserved_at=utcnow(),max_cycles=MAX_RECOVERY_CYCLES,original_attempts_reset=False)
 row['history'].append({'cycle':row['cycles_started'],'started_at':row['reserved_at']})
 atomic_json(rp,row)
 return row

def finish(folder,status,failure=None):
 rp=folder/'production-recovery.json'
 if not rp.exists():return
 row=load_json(rp);row.update(status=status,completed_at=utcnow())
 if failure is not None:row['last_failure']=failure
 atomic_json(rp,row)
