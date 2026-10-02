#!/usr/bin/env python3
"""Generate whole-scene reference-conditioned samples; never composite product pixels."""
from __future__ import annotations
import base64,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue_cloudflare as backend
from deterministic_product_compositor import load_b64_asset,remove_border_background
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'automation'/'assets';OUT=ROOT/'artifacts'/'city-content-queue'/'test-images';API=(os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations');MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()
def data_url(image):
 b=io.BytesIO();image.convert('RGB').save(b,'WEBP',quality=92,method=6);return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
def raw_asset(name,mime):return f'data:{mime};base64,'+(ASSETS/name).read_text(encoding='ascii').strip()
def scale_guide(images,widths):
 canvas=Image.new('RGBA',(1200,675),(238,238,235,255));x=96;base_y=610
 for image,width in zip(images,widths):
  cut=remove_border_background(image);cut=cut.resize((width,max(1,round(cut.height*width/cut.width))),Image.Resampling.LANCZOS);canvas.alpha_composite(cut,(x,base_y-cut.height));x+=width+8
 return data_url(canvas)
def generate(name,prompt,refs):
 payload={'model':MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs}};last=None
 for attempt in range(1,7):
  try:
   req=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json'},method='POST')
   with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
   row=(data.get('data') or [{}])[0];blob=base64.b64decode(row['b64_json']) if row.get('b64_json') else urllib.request.urlopen(row['url'],timeout=300).read();image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
   if w/h>target:nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
   else:nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
   image=image.resize((1200,675),Image.Resampling.LANCZOS);stage=io.BytesIO();image.save(stage,'JPEG',quality=95,optimize=True);marked=Image.open(io.BytesIO(backend.watermark(stage.getvalue()))).convert('RGB');OUT.mkdir(parents=True,exist_ok=True);marked.save(OUT/name,'WEBP',quality=84,method=6);return
  except Exception as exc:
   last=exc
   if attempt<6:time.sleep(min(120,10*2**(attempt-1)))
 raise RuntimeError(f'image generation failed: {last!r}')
if not KEY:raise RuntimeError('image API key missing')
shared='''Generate the entire image in one coherent photographic render. This is NOT compositing: do not paste, mask, cut out, overlay or preserve source pixels. Re-render the referenced product physically inside the same 3D scene from the first pass, with one camera, one lens, continuous depth of field, matching grain and sharpness, soil occlusion, physically correct contact and cast shadows, reflected soil light, consistent sunlight direction and color temperature. Absolutely no white halo, sticker edge, flat packshot, floating object or Photoshop appearance. Wide 16:9 Iranian agricultural editorial photograph. No person, body part, silhouette, vehicle, tractor, bottle, bucket, loose box, caption or invented commercial product. The field and irrigation context remain the main subject.'''
tape=load_b64_asset(ASSETS/'afp-tape.webp.b64');package=load_b64_asset(ASSETS/'afp-layflat.webp.b64');bare=load_b64_asset(ASSETS/'afp-layflat-bare.jpg.b64')
tape_prompt=shared+''' Render exactly one AFP drip-tape carton roll, faithful to the identity reference: white-and-blue low wide cylindrical sleeve, circular top and center hole, straight wall, blue AFP mark and blue lower band. Keep it fully visible, off-center on the lower third and 20-23% of frame width. Show an orderly irrigated crop field with installed drip-tape laterals. The final attached frame is only a scale/layout guide, not pixels to copy.'''
lay_prompt=shared+''' Render exactly two separate layflat objects faithful to both identity references: one packaged low wide AFP layflat coil with folded printed panels, straps and center opening; one bare black woven flat coil with concentric fabric layers, small brown center and short flat hose end. Keep them separate, horizontal and on the same soil plane. The complete pair must occupy 12-15% of frame width, fully visible and off-center on the lower third. Show a water-transfer field context. The final attached frame is only a scale/layout guide, not pixels to copy.'''
generate('integrated-tape-test.webp',tape_prompt,[raw_asset('afp-tape.webp.b64','image/webp'),scale_guide([tape],[264])])
generate('integrated-layflat-test.webp',lay_prompt,[raw_asset('afp-layflat.webp.b64','image/webp'),raw_asset('afp-layflat-bare.jpg.b64','image/jpeg'),scale_guide([package,bare],[92,68])])
(OUT/'authoritative-integrated-test.json').write_text(json.dumps({'model':MODEL,'policy':'single-pass-integrated-reference-render-v1','method':'whole-scene-reference-conditioned-rerender','compositing':False,'cutout_pixels':False,'target_frame_share':{'tape':'20-23% width','layflat_pair':'12-15% width'},'requires_human_approval':True,'production_policy_changed':False},indent=2),encoding='utf-8')
