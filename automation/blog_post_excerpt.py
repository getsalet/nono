"""Split native before/after-Read-more fields without changing article HTML.

Roya renders the two fields together on a full article. The continuation must
therefore exclude the leading image and intro already stored in the summary.
"""
from html.parser import HTMLParser
import re
class _Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
 def handle_data(self,text):self.parts.append(text)
def native_split(body):
 for match in re.finditer(r'<p\b[^>]*>(.*?)</p\s*>',body,re.I|re.S):
  p=_Text();p.feed(match.group(1));text=re.sub(r'\s+',' ',' '.join(p.parts)).strip()
  if len(text)>60:
   prefix,continuation=body[:match.end()],body[match.end():]
   if not continuation.strip():raise ValueError('No continuation after article introduction; refuse full-body listing')
   if len(prefix)>len(body)*.65:raise ValueError('Introduction is not a short excerpt; refuse full-body listing')
   return prefix,continuation
 raise ValueError('A real introductory paragraph is required')
def native_bodies(body,panel):
 if panel.rstrip('/')=='https://www.royablog.ir':return native_split(body)
 return body,''
