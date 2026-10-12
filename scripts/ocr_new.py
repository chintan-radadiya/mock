from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess,re
out=Path('extraction/new');out.mkdir(exist_ok=True)
def run(p):
 folder=out/p.parent.name;folder.mkdir(exist_ok=True)
 im=Image.open(p); im=im.crop((0,145,1920,1020)).resize((2880,1312))
 tmp=folder/(p.stem+'.png');im.save(tmp)
 r=subprocess.run(['tesseract',str(tmp),'stdout','--psm','3'],capture_output=True,encoding='utf-8')
 (folder/(p.stem+'.txt')).write_text(r.stdout,encoding='utf-8')
 return p.name
paths=[p for d in ['dilr-sectional-1','simcat-2'] for p in (Path('source-images')/d).glob('*.png')]
with ThreadPoolExecutor(max_workers=4) as pool:
 for n in pool.map(run,paths): print(n,flush=True)
