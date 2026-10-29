"""Preserve source table cell boundaries; never infer rows from flattened text.
Only complete, simple tables covered verbatim by an admitted quote are exposed.
No extra source sections, inferred diagnosis or approval is introduced.
"""
import copy,re

def norm(value):return re.sub(r'\s+',' ',str(value).replace('ي','ی').replace('ك','ک').replace('\u200c',' ')).strip()

def extract_tables(main):
 result=[]
 for table in main.find_all('table')[:12]:
  if table.find('table')or table.select('[rowspan], [colspan]'):continue
  rows=[[norm(c.get_text(' ',strip=True))for c in row.find_all(['th','td'],recursive=False)]for row in table.find_all('tr')]
  if not 2<=len(rows)<=40 or not rows[0]or not 2<=len(rows[0])<=8 or any(len(r)!=len(rows[0])or any(not c or len(c)>2000 for c in r)for r in rows):continue
  text=norm(table.get_text(' ',strip=True))
  # Captions and other out-of-cell material cannot silently change pairings.
  if text!=norm(' '.join(c for r in rows for c in r)):continue
  result.append({'text':text,'rows':rows,'extraction':'literal_html_cells_v1','inferences_added':False})
 return result

def admitted_tables(source,quotes):
 result=[]
 for table in source.get('tables',[]):
  rows=table.get('rows');text=table.get('text')
  if not isinstance(rows,list)or not rows or any(not isinstance(r,list)or any(not isinstance(c,str)for c in r)for r in rows):raise ValueError('Invalid source table cells')
  if not isinstance(text,str)or text!=norm(' '.join(c for r in rows for c in r))or text not in norm(source['text']):raise ValueError('Source table not verifiable')
  if any(text in norm(q)for q in quotes):result.append(copy.deepcopy(table))
 return result
