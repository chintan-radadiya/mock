import csv,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
from concurrent.futures import ThreadPoolExecutor
records=json.loads(Path('extraction/clean-records.json').read_text(encoding='utf-8'))
def run(job):
 d,q=job;n=q['image'];p=Path(f'extraction/structured/{d}/{n}.tsv');m=json.loads(p.with_suffix('.meta.json').read_text());rows=list(csv.DictReader(p.open(encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE));headers=[r for r in rows if r['text']=='Toppers'];result={}
 if not headers:return d,n,result
 h=headers[-1];hx=int(h['left'])/3+m['x'];hy=int(h['top'])/3+m['y'];im=Image.open(f'source-images/{d}/Screenshot ({n}).png')
 for term,key in [('Attempt','topperAttemptPercent'),('Accuracy','topperAccuracyPercent'),('Taken','topperTimeSeconds'),('PValue','topperPValue')]:
  matches=[r for r in rows if r['text'].lower()==term.lower() and int(r['top'])/3+m['y']>hy]
  if not matches:continue
  r=matches[-1];y=int(r['top'])/3+m['y'];height=int(r['height'])/3
  if y+height>1015:continue
  crop=im.crop((int(hx)-63,int(y)-4,int(hx)+65,int(y+height)+5));op=Path(f'extraction/structured/{d}/{n}-{key}.png');crop.resize((crop.width*5,crop.height*5)).save(op)
  val=subprocess.run(['tesseract',str(op),'stdout','--psm','7','-c','tessedit_char_whitelist=0123456789.%:'],capture_output=True,encoding='utf-8').stdout.strip()
  if key.endswith('Seconds'):
   if re.fullmatch(r'\d+:[0-5]\d',val):a,b=val.split(':');result[key]=int(a)*60+int(b)
  elif re.fullmatch(r'\d+(?:\.\d+)?%?',val) and 0<=float(val.rstrip('%'))<=100:result[key]=float(val.rstrip('%'))
 return d,n,result
result={d:{} for d in records}
with ThreadPoolExecutor(max_workers=4) as pool:
 for d,n,b in pool.map(run,[(d,q) for d,rs in records.items() for q in rs]):result[d][n]=b;print(d,n,b,flush=True)
Path('extraction/benchmarks-reviewed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
