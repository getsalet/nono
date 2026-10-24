"""AFP reference conditioning and deterministic phone label, adapted from legacy image policy."""
import base64,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
PHONE_LABEL='AFP | 09134922013'
def reference_images():
 raw=base64.b64decode((Path(__file__).with_name('assets')/'afp-tape.webp.b64').read_text().strip(),validate=True)
 product=Image.open(io.BytesIO(raw)).convert('RGB').resize((280,170),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(1200,675),(238,238,235));canvas.paste(product,(90,450));out=io.BytesIO();canvas.save(out,'WEBP',quality=90)
 return ['data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode()]
def image_prompt(topic,kind):
 roles={1:'wide crop-specific field overview with mature dry-bean pods when the topic is dry-bean harvesting',2:'near-overhead close agronomic detail of the exact crop and dry pods; no horizon or panorama',3:'unattended technical irrigation detail with drip lines, filtration and crop context; not a repeat of the wide view'}
 return ('Create a realistic editorial agricultural illustration for '+topic['crop']+': '+topic['title']+'. Role: '+roles[kind]+'. '+
 'Use the attached reference to reconstruct exactly one AFP white-and-blue low wide cylindrical drip-tape carton roll in the scene, not a pasted sticker. '+
 'Preserve authentic AFP and Drip Irrigation Tape package print, proportions, construction and colors. Product is secondary, off-center lower-left, approximately 20-23 percent of frame width, no more than 32 percent height, diameter 1.5-1.9 times height; natural contact shadow on soil. '+
 'The subject and crop are the main story. No people, faces, hands or silhouettes. No extra package, bottle, bucket, second roll, giant product, layflat hose, invented logo or writing. No phone label: it will be added accurately afterward. '+
 'Keep bottom-right clear for a phone label. Landscape 16:9. Physical product placement must be believable; crop must match the topic, not an unrelated species. Illustration, not evidence of agronomic performance.')
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
