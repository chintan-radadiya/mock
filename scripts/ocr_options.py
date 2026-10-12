import json,subprocess
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
records=json.loads(Path('extraction/box-records.json').read_text(encoding='utf-8'))
def run(job):
 d,q=job;n=q['image'];m=json.loads(Path(f'extraction/structured/{d}/{n}.meta.json').read_text());im=Image.open(f'source-images/{d}/Screenshot ({n}).png');out=Path(f'extraction/structured/{d}')
 if isinstance(q['answer'],list):return d,q
 big=d=='dilr-sectional-1' or 69<=n<=73 or n>=92
 edges=q['edges'];opts=[];scores=[]
 for j in range(4):
  y0,y1=edges[2*j:2*j+2];x0=m['x']+(67 if big else 50);x1=m['right']-(57 if n>=92 else 44 if d=='dilr-sectional-1' and n<=36 else 32)
  crop=im.crop((x0,y0+3,x1,y1-3));crop=crop.resize((crop.width*3,crop.height*3));p=out/f'{n}-option{j}.png';crop.save(p)
  result=subprocess.run(['tesseract',str(p),'stdout','--psm','6'],capture_output=True,encoding='utf-8').stdout
  opts.append({'id':'ABCD'[j],'text':' '.join(result.split())})
  score=0
  for y in range(y0+2,y1-2):
   for x in range(x1+2,m['right']):
    a,b,c=im.getpixel((x,y))[:3]
    if b>a+20 and b>c+8 and b>120:score+=1
  scores.append(score)
 q['options']=opts;q['answer']='ABCD'[scores.index(max(scores))] if max(scores)>20 else None;q['answerPixelCounts']=scores
 # use tesseract text before first option from tight region rather than label parsing
 p=out/f'{n}-prompt.png';crop=im.crop((m['x'],m['y']+28 if m['y']==155 else m['y']+42,m['right']-15,edges[0]-5));crop.resize((crop.width*3,crop.height*3)).save(p)
 result=subprocess.run(['tesseract',str(p),'stdout','--psm','6'],capture_output=True,encoding='utf-8').stdout
 q['prompt']=result.strip();return d,q
jobs=[(d,q) for d,rs in records.items() for q in rs]
res={d:[] for d in records}
with ThreadPoolExecutor(max_workers=4) as pool:
 for d,q in pool.map(run,jobs):res[d].append(q);print(d,q['image'],q['answer'],flush=True)
Path('extraction/clean-records.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
