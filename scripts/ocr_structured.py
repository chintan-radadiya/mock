from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess,re,json
out=Path('extraction/structured');out.mkdir(exist_ok=True)
def run(p):
 n=int(re.search(r'\((\d+)\)',p.name)[1]); d=p.parent.name
 if d=='dilr-sectional-1': x0,x1,y=(972,1880,185) if n<=36 else (910,1777,155)
 elif 57<=n<=61 or 66<=n<=68: x0,x1,y=638,1154,155
 elif n>=92:x0,x1,y=532,1225,155
 else:x0,x1,y=910,1777,155
 folder=out/d;folder.mkdir(exist_ok=True);stem=folder/str(n)
 im=Image.open(p);im.crop((x0,y,x1,1018)).resize(((x1-x0)*3,(1018-y)*3)).save(str(stem)+'.png')
 subprocess.run(['tesseract',str(stem)+'.png',str(stem),'--psm','6','txt','tsv'],capture_output=True)
 # green correct marker is just outside option border, before navigation sidebar
 ticks=[]
 for yy in range(y,850):
  hits=sum(1 for xx in range(x1-28,x1) if (lambda c:c[1]>c[0]+20 and c[1]>c[2]+8 and c[1]>120)(im.getpixel((xx,yy))[:3]))
  if hits>=3:ticks.append(yy)
 spans=[]
 for yy in ticks:
  if not spans or yy>spans[-1][-1]+1:spans.append([yy])
  else:spans[-1].append(yy)
 (folder/(str(n)+'.meta.json')).write_text(json.dumps({'x':x0,'y':y,'right':x1,'ticks':[sum(a)/len(a) for a in spans if len(a)>4]}))
 return d+' '+str(n)
paths=[p for d in ['dilr-sectional-1','simcat-2'] for p in (Path('source-images')/d).glob('*.png')]
with ThreadPoolExecutor(max_workers=4) as pool:
 for n in pool.map(run,paths):print(n,flush=True)
