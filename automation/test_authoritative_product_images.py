#!/usr/bin/env python3
"""Generate two isolated samples from the user-approved product references."""
from __future__ import annotations
import base64, io, json, os, urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue_cloudflare as backend

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'automation'/'assets'
OUT=ROOT/'artifacts'/'city-content-queue'/'test-images'
API=(os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations')
MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash')
KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()

def asset(filename,mime):
    return f"data:{mime};base64,"+(ASSETS/filename).read_text(encoding='ascii').strip()

def generate(name,prompt,refs):
    payload={'model':MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs}}
    req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
    row=(data.get('data') or [{}])[0]
    blob=base64.b64decode(row['b64_json']) if row.get('b64_json') else urllib.request.urlopen(row['url'],timeout=300).read()
    image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
    if w/h>target:
        nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
    else:
        nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
    image=image.resize((1200,675),Image.Resampling.LANCZOS)
    stage=io.BytesIO();image.save(stage,'JPEG',quality=95,optimize=True)
    marked=Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert('RGB')
    OUT.mkdir(parents=True,exist_ok=True);marked.save(OUT/name,'WEBP',quality=82,method=6)

if not KEY: raise RuntimeError('image API key missing')
layflat_prompt='''Photorealistic 16:9 agricultural editorial test. Use ONLY the two attached approved layflat products and preserve their exact identity and geometry at high fidelity. Exactly two separate products: the packaged AFP coil with the same four folded white-and-blue printed cardboard panels, crossing dark straps, center opening and low-wide proportions; and the bare black woven layflat-hose coil with flat concentric fabric layers, diagonal woven texture, small brown cardboard center and one short loose flat hose end. Both fully visible, separate, horizontal and physically plausible, about 15-20% combined frame width, off-center lower third. Wide high-oblique unattended farm water-transfer context. Zero people, body parts, silhouettes, vehicles, tractors, extra coils, extra packages, bottles or tools. Reject crushed or silver tent-like packaging, smooth tubing, cable spool, tire shape, invented products, floating or fused objects, captions and added text.'''
tape_prompt='''Photorealistic 16:9 agricultural editorial test. Use ONLY the attached approved AFP drip-tape product and preserve its exact identity and geometry at high fidelity. Exactly one white-and-blue cylindrical carton sleeve with the original near-square diameter-to-height proportions, circular top, central hole, straight white wall, large blue AFP mark and blue lower band. Fully visible, physically plausible, about 20-23% frame width, off-center lower third. Wide unattended row-crop field with installed drip tape as context. Zero people, body parts, silhouettes, vehicles, tractors, second roll, layflat hose, box, bottle, jar, bucket or tool. Reject squashed, stretched or invented packaging, captions and added text.'''
generate('authoritative-layflat-test.webp',layflat_prompt,[asset('afp-layflat.webp.b64','image/webp'),asset('afp-layflat-bare.jpg.b64','image/jpeg')])
generate('authoritative-tape-test.webp',tape_prompt,[asset('afp-tape.webp.b64','image/webp')])
(OUT/'authoritative-product-test.json').write_text(json.dumps({'model':MODEL,'layflat_references':['afp-layflat.webp','afp-layflat-bare.jpg'],'tape_reference':['afp-tape.webp'],'production_policy_changed':False},indent=2),encoding='utf-8')
