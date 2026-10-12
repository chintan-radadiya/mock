from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess
out=Path('extraction/new')
def run(p):
 im=Image.open(p); folder=out/p.parent.name
 for label,box in [('left',(25,155,890,1015)),('right',(910,155,1777,1015))]:
  crop=folder/(p.stem+'-'+label+'.png'); im.crop(box).resize((1730,1720)).save(crop)
  r=subprocess.run(['tesseract',str(crop),'stdout','--psm','6'],capture_output=True,encoding='utf-8')
  (folder/(p.stem+'-'+label+'.txt')).write_text(r.stdout,encoding='utf-8')
 return p.name
paths=[p for d in ['dilr-sectional-1','simcat-2'] for p in (Path('source-images')/d).glob('*.png')]
with ThreadPoolExecutor(max_workers=4) as pool:
 for n in pool.map(run,paths): print(n,flush=True)
