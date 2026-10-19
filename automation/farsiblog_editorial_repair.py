"""Narrow FAQ-link placement repair; never changes claims, adds links or approves QA."""
import copy,html,re
POLICY='approved-faq-link-sentence-relocation-v1'
ANCHOR=re.compile(r'<a\s+href=["\']([^"\']+)["\']\s*>([^<>]+)</a>',re.I)
def relocate(post,links):
 """Move an existing self-contained linked sentence to prose; keep FAQ answers.
 Refuse extra/unknown links, complex markup, short leftover answers or ambiguity.
 No sentence/anchor/destination is invented. Final full QA remains required.
 """
 if not isinstance(post,dict)or not isinstance(post.get('html'),str)or len(links)!=2:return None
 body=post['html'];anchors=list(ANCHOR.finditer(body))
 if len(anchors)!=2 or len(re.findall(r'<a\b',body,re.I))!=2:return None
 approved={x['url']:x['anchor']for x in links}
 if len(approved)!=2 or {html.unescape(a[1])for a in anchors}!=set(approved):return None
 if any(html.unescape(a[2])!=approved.get(html.unescape(a[1]))for a in anchors):return None
 details=list(re.finditer(r'<details\b[^>]*>.*?</details>',body,re.S|re.I))
 if len(details)!=3:return None
 moves=[];edits=[];slot='AFP_RELOCATION_SENTENCE_SLOT'
 if slot in body:return None
 for block in details:
  content=block[0]
  if not re.search(r'<a\b',content,re.I):continue
  paragraphs=list(re.finditer(r'<p>(.*?)</p>',content,re.S|re.I));local=[];handled=0
  for paragraph in paragraphs:
   text=paragraph[1];matches=list(ANCHOR.finditer(text))
   if not matches:continue
   if len(matches)!=1 or re.sub(ANCHOR,'',text).count('<'):return None
   a=matches[0];template=text[:a.start()]+slot+text[a.end():]
   sentences=re.split(r'(?<=[.!?؟])\s+',template.strip());moving=[s for s in sentences if slot in s];remaining=[s for s in sentences if slot not in s]
   if len(moving)!=1 or not moving[0].startswith(('برای انتخاب ','برای بررسی ','برای مشاهده ','برای مطالعه ')):return None
   rest=' '.join(remaining).strip()
   if len(html.unescape(rest).split())<12:return None
   moves.append('<p>'+moving[0].replace(slot,a[0])+'</p>');handled+=1
   local.append((paragraph.start(1),paragraph.end(1),rest))
  if handled!=len(re.findall(r'<a\b',content,re.I)):return None
  for first,last,replacement in reversed(local):content=content[:first]+replacement+content[last:]
  edits.append((block.start(),block.end(),content))
 if not moves:return None
 for first,last,replacement in reversed(edits):body=body[:first]+replacement+body[last:]
 at=re.search(r'<details\b',body,re.I).start();prefix=body[:at]
 heading=re.search(r'<h[23]\b[^>]*>[^<]*(?:پرسش|سؤال|سوال)[^<]*</h[23]>\s*$',prefix,re.I)
 if heading:at=heading.start()
 body=body[:at]+''.join(moves)+body[at:]
 result=copy.deepcopy(post);result['html']=body
 return result

def recover_saved(record,item,links,blog,root,validate=True):
 """One bounded recovery of this exact failed tape20 draft, not another model call."""
 if blog!='farsiblog'or item.get('family')!='tape20'or item.get('published')or item.get('faq_link_recovery_policy')==POLICY:return None
 if item.get('status')!='failed'or record.get('status')!='failed'or record.get('published'):return None
 if record.get('key')!=item.get('key')or record.get('target_url')!=item.get('target_url'):return None
 if record.get('failure_stage')not in ('text_validation','validation')or record.get('qa',{}).get('errors')!=['No promotional links in FAQs']:return None
 from blog_draft_preflight import clean,check
 post=record.get('post')
 if not isinstance(post,dict):return None
 result=relocate(clean(post),links)
 if result is None:return None
 if validate and check(item,result,blog,root,links):return None
 return result
