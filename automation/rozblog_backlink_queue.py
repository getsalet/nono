#!/usr/bin/env python3
"""Independent RozBlog city articles using the shared validated pipeline."""
import os,sys
for suffix in ('COUNT','TARGET','DRY_RUN','PUBLISH','PUBLISH_LIMIT'):
 if 'ROZBLOG_'+suffix in os.environ:os.environ['FARSIBLOG_'+suffix]=os.environ['ROZBLOG_'+suffix]
import farsiblog_backlink_queue as engine
engine.CITY_BLOG='rozblog';engine.BLOG='https://drip-irrigation.rozblog.com'
engine.QUEUE=engine.ROOT/'data/rozblog/backlink-queue.json';engine.ART=engine.ROOT/'artifacts/rozblog-backlink-queue';engine.STATE=engine.ROOT/'state/rozblog-backlink-progress.json'
if __name__=='__main__':
 try:sys.exit(engine.main())
 except Exception as exc:print('RozBlog generation stopped: '+str(exc),file=sys.stderr);sys.exit(1)
