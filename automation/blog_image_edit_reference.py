"""Mask the deterministic contact stamp in an EDIT REFERENCE, never an output.

The model must reconstruct the small marked soil area. Output still receives
exactly one deterministic contact stamp through the normal renderer.
"""
import io
from PIL import Image, ImageDraw, ImageStat

def masked_finish_reference(raw):
 image=Image.open(io.BytesIO(raw)).convert('RGB')
 w,h=image.size
 if w<512 or h<512:raise ValueError('Landscape edit reference too small')
 # The approved diagnostic scenes put the complete carton on the LEFT.
 # Include a generous margin around the contact stamp to avoid residual glyphs.
 box=(int(w*.64),int(h*.87),w,h)
 soil=image.crop((box[0],int(h*.79),w,box[1]))
 color=tuple(int(v) for v in ImageStat.Stat(soil).median)
 ImageDraw.Draw(image).rectangle(box,fill=color)
 out=io.BytesIO();image.save(out,'PNG')
 return out.getvalue()
