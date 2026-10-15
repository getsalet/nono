"""Deterministic reference-rule contact watermark; never ask a model to draw digits."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
TEXT='AFP | 09134922013'
POLICY='afp-contact-bottom-right-v1'
def layout(size):
 width,height=size;point=max(18,width//38)
 font=None
 for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
  if Path(path).exists():font=ImageFont.truetype(path,point);break
 if font is None:font=ImageFont.load_default(size=point)
 box=ImageDraw.Draw(Image.new('L',size)).textbbox((0,0),TEXT,font=font);tw,th=box[2]-box[0],box[3]-box[1];pad=max(10,width//80)
 x=width-tw-pad*2;y=height-th-pad*2
 return font,(x,y-box[1]),(x-pad,y-pad,width-pad//2,height-pad//2)
def apply(image):
 image=image.convert('RGBA');layer=Image.new('RGBA',image.size,(0,0,0,0));draw=ImageDraw.Draw(layer)
 font,point,box=layout(image.size);draw.rounded_rectangle(box,radius=9,fill=(0,0,0,155));draw.text(point,TEXT,font=font,fill=(255,255,255,235))
 return Image.alpha_composite(image,layer).convert('RGB')
def present(image):
 """Check exact glyph locations and backing panel, including after WebP encoding."""
 image=image.convert('RGB');font,point,box=layout(image.size)
 mask=Image.new('L',image.size,0);ImageDraw.Draw(mask).text(point,TEXT,font=font,fill=255)
 bounds=mask.getbbox()
 if not bounds:return False
 pixels=image.crop(bounds);glyph=mask.crop(bounds);total=white=0
 for rgb,alpha in zip(pixels.getdata(),glyph.getdata()):
  if alpha>=235:total+=1;white+=min(rgb)>=185
 if not total or white/total<0.90:return False
 # Dark translucent backing is required; a white product photo must not pass.
 x1,y1,x2,y2=map(int,box);samples=[image.getpixel((x,y1+4))for x in range(x1+12,x2-12,8)]
 return bool(samples)and sum(max(p)<180 for p in samples)/len(samples)>0.85
