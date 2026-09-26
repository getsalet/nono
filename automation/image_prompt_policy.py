#!/usr/bin/env python3
"""Product routing plus deterministic visual diversity for generated city images."""
from __future__ import annotations

import hashlib,base64,io
from collections import deque
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageFilter
ASSET_DIR=Path(__file__).with_name('assets')

DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}


def product_family(item):
    item=item or {};sid=str(item.get('source_id') or '').lower()
    text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
    if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')):
        return 'layflat'
    return 'tape20'


TAPE_SCENES={
  1:'wide city-article hero where the agricultural field, crop rows and local irrigation context are the main subject',
  2:'practical selection or comparison scene where farm requirements and the article topic are the main subject',
  3:'technical irrigation scene where filtration, pressure control or water distribution is the main subject',
  4:'active installation scene along crop rows where the work and correct placement are the main subject',
  5:'maintenance and inspection scene where the drip line, emitter area or connection detail is the main subject'
}
LAYFLAT_SCENES={
  1:'wide city-article hero where the field and agricultural water-transfer context are the main subject',
  2:'practical selection or measurement scene where the farm requirement and hose application are the main subject',
  3:'technical water-transfer scene where a plausible pump, manifold or connection is the main subject',
  4:'active field setup where laying out or connecting the collapsible hose is the main subject',
  5:'maintenance and inspection scene where a hose connection, bend, surface or storage method is the main subject'
}

CAMERAS=[
 'high oblique 35mm viewpoint with visible field geometry',
 'ground-level wide-angle viewpoint with strong leading crop rows',
 'three-quarter eye-level commercial viewpoint',
 'side-profile documentary viewpoint with shallow depth of field',
 'tight detail viewpoint with a long-lens compressed background',
 'wide environmental viewpoint from the opposite side of the field',
 'slightly elevated diagonal viewpoint with an asymmetric horizon',
]
BACKGROUNDS=[
 'an open row-crop field with long irrigation lines',
 'the edge of a young orchard with irregular natural soil',
 'a greenhouse entrance and cultivated beds in the distance',
 'a broad dry-soil field with sparse crop rows and distant hills',
 'a green field edge beside a compact irrigation station',
 'a recently prepared seedbed with textured furrows',
 'a mature crop field with a narrow service path',
]
LIGHTING=[
 'soft early-morning side light',
 'bright overcast daylight with low contrast',
 'late-afternoon golden light and long natural shadows',
 'clean midday light with crisp but realistic shadows',
 'diffused light after light cloud cover',
 'backlit sunrise atmosphere without lens flare obscuring the subject',
 'warm pre-sunset light with a cooler distant background',
]
COMPOSITIONS=[
 'subject on the left third with open contextual space on the right',
 'subject on the right third with crop rows leading inward',
 'low foreground subject with a high environmental background',
 'asymmetric diagonal composition with no centered product pose',
 'layered foreground, midground and background composition',
 'wide negative space composition suitable for an editorial article',
 'close foreground detail balanced by a distant field scene',
]


def _variation(item,kind):
    identity='|'.join(str((item or {}).get(k) or '') for k in ('source_id','slug','city','province','topic'))
    base=int(hashlib.sha256((identity+'|visual-diversity-v20').encode('utf-8')).hexdigest()[:12],16)
    index=max(0,int(kind)-1)
    # Different coprime steps prevent the five images of one article from
    # receiving the same angle, background, light or composition.
    return {
      'camera':CAMERAS[(base+index)%len(CAMERAS)],
      'background':BACKGROUNDS[(base*3+index*2)%len(BACKGROUNDS)],
      'light':LIGHTING[(base*5+index*3)%len(LIGHTING)],
      'composition':COMPOSITIONS[(base*7+index*4)%len(COMPOSITIONS)],
      'token':hashlib.sha256(f'{identity}|{kind}|v20'.encode('utf-8')).hexdigest()[:10],
    }


def reference_images(kind,item=None):return []


def image_prompt(item,kind):
    family=product_family(item);variation=_variation(item,kind)
    city=str((item or {}).get('city') or 'the target city');province=str((item or {}).get('province') or 'Iran')
    scene=(LAYFLAT_SCENES if family=='layflat' else TAPE_SCENES).get(kind)
    diversity=(f'Camera: {variation["camera"]}. Background: {variation["background"]}. Lighting: {variation["light"]}. Composition: {variation["composition"]}. Make this image visibly different from the other article images. Use visual variation token {variation["token"]} only as a seed and never render it.')
    return ('Photorealistic 16:9 editorial agricultural photograph with the article action as the primary subject. '+f'Scene role: {scene}. Use a plausible Iranian agricultural environment suitable for {city}, {province}. '
      'IMPORTANT: do not generate, draw or imitate any irrigation product package, roll, AFP logo, brand text, label, carton, layflat package or product-shaped object. Leave clean naturally lit ground space in the lower-left corner for a later exact product overlay. '
      'No fake writing, product close-up, centered package, duplicate product, floating object, collage, caption or watermark. '+diversity)

def _is_background(pixel):
    r,g,b,a=pixel
    return a==0 or (r>=232 and g>=232 and b>=232 and max(r,g,b)-min(r,g,b)<=22)


@lru_cache(maxsize=2)
def _product_cutout(family):
    filename='afp-layflat.webp.b64' if family=='layflat' else 'afp-tape.webp.b64'
    blob=base64.b64decode((ASSET_DIR/filename).read_text(encoding='ascii'))
    image=Image.open(io.BytesIO(blob)).convert('RGBA');width,height=image.size;pixels=image.load()
    seen=bytearray(width*height);queue=deque()
    def add(x,y):
        idx=y*width+x
        if not seen[idx] and _is_background(pixels[x,y]):seen[idx]=1;queue.append((x,y))
    for x in range(width):add(x,0);add(x,height-1)
    for y in range(height):add(0,y);add(width-1,y)
    while queue:
        x,y=queue.popleft();r,g,b,a=pixels[x,y];pixels[x,y]=(r,g,b,0)
        if x:add(x-1,y)
        if x+1<width:add(x+1,y)
        if y:add(x,y-1)
        if y+1<height:add(x,y+1)
    alpha=image.getchannel('A');box=alpha.getbbox()
    if not box:raise RuntimeError('Exact product asset became empty after background removal')
    return image.crop(box)


def composite_product(scene,item,kind):
    """Overlay the untouched approved product asset; never redraw its shape/text."""
    canvas=scene.convert('RGBA');product=_product_cutout(product_family(item)).copy()
    target_width=max(170,int(canvas.width*0.19));target_height=max(1,round(product.height*target_width/product.width))
    product=product.resize((target_width,target_height),Image.Resampling.LANCZOS)
    margin=max(18,int(canvas.width*0.025));x=margin;y=canvas.height-product.height-max(14,int(canvas.height*0.025))
    alpha=product.getchannel('A')
    shadow_alpha=alpha.filter(ImageFilter.GaussianBlur(max(4,target_width//35))).point(lambda value:value*90//255)
    shadow=Image.new('RGBA',product.size,(0,0,0,0));shadow.putalpha(shadow_alpha)
    canvas.alpha_composite(shadow,(x+max(4,target_width//45),y+max(7,target_width//30)))
    canvas.alpha_composite(product,(x,y))
    return canvas.convert('RGB')


def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES={}
    backend.image_prompt=image_prompt
