#!/usr/bin/env python3
"""Generate clean backgrounds, then add only approved product pixels."""
from __future__ import annotations
import base64,io,json,os,urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue_cloudflare as backend
from deterministic_product_compositor import load_b64_asset,compose_layflat,compose_tape
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'automation'/'assets';OUT=ROOT/'artifacts'/'city-content-queue'/'test-images'
API=(os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations');MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()

def background(prompt):
    payload={'model':MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json'}}
    req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
    row=(data.get('data') or [{}])[0];blob=base64.b64decode(row['b64_json']) if row.get('b64_json') else urllib.request.urlopen(row['url'],timeout=300).read()
    image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
    if w/h>target:nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
    else:nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
    return image.resize((1200,675),Image.Resampling.LANCZOS)

def save(name,image):
    stage=io.BytesIO();image.save(stage,'JPEG',quality=95,optimize=True);marked=Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert('RGB');OUT.mkdir(parents=True,exist_ok=True);marked.save(OUT/name,'WEBP',quality=82,method=6)

if not KEY:raise RuntimeError('image API key missing')
clean='''Create a photorealistic 16:9 wide high-oblique Iranian agricultural field background for an irrigation article. Show only natural soil, crop rows and installed irrigation lines. Leave the entire lower-left third as clean open soil with realistic perspective and contact-lighting, reserved for later product compositing. Absolutely no product, roll, coil, package, carton, text, logo, watermark, person, body part, silhouette, tractor, vehicle, machine, bottle, jar, bucket, tool, box, building or animal anywhere. The empty farm environment must be the subject.'''
lay_bg=background(clean+' Use a dry-soil water-transfer field context with broad negative space.')
tape_bg=background(clean+' Use orderly young row crops and visible installed drip-tape laterals.')
package=load_b64_asset(ASSETS/'afp-layflat.webp.b64');bare=load_b64_asset(ASSETS/'afp-layflat-bare.jpg.b64');tape=load_b64_asset(ASSETS/'afp-tape.webp.b64')
save('composited-layflat-test.webp',compose_layflat(lay_bg,package,bare))
save('composited-tape-test.webp',compose_tape(tape_bg,tape))
(OUT/'authoritative-compositor-test.json').write_text(json.dumps({'model':MODEL,'method':'background-generation-plus-deterministic-approved-product-compositing','production_policy_changed':False,'tape_width_px':105,'canvas_width_px':1200},indent=2),encoding='utf-8')
