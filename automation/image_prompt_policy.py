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
 1:'EDITORIAL HERO: wide elevated field view with long crop geometry; one integrated AFP carton on the lower-left third; the farm remains clearly visible',
 2:'SELECTION EVIDENCE: steep near-overhead technical still life on dark soil with one integrated AFP carton and one straight drip-tape segment showing repeated emitter points',
 3:'HEADWORKS DETAIL: elevated equipment still life on a clean concrete pad with fixed filter, pressure gauge, regulator and manifold; one integrated AFP carton at the far edge',
 4:'INSTALLATION PROOF: elevated diagonal view of installed drip tape and crop beds with one integrated AFP carton at a field edge',
 5:'MAINTENANCE DETAIL: close technical still life of an installed emitter, connector or flush point with one integrated AFP carton visible',
}
LAYFLAT_ROLE_DIRECTIVES={
 1:'EDITORIAL HERO: wide elevated water-transfer field view; the integrated packaged coil and bare woven coil share one soil plane in the lower third',
 2:'SELECTION EVIDENCE: steep near-overhead technical still life on textured soil showing only the integrated two-coil pair and one connector or diameter cue',
 3:'HEADWORKS DETAIL: elevated equipment still life on a clean concrete pad with fixed pump, gauge and manifold; the integrated two-coil pair sits at the far edge',
 4:'INSTALLATION PROOF: elevated diagonal view of one installed layflat connection entering the field with the integrated two-coil pair at the edge',
 5:'MAINTENANCE DETAIL: close technical still life of a connector, fold or woven-surface detail with the integrated two-coil pair visible',
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
    def guide(rows):
        canvas=Image.new('RGBA',(1200,675),(238,238,235,255));x=96;base_y=610
        for filename,mime,width in rows:
            raw=base64.b64decode((ASSET_DIR/filename).read_text(encoding='ascii').strip())
            product=Image.open(io.BytesIO(raw)).convert('RGBA')
            product.thumbnail((width,600),Image.Resampling.LANCZOS)
            canvas.alpha_composite(product,(x,base_y-product.height));x+=product.width+8
        buf=io.BytesIO();canvas.convert('RGB').save(buf,'WEBP',quality=92,method=6)
        return 'data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')
    if family=='layflat':
        return [
          'data:image/webp;base64,'+(ASSET_DIR/'afp-layflat.webp.b64').read_text(encoding='ascii').strip(),
          'data:image/jpeg;base64,'+(ASSET_DIR/'afp-layflat-bare.jpg.b64').read_text(encoding='ascii').strip(),
          guide([('afp-layflat.webp.b64','image/webp',360),('afp-layflat-bare.jpg.b64','image/jpeg',300)]),
        ]
    return [
      'data:image/webp;base64,'+(ASSET_DIR/'afp-tape.webp.b64').read_text(encoding='ascii').strip(),
      guide([('afp-tape.webp.b64','image/webp',300)]),
    ]


def sanitize_qa_feedback(text,kind=None):
    raw=str(text or '').lower();notes=[]
    if any(x in raw for x in ('person','people','farmer','worker','human','face','hand','arm','leg','silhouette','animal','cow')):
        notes.append('Render a vacant controlled still life containing only the approved product and the role-listed agricultural surfaces or fixed infrastructure.')
    if any(x in raw for x in ('width','height','large','small','oversized','scale','dominant')):
        notes.append('Use the approved family scale and keep every product fully inside the frame.')
    if any(x in raw for x in ('duplicate','similar','camera','angle','role','elevated','oblique','overhead')):
        notes.append('Follow the mandatory role camera, surface and evidence blueprint exactly.')
    if any(x in raw for x in ('second','third','extra','count','missing carton','missing product','coil','package')):
        notes.append('Preserve the exact approved product count and construction.')
    if any(x in raw for x in ('halo','cutout','pasted','sticker','shadow','floating','perspective')):
        notes.append('Re-render the whole photograph coherently with shared lighting, lens, soil contact and cast shadow.')
    if any(x in raw for x in ('filter','gauge','regulator','manifold','headworks','concrete')):
        notes.append('For the equipment role include the complete fixed filter, gauge, regulator and manifold assembly on clean concrete.')
    if any(x in raw for x in ('emitter','spacing','selection','tape segment')):
        notes.append('For the selection role show one straight installed tape segment with clearly repeated emitter points.')
    return ' '.join(dict.fromkeys(notes)) or 'Follow the mandatory role blueprint exactly and keep the integrated product physically plausible.'


def image_prompt(item,kind):
    family=product_family(item);variation=_variation(item,kind);kind=int(kind)
    city=str((item or {}).get('city') or 'the target city');province=str((item or {}).get('province') or 'Iran')
    role=role_directive(family,kind)
    raw_feedback=str((item or {}).get('_image_qa_feedback') or '')
    correction=sanitize_qa_feedback(raw_feedback,kind) if raw_feedback else ''
    correction_instruction=f'Quality revision: {correction} ' if correction else ''
    role_scene={
      1:'Wide elevated 35mm field view with long crop geometry, clear middle distance and natural horizon. Use open soil in the lower third.',
      2:'Steep 65-degree near-overhead technical view. Fill the frame only with dark textured soil and one straight piece of installed irrigation evidence; crop out the horizon and architecture.',
      3:'Elevated 55-degree equipment-record view. Fill the frame with a clean concrete pad and one permanently fixed filtration and distribution assembly.',
      4:'Elevated diagonal installed-result view of crop beds and irrigation lines, with asymmetric geometry.',
      5:'Close elevated documentary view of one installed maintenance detail on soil, with shallow depth of field.',
    }.get(kind,'Elevated agricultural documentary view.')
    integrated=('Generate the complete photograph as one coherent single-pass physical render. The reference images provide product identity and scale only. Reconstruct the product inside the same 3D scene from the first pass; use one camera, one lens, continuous depth of field, consistent grain, shared sunlight, correct soil occlusion, contact shadow, cast shadow and reflected ground light. Never paste, mask, cut out, overlay or preserve source pixels.')
    allowed=('Create a vacant controlled agricultural still life. Visible content is limited to the approved AFP product, natural soil or concrete, crops where the role permits them, installed irrigation lines and the fixed infrastructure named by the role. Keep the composition free of activity and unrelated movable objects.')
    if family=='layflat':
        product=('Exactly two related objects: one low wide packaged AFP layflat coil with folded printed panels, crossing straps and center opening; and one separate bare black woven flat coil with concentric fabric layers, diagonal texture, a small brown center and one short flat hose end. Both rest horizontally on one surface and remain separate.')
        scale='The complete pair occupies 45 to 78 percent of frame width and stays fully visible.'
    else:
        product=('Exactly one AFP drip-tape product: a low wide cylindrical white-and-blue carton sleeve with circular top, central hole, straight walls, blue AFP mark and blue lower band. Preserve its approved proportions and construction.')
        scale='The complete product occupies 20 to 32 percent of frame width and stays fully visible.'
    placement={1:'Place it on the lower-left third.',2:'Place it on the lower-right third.',3:'Place it at the far-right edge of the concrete pad.',4:'Place it at one lower corner.',5:'Place it in the rear third while the maintenance detail stays sharp.'}.get(kind,'Place it on the lower third.')
    locality=f'Use a plausible neutral Iranian agricultural setting suitable for {city}, {province}; do not invent landmarks or region-specific architecture.'
    token=variation['token']
    return f'''Create one photorealistic 16:9 agricultural editorial photograph. {integrated} Mandatory role blueprint: {role}. {role_scene} {allowed} {product} {scale} {placement} {locality} {correction_instruction}Use natural documentary color, realistic material texture and physically correct scale. Make this role visibly different from the other article roles. Variation seed {token}; never render the seed as text. Add no caption, label, headline or watermark; the required watermark is applied after rendering.'''


def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
