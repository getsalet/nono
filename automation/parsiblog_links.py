"""Application-owned contextual links, before strict QA and editorial review.

No arbitrary URL is repaired into an approved URL. Only approved destinations
and the existing controlled tokens are accepted; unknown URLs remain errors.
"""
from bs4 import BeautifulSoup, NavigableString
from parsiblog_policy import links_for,urlkey,normalized_title,resolve_link_tokens
import roya_backlink_queue as common

def render_contextual_links(item,obj):
 if not isinstance(obj,dict)or not isinstance(obj.get('html'),str):
  return ['Link renderer requires a JSON object with HTML text'],{}
 links=links_for(item)
 resolve_link_tokens(obj,links);common.normalize_approved_hrefs(obj,links)
 soup=BeautifulSoup(obj['html'],'html.parser')
 approved={urlkey(x['url'])for x in links}
 if any(urlkey(a.get('href',''))not in approved for a in soup.find_all('a')):
  return ['Unapproved link destination; no automatic URL substitution'],{}
 # Preserve visible prose; the renderer alone owns the three actual anchors.
 for a in list(soup.find_all('a')):a.unwrap()
 faq=next((h for h in soup.find_all('h2')if normalized_title(h.get_text(' ',strip=True))in ('پرسش های متداول','سوالات متداول','سؤالات متداول')),None)
 if faq is None:return ['Final FAQ heading required before link rendering'],{}
 body=[]
 for node in soup.find_all(['p','h2']):
  if node is faq:break
  if node.name=='p' and node.get_text(' ',strip=True)and not node.find('img'):body.append(node)
 if len(body)<3:return ['Three distinct body paragraphs required for contextual links'],{}
 used=set();placements=[]
 fallback={
  'home':('برای آشنایی با گروه محصول، صفحه ',' را مطالعه کنید.'),
  'city':('در کنار بررسی اطلاعات زمین، ',' را نیز مرور کنید.'),
  'category':('برای مقایسه گزینه‌های محصول، ',' را مطالعه کنید.')}
 for link in links:
  candidates=[p for p in body if id(p)not in used]
  para=next((p for p in candidates if any(link['anchor']in str(n)for n in p.descendants if isinstance(n,NavigableString))),candidates[0])
  anchor=soup.new_tag('a',href=link['url']);anchor.string=link['anchor']
  node=next((n for n in para.descendants if isinstance(n,NavigableString)and link['anchor']in str(n)),None)
  if node is not None:
   before,after=str(node).split(link['anchor'],1);node.replace_with(NavigableString(before),anchor,NavigableString(after));placement='existing phrase'
  else:
   prefix,suffix=fallback[link['role']];para.append(NavigableString(' '+prefix));para.append(anchor);para.append(NavigableString(suffix));placement='contextual reading sentence'
  used.add(id(para));placements.append({'role':link['role'],'paragraph_index':body.index(para),'placement':placement})
 obj['html']=str(soup)
 return [],{'policy':'application-owned-three-links-v1','placements':placements,'link_count':len(soup.find_all('a'))}
