#!/usr/bin/env python3
"""Generate isolated, reference-conditioned product scenes for human approval."""
from __future__ import annotations
import base64,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue_cloudflare as backend
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'automation'/'assets';OUT=ROOT/'artifacts'/'city-content-queue'/'test-images'
API=(os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations');MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()

def asset(filename,mime):return f"data:{mime};base64,"+(ASSETS/filename).read_text(encoding='ascii').strip()

def generate(name,prompt,refs):
    payload={'model':MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs}}
    last=None
    for attempt in range(1,7):
        try:
            req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
            row=(data.get('data') or [{}])[0];blob=base64.b64decode(row['b64_json']) if row.get('b64_json') else urllib.request.urlopen(row['url'],timeout=300).read()
            image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
            if w/h>target:nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
            else:nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
            image=image.resize((1200,675),Image.Resampling.LANCZOS)
            stage=io.BytesIO();image.save(stage,'JPEG',quality=95,optimize=True)
            marked=Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert('RGB');OUT.mkdir(parents=True,exist_ok=True);marked.save(OUT/name,'WEBP',quality=84,method=6)
            return
        except Exception as exc:
            last=exc
            if attempt==6:break
            delay=min(120,10*(2**(attempt-1)));print(f'image_attempt={attempt}/6 failed={exc!r} backoff_seconds={delay}',flush=True);time.sleep(delay)
    raise RuntimeError(f'image generation failed after retries: {last!r}')

if not KEY:raise RuntimeError('image API key missing')
shared='''Create a single coherent photorealistic photograph, not a collage, cutout, pasted product, mockup, packshot, or product-on-background composite. Re-render the referenced product naturally inside the scene so camera perspective, soil contact, occlusion, depth of field, sunlight direction, color temperature, cast shadow, ambient shadow and soil bounce are physically consistent. The product must visibly press into uneven soil and inherit the same lens and lighting as the farm. Preserve the approved reference product's recognizable construction, proportions, colors and branding; do not replace it with a generic or invented object. Wide 16:9 Iranian agricultural editorial photograph. The farm remains the main subject. No people, body parts, silhouettes, vehicles, tractors, bottles, buckets, tools, unrelated products, captions or generated watermark.'''
layflat_prompt=shared+''' Use ONLY the two attached approved layflat products. Exactly two separate objects: (1) the low, wide packaged AFP layflat coil with four folded white-and-blue printed cardboard panels, crossing dark straps and center opening; (2) the bare black woven layflat-hose coil with flat concentric fabric layers, diagonal woven texture, small brown cardboard center and one short loose flat hose end. Place both naturally on the same foreground soil plane, fully visible, separate and not touching, in a realistic water-transfer field context. Together they should occupy roughly 24-30% of frame width—clearly visible but secondary. Use a medium-distance low three-quarter camera view. Reject floating objects, razor-sharp cutout edges, white halos, mismatched shadows, crushed silver packaging, smooth tubing, cable spools, tires, fused products, extra coils and extra packages.'''
tape_prompt=shared+''' Use ONLY the attached approved AFP drip-tape product. Exactly one white-and-blue cylindrical carton sleeve with near-square diameter-to-height proportions, circular top, central hole, straight white wall, large blue AFP mark and blue lower band. Place it naturally on level soil beside active crop rows with installed drip-tape laterals. It must occupy roughly 12-15% of frame width, fully visible and off-center in the lower-left or lower-middle third—neither tiny nor a foreground hero. Use a medium-distance low three-quarter camera view. Reject floating placement, razor-sharp cutout edges, white halos, mismatched shadows, squashed or stretched cartons, generic barrels, extra rolls and invented packaging.'''
family=os.getenv('TEST_FAMILY','both').strip().lower()
if family in {'both','layflat'}:generate('authoritative-layflat-test.webp',layflat_prompt,[asset('afp-layflat.webp.b64','image/webp'),asset('afp-layflat-bare.jpg.b64','image/jpeg')])
if family in {'both','tape'}:generate('authoritative-tape-test.webp',tape_prompt,[asset('afp-tape.webp.b64','image/webp')])
(OUT/'authoritative-product-test.json').write_text(json.dumps({'model':MODEL,'method':'reference-conditioned-single-pass-integrated-render','tested_family':family,'production_policy_changed':False,'forbidden_method':'pixel-cutout-compositing','target_frame_share':{'tape':'12-15% width','layflat_combined':'24-30% width'}},indent=2),encoding='utf-8')
