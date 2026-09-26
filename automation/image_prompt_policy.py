#!/usr/bin/env python3
"""Product routing plus deterministic visual diversity for generated city images."""
from __future__ import annotations

import hashlib

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
  1:'editorial hero showing one intact original AFP drip-tape carton as the main subject beside long crop rows',
  2:'close product-detail scene showing the original AFP carton, central core, blue band and packaging texture at realistic scale',
  3:'technical irrigation context with drip tape, filtration or pressure-control equipment visible and the AFP product identity present but not dominating the frame',
  4:'active installation context along a crop row, with hands or a farmer shown naturally and safely while drip tape is positioned correctly',
  5:'maintenance and inspection context showing a drip line, emitter area or connection detail in a real cultivated field'
}
LAYFLAT_SCENES={
  1:'editorial hero showing one original packaged AFP woven layflat-hose roll at the edge of an agricultural field',
  2:'close product-detail scene showing the original black woven roll, wrap, straps, weave and package geometry at realistic scale',
  3:'technical water-transfer context with a deployed layflat hose and a plausible pump, manifold or connection visible',
  4:'active field setup showing a worker safely laying out or connecting the collapsible hose, without posing for the camera',
  5:'maintenance and inspection context showing the hose connection, surface weave, bend or storage method in a real farm setting'
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


def reference_images(kind,item=None):
    return [LAYFLAT_REFERENCE_PACKAGE] if product_family(item)=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]


def image_prompt(item,kind):
    family=product_family(item);variation=_variation(item,kind)
    city=str((item or {}).get('city') or 'the target city')
    province=str((item or {}).get('province') or 'Iran')
    scene=(LAYFLAT_SCENES if family=='layflat' else TAPE_SCENES).get(kind)
    if family=='layflat':
        identity=(
          'When the packaged product is visible, it must match the supplied approved AFP layflat reference: one black woven yarn-reinforced collapsible hose roll with the original wrap, straps, weave, proportions and label layout. '
          'The brand text may only be "AFP", "آبگسترفراپارسیان" and lowercase "layflat". Never turn it into drip tape or a rigid pipe.')
    else:
        identity=(
          'When the packaged product is visible, it must match the supplied approved AFP 20-centimeter drip-tape reference: one white cylindrical carton with the AFP logo, blue lower band, central cardboard core and original side-label layout. '
          'The only approved visible strings are "AFP", "آبگسترفراپارسیان" and "DRIP Irrigation tape". Do not invent specifications or replacement packaging.')
    lock=(
      'For image roles 1 and 2, keep the original package intact and make it the clear subject. '
      'For roles 3, 4 and 5, prioritize the distinct real-world technical, installation or maintenance action; the package may be secondary or outside the frame. '
      'Show one coherent scene, realistic equipment, believable scale and physical contact shadows. No duplicate product, floating object, fake writing, gibberish label, caption, watermark or collage.')
    diversity=(
      f'Camera: {variation["camera"]}. Background: {variation["background"]}. Lighting: {variation["light"]}. Composition: {variation["composition"]}. '
      'Make this image visibly different from the other images in the same article: do not repeat camera height, horizon placement, soil texture, crop layout, subject position or background. '
      f'Use visual variation token {variation["token"]} only as a creative seed; never render the token as text.')
    location=(
      f'Use a plausible Iranian agricultural environment suitable for {city}, {province}, without famous landmarks or unsupported claims about local soil, crops, climate or water.')
    return (
      'Photorealistic 16:9 editorial agricultural photograph, natural color, realistic detail, no synthetic studio background. '
      +identity+' Scene role: '+scene+'. '+location+' '+diversity+' '+lock)


def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
