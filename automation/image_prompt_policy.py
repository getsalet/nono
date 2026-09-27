#!/usr/bin/env python3
"""Product routing plus deterministic visual diversity for generated city images."""
from __future__ import annotations

import base64,hashlib,io,re
from pathlib import Path
from PIL import Image
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
  1:'wide city-article landscape where the agricultural field, crop rows and local irrigation context dominate while one approved drip-tape carton remains small and secondary',
  2:'practical selection scene showing one approved carton beside visible emitter-spacing or field-requirement evidence',
  3:'technical irrigation scene where fixed filtration, pressure control and water distribution hardware dominate while one approved carton remains secondary',
  4:'unattended post-installation scene of drip tape laid across soil and crop beds with one approved carton retained as small off-center product evidence',
  5:'maintenance and inspection scene where an emitter, connector or flush-point detail dominates while one approved carton remains secondary'
}
LAYFLAT_SCENES={
  1:'wide city-article landscape where agricultural water transfer dominates while the approved two-coil pair remains small and secondary',
  2:'practical selection scene showing the approved two-coil pair beside diameter, connector or field-requirement evidence',
  3:'technical water-transfer scene where a fixed unattended pump, manifold or connection dominates while the approved pair remains secondary',
  4:'unattended installed-result scene with an extended layflat connection leading into the field and the approved pair kept small at the field edge',
  5:'maintenance scene where a connector, fold, woven surface or storage detail dominates while the approved pair remains secondary'
}

TAPE_ROLE_DIRECTIVES={
 1:'EDITORIAL HERO: wide high-oblique view; the farm and irrigation context dominate; exactly one approved carton stays small, fully visible and off-center on the lower third',
 2:'SELECTION EVIDENCE: near-overhead technical arrangement with exactly one approved carton plus emitter-spacing or specification evidence; no skyline, barn, tractor or panorama',
 3:'HEADWORKS STORY: medium side view of unattended fixed filter, gauge, regulator and manifold; exactly one approved carton remains small and secondary',
 4:'INSTALLATION PROOF: asymmetric unattended view of installed drip tape and crop beds; exactly one approved carton remains small at a field edge; no centered vanishing point',
 5:'MAINTENANCE DETAIL: connector, emitter or flush-point detail dominates; exactly one approved carton remains fully visible but secondary; do not repeat role 3',
}
LAYFLAT_ROLE_DIRECTIVES={
 1:'EDITORIAL HERO: wide high-oblique water-transfer context; exactly the approved packaged coil and bare black woven coil remain small, separate and off-center',
 2:'SELECTION EVIDENCE: near-overhead technical comparison with exactly the approved two-coil pair plus diameter or connector evidence; no skyline or panorama',
 3:'HEADWORKS STORY: medium side view of a fixed unattended pump, gauge and manifold; the approved two-coil pair remains small, separate and secondary',
 4:'INSTALLATION PROOF: asymmetric unattended view of an extended layflat connection entering the field; the approved two-coil pair remains small at the field edge',
 5:'MAINTENANCE DETAIL: connector, fold or woven-surface detail dominates; the approved two-coil pair remains fully visible but secondary; do not repeat role 3',
}
ROLE_DIRECTIVES=TAPE_ROLE_DIRECTIVES


def role_directive(item_or_family,kind):
    family=item_or_family if isinstance(item_or_family,str) else product_family(item_or_family)
    roles=LAYFLAT_ROLE_DIRECTIVES if family=='layflat' else TAPE_ROLE_DIRECTIVES
    return roles.get(int(kind),roles[1])

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


def visual_brief(item,max_chars=700):
    item=item or {};parts=[]
    for key in ('title','topic_title','topic_focus','focus_keyword','excerpt','meta_description','summary','city','county','province'):
        value=re.sub(r'<[^>]+>',' ',str(item.get(key) or ''))
        value=re.sub(r'\s+',' ',value).strip()
        if value and value not in parts:parts.append(value)
    brief=' | '.join(parts)
    return brief[:max_chars].rsplit(' ',1)[0] if len(brief)>max_chars else brief


def reference_images(kind,item=None):
    family=product_family(item)
    if family=='layflat':
        # Raw close-up references repeatedly made the two-object set fill most
        # of the generated frame. Put both identity references on the same
        # scale-conditioned neutral canvas used by the tape product.
        refs=[]
        for filename in ('afp-layflat.webp.b64','afp-layflat-bare.jpg.b64'):
            raw=base64.b64decode((ASSET_DIR/filename).read_text(encoding='ascii').strip())
            product=Image.open(io.BytesIO(raw)).convert('RGB')
            product.thumbnail((150,112),Image.Resampling.LANCZOS)
            canvas=Image.new('RGB',(1200,675),(238,238,235))
            canvas.paste(product,(90,675-product.height-55))
            buf=io.BytesIO();canvas.save(buf,'WEBP',quality=90,method=6)
            refs.append('data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii'))
        return refs
    # Condition scale as well as identity. A raw close-up reference repeatedly
    # made the generator fill 35-50% of the frame. This 22%-wide padded
    # reference matches the production contract while preserving exact product
    # geometry and branding.
    raw=base64.b64decode((ASSET_DIR/'afp-tape.webp.b64').read_text(encoding='ascii').strip())
    product=Image.open(io.BytesIO(raw)).convert('RGB').resize((300,180),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(1200,675),(238,238,235))
    canvas.paste(product,(84,675-product.height-55))
    buf=io.BytesIO();canvas.save(buf,'WEBP',quality=90,method=6)
    return ['data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')]


def image_prompt(item,kind):
    family=product_family(item);variation=_variation(item,kind)
    city=str((item or {}).get('city') or 'the target city');province=str((item or {}).get('province') or 'Iran')
    scene=(LAYFLAT_SCENES if family=='layflat' else TAPE_SCENES).get(kind)
    correction=str((item or {}).get('_image_qa_feedback') or '').strip()
    correction_instruction=f'Previous candidate was rejected by strict visual QA. Correct every issue: {correction}. ' if correction else ''
    role_safety=('For this installation-proof role use an unattended asymmetric scene. Keep the required product evidence small at the field edge; include no tractor, vehicle, cabin or living being. ' if int(kind)==4 else '')
    brief=visual_brief(item)
    role=role_directive(family,kind)
    diversity=(f'Camera: {variation["camera"]}. Background: {variation["background"]}. Lighting: {variation["light"]}. Composition: {variation["composition"]}. Make this image visibly different from the other article images. Use visual variation token {variation["token"]} only as a seed and never render it.')
    if family=='layflat':
        shape=('exactly two separate related layflat-hose objects placed naturally beside each other: first, the packaged low wide black woven hose coil with the same folded printed cardboard pieces, crossing straps, center opening and package proportions; second, the unboxed black woven layflat hose coil exactly like its reference, as a low flat horizontal coil made of many tight concentric layers with a short hollow brown cardboard center, visible diagonal woven fabric texture, realistic compressed thickness and one short loose hose end')
        exact=('Keep the packaged object marks "AFP" and "layflat" readable. The bare black coil has no carton, logo or writing. The two references are separate objects in the same final scene, never alternatives and never fused. Both coils rest flat, horizontal and parallel to the soil. Never turn the bare coil into smooth round tubing, a tall cable spool, an upright wheel, a solid tire or a plastic pipe coil.')
        scale=('Use the approved 05-pair-far scale: the complete two-object group occupies approximately 12 to 15 percent of frame width, stays low on the soil and appears about four metres from the camera. Keep the pair off-center on the lower third.')
        people_rule=('NO PEOPLE OR VEHICLES in any image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette, distant human figure, tractor, harvester, vehicle or machine cabin. Show the article-specific field, crop, irrigation system and fixed unattended equipment without any human-associated machinery.')
    else:
        shape='a wide cylindrical 1000-meter drip-tape roll in the same white-and-blue carton sleeve, with the same diameter-to-height ratio, central top hole, straight carton walls and blue lower band'
        exact='Keep the exact readable marks "AFP" and "Drip Irrigation Tape"; never change it into layflat hose.'
        scale=('Use the approved 03-compact scale: the product occupies approximately 20 to 23 percent of frame width, its top stays clearly below knee height and it sits about two metres from the camera. Keep it off-center on the lower third.')
        people_rule=('NO PEOPLE OR VEHICLES in any drip-tape image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette, distant human figure, tractor, harvester, vehicle or machine cabin. Show the article-specific field, crop, irrigation system and fixed unattended equipment without any human-associated machinery.')
    return ('Create one photorealistic 16:9 agricultural editorial photograph. The attached image is an identity and geometry reference, not a flat layer to paste. '
      +f'Article visual brief extracted from the post: {brief}. Every background and technical detail must visibly express this brief rather than a generic farm. Mandatory role blueprint: {role}. Scene role: {scene}. {role_safety}{correction_instruction}Use a plausible Iranian agricultural environment suitable for {city}, {province}, without inventing landmarks, crops, climate facts or local infrastructure. The background and equipment must follow this article scene and remain the main subject. The required approved product evidence stays visible in every role; the role changes the technical narrative and camera, never the product identity or object count. {people_rule} Reconstruct the product as a true three-dimensional object: {shape}. '
      'Show it from a slightly different but physically plausible three-quarter angle, about 10 to 20 degrees from the reference. Preserve silhouette, packaging construction, proportions, material, printed-panel layout and brand colors. '
      +exact+' '+scale+' Enforce believable real-world scale. A drip-tape carton roll is roughly 40 to 55 cm across and 20 to 30 cm high; each layflat coil is roughly 45 to 65 cm across and 15 to 25 cm high. People must not appear. Every roll must remain clearly below implied knee height and must never look waist-high or table-sized. '
      'Use a wide environmental composition with substantial space around the product; never make the product the hero, central subject or foreground focal point. Reject forced-perspective enlargement, giant packaging, people touching or leaning on the package, and any crop that cuts through the product. Match perspective, depth of field, color cast, contact shadow, reflected light and slight soil interaction. '
      'Absolutely no sticker look, hard cut-out edge, white halo, flat front-facing packshot, collage, floating or duplicate product, caption, added logo or invented writing. '+diversity)


def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
