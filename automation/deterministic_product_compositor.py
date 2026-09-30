#!/usr/bin/env python3
"""Composite approved product photography onto generated editorial backgrounds."""
from __future__ import annotations
from collections import deque
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import base64


def load_b64_asset(path: Path) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(path.read_text(encoding='ascii').strip()))).convert('RGBA')


def remove_border_background(image: Image.Image) -> Image.Image:
    """Remove near-white pixels connected to the border and suppress white cutout halos."""
    src=image.convert('RGBA');pix=src.load();w,h=src.size
    seen=bytearray(w*h);q=deque()
    def bg(x,y):
        r,g,b,a=pix[x,y]
        return a>0 and min(r,g,b)>=225 and max(r,g,b)-min(r,g,b)<=28
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
    # One-pixel erosion removes pale matte fringes; a tiny blur restores antialiasing.
    alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.35))
    src.putalpha(alpha)
    box=src.getbbox()
    return src.crop(box) if box else src


def _fit_width(image: Image.Image,width: int) -> Image.Image:
    height=max(1,round(image.height*width/image.width))
    return image.resize((width,height),Image.Resampling.LANCZOS)


def _paste_grounded(canvas: Image.Image,product: Image.Image,x: int,y: int) -> None:
    """Add directional cast shadow, tight contact shadow, and subtle soil bounce."""
    alpha=product.getchannel('A')
    # Directional shadow follows the actual product footprint instead of a generic oval.
    flat_h=max(10,round(product.height*0.16))
    cast=alpha.resize((product.width,flat_h),Image.Resampling.LANCZOS)
    cast=cast.filter(ImageFilter.GaussianBlur(max(4,product.width//38)))
    cast=cast.point(lambda p: round(p*0.25))
    shadow=Image.new('RGBA',canvas.size,(18,12,7,0))
    shadow_alpha=Image.new('L',canvas.size,0)
    shadow_alpha.paste(cast,(x+round(product.width*0.08),y+product.height-flat_h//2))
    shadow.putalpha(shadow_alpha)
    canvas.alpha_composite(shadow)

    # Tight dark contact immediately under the object prevents the floating/sticker look.
    contact_layer=Image.new('RGBA',canvas.size,(10,7,4,0))
    contact_mask=Image.new('L',canvas.size,0)
    draw=ImageDraw.Draw(contact_mask)
    inset=max(3,round(product.width*0.08))
    ch=max(5,round(product.height*0.045))
    cy=y+product.height-round(ch*0.35)
    draw.ellipse((x+inset,cy-ch,x+product.width-inset,cy+ch),fill=105)
    contact_mask=contact_mask.filter(ImageFilter.GaussianBlur(max(2,ch//2)))
    contact_layer.putalpha(contact_mask)
    canvas.alpha_composite(contact_layer)

    # Keep the approved product intact; only add a very subtle warm ground reflection low down.
    grounded=product.copy()
    bounce=Image.new('RGBA',grounded.size,(118,82,48,0))
    bounce_alpha=Image.new('L',grounded.size,0);bp=bounce_alpha.load();pa=alpha.load()
    start=int(grounded.height*0.72)
    for yy in range(start,grounded.height):
        strength=round(18*(yy-start)/max(1,grounded.height-start-1))
        for xx in range(grounded.width):bp[xx,yy]=round(strength*pa[xx,yy]/255)
    bounce.putalpha(bounce_alpha)
    grounded=Image.alpha_composite(grounded,bounce)
    canvas.alpha_composite(grounded,(x,y))


def compose_tape(background: Image.Image,asset: Image.Image) -> Image.Image:
    canvas=background.convert('RGBA');product=_fit_width(remove_border_background(asset),160)
    x=145;y=canvas.height-product.height-54
    _paste_grounded(canvas,product,x,y)
    return canvas.convert('RGB')


def compose_layflat(background: Image.Image,package: Image.Image,bare: Image.Image) -> Image.Image:
    canvas=background.convert('RGBA')
    package=_fit_width(remove_border_background(package),220)
    bare=_fit_width(remove_border_background(bare),175)
    base_y=canvas.height-52
    _paste_grounded(canvas,package,74,base_y-package.height)
    _paste_grounded(canvas,bare,74+package.width+14,base_y-bare.height)
    return canvas.convert('RGB')
