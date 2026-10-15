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
 # Editorial split panel makes the illustration explicit: products are NOT
 # presented as real objects photographed in the generated farm scene.
 if background.size!=(1200,675):raise RuntimeError('Product composition requires 1200x675 background')
 sources=product_sources(family)
 from PIL import ImageOps
 canvas=Image.new('RGB',(1200,675),'white')
 panel_right=int(variation[:6],16)%2==0
 field_x=0 if panel_right else 520
 canvas.paste(ImageOps.fit(background.convert('RGB'),(680,675),Image.Resampling.LANCZOS),(field_x,0))
 product_x=680 if panel_right else 0
 draw=ImageDraw.Draw(canvas);divider=680 if panel_right else 516
 draw.rectangle((divider,0,divider+3,674),fill=(13,108,124))
 frames=[(product_x+70,147,380,380)]if family=='tape20'else[(product_x+90,40,340,280),(product_x+90,355,340,280)]
 for (name,raw),(x,y,w,h)in zip(sources,frames):
  # Retain the entire authentic photo, including its original white background.
  product=Image.open(io.BytesIO(raw)).convert('RGB');product.thumbnail((w,h),Image.Resampling.LANCZOS)
  canvas.paste(product,(x+(w-product.width)//2,y+(h-product.height)//2))
 return canvas

def provenance(family):
 return [{'asset':name,'sha256':hashlib.sha256(raw).hexdigest()}for name,raw in product_sources(family)]
