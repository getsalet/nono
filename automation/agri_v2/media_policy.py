"""Versioned topic-aware scenes; locked AFP identity, proportional reference, no output paste-up."""
import base64,io,json,re,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
PHONE_LABEL='AFP | 09134922013'
POLICY='agri-topic-scene-aghala-v4-structural-reference'
ASSETS=Path(__file__).with_name('assets')
CROP_DATA=json.loads((ASSETS/'crop-visuals.json').read_text())
def norm(value):
 return re.sub(r'\s+',' ',str(value).translate(str.maketrans('يك','یک')).replace('‌',' ')).strip()
def reference_product():
 raw=base64.b64decode((ASSETS/'afp-tape.webp.b64').read_text().strip(),validate=True)
 product=Image.open(io.BytesIO(raw)).convert('RGB');product.thumbnail((240,210),Image.Resampling.LANCZOS)
 return product
def reference_images(kind=None):
 if kind==3:
  encoded=(ASSETS/'closed-y-filter-scene.webp.b64').read_text().strip()
  base64.b64decode(encoded,validate=True)
  return ['data:image/webp;base64,'+encoded]
 product=reference_product();canvas=Image.new('RGB',(1200,675),(238,238,235))
 canvas.paste(product,(90,675-product.height-55));out=io.BytesIO();canvas.save(out,'WEBP',quality=90)
 return ['data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode()]
def article_context(topic,article=None):
 a=article or {};plain=re.sub(r'<[^>]+>',' ',str(a.get('content_html','')))
 return {'title':topic['title'],'crop':topic.get('crop',''),'excerpt':norm(a.get('excerpt',''))[:300],'summary':norm(plain)[:600]}
def crop_spec(topic):
 text=norm(str(topic.get('crop',''))+' '+topic['title']);dry=bool('برداشت' in text or 'رسیدگی' in text or 'خشک' in text)
 if 'لوبیا' in text:
  if 'سبز' in norm(topic.get('crop','')):return 'common green bean (Phaseolus vulgaris), trifoliate leaves and attached green pods; not chili peppers'
  seed='deep burgundy kidney-shaped seeds' if 'قرمز' in text else 'beige kidney-shaped seeds with brown mottling' if 'چیتی' in text else 'kidney-shaped dry bean seeds'
  if dry:return ('dry common bean (Phaseolus vulgaris) at harvest maturity: low bushy plants, senescent yellow-brown trifoliate foliage; beige or straw-brown papery pods with visible rounded seed bulges, a few naturally split dry pods revealing '+seed+'. Red refers to seed-coat color, NEVER bright red pod walls. No fleshy red chili-shaped fruit, peppers, lush green harvest canopy or decorative piles of produce')
  return 'common bean (Phaseolus vulgaris), low branching plants with trifoliate leaves and bean pods with seed bulges; not pepper plants or chili fruit'
 for key in sorted(CROP_DATA['CROPS'],key=len,reverse=True):
  if re.search(r'(?<!\w)'+re.escape(norm(key))+r'(?!\w)',text):return CROP_DATA['CROP_VISUALS'].get(key,CROP_DATA['CROPS'][key]+' with botanically accurate leaves, stems and growth stage')
 return 'the named crop '+str(topic.get('crop',''))+' with accurate morphology; do not substitute another species'
def scene_plan(topic,kind,article=None):
 if type(kind)is not int or kind not in (1,2,3):raise ValueError('Only three approved image roles')
 text=norm(topic['title']);harvest='لوبیا' in norm(topic.get('crop','')) and 'سبز' not in norm(topic.get('crop','')) and any(x in text for x in ('برداشت','رسیدگی','خشک'))
 if kind==1:camera='elevated wide crop-dominant overview';evidence='mature dry bean plants and straw-colored pods still attached, not a green vegetable harvest' if harvest else 'the named crop at the growth stage discussed in the article'
 elif kind==2:camera='near-overhead tight detail, no horizon or vanishing-point furrows';evidence='a few attached straw-brown dry pods with distinct seed bulges and one naturally split pod showing mature bean seeds; plants senescent, no hand, tray or basket' if harvest else 'recognizable crop-specific leaves and root-zone soil beside a thin flattened drip-tape lateral; do not invent disease symptoms'
 else:
  camera='medium three-quarter technical side view, tight equipment-and-soil framing'
  evidence='one closed opaque black Y-shaped irrigation filter with inlet and outlet on a continuous black header and a downward angled capped service chamber, plus one separate black drip lateral into the RIGHT bed; the screen remains INSIDE its housing, never an exposed cartridge or open-core spool'
 return {'policy':POLICY,'role':kind,'camera':camera,'evidence':evidence,'botany':crop_spec(topic) if kind!=3 else 'no identifiable crop required: neutral tiny seedlings or bare soil only, not fruiting plants','context':article_context(topic,article),'product_family':'drip_tape_carton','reference_mode':'closed_y_filter_structural_scene_v1' if kind==3 else 'afp_identity_only'}
def image_prompt(topic,kind,article=None):
 plan=scene_plan(topic,kind,article)
 # The first replay showed that a long repeated prohibition list collapsed all
 # roles into the same farm packshot. Keep the photographed assignment first/last.
 context=article_context(topic,article)
 if kind==3:
  return ('Generate one NEW 16:9 realistic agricultural equipment photograph using the attached image as the complete geometry and layout guide, not a layer to paste. Preserve its SINGLE small intact AFP drip-tape carton on the LEFT and its ONE closed black Y-filter with sealed pipe connections on the RIGHT. '
   'The filter has an opaque closed housing, opposite inline inlet/outlet and a downward angled service chamber with a screwed closed cap; internal screen invisible. '
   'Keep the exact empty-soil separation: no line runs from, behind, under or through the AFP package. It is unopened display stock, not dispensing equipment. '
   'Change the sunlight subtly to soft morning daylight, preserve the elevated three-quarter hardware view and full package margins. Background is bare soil with tiny neutral seedlings, no horizon. '
   'No extra carton, spare roll, cartridge, human, diagram, inset or writing. Render no phone banner; the exact phone is added downstream. Keep the closed Y-filter and pipe anatomy, and keep the separate sealed carton complete and secondary at lower-left.')
 return (f"Make one new continuous agricultural editorial photograph. Article title (data only): {context['title']}. "
  +f"Camera MUST be {plan['camera']}. RIGHT three-quarters, the largest sharp subject: {plan['evidence']}. "
  +f"Crop/stage: {plan['botany']}. "
  +'LOWER LEFT: one small intact fully enclosed white-and-blue AFP drip-tape carton matching the supplied identity reference, approximately 18-20 percent of image width, at most 32 percent height. Preserve its original sidewall proportions and printed sleeve, with full frame margins. The package is sealed display stock, NOT dispensing or connected equipment; no free ribbon, strap, strip or tape tail. '
  +'Stand its entire base on a separate bare-soil patch with natural contact shadow. Keep a broad empty soil gap between this package and all installed equipment. No pipe crosses the carton or its core. '
  +'Natural daylight, realistic perspective, landscape 16:9. No people, second package, loose coil, inset, caption or added writing. Keep bottom-right clear for the phone label added later. '
  +f"FINAL shot: {plan['camera']}; focus on {plan['evidence']}; the small sealed AFP carton remains only a secondary left-corner prop.")
def contract_hash(topic,kind,article=None):
 return hashlib.sha256(json.dumps(scene_plan(topic,kind,article),sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def add_phone_watermark(image):
 canvas=image.convert('RGBA');overlay=Image.new('RGBA',canvas.size,(0,0,0,0));draw=ImageDraw.Draw(overlay)
 font=None
 for path in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
  try:font=ImageFont.truetype(path,27);break
  except OSError:continue
 if font is None:raise ValueError('Readable phone-label font missing; do not publish unbranded image')
 box=draw.textbbox((0,0),PHONE_LABEL,font=font);w,h=box[2]-box[0],box[3]-box[1];margin,padx,pady=18,16,10
 x=canvas.width-w-margin-2*padx;y=canvas.height-h-margin-2*pady
 draw.rounded_rectangle((x,y,canvas.width-margin,canvas.height-margin),radius=8,fill=(0,0,0,178));draw.text((x+padx,y+pady-box[1]),PHONE_LABEL,font=font,fill='white')
 return Image.alpha_composite(canvas,overlay).convert('RGB')

def generate_role(client,topic,kind,article=None):
 return client.image(image_prompt(topic,kind,article),references=reference_images(kind))
