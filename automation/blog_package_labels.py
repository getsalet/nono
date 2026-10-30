"""Exact owner-approved package captions; geometry and blind readback are separate.
Never redraw the AFP mark or replace the product photograph. Only two small
caption regions on the white package sleeve may be cleaned and typeset.
"""
import base64,hashlib,io,json,math,os,re,time,unicodedata
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
 try:
  g=detect_geometry(raw);boxes=[g['afp_bbox'],g['symbol_bbox']];x0=min(a[0]for a in boxes)*im.width/1000-24;x1=max(a[2]for a in boxes)*im.width/1000+32;y0=min(a[1]for a in boxes)*im.height/1000-8;y1=max(max(p[1]for p in g[k+'_quad'])for k in ('english','persian'))*im.height/1000+12
  detail=im.crop((max(0,int(x0)),max(0,int(y0)),min(im.width,int(x1)),min(im.height,int(y1))))
 except RuntimeError:detail=im.crop((0,int(im.height*.27),int(im.width*.62),im.height))
 detail=detail.resize((detail.width*4,detail.height*4),Image.Resampling.LANCZOS);buf=io.BytesIO();detail.save(buf,'PNG')
 instruction=('Read the actual printed package captions literally, without translating, guessing, spelling correction or completing words. No expected wording is provided. '
  'Return the exact visible characters, preserving Persian dots and letters. Ignore contact watermark and side-panel fine print. '
  'The FULL FRAME establishes context. Detail views show the SAME image, not new products. '
  'english_text is the small caption BELOW the large AFP letters. persian_text is the company caption BELOW the BLUE WATER-DROP SYMBOL to the left of AFP. '
  'Two rectified caption crops, if present, contain only the original photographed/printed pixels enlarged for reading. They do not provide expected text. '
  'For unreadable text return empty string and legible=false; never infer words from product type or a familiar company name. '
  'Return JSON only: {"english_text":"","persian_text":"","english_legible":false,"persian_legible":false}.')
 content=[{'type':'text','text':instruction}]
 for label,data,mime in [('FULL FRAME',full.getvalue(),'image/webp'),('OVERLAPPING LEFT DETAIL; coordinates refer to FULL FRAME',buf.getvalue(),'image/png')]:
  content +=[{'type':'text','text':label},{'type':'image_url','image_url':{'url':'data:'+mime+';base64,'+base64.b64encode(data).decode(),'detail':'high'}}]
 try:
  g=detect_geometry(raw)
  for lang in ('english','persian'):
   q=[(x*im.width/1000,y*im.height/1000)for x,y in g[lang+'_quad']]
   # PIL QUAD order: TL, BL, BR, TR. No generated text or spelling hints.
   width=max(1,round(math.dist(q[0],q[1])*8));height=max(1,round(math.dist(q[0],q[3])*8))
   strip=im.transform((width,height),Image.Transform.QUAD,tuple(v for pt in (q[0],q[3],q[2],q[1])for v in pt),Image.Resampling.BICUBIC)
   data=io.BytesIO();strip.save(data,'PNG')
   content+=[{'type':'text','text':lang.upper()+' CAPTION ONLY; same original pixels, perspective-rectified for literal reading.'},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode(),'detail':'high'}}]
 except RuntimeError:pass
 payload={'model':os.getenv('IMAGE_REVIEW_MODEL','agnes-3.0-flash'),'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'user','content':content}]}
 for attempt in range(2):
  key=roya.BASE._key_pool.next()
  try:
   response=roya.BASE.fetch_json(roya.BASE.AGNES_BASE+'/chat/completions',{'Authorization':'Bearer '+key,'Content-Type':'application/json'},payload,timeout=180);break
  except RuntimeError as exc:
   status=getattr(exc,'http_status',None);delay=getattr(exc,'rate_limit_retry_after_seconds',None)or getattr(exc,'retry_after_seconds',None)or 5
   if attempt or status not in(429,500,502,503,504)or delay>180:raise
   time.sleep(max(5,delay))
 value=response['choices'][0]['message']['content']
 if isinstance(value,list):value=''.join(x.get('text','')for x in value if isinstance(x,dict))
 return json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip(),flags=re.I))

def font_file(lang):
 # Bundled, hash-pinned fonts make local and CI rendering identical.
 import tempfile
 name,digest=FONT_ASSETS[lang]
 raw=base64.b64decode((Path(__file__).parent/'assets/package-caption-fonts'/(name+'.b64')).read_text())
 if hashlib.sha256(raw).hexdigest()!=digest:raise RuntimeError('Verified caption font checksum failed')
 target=Path(tempfile.gettempdir())/('afp-'+digest+'.ttf')
 if not target.exists()or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:target.write_bytes(raw)
 return str(target)
FONT_ASSETS={'fa': ('NotoSansArabic-Regular.ttf', 'c270782ee478c685f95509e724125729e1284c82ebfbe414cc67926f29449e1d'), 'en': ('NotoSans-Caption.ttf', 'a4c98c43b4fe681cc0b49ecddc820cfc6e79074f4b693b8a6ccc38dadcda24e9')}

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
 from PIL import ImageChops
 im=Image.open(io.BytesIO(raw)).convert('RGB');geometry=safe_geometry(locations,im.size);details={}
 px=im.load();pb=locations['package_bbox'];crop=(max(0,int(pb[0]*im.width/1000)),max(0,int(pb[1]*im.height/1000)),min(im.width,int(pb[2]*im.width/1000)+1),min(im.height,int(pb[3]*im.height/1000)+1))
 anchors=[[v*(im.width if i%2==0 else im.height)/1000 for i,v in enumerate(locations[k])]for k in ('afp_bbox','symbol_bbox')]
 afp,symbol=anchors;aw=afp[2]-afp[0];ah=afp[3]-afp[1]
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
  in_caption=False
  for lang in ('english','persian'):
   q=geometry[lang][0];x0=min(p[0]for p in q);x1=max(p[0]for p in q);y0=min(p[1]for p in q)
   if x0-6<sum(xs)/len(xs)<x1+6 and sum(ys)/len(ys)>y0-14 and max(ys)<crop[3]-(crop[3]-crop[1])*.09:in_caption=True
  target=sm if ch<=max(22,ah*.65)and cw<=aw*1.1 and in_caption else pr
  for point in component:target[point]=255
 mask=ImageChops.subtract(small.filter(ImageFilter.MaxFilter(5)),protected.filter(ImageFilter.MaxFilter(3)))
 clean=im.copy();cp=clean.load();bounds=mask.getbbox()
 if bounds:
  for x in range(bounds[0],bounds[2]):
   samples=[px[x,y]for y in range(max(crop[1],bounds[1]-10),min(crop[3],bounds[3]+10))if min(px[x,y])>105 and max(px[x,y])-min(px[x,y])<32]
   if not samples:raise RuntimeError('Clean sleeve shading unavailable')
   color=tuple(sorted(v[c]for v in samples)[len(samples)//2]for c in range(3))
   for y in range(bounds[1],bounds[3]):
    if mask.getpixel((x,y)):cp[x,y]=color
  im=Image.composite(clean,im,mask)
 for lang,text,script in [('english',ENGLISH,'en'),('persian',PERSIAN,'fa')]:
  q,width,height=geometry[lang];width=int(width);height=int(height);direction='rtl'if script=='fa'else'ltr';path=font_file(script)
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
 original=Image.open(io.BytesIO(raw)).convert('RGB')
 protected_boxes=locations.get('afp_glyph_bboxes',[locations['afp_bbox']])+[locations['symbol_bbox']]
 for box_ in protected_boxes:
  a=[v*(im.width if i%2==0 else im.height)/1000 for i,v in enumerate(box_)]
  for y in range(max(0,int(a[1])),min(im.height,int(math.ceil(a[3])))):
   for x in range(max(0,int(a[0])),min(im.width,int(math.ceil(a[2])))):
    rgb=original.getpixel((x,y))
    if rgb[2]>rgb[0]*1.3 and rgb[2]>70 and rgb[0]<140 and im.getpixel((x,y))!=rgb:raise RuntimeError('Caption would modify original brand mark')
 return im,{'policy':POLICY,'source_sha256':hashlib.sha256(raw).hexdigest(),'captions':details}

def detect_geometry(raw):
 """Local geometric anchors from the three large blue AFP glyphs and blue band.
 Ambiguous/occluded marks fail closed; no template coordinates or article IDs.
 The A/F/P enclosed-hole pattern is an additional guard against field objects.
 """
 import itertools
 im=Image.open(io.BytesIO(raw)).convert('RGB');w,h=im.size;px=im.load()
 points={(x,y)for y in range(int(h*.25),h)for x in range(int(w*.04),int(w*.65))if px[x,y][0]<150 and px[x,y][2]>60 and px[x,y][2]>px[x,y][0]*1.2 and px[x,y][2]>px[x,y][1]*1.06};comps=[]
 while points:
  seed=points.pop();stack=[seed];part=[]
  while stack:
   x,y=stack.pop();part.append((x,y))
   for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
    if n in points:points.remove(n);stack.append(n)
  if len(part)<60:continue
  xs=[p[0]for p in part];ys=[p[1]for p in part];comps.append({'box':(min(xs),min(ys),max(xs)+1,max(ys)+1),'area':len(part),'points':set(part)})
 def width(c):return c['box'][2]-c['box'][0]
 def height(c):return c['box'][3]-c['box'][1]
 def holes(c):
  x0,y0,x1,y1=c['box'];white={(x,y)for y in range(y0,y1)for x in range(x0,x1)if(x,y)not in c['points']};count=0
  while white:
   stack=[white.pop()];edge=False;area=0
   while stack:
    x,y=stack.pop();area+=1;edge|=x in(x0,x1-1)or y in(y0,y1-1)
    for n in((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
     if n in white:white.remove(n);stack.append(n)
   if not edge and area>=4:count+=1
  return count
 letters=sorted([c for c in comps if 22<=height(c)<=h*.15 and 8<=width(c)<=w*.09 and c['area']>=80],key=lambda c:c['box'][0])
 if len(letters)>35:raise RuntimeError('Caption anchors ambiguous')
 candidates=[]
 for group in itertools.combinations(letters,3):
  heights=[height(c)for c in group];average=sum(heights)/3
  if max(heights)>min(heights)*1.4:continue
  gaps=[group[i+1]['box'][0]-group[i]['box'][2]for i in(0,1)]
  if min(gaps)<0 or max(gaps)>average*.65:continue
  tops=[c['box'][1]for c in group]
  if max(tops)-min(tops)>average*.6:continue
  span=group[-1]['box'][2]-group[0]['box'][0]
  if not 1.65<=span/average<=4.2:continue
  if[holes(c)for c in group]!=[1,0,1]:continue
  candidates.append(group)
 if len(candidates)!=1:raise RuntimeError('Caption anchors not uniquely recognized')
 group=candidates[0];afp=(group[0]['box'][0],min(c['box'][1]for c in group),group[-1]['box'][2],max(c['box'][3]for c in group));aw=afp[2]-afp[0];ah=afp[3]-afp[1]
 bands=[c for c in comps if width(c)>aw*1.4 and height(c)>12 and c['area']>sum(a['area']for a in group)and c['box'][1]>afp[3]+8 and c['box'][0]<(afp[0]+afp[2])/2<c['box'][2]]
 if len(bands)!=1:raise RuntimeError('Caption blue base band ambiguous')
 band_component=bands[0];band=band_component['box']
 icons=[c for c in comps if 18<=width(c)<=aw*.9 and 15<=height(c)<=ah*2.5 and c['area']>150 and band[0]+10<c['box'][0]<c['box'][2]<afp[0]-4 and c['box'][1]>afp[1]-ah*1.8 and c['box'][3]<afp[3]+10]
 if not icons:raise RuntimeError('Caption water-drop symbol not located')
 icon=max(icons,key=lambda c:c['area'])['box']
 for c in icons:
  a=c['box']
  if max(0,a[0]-icon[2],icon[0]-a[2])<8 and max(0,a[1]-icon[3],icon[1]-a[3])<15:icon=(min(icon[0],a[0]),min(icon[1],a[1]),max(icon[2],a[2]),max(icon[3],a[3]))
 if icon[2]-icon[0]>aw*.9:raise RuntimeError('Caption symbol extent ambiguous')
 xs=[(c['box'][0]+c['box'][2])/2 for c in group];ys=[c['box'][3]for c in group];mx=sum(xs)/3;my=sum(ys)/3;slope=sum((x-mx)*(y-my)for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
 if abs(slope)>.3:raise RuntimeError('Caption viewing angle too steep')
 height_=max(18,min(26,ah*.42));left=max(afp[0]-aw*.12-2,icon[2]+8);right=min(afp[2]+aw*.12+2,band[2]-10)
 def y(x):return my+slope*(x-mx)+7
 english=[(left,y(left)),(right,y(right)),(right,y(right)+height_),(left,y(left)+height_)]
 iw=icon[2]-icon[0];cx=(icon[0]+icon[2])/2;left=max(band[0]+10,cx-iw*.7);right=min(afp[0]-8,cx+iw*.7);fy=icon[3]+7
 persian=[(left,fy+slope*(right-left)/2),(right,fy-slope*(right-left)/2),(right,fy-slope*(right-left)/2+height_),(left,fy+slope*(right-left)/2+height_)]
 for quad in(english,persian):
  for step in range(9):
   t=step/8;x=quad[3][0]*(1-t)+quad[2][0]*t;y=quad[3][1]*(1-t)+quad[2][1]*t
   below=[py for px_,py in band_component['points']if abs(px_-x)<=3]
   if not below or y>min(below)-4:raise RuntimeError('Caption white sleeve has insufficient room')
 package=(band[0]-3,max(0,min(afp[1]-ah*1.8,icon[1]-ah*.5)),band[2]+3,band[3]+5)
 normbox=lambda a:[v*1000/(w if i%2==0 else h)for i,v in enumerate(a)]
 normquad=lambda a:[[x*1000/w,y*1000/h]for x,y in a]
 result={'afp_glyph_bboxes':[normbox(c['box'])for c in group],'method':'local-afp-glyph-topology-v1','package_count':1,'geometry_confidence':1,'package_bbox':normbox(package),'afp_bbox':normbox(afp),'symbol_bbox':normbox(icon),'english_quad':normquad(english),'persian_quad':normquad(persian)}
 safe_geometry(result,im.size)
 return result


def enabled(root,expected):
 path=Path(root)/'data/blog-image-acceptance-policy.json'
 if not path.exists():return False
 flag=json.loads(path.read_text()).get('require_exact_package_labels',False)
 if type(flag)is not bool:raise RuntimeError('Invalid exact package caption policy')
 return expected=='tape20' and flag

def record_errors(record):
 if record.get('exact_labels_required')is not True:return []
 proof=record.get('package_label_review',{})
 if not isinstance(proof,dict)or proof.get('policy')!=POLICY or proof.get('sha256')!=record.get('sha256'):return ['Current hash-bound exact package caption review required']
 return exact_errors(proof.get('reading'))

def prepare_cached(cache):
 """Render once per candidate; preserve the cache on font/transport failure.
 OCR happens in the independent gate, never inside the image-provider lease.
 """
 cache=Path(cache);raw=cache.read_bytes();digest=hashlib.sha256(raw).hexdigest();path=cache.with_suffix('.captions.json')
 try:proof=json.loads(path.read_text())
 except (OSError,ValueError):proof={}
 if proof.get('policy')==POLICY and proof.get('sha256')==digest:return raw,proof
 try:im,proof=typeset(raw,detect_geometry(raw))
 except RuntimeError as exc:
  # Layout is a definitive candidate defect. Fonts/runtime failures are not.
  if str(exc).startswith(('Caption anchors','Caption blue','Caption water','Caption symbol','Caption viewing','Caption white','Caption area','Caption overlaps','Caption not aligned','New caption','Caption would modify')):raise RuntimeError('Product image rejected: '+str(exc))from None
  raise
 out=io.BytesIO();im.save(out,'WEBP',quality=95,method=6);result=out.getvalue();proof['sha256']=hashlib.sha256(result).hexdigest()
 tmp=cache.with_suffix('.tmp');tmp.write_bytes(result);tmp.replace(cache)
 path.write_text(json.dumps(proof,ensure_ascii=False,indent=2))
 return result,proof
