#!/usr/bin/env python3
"""Composite approved product photography onto generated editorial backgrounds."""
from __future__ import annotations
from collections import deque
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter
import base64


def load_b64_asset(path: Path) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(path.read_text(encoding='ascii').strip()))).convert('RGBA')


def remove_border_background(image: Image.Image) -> Image.Image:
    """Remove only near-white pixels connected to the source image border."""
    src=image.convert('RGBA');pix=src.load();w,h=src.size
    seen=bytearray(w*h);q=deque()
    def bg(x,y):
        r,g,b,a=pix[x,y]
        return a>0 and min(r,g,b)>=232 and max(r,g,b)-min(r,g,b)<=22
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
    alpha=alpha.filter(ImageFilter.GaussianBlur(0.55))
    src.putalpha(alpha)
    box=src.getbbox()
    return src.crop(box) if box else src


def _fit_width(image: Image.Image,width: int) -> Image.Image:
    height=max(1,round(image.height*width/image.width))
    return image.resize((width,height),Image.Resampling.LANCZOS)


def _paste_with_shadow(canvas: Image.Image,product: Image.Image,x: int,y: int) -> None:
    alpha=product.getchannel('A')
    shadow=Image.new('RGBA',canvas.size,(0,0,0,0))
    shadow_mask=Image.new('L',canvas.size,0)
    # A flattened, soft contact shadow grounds the exact product without changing it.
    ellipse=Image.new('L',(product.width,max(10,product.height//5)),0)
    ep=ellipse.load();ew,eh=ellipse.size
    for yy in range(eh):
        for xx in range(ew):
            dx=(xx-ew/2)/(ew/2);dy=(yy-eh/2)/(eh/2)
            if dx*dx+dy*dy<=1:ep[xx,yy]=125
    shadow_mask.paste(ellipse,(x,y+product.height-eh//2))
    shadow_mask=shadow_mask.filter(ImageFilter.GaussianBlur(8))
    shadow.putalpha(shadow_mask);canvas.alpha_composite(shadow)
    canvas.alpha_composite(product,(x,y))


def compose_tape(background: Image.Image,asset: Image.Image) -> Image.Image:
    canvas=background.convert('RGBA');product=_fit_width(remove_border_background(asset),105)
    x=155;y=canvas.height-product.height-68
    _paste_with_shadow(canvas,product,x,y)
    return canvas.convert('RGB')


def compose_layflat(background: Image.Image,package: Image.Image,bare: Image.Image) -> Image.Image:
    canvas=background.convert('RGBA')
    package=_fit_width(remove_border_background(package),185)
    bare=_fit_width(remove_border_background(bare),150)
    base_y=canvas.height-62
    _paste_with_shadow(canvas,package,92,base_y-package.height)
    _paste_with_shadow(canvas,bare,92+package.width+18,base_y-bare.height)
    return canvas.convert('RGB')
