"""Use the standard Persian technical term before QA; never relax readback."""
import copy,re
TERM=re.compile(r'نرمال[\u200c ]کننده فشار')
def normalize(post):
 result=copy.deepcopy(post)
 if not isinstance(result,dict) or not isinstance(result.get('html'),str):return result
 # Only prose text nodes, never URLs, tags or attributes.
 pieces=re.split(r'(<[^>]*>)',result['html'])
 for i in range(0,len(pieces),2):pieces[i]=TERM.sub('تنظیم‌کننده فشار',pieces[i])
 result['html']=''.join(pieces)
 return result

def errors(post):
 body=post.get('html','')if isinstance(post,dict)else''
 prose=' '.join(re.split(r'<[^>]*>',body))
 return ['Use standard Persian pressure-regulator wording before publication']if TERM.search(prose)else[]
