from pathlib import Path
from PIL import Image,ImageOps
from concurrent.futures import ThreadPoolExecutor
import csv,json,re,subprocess

def lines(path):
    rows=list(csv.DictReader(path.open(encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE));groups={}
    for r in rows:
        if r['text'].strip():groups.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
    return [{'text':' '.join(w['text'] for w in ws),'x':min(int(w['left']) for w in ws)/3,'y':min(int(w['top']) for w in ws)/3,'bottom':max(int(w['top'])+int(w['height']) for w in ws)/3} for ws in groups.values()]

def ocr(im,path,psm=6,digits=False):
    im=ImageOps.grayscale(im)
    im=ImageOps.expand(im,border=10,fill=255);im.resize((im.width*3,im.height*3)).save(str(path)+'.png')
    cmd=['tesseract',str(path)+'.png','stdout','--psm',str(psm)]
    if digits:cmd+=['-c','tessedit_char_whitelist=0123456789.-']
    return subprocess.run(cmd,capture_output=True,encoding='utf-8',check=True).stdout.strip()

def run(job):
    d,i,p=job;out=Path('extraction/oct13')/d/p.stem;ls=lines(out/'right.tsv')
    im=Image.open(p).convert('RGB');w,h=im.size;x=w//2 if w>1000 else 0
    stats=next((l['y'] for l in ls if 'Statistics' in l['text']),h)
    qline=next((l for l in ls if re.search(r'\d{1,2}\s*/\s*(?:22|24)',l['text'])),None)
    start=qline['bottom']+3 if qline else 0
    enter=next((l for l in ls if 'Enter your response' in l['text'] or 'Enter your answer' in l['text']),None)
    correct=next((l for l in ls if 'Correct Answer' in l['text']),None)
    r={'file':p.name,'index':i,'section':'VARC' if i<=24 else 'DILR' if i<=46 else 'QA','number':i if i<=24 else i-24 if i<=46 else i-46,'stats':stats,'x':x,'raw':(out/'right.txt').read_text(encoding='utf-8')}
    if enter:
        r['type']='TITA';r['prompt']='\n'.join(l['text'] for l in ls if start<=l['y']<enter['y'])
        if correct:
            answer_y=int(correct['y']+14);answer_x=x+int(correct['x'])
            r['answer']=[ocr(im.crop((max(0,answer_x),max(0,answer_y-3),min(w,answer_x+230),min(h,answer_y+45))),out/'answer',7,True)]
        else:r['answer']=[]
    else:
        r['type']='MCQ'
        ys=[]
        for y in range(int(start),int(stats)-8):
            cs=[im.getpixel((xx,y)) for xx in range(x+120,w-70,4)]
            hits=sum(1 for a,b,c in cs if (180<a<245 and abs(a-b)<6 and abs(b-c)<6) or (a<100 and b>130 and c>220))
            if cs and hits/len(cs)>.85:ys.append(y)
        spans=[]
        for y in ys:
            if not spans or y>spans[-1][-1]+1:spans.append([y])
            else:spans[-1].append(y)
        edges=[round(sum(s)/len(s)) for s in spans]
        if len(edges)==9:edges=edges[:8]
        r['edges']=edges
        r['prompt']='\n'.join(l['text'] for l in ls if start<=l['y']<(edges[0] if edges else stats))
        r['options']=[];r['answer']=None
        if len(edges)==8:
            for k,(top,bottom) in enumerate(zip(edges[::2],edges[1::2])):
                # OCR only option content, excluding letter badge and answer tick.
                left=next((xx for xx in range(x,w-100) if (lambda c:180<c[0]<245 and abs(c[0]-c[1])<6 and abs(c[1]-c[2])<6 or c[0]<100 and c[1]>130 and c[2]>220)(im.getpixel((xx,top)))),x)
                text=ocr(im.crop((x+3,top+3,w-40,bottom-2)),out/f'option-{k}')
                text=re.sub(r'^'+chr(65+k)+r'[\s_]+','',text)
                r['options'].append({'id':chr(65+k),'text':' '.join(text.split())})
                green=sum(1 for yy in range(top+2,bottom-1) for xx in range(w-35,w) if (lambda c:c[1]>c[0]+20 and c[1]>c[2]+8 and c[1]>120)(im.getpixel((xx,yy))))
                if green>20:r['answer']=chr(65+k)
    return r

if __name__=='__main__':
    jobs=[]
    for d in ['simcat-3','take-home-1','simcat-4']:
        paths=sorted((Path('source-images')/d).glob('*.png'),key=lambda p:p.name)
        if d=='simcat-4': paths=[p for p in paths if int(p.stem.split()[-1])<=112823]
        else: paths=paths[:68]
        jobs.extend((d,i,p) for i,p in enumerate(paths,1))
    with ThreadPoolExecutor(max_workers=6) as pool:
        records=list(pool.map(run,jobs))
    Path('extraction/oct13-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in records:print(r['file'],r['section'],r['number'],r['answer'],len(r.get('edges',[])),r['prompt'][:65])
