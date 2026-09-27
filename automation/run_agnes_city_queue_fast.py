#!/usr/bin/env python3
"""Run the resilient queue while preserving failures for explicit repair."""
import json,os,runpy
from pathlib import Path
import city_content_queue as base
HERE=Path(__file__).resolve().parent
base.MAX_ATTEMPTS=max(1,int(os.getenv('MAX_ATTEMPTS','4')))
IMAGE_RETRY_POLICY='retry-after-v13-isolated-technical-role-fix'

# Same-group workflow concurrency means any committed processing item belongs to
# an interrupted earlier run. Return it to pending without consuming an attempt.
if base.QUEUE.exists():
    state=json.loads(base.QUEUE.read_text(encoding='utf-8'));recovered=0;repairable=0
    # Reserve most of every parallel batch for fresh pending work. Retrying all
    # quarantined failures at once previously consumed all three worker slots
    # and made successful progress appear frozen.
    repair_limit=max(0,int(os.getenv('REPAIR_FAILED_LIMIT','1')))
    repaired_signals=('unexpected Latin words: AFP','PVC claim for irrigation tape','image hard gate rejected role','Image-set diversity gate rejected')
    for item in state.get('items',[]):
        if item.get('status')=='processing':
            item['status']='pending';item['attempts']=max(0,int(item.get('attempts',0))-1)
            item.pop('started_at',None);item['last_error']='Recovered after interrupted workflow';recovered+=1
        elif (item.get('status')=='failed' and any(x in item.get('last_error','') for x in repaired_signals)
              and item.get('retry_policy')!=IMAGE_RETRY_POLICY and repairable<repair_limit):
            item['status']='pending';item['attempts']=0;item['retry_policy']=IMAGE_RETRY_POLICY
            item.pop('failed_at',None);item.pop('started_at',None);repairable+=1
    if recovered or repairable:
        state['updated_at']=base.now();base.QUEUE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'recovered_processing_items={recovered} repairable_failures_reset={repairable}',flush=True)

if os.getenv('RETRY_FAILED','0')=='1':
    try:
        import keep_failed_in_queue
        reset_count=keep_failed_in_queue.reset_failed_for_retry(base.QUEUE)
        print(f'retry_failed_reset={reset_count}',flush=True)
    except Exception as exc:
        print(f'keep_failed_in_queue_warning={type(exc).__name__}: {exc}',flush=True)

runpy.run_path(str(HERE/'run_agnes_city_queue_resilient.py'),run_name='__main__')
