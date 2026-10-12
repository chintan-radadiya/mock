import json,csv,re
from pathlib import Path
root=Path('extraction/structured')
tita={'dilr-sectional-1':{19:'3',24:'74',32:'4',40:'5'},'simcat-2':{58:'1324',60:'1',66:'3241',68:'5',76:'15',80:'184',81:'7670',82:'20',85:'204',86:'17',93:'20',97:'6',101:'1085',105:'524',106:'90',107:'77',108:'12',112:'405',113:'400'}}
allrecords={}
for d in tita:
 records=[]
 for p in sorted((root/d).glob('*.txt'),key=lambda p:int(p.stem)):
  n=int(p.stem);text=p.read_text(encoding='utf-8');meta=json.loads(p.with_suffix('.meta.json').read_text());rows=list(csv.DictReader(p.with_suffix('.tsv').open(encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE))
  words=[r for r in rows if r['text'].strip()];lines={}
  for r in words:lines.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
  ls=[{'text':' '.join(w['text'] for w in v),'y':min(int(w['top']) for w in v)/3+meta['y'],'words':v} for v in lines.values()]
  before=[]
  for l in ls:
   if re.search(r'Statistics|Correct Answer|Enter your response',l['text']):break
   before.append(l)
  qnum=next((int(m[1]) for l in before if (m:=re.search(r'(\d{1,2})/(?:22|24)',l['text']))),None)
  opts=[];prompt=[]
  for l in before:
   if re.search(r'\d{1,2}/(?:22|24)',l['text']):continue
   m=re.match(r'^([ABCD])(?:\s|_|[a-z](?=\s))',l['text'])
   if m and (len(opts)==0 and m[1]=='A' or len(opts)>0 and ord(m[1])==ord(opts[-1]['id'])+1):opts.append({'id':m[1],'text':re.sub(r'^([ABCD])[a-z]?[_\s]*','',l['text']),'y':l['y']})
   elif opts:opts[-1]['text']+=' '+l['text']
   else:prompt.append(l['text'])
  answer=tita[d].get(n)
  if answer is None and len(opts)==4 and meta['ticks']:answer=min(opts,key=lambda o:abs(o['y']-meta['ticks'][0]))['id']
  cat=re.search(r'Question Type\s+([ABC])',text)
  records.append({'image':n,'number':qnum,'prompt':'\n'.join(prompt),'options':opts if n not in tita[d] else [],'answer':[answer] if n in tita[d] else answer,'category':cat[1] if cat else None,'ticks':meta['ticks'],'raw':text})
 allrecords[d]=records
Path('extraction/draft-records.json').write_text(json.dumps(allrecords,ensure_ascii=False,indent=2),encoding='utf-8')
for d,rs in allrecords.items():
 for r in rs: print(d,r['image'],r['number'],r['answer'],len(r['options']),r['prompt'][:95])
