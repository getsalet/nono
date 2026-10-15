#!/usr/bin/env python3
"""Independent LoxBlog articles; share source metadata, never article prose."""
import os,sys
for suffix in ('COUNT','TARGET','DRY_RUN','PUBLISH','PUBLISH_LIMIT'):
 if 'LOXBLOG_'+suffix in os.environ:os.environ['FARSIBLOG_'+suffix]=os.environ['LOXBLOG_'+suffix]
import farsiblog_backlink_queue as engine
engine.CITY_BLOG='loxblog';engine.BLOG='https://afp.lxb.ir'
engine.QUEUE=engine.ROOT/'data/loxblog/backlink-queue.json';engine.ART=engine.ROOT/'artifacts/loxblog-backlink-queue';engine.STATE=engine.ROOT/'state/loxblog-backlink-progress.json'
def main():
 code=engine.main()
 status=engine.ART/'status.md'
 if status.exists():status.write_text(status.read_text().replace('فارسی‌بلاگ AFP','لوکس‌بلاگ AFP').replace('بین سه وبلاگ','بین پنج وبلاگ'))
 return code
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('LoxBlog generation stopped: '+str(exc),file=sys.stderr);sys.exit(1)
