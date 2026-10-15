"""Keep authentic AFP product pixels; generate ONLY the educational background."""
import base64,hashlib,io
from collections import deque
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
ASSETS=Path(__file__).with_name('assets')
PHOTOS={'tape20':('afp-tape.webp.b64',),'hose':('afp-layflat.webp.b64','afp-layflat-bare.jpg.b64')}

def remove_edge_background(image):
 # Flood only near-white pixels CONNECTED to the outer edge. White AFP labels
 # enclosed by the product silhouette are retained, unlike global white removal.
 image=image.convert('RGB');w,h=image.size;pixels=image.load();seen=bytearray(w*h);queue=deque()
 def eligible(x,y):
  r,g,b=pixels[x,y];return min(r,g,b)>=233 and max(r,g,b)-min(r,g,b)<=25
 def add(x,y):
  i=y*w+x
  if not seen[i]and eligible(x,y):seen[i]=1;queue.append((x,y))
 for x in range(w):add(x,0);add(x,h-1)
 for y in range(h):add(0,y);add(w-1,y)
 while queue:
  x,y=queue.popleft()
  if x:add(x-1,y)
  if x+1<w:add(x+1,y)
  if y:add(x,y-1)
  if y+1<h:add(x,y+1)
 alpha=Image.frombytes('L',(w,h),bytes(0 if value else 255 for value in seen))
 image=image.convert('RGBA');image.putalpha(alpha)
 bbox=alpha.getbbox()
 if not bbox:raise RuntimeError('Authentic product cutout is empty')
 return image.crop(bbox)

def product_sources(family):
 if family not in PHOTOS:raise RuntimeError('Unknown product family: real-photo composition refused')
 return [(name,base64.b64decode((ASSETS/name).read_text().strip()))for name in PHOTOS[family]]

def compose(background,family,variation):
 canvas=background.convert('RGBA');w,h=canvas.size
 if(w,h)!=(1200,675):raise RuntimeError('Product composition requires 1200x675 background')
 start=([160,310,460]if family=='hose'else[190,460,740])[int(variation[:6],16)%3]
 base_y=590;x=start
 for name,raw in product_sources(family):
  product=remove_edge_background(Image.open(io.BytesIO(raw)))
  width=260 if family=='hose' else 248
  product=product.resize((width,round(product.height*width/product.width)),Image.Resampling.LANCZOS)
  y=base_y-product.height
  if x<64 or y<220 or x+product.width>1136 or base_y>625:raise RuntimeError('Product composition would exceed safe frame')
  shadow=Image.new('RGBA',canvas.size,(0,0,0,0));draw=ImageDraw.Draw(shadow)
  draw.ellipse((x+8,base_y-15,x+product.width-8,base_y+12),fill=(30,26,20,95))
  canvas=Image.alpha_composite(canvas,shadow.filter(ImageFilter.GaussianBlur(8)))
  canvas.alpha_composite(product,(x,y));x+=product.width+42
 return canvas.convert('RGB')

def provenance(family):
 return [{'asset':name,'sha256':hashlib.sha256(raw).hexdigest()}for name,raw in product_sources(family)]
