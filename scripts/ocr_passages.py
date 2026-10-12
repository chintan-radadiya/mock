from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import subprocess
jobs=[('dilr-sectional-1',19,950),('dilr-sectional-1',24,950),('dilr-sectional-1',31,950),('dilr-sectional-1',36,950),('dilr-sectional-1',41,870),('simcat-2',45,893),('simcat-2',49,893),('simcat-2',53,893),('simcat-2',62,893),('simcat-2',69,870),('simcat-2',74,893),('simcat-2',78,893),('simcat-2',82,893),('simcat-2',87,893)]
def run(job):
 d,n,x=job;im=Image.open(f'source-images/{d}/Screenshot ({n}).png');p=Path(f'extraction/structured/{d}/{n}-passage');im.crop((30,195 if x!=893 else 165,x-10,1018)).resize(((x-40)*2,(1018-(195 if x!=893 else 165))*2)).save(str(p)+'.png');subprocess.run(['tesseract',str(p)+'.png',str(p),'--psm','6'],capture_output=True);return n
with ThreadPoolExecutor(max_workers=4) as pool:
 for n in pool.map(run,jobs):print(n,flush=True)
