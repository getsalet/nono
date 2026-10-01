#!/usr/bin/env python3
"""Place exact approved product pixels into product-free editorial backgrounds."""
from __future__ import annotations
from collections import deque
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import base64

TAPE_WIDTH=264                    # 22% of 1200px, restored approved envelope 20-23%
LAYFLAT_PACKAGE_WIDTH=92
LAYFLAT_BARE_WIDTH=68
LAYFLAT_GAP=8                     # 168px total, 14% of 1200px, restored 12-15%

def load_b64_asset(path:Path)->Image.Image:
 return Image.open(BytesIO(base64.b64decode(path.read_text(encoding='ascii').strip()))).convert('RGBA')

def remove_border_background(image:Image.Image)->Image.Image:
 src=image.convert('RGBA');pix=src.load();w,h=src.size;seen=bytearray(w*h);q=deque()
 def bg(x,y):
  r,g,b,a=pix[x,y];return a>0 and min(r,g,b)>=225 and max(r,g,b)-min(r,g,b)<=28
 def add(x,y):
  i=y*w+x
  if not seen[i] and bg(x,y):seen[i]=1;q.append((x,y))
 for x in range(w):add(x,0);add(x,h-1)
 for y in range(h):add(0,y);add(w-1,y)
 while q:
  x,y=q.popleft()
  if x:add(x-1,y)
  if x+1<w:add(x+1,y)
  if y:add(x,y-1)
  if y+1<h:add(x,y+1)
 alpha=Image.new('L',(w,h),255);ap=alpha.load()
 for y in range(h):
  for x in range(w):
   if seen[y*w+x]:ap[x,y]=0
 alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.35));src.putalpha(alpha)
 box=src.getbbox();return src.crop(box) if box else src

def _fit_width(image,width):
 return image.resize((width,max(1,round(image.height*width/image.width))),Image.Resampling.LANCZOS)

def _paste_grounded(canvas,product,x,y):
 alpha=product.getchannel('A');flat_h=max(8,round(product.height*.16))
 cast=alpha.resize((product.width,flat_h),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(max(3,product.width//38))).point(lambda p:round(p*.25))
 shadow=Image.new('RGBA',canvas.size,(18,12,7,0));mask=Image.new('L',canvas.size,0);mask.paste(cast,(x+round(product.width*.08),y+product.height-flat_h//2));shadow.putalpha(mask);canvas.alpha_composite(shadow)
 contact=Image.new('RGBA',canvas.size,(10,7,4,0));cm=Image.new('L',canvas.size,0);draw=ImageDraw.Draw(cm);inset=max(3,round(product.width*.08));ch=max(4,round(product.height*.045));cy=y+product.height-round(ch*.35);draw.ellipse((x+inset,cy-ch,x+product.width-inset,cy+ch),fill=105);cm=cm.filter(ImageFilter.GaussianBlur(max(2,ch//2)));contact.putalpha(cm);canvas.alpha_composite(contact)
 grounded=product.copy();bounce=Image.new('RGBA',grounded.size,(118,82,48,0));ba=Image.new('L',grounded.size,0);bp=ba.load();pa=alpha.load();start=int(grounded.height*.72)
 for yy in range(start,grounded.height):
  strength=round(18*(yy-start)/max(1,grounded.height-start-1))
  for xx in range(grounded.width):bp[xx,yy]=round(strength*pa[xx,yy]/255)
 bounce.putalpha(ba);canvas.alpha_composite(Image.alpha_composite(grounded,bounce),(x,y))

def compose_tape(background,asset,x=None,base_margin=50):
 canvas=background.convert('RGBA');product=_fit_width(remove_border_background(asset),TAPE_WIDTH);x=round(canvas.width*.09) if x is None else x;y=canvas.height-product.height-base_margin;_paste_grounded(canvas,product,x,y);return canvas.convert('RGB')

def compose_layflat(background,package,bare,x=None,base_margin=50):
 canvas=background.convert('RGBA');package=_fit_width(remove_border_background(package),LAYFLAT_PACKAGE_WIDTH);bare=_fit_width(remove_border_background(bare),LAYFLAT_BARE_WIDTH);x=round(canvas.width*.09) if x is None else x;base_y=canvas.height-base_margin;_paste_grounded(canvas,package,x,base_y-package.height);_paste_grounded(canvas,bare,x+package.width+LAYFLAT_GAP,base_y-bare.height);return canvas.convert('RGB')
