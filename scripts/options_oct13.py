from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import json,numpy as np
from parse_oct13 import ocr

def run(job):
 d,r=job
 if len(r.get('edges',[]))!=8:return r
 im=Image.open(Path('source-images')/d/r['file']).convert('RGB');x=r['x'];edges=r['edges'];a=np.array(im).astype(int)
 starts=[]
 for top,bottom in zip(edges[::2],edges[1::2]):
  pix=a[top+8:bottom-8,x:x+125];mask=(pix[:,:,0]>205)&(pix[:,:,0]<225)&(abs(pix[:,:,0]-pix[:,:,1])<3)&(abs(pix[:,:,1]-pix[:,:,2])<3)
  cols=np.where(mask.sum(axis=0)>=8)[0];spans=[]
  for c in cols:
   if not spans or c>spans[-1][-1]+1:spans.append([int(c)])
   else:spans[-1].append(int(c))
  candidates=[s for s in spans if 18<=len(s)<=40]
  if candidates:starts.append(x+candidates[0][-1]+8)
 if not starts:print('NO BADGE',d,r['index']);return r
 left=round(sum(starts)/len(starts));out=Path('extraction/oct13')/d/Path(r['file']).stem
 for k,(top,bottom) in enumerate(zip(edges[::2],edges[1::2])):
  text=ocr(im.crop((left,top+3,im.width-40,bottom-2)),out/f'clean-option-{k}')
  r['options'][k]['text']=' '.join(text.split()).strip('| ')
 return r

if __name__=='__main__':
 rs=json.loads(Path('extraction/oct13-records.json').read_text(encoding='utf-8'))
 with ThreadPoolExecutor(max_workers=6) as pool:rs=list(pool.map(run,[('simcat-3' if i<68 else 'take-home-1',r) for i,r in enumerate(rs)]))
 Path('extraction/oct13-records.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2),encoding='utf-8')
