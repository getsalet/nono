#!/usr/bin/env python3
"""Generate product-free scenes, then place only exact approved product pixels."""
from __future__ import annotations
import base64,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue_cloudflare as backend
from deterministic_product_compositor import *
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'automation'/'assets';OUT=ROOT/'artifacts'/'city-content-queue'/'test-images';API=(os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations');MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()
def background(prompt):
 payload={'model':MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json'}};last=None
 for attempt in range(1,7):
  try:
   req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST')
   with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
   row=(data.get('data') or [{}])[0];blob=base64.b64decode(row['b64_json']) if row.get('b64_json') else urllib.request.urlopen(row['url'],timeout=300).read();image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
   if w/h>target:nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
   else:nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
   return image.resize((1200,675),Image.Resampling.LANCZOS)
  except Exception as exc:
   last=exc
   if attempt<6:time.sleep(min(120,10*2**(attempt-1)))
 raise RuntimeError(f'background generation failed: {last!r}')
def save(name,image):
 stage=io.BytesIO();image.save(stage,'JPEG',quality=95,optimize=True);marked=Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert('RGB');OUT.mkdir(parents=True,exist_ok=True);marked.save(OUT/name,'WEBP',quality=84,method=6)
if not KEY:raise RuntimeError('image API key missing')
clean='''Create a coherent photorealistic 16:9 Iranian agricultural editorial background. Warm late-afternoon light comes from upper left. Show natural textured soil and irrigation infrastructure relevant to the requested role. Reserve level open soil in the lower-left third with correct perspective and contact lighting. Absolutely no product, roll, coil, package, carton, text, logo, watermark, person, body part, silhouette, tractor, vehicle, machine, bottle, jar, bucket, movable tool, cardboard box, animal or invented commercial object.'''
lay=background(clean+' Water-transfer field context with an installed unattended hose connection; wide high-oblique view; background remains dominant.')
tape=background(clean+' Orderly young row crops with installed drip-tape laterals; wide high-oblique view; background remains dominant.')
package=load_b64_asset(ASSETS/'afp-layflat.webp.b64');bare=load_b64_asset(ASSETS/'afp-layflat-bare.jpg.b64');roll=load_b64_asset(ASSETS/'afp-tape.webp.b64')
save('composited-layflat-test.webp',compose_layflat(lay,package,bare));save('composited-tape-test.webp',compose_tape(tape,roll))
(OUT/'authoritative-compositor-test.json').write_text(json.dumps({'model':MODEL,'policy':'exact-approved-product-compositor-v2','method':'product-free-background-plus-grounded-exact-product-pixels','production_policy_changed':False,'canvas_width_px':1200,'tape_width_px':TAPE_WIDTH,'tape_width_percent':round(TAPE_WIDTH/12,2),'layflat_group_width_px':LAYFLAT_PACKAGE_WIDTH+LAYFLAT_GAP+LAYFLAT_BARE_WIDTH,'layflat_group_width_percent':round((LAYFLAT_PACKAGE_WIDTH+LAYFLAT_GAP+LAYFLAT_BARE_WIDTH)/12,2),'identity_guarantee':'approved asset pixels only','grounding':['directional_alpha_shadow','tight_contact_shadow','white_halo_suppression','subtle_soil_bounce']},indent=2),encoding='utf-8')
