#!/usr/bin/env python3
"""Probe the 25 explicitly named existing Agnes secrets inside GitHub Actions.
No secret values, fingerprints, prompts, responses or exception text are saved.
This audit makes tiny text requests; image capability is explicitly NOT inferred.
"""
import concurrent.futures,datetime,json,os,socket,time,urllib.error,urllib.request
from pathlib import Path
NAMES=['AGNES_API_KEY',*[f'AGNES_API_KEY{i}'for i in range(2,26)]]
ENDPOINT='https://apihub.agnes-ai.com/v1/chat/completions'
MODEL='agnes-2.5-flash'
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'data/agnes-key-health/latest.json'

def classify_http(code):
 return {401:'authentication_rejected',402:'billing_or_credit_required',403:'access_denied',404:'model_or_route_unavailable',408:'request_timeout',429:'rate_limited_or_quota',500:'provider_error',502:'provider_error',503:'provider_unavailable',504:'provider_timeout'}.get(code,'http_error')

def probe(key):
 result={'status':'not_tested','attempts':0,'image_capability':'not_tested'}
 for attempt in range(1,3):
  result['attempts']=attempt;begin=time.monotonic()
  payload={'model':MODEL,'messages':[{'role':'user','content':'Return exactly AFP_OK and nothing else.'}],'max_tokens':64,'temperature':0}
  req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'AFP-secret-health-check/1.0'})
  try:
   with urllib.request.urlopen(req,timeout=35)as response:
    result['http_status']=response.status;data=json.loads(response.read(512*1024))
   choices=data.get('choices')
   if not isinstance(choices,list)or not choices:result['status']='invalid_response_shape'
   else:
    content=choices[0].get('message',{}).get('content')
    if isinstance(content,list):content=''.join(x.get('text','')for x in content if isinstance(x,dict))
    result['status']='healthy'if isinstance(content,str)and content.strip()=='AFP_OK'else'nonconforming_response'
  except urllib.error.HTTPError as exc:
   result['http_status']=exc.code;result['status']=classify_http(exc.code)
   exc.close() # Raw provider error body is deliberately never read or persisted.
  except (TimeoutError,socket.timeout):result['status']='network_timeout'
  except urllib.error.URLError:result['status']='network_error'
  except (ValueError,KeyError,TypeError,UnicodeError):result['status']='invalid_response_shape'
  except Exception:result['status']='transport_or_protocol_error'
  result['latency_ms']=round((time.monotonic()-begin)*1000)
  if result['status']not in {'provider_unavailable','provider_error','provider_timeout','network_timeout','network_error','request_timeout'}or attempt==2:break
  time.sleep(2)
 return result

def write(report):
 OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2));tmp.replace(OUT)

def audit(env=None,worker=probe):
 env=os.environ if env is None else env
 report={'schema_version':1,'tested_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':MODEL,'endpoint':ENDPOINT,'expected_slots':25,'scope':'text authentication and minimal completion only; no image capability claim','keys':[],'complete':False}
 # Values stay in memory. Duplicate names may share one request, but do not imply
 # additional independent quota or independent working credentials.
 groups={};rows={}
 for name in NAMES:
  value=env.get(name,'').strip()
  row={'secret_name':name,'configured':bool(value),'status':'not_tested','image_capability':'not_tested'};rows[name]=row
  if not value:row['status']='not_configured'
  elif value in groups:
   row['duplicate_of']=groups[value][0]
   groups[value].append(name)
  else:groups[value]=[name]
 report['keys']=[rows[n]for n in NAMES];write(report)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures={pool.submit(worker,value):names for value,names in groups.items()}
  for future in concurrent.futures.as_completed(futures):
   result=future.result()
   for name in futures[future]:rows[name].update(result)
   write(report)
 report['complete']=True
 report['configured_slots']=sum(x['configured']for x in report['keys'])
 report['unique_configured_credentials']=len(groups)
 report['healthy_slots']=sum(x['status']=='healthy'for x in report['keys'])
 report['healthy_unique_credentials']=sum(rows[names[0]]['status']=='healthy'for names in groups.values())
 write(report)
 return report
if __name__=='__main__':
 result=audit()
 print(json.dumps({k:result[k]for k in ['complete','expected_slots','configured_slots','unique_configured_credentials','healthy_slots','healthy_unique_credentials']}))
 for row in result['keys']:print(json.dumps({k:v for k,v in row.items()if k in ['secret_name','status','http_status','duplicate_of']}))
