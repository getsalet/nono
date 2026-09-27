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
IMAGE_ROLE_SLUGS={
 1:'تصویر-شاخص',
 2:'راهنمای-انتخاب',
 3:'جزئیات-فنی',
 4:'نصب-در-مزرعه',
 5:'نگهداری-و-کاربرد',
}


def product_family(item):
    item=item or {};sid=str(item.get('source_id') or '').lower()
    text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
    if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')):
        return 'layflat'
    return 'tape20'


def seo_image_name(item,kind,extension='webp'):
    """Build a stable keyword-rich filename for every generated city image."""
    item=item or {};family=product_family(item)
    product='لوله-نخی-تاشو' if family=='layflat' else 'نوار-تیپ-20-سانتی'
    location=str(item.get('slug') or '-'.join(
        x for x in (str(item.get('city') or ''),str(item.get('province') or '')) if x
    ) or str(item.get('source_id') or 'شهر'))
    role=IMAGE_ROLE_SLUGS.get(int(kind),f'تصویر-{kind}')
    raw=f'{product}-{location}-{role}'.replace('ي','ی').replace('ك','ک').replace('‌','-')
    safe=''.join(ch if ch.isalnum() or ch=='-' else '-' for ch in raw)
    safe=re.sub(r'-+','-',safe).strip('-')
    suffix=str(extension or 'webp').lower().lstrip('.')
    return f'{safe}.{suffix}'


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
 2:'SELECTION EVIDENCE: elevated technical arrangement with exactly one approved carton plus visible emitter-spacing or field-selection evidence; keep the background simple but an ordinary field edge or farm building may appear',
 3:'HEADWORKS STORY: medium side view of unattended fixed filter, gauge, regulator and manifold; exactly one approved carton remains small and secondary',
 4:'INSTALLATION PROOF: asymmetric unattended view of installed drip tape and crop beds; exactly one approved carton remains small at a field edge; no centered vanishing point',
 5:'MAINTENANCE DETAIL: unattended close view of an installed drip-tape emitter, connector, flush-point or material detail; exactly one approved carton remains visible; no person, second roll, box, bottle or unrelated commercial container; do not repeat role 3',
}
LAYFLAT_ROLE_DIRECTIVES={
 1:'EDITORIAL HERO: wide high-oblique water-transfer context; exactly the approved packaged coil and bare black woven coil remain small, separate and off-center',
 2:'SELECTION EVIDENCE: elevated technical comparison with the approved two-coil pair; show diameter or construction difference through the pair itself; no third commercial package, bottle, person or extra coil',
 3:'HEADWORKS STORY: medium side view of a fixed unattended pump, gauge and manifold; the approved two-coil pair remains small, separate and secondary',
 4:'INSTALLATION PROOF: asymmetric unattended view of an extended layflat connection entering the field; the approved two-coil pair remains small at the field edge',
 5:'MAINTENANCE DETAIL: unattended close view of a connector, fold or woven-surface detail; the approved two-coil pair remains visible and physically plausible; no person, third commercial package, extra coil, box or bottle; do not repeat role 3',
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
    if family=='layflat' and int(kind)==2:
        # Role 2 is an isolated technical comparison. Generic camera/background
        # variation previously contradicted the near-overhead brief and caused
        # tractors, horizons, extra connectors and oversized foreground coils.
        diversity=(f'Camera: elevated technical view. Background: textured soil or a restrained field edge, with no person, bottle or third commercial package. Composition: the exact two-coil pair remains separate and fully visible, preferably occupying 20 to 35 percent of frame width. An ordinary distant building or unattended farm equipment may appear but must not dominate. Use visual variation token {variation["token"]} only as a seed and never render it.')
    elif family=='tape20' and int(kind)==2:
        # Keep tape selection evidence on a controlled, horizon-free patch of
        # soil. Generic environment variation repeatedly introduced barns,
        # tractors, centered product poses and fake specification cards.
        diversity=(f'Camera: elevated 60-degree downward near-overhead view from at least five metres away. Background: only broad empty textured soil and one short installed drip-tape segment with physically visible emitter spacing; crop every horizon, building, barn, person, animal, tractor, vehicle, machine, box, bottle, ruler, tool and specification card out of frame. Composition: exactly one approved carton, fully visible and off-center on the lower third, occupying 15 to 22 percent of frame width; the short installed tape segment is evidence, not a second roll or package. Do not generate any extra readable text. Use visual variation token {variation["token"]} only as a seed and never render it.')
    elif int(kind)==5:
        # Maintenance must be a controlled detail shot. A generic farm
        # background repeatedly introduced people, tractors and extra products.
        product_note=('Keep exactly one carton visible at roughly 18 to 32 percent of frame width.' if family=='tape20' else 'Keep exactly the approved two-coil pair visible at roughly 20 to 40 percent of frame width.')
        diversity=(f'Camera: elevated close documentary view aimed at soil, with the installed maintenance detail sharp in the foreground. Keep all people, human body parts, bottles, jars and extra commercial packages out of frame. A restrained field edge, fixed hardware or distant unattended equipment may appear. Composition: the connector, emitter, flush-point, fold or woven detail is the technical focus while the approved product evidence remains physically plausible. {product_note} Use visual variation token {variation["token"]} only as a seed and never render it.')
    elif int(kind)==3:
        diversity=(f'Camera: medium three-quarter view aimed slightly downward at one fixed unattended filter, gauge and manifold station. Background: cropped soil and irrigation hardware only; no horizon, people, vehicles, tractors, cabins, boxes or extra commercial products. Composition: fixed headworks dominate while approved product evidence stays small and off-center. Use visual variation token {variation["token"]} only as a seed and never render it.')
    elif int(kind)==4:
        diversity=(f'Camera: elevated asymmetric diagonal view aimed downward at installed irrigation lines and crop beds. Background: crop beds and soil only with no visible horizon, person, vehicle, tractor, cabin, box or second product. Composition: installed result dominates and approved product evidence stays small at a field edge. Use visual variation token {variation["token"]} only as a seed and never render it.')
    else:
        diversity=(f'Camera: {variation["camera"]}. Background: {variation["background"]}. Lighting: {variation["light"]}. Composition: {variation["composition"]}. Make this image visibly different from the other article images. Use visual variation token {variation["token"]} only as a seed and never render it.')
    if family=='layflat':
        shape=('exactly two separate related layflat-hose objects placed naturally beside each other: first, the packaged low wide black woven hose coil with the same folded printed cardboard pieces, crossing straps, center opening and package proportions; second, the unboxed black woven layflat hose coil exactly like its reference, as a low flat horizontal coil made of many tight concentric layers with a short hollow brown cardboard center, visible diagonal woven fabric texture, realistic compressed thickness and one short loose hose end')
        exact=('Keep the packaged object marks "AFP" and "layflat" readable. The bare black coil has no carton, logo or writing. The two references are separate objects in the same final scene, never alternatives and never fused. Both coils rest flat, horizontal and parallel to the soil. Never turn the bare coil into smooth round tubing, a tall cable spool, an upright wheel, a solid tire or a plastic pipe coil.')
        scale=('Use a practical editorial scale: the complete two-object group preferably occupies 20 to 35 percent of frame width, stays low on the soil and remains fully visible. Avoid giant foreground staging, but centered placement alone is not a failure.')
        people_rule=('NO PEOPLE OR VEHICLES in any image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette, distant human figure, tractor, harvester, vehicle or machine cabin. Show the article-specific field, crop, irrigation system and fixed unattended equipment without any human-associated machinery.')
    else:
        shape='a wide cylindrical 1000-meter drip-tape roll in the same white-and-blue carton sleeve, with the same diameter-to-height ratio, central top hole, straight carton walls and blue lower band'
        exact='Keep the exact readable marks "AFP" and "Drip Irrigation Tape"; never change it into layflat hose.'
        scale=('Use a practical editorial scale: the product preferably occupies 20 to 28 percent of frame width, stays low in real-world scale and remains fully visible. Avoid giant foreground staging, but centered placement alone is not a failure.')
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
