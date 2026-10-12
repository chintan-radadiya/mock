from PIL import Image
from pathlib import Path
import json
r=json.loads(Path('extraction/draft-records.json').read_text(encoding='utf-8'))
for d,rs in r.items():
 for q in rs:
  if isinstance(q['answer'],list):continue
  n=q['image'];m=json.loads(Path(f'extraction/structured/{d}/{n}.meta.json').read_text());im=Image.open(f'source-images/{d}/Screenshot ({n}).png');x0=m['x'];x1=m['right']-45
  hits=[]
  for y in range(m['y']+30,950):
   count=0
   for x in range(x0+20,x1-15,3):
    a,b,c=im.getpixel((x,y))[:3]
    if (190<a<240 and abs(a-b)<5 and abs(b-c)<5) or (a<80 and 130<b<230 and c>220):count+=1
   if count>((x1-x0-35)/3)*.75:hits.append(y)
  edges=[]
  for y in hits:
   if not edges or y>edges[-1][-1]+1:edges.append([y])
   else:edges[-1].append(y)
  edges=[round(sum(e)/len(e)) for e in edges]
  q['edges']=edges
  print(d,n,edges[:10])
Path('extraction/box-records.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
