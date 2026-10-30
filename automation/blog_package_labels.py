"""Exact owner-approved package captions; geometry and blind readback are separate.
Never redraw the AFP mark or replace the product photograph. Only two small
caption regions on the white package sleeve may be cleaned and typeset.
"""
import base64,hashlib,io,json,math,os,re,unicodedata
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,features
import roya_backlink_queue as roya
ENGLISH='Drip Irrigation Tape'
PERSIAN='آبگسترفراپاریان'
POLICY='afp-exact-bilingual-captions-v1'

def normalized(value,lang):
 if not isinstance(value,str):return ''
 value=unicodedata.normalize('NFKC',value).replace('ي','ی').replace('ك','ک')
 return re.sub(r'[\s\u200c\u200e\u200f]','',value).casefold() if lang=='fa' else ' '.join(value.split()).casefold()

def exact_errors(value):
 if not isinstance(value,dict):return ['Independent literal label transcription required']
 errors=[]
 for lang,expected in (('english',ENGLISH),('persian',PERSIAN)):
  if value.get(lang+'_legible')is not True or normalized(value.get(lang+'_text'),'fa'if lang=='persian'else'en')!=normalized(expected,'fa'if lang=='persian'else'en'):errors.append('Exact package caption not independently read: '+lang)
 return errors

def inspect(raw):
 """Blind literal OCR plus placement. Expected captions are NOT sent to reader."""
 im=Image.open(io.BytesIO(raw)).convert('RGB');full=io.BytesIO();im.save(full,'WEBP',quality=95)
 detail=im.crop((0,int(im.height*.27),int(im.width*.62),im.height));detail=detail.resize((int(detail.width*2),int(detail.height*2)),Image.Resampling.LANCZOS);buf=io.BytesIO();detail.save(buf,'JPEG',quality=95)
 instruction=('Read the actual printed package captions literally, without translating, guessing, spelling correction or completing words. No expected wording is provided. '
  'Ignore the phone/contact stamp and side-panel fine print. Find the ONE upright white-and-blue carton in the FULL FRAME. '
  'english_text is the complete small caption directly BELOW the large AFP letters. persian_text is the small company caption directly BELOW the BLUE WATER-DROP SYMBOL to the left of AFP, even if it is actually malformed Latin or unreadable. '
  'For unreadable text return empty string and legible=false, never infer words from product type. Detail view is a crop of the SAME image; ALL coordinates must use the FULL FRAME, normalized 0..1000. '
  'Identify package_bbox, afp_bbox and symbol_bbox as [left,top,right,bottom]. Identify english_quad and persian_quad, each in order top-left,top-right,bottom-right,bottom-left. '
  'The quads must cover the ENTIRE existing caption and a small clean-white margin, below their respective mark, above the blue band, without covering ANY part of AFP or the water-drop symbol. If a caption is absent, identify a safe blank area directly below its mark. '
  'Geometry confidence is about safe exact location, not text recognition. Do not include cast shadow or soil in any caption quad. '
  'Return JSON only: {"english_text":"","persian_text":"","english_legible":false,"persian_legible":false,"package_count":1,"geometry_confidence":0.0,"package_bbox":[0,0,0,0],"afp_bbox":[0,0,0,0],"symbol_bbox":[0,0,0,0],"english_quad":[[0,0],[0,0],[0,0],[0,0]],"persian_quad":[[0,0],[0,0],[0,0],[0,0]]}.')
 content=[{'type':'text','text':instruction}]
 for label,data,mime in [('FULL FRAME',full.getvalue(),'image/webp'),('OVERLAPPING LEFT DETAIL; coordinates refer to FULL FRAME',buf.getvalue(),'image/jpeg')]:
  content +=[{'type':'text','text':label},{'type':'image_url','image_url':{'url':'data:'+mime+';base64,'+base64.b64encode(data).decode(),'detail':'high'}}]
 key=roya.BASE._key_pool.next()
 payload={'model':os.getenv('IMAGE_REVIEW_MODEL','agnes-3.0-flash'),'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'user','content':content}]}
 response=roya.BASE.fetch_json(roya.BASE.AGNES_BASE+'/chat/completions',{'Authorization':'Bearer '+key,'Content-Type':'application/json'},payload,timeout=180)
 value=response['choices'][0]['message']['content']
 if isinstance(value,list):value=''.join(x.get('text','')for x in value if isinstance(x,dict))
 return json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip(),flags=re.I))

def font_file(lang):
 candidates=(('/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf','/usr/share/fonts/google-noto/NotoSansArabic-Regular.ttf','/usr/share/fonts/google-noto-vf/NotoSansArabic[wght].ttf')if lang=='fa'else('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/dejavu/DejaVuSans.ttf','/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf'))
 for name in candidates+('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/dejavu/DejaVuSans.ttf'):
  if Path(name).exists():return name
 raise RuntimeError('Verified caption font unavailable')

def safe_geometry(value,size):
 if value.get('package_count')!=1 or type(value.get('geometry_confidence'))not in(int,float)or value['geometry_confidence']<.9:raise RuntimeError('Caption geometry uncertain')
 w,h=size
 def box(k):
  a=value.get(k)
  if not isinstance(a,list)or len(a)!=4 or any(type(x)not in(int,float)or not 0<=x<=1000 for x in a):raise RuntimeError('Invalid caption anchor')
  x0,y0,x1,y1=a
  if x1<=x0 or y1<=y0:raise RuntimeError('Invalid caption anchor')
  return [x0*w/1000,y0*h/1000,x1*w/1000,y1*h/1000]
 package=box('package_bbox');afp=box('afp_bbox');symbol=box('symbol_bbox');result={}
 for lang,anchor in [('english',afp),('persian',symbol)]:
  q=value.get(lang+'_quad')
  if not isinstance(q,list)or len(q)!=4:raise RuntimeError('Missing caption quad')
  if any(not isinstance(p,list)or len(p)!=2 or any(type(x)not in(int,float)or not 0<=x<=1000 for x in p)for p in q):raise RuntimeError('Invalid caption quad')
  q=[(x*w/1000,y*h/1000)for x,y in q];xs=[p[0]for p in q];ys=[p[1]for p in q]
  width=min(math.dist(q[0],q[1]),math.dist(q[3],q[2]));height=min(math.dist(q[0],q[3]),math.dist(q[1],q[2]))
  if width<(85 if lang=='english'else 55)or not 10<=height<=50 or width/height<3:raise RuntimeError('Caption area too small or distorted')
  if min(xs)<package[0]+2 or max(xs)>package[2]-2 or min(ys)<anchor[1]+(anchor[3]-anchor[1])*.65 or max(ys)>package[3]-(package[3]-package[1])*.08:raise RuntimeError('Caption overlaps mark or leaves sleeve')
  if abs(sum(xs)/4-(anchor[0]+anchor[2])/2)>(package[2]-package[0])*.2:raise RuntimeError('Caption not aligned with its mark')
  crosses=[]
  for i in range(4):
   a,b,c=q[i],q[(i+1)%4],q[(i+2)%4];crosses.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
  if min(crosses)<=0:raise RuntimeError('Non-convex caption geometry')
  result[lang]=(q,width,height)
 return result

def inverse_coefficients(q,width,height):
 # Destination -> source homography, solved without a numeric dependency.
 src=[(0,0),(width,0),(width,height),(0,height)];rows=[]
 for(x,y),(u,v)in zip(q,src):rows +=[[x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]]
 for i in range(8):
  pivot=max(range(i,8),key=lambda r:abs(rows[r][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
  if abs(rows[i][i])<1e-9:raise RuntimeError('Degenerate caption geometry')
  z=rows[i][i];rows[i]=[v/z for v in rows[i]]
  for j in range(8):
   if j!=i:
    z=rows[j][i];rows[j]=[a-z*b for a,b in zip(rows[j],rows[i])]
 return tuple(r[-1]for r in rows)

def typeset(raw,locations):
 if not features.check('raqm'):raise RuntimeError('Joined Persian shaping unavailable; no disconnected-letter fallback')
 im=Image.open(io.BytesIO(raw)).convert('RGB');geometry=safe_geometry(locations,im.size);details={}
 for lang,text,script in [('english',ENGLISH,'en'),('persian',PERSIAN,'fa')]:
  q,width,height=geometry[lang];width=int(width);height=int(height);direction='rtl'if script=='fa'else'ltr';path=font_file(script)
  x0=max(0,int(min(p[0]for p in q)));x1=min(im.width,int(math.ceil(max(p[0]for p in q)))+1);y0=max(2,int(min(p[1]for p in q)));y1=min(im.height-3,int(math.ceil(max(p[1]for p in q)))+1)
  # Remove small caption-ink components only. Whole-image connected
  # components keep the much larger AFP letters and water-drop mark protected,
  # even when the old caption baseline is tilted or the locator is imprecise.
  px=im.load();pb=locations['package_bbox'];crop=(max(0,int(pb[0]*im.width/1000)),max(0,int(pb[1]*im.height/1000)),min(im.width,int(pb[2]*im.width/1000)+1),min(im.height,int(pb[3]*im.height/1000)+1))
  soft=im.filter(ImageFilter.GaussianBlur(2)).load()
  points={(x,y)for y in range(crop[1],crop[3])for x in range(crop[0],crop[2])if (px[x,y][2]>px[x,y][0]*1.08 and px[x,y][0]<165 and px[x,y][1]<190)or(sum(px[x,y])+18<sum(soft[x,y])and max(px[x,y])<210)}
  small=Image.new('L',im.size,0);protected=Image.new('L',im.size,0);sm=small.load();pr=protected.load()
  while points:
   seed=points.pop();stack=[seed];component=[]
   while stack:
    x,y=stack.pop();component.append((x,y))
    for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
     if n in points:points.remove(n);stack.append(n)
   xs=[p[0]for p in component];ys=[p[1]for p in component];ch=max(ys)-min(ys)+1;cw=max(xs)-min(xs)+1
   target=sm if ch<=22 and cw<=100 and x0-12<sum(xs)/len(xs)<x1+12 and y0-14<sum(ys)/len(ys)<y1+14 else pr
   for point in component:target[point]=255
  from PIL import ImageChops
  mask=ImageChops.subtract(small.filter(ImageFilter.MaxFilter(5)),protected.filter(ImageFilter.MaxFilter(3)))
  clean=im.copy();cp=clean.load()
  bounds=mask.getbbox()
  if bounds:
   for x in range(bounds[0],bounds[2]):
    samples=[px[x,y]for y in range(max(0,y0-15),min(im.height,y1+15))if min(px[x,y])>105 and max(px[x,y])-min(px[x,y])<32]
    if not samples:raise RuntimeError('Clean sleeve shading unavailable')
    color=tuple(sorted(v[c]for v in samples)[len(samples)//2]for c in range(3))
    for y in range(bounds[1],bounds[3]):
     if mask.getpixel((x,y)):cp[x,y]=color
   im=Image.composite(clean,im,mask)
  scale=4;canvas=Image.new('RGBA',(width*scale,height*scale),(0,0,0,0));draw=ImageDraw.Draw(canvas)
  for points in range(height*scale,8*scale,-1):
   font=ImageFont.truetype(path,points,layout_engine=ImageFont.Layout.RAQM);box=draw.textbbox((0,0),text,font=font,direction=direction,language=script)
   if box[2]-box[0]<=width*scale*.96 and box[3]-box[1]<=height*scale*.92:break
  else:raise RuntimeError('Caption too small to typeset legibly')
  draw.text(((width*scale-box[2]+box[0])/2-box[0],(height*scale-box[3]+box[1])/2-box[1]),text,font=font,fill=(35,67,126,255),direction=direction,language=script)
  canvas=canvas.resize((width,height),Image.Resampling.LANCZOS)
  warped=canvas.transform(im.size,Image.Transform.PERSPECTIVE,inverse_coefficients(q,width,height),Image.Resampling.BICUBIC)
  if ImageChops.multiply(warped.getchannel('A'),protected).getbbox():raise RuntimeError('New caption would overlap original logo')
  im=Image.alpha_composite(im.convert('RGBA'),warped).convert('RGB');details[lang]={'text':text,'font':Path(path).name,'point_size':points/scale,'quad':q}
 return im,{'policy':POLICY,'source_sha256':hashlib.sha256(raw).hexdigest(),'captions':details}
