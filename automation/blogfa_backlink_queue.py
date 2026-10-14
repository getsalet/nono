#!/usr/bin/env python3
"""Independent Blogfa queue; only source geography is shared, never prose."""
import os,sys
for suffix in ('COUNT','TARGET','DRY_RUN','PUBLISH','PUBLISH_LIMIT'):
 if 'BLOGFA_'+suffix in os.environ:os.environ['FARSIBLOG_'+suffix]=os.environ['BLOGFA_'+suffix]
import farsiblog_backlink_queue as engine
engine.CITY_BLOG='blogfa';engine.BLOG='https://afp-pipe.blogfa.com'
engine.QUEUE=engine.ROOT/'data/blogfa/backlink-queue.json';engine.ART=engine.ROOT/'artifacts/blogfa-backlink-queue';engine.STATE=engine.ROOT/'state/blogfa-backlink-progress.json'
if __name__=='__main__':
 try:sys.exit(engine.main())
 except Exception as exc:print('Blogfa generation stopped: '+str(exc),file=sys.stderr);sys.exit(1)
