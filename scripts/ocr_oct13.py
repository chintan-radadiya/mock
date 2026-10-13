from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess,json

def run(p):
    out=Path('extraction/oct13')/p.parent.name/p.stem
    out.mkdir(parents=True,exist_ok=True)
    im=Image.open(p).convert('RGB');w,h=im.size
    parts={'right':(w//2 if w>1000 else 0,0,w,h)}
    if w>1000:parts['left']=(0,0,w//2,h)
    for label,box in parts.items():
        stem=out/label
        im.crop(box).resize(((box[2]-box[0])*3,h*3)).save(str(stem)+'.png')
        subprocess.run(['tesseract',str(stem)+'.png',str(stem),'--psm','6','txt','tsv'],capture_output=True,check=True)
    return p.parent.name+' '+p.stem

paths=[p for d in ['simcat-3','take-home-1','simcat-4'] for p in sorted((Path('source-images')/d).glob('*.png'),key=lambda p:int(p.stem.split()[-1]))]
with ThreadPoolExecutor(max_workers=6) as pool:
    for result in pool.map(run,paths):print(result,flush=True)
