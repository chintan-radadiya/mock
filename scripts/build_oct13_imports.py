"""Reviewed image imports. Source graphs stay as original raster crops."""
from pathlib import Path
from PIL import Image
import json,re,io,base64,csv,statistics
from parse_oct13 import lines

ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'extraction/oct13-records.json').read_text(encoding='utf-8'))
TITA=[{5:'2143',21:'2413',23:'2',24:'4',29:'16',39:'11',42:'2',43:'5',44:'5',45:'1',46:'6',51:'1540',53:'900523',59:'25',62:'1920',66:'100',68:'460'},
      {17:'2143',18:'4231',23:'2',24:'4',25:'13',26:'231',32:'2',33:'261',44:'5',47:'27693',52:'46',55:'45',56:'42',59:'7'}]
OPTIONS=[{27:['1st','2nd','3rd','4th'],33:['0','1','2','3'],34:['9th March','10th March','11th March','12th March'],35:['17th March','18th March','19th March','20th March'],36:['8th March','9th March','10th March','11th March'],38:['9th March','10th March','11st March','13nd March'],50:['85π/4 sq. units','85π/2 sq. units','85π/6 sq. units','85π/8 sq. units'],56:['3','4','5','6'],60:['50√2','200','100√2','100'],61:['1/2','1/4','1/8','2']},
         {30:['9.6','9.6 or 4.45','4.65','9.6 or 4.65'],31:['53 1/3','47 1/3','46 2/3','42 2/3'],38:['0 litres per hour','1 litre per hour','2 litres per hour','3 litres per hour'],39:['4','6','8','10'],48:['a + b = c','1/a + 1/b = 1/c','a × b = c','a = bc'],54:['390/11','300/11','360/11','330/11'],60:['x < 3','x > 2','0 ≤ x ≤ 4','No real values of x satisfy the given inequality'],62:['4√3','2√3','3','4'],63:['20√7','10√7','(25/3)√7','(20/3)√7'],64:['1 : 1','25 : 64','64 : 25','More information is needed to answer this question'],65:['2√5 cm','4√5 cm','5 cm','6√5 cm'],67:['6^(2/3)','6^(1/3)','6^(1/9)','6^(2/9)']}]
PROMPTS=[{
25:'What is the point value awarded for 2nd place (P2)?',26:'Who finished 2nd in Star-Forge?',
47:'If set A = {a₁, a₂, a₃, …, a₁₀₀}, where a₁, a₂, a₃, …, a₁₀₀ form an arithmetic progression and the sum of the first n terms is Sₙ = 2n² + 3n, how many elements in set A are divisible by 11?',
51:'Find the number of integer solutions to the equation x + y + z + w = 25,\n\nGiven, x ≥ 1, y ≥ 2, z ≥ 3, and w ≥ 0.',
52:'A delivery company is building a new warehouse on a 50-mile highway. The warehouse will be located at mile marker x. The company decides the warehouse must be built somewhere between mile 0 and mile p (0 ≤ x ≤ p ≤ 50). The daily cost to run the warehouse is calculated using:\n\nC(x) = |x| + |p − x| + |p + 24 − x|\n\nThe maximum possible daily cost for any allowed location is exactly 50. What is the value of p?',
55:'For how many integer values of ‘t’, the quadratic equation x² − (t + 10)x + (10t + 16) = 0 has two real, distinct and positive roots whose difference is less than 6?',
56:'Let f(x) = |x − 2| + |x − 4|. How many integer values of x satisfy f(x) < 4?',
61:'Let ‘x’ be a positive real number (x ≠ 1, 1/2, 1/4) such that logₓ 2 + log₂ₓ 4 + log₄ₓ 8 = 3. The product of all possible values of ‘x’ is ______.',
64:'In an ancient Chinese legend, Nüwa assigns two celestial craftsmen, Wei and Jun, to repair a breach in the heavens. Working alone, Wei can complete the repair in 14 days and Jun can complete it in 21 days. However, Xiangliu, the destructive serpent unleashed by Gonggong’s chaos, undoes work each day equal to 1/42 of the total repair work. If all of Wei, Jun and Xiangliu start working simultaneously, how many days will it take to complete the work?',
66:'In the diagram given below, EBF is a right-angled isosceles triangle where EB ⟂ BF.\n\nIt is given that ∠ADC is a right angle, BF = 20 cm, AD = 12 cm and ED = 10√2 cm.\n\nFind the area (in cm²) of the quadrilateral ABCD.'},
{48:'If 6ᵃ = 7ᵇ = 42ᶜ, which of the following statements can be correct?',
56:'A container holds a 700 ml mixture of alcohol and water at a specific alcohol concentration. In each operation, 100 ml of this mixture is removed and replaced with water. After performing this operation three times, the alcohol concentration in the mixture becomes 30 6/7%. What was the percent alcohol concentration in the mixture after only one operation?',
58:'Given the quadratic equation x² + bx + c = 0, if the sum of its roots is 1 and the sum of squares of its roots is 25, what is the product of ‘b’ and ‘c’?',
59:'What is the minimum value of the function f(x) = |x − 1| + |x − 5| + |x − 8|?',
60:'Find the range of values of x that satisfy the inequality x⁴ − 6x³ + 13x² − 12x + 4 < 0.',
62:'What is the length of the perpendicular dropped from the origin to the line √3x − y = 4√3?',
63:'In △ABC, ray BP bisects ∠ABC intersecting side AC at point P such that A-P-C. If ℓ(AB) = 8, ℓ(BC) = 10 and ℓ(AC) = 12, calculate the area of △APB (in square units).',
64:'In trapezium ABCD, sides AB and CD are parallel to each other. The diagonals AC and BD intersect at point O. If ℓ(AB)/ℓ(CD) = 5/8, what is the ratio of the areas of △AOD and △BOC?',
67:'If log₃ x + log₉ x = log₂₇ 6, the value of ‘x’ is ______.'}]

def clean(s):
    s=s.replace('Al systems','AI systems').replace('Al-powered','AI-powered').replace('Al development','AI development').replace('Al ecosystem','AI ecosystem').replace('generative Al','generative AI').replace('play 2 role','play a role').replace('build 2 society','build a society').replace('in 2 group','in a group')
    for a,b in {'Asecurity':'A security','Adelivery':'A delivery','Asix-digit':'A six-digit','Anactor':'An actor','Avessel':'A vessel','Ashopkeeper':'A shopkeeper','Ina library':'In a library','Akey':'A key','asacred':'a sacred','animage':'an image','afew':'a few','trustin':'trust in','andfabrication':'and fabrication','deepenherenduringappeal':'deepen her enduring appeal','Areservoir':'A reservoir','Acompany':'A company','Asmall':'A small','Asa result':'As a result','avant-gardeis':'avant-garde is','itto':'it to','emplovees':'employees','Init,':'In it,','catalystforchange':'catalyst for change','Al\'s':'AI\'s','promote Al':'promote AI'}.items():s=s.replace(a,b)
    s=re.sub(r'\bitis\b','it is',s);s=re.sub(r'\bItis\b','It is',s);s=re.sub(r'\binjust\b','in just',s)
    for a,b in {'on 2 card':'on a card','2 moral':'a moral','2 convincing':'a convincing','2 poetic':'a poetic','was 2 fan':'was a fan','remain 2 matter':'remain a matter','oneself ina':'oneself in a','the Islamic threat*':'the Islamic threat”','abominable mystery:':'abominable mystery.”'}.items():s=s.replace(a,b)
    s=re.sub(r'\n(?=\d+[.]\s)', '\n\n',s)
    s=re.sub(r'_{2,}[({](\d)[)}]_{1,}[-—.]*',r'___(\1)___',s)
    return '\n\n'.join(' '.join(p.split()).strip(' |') for p in s.strip().split('\n\n')).strip()

def asset(t,item,d,file,box,key,alt):
    im=Image.open(ROOT/'source-images'/d/file).crop(box)
    if im.width<300:
        scale=min(2,400/im.width);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    buf=io.BytesIO();im.save(buf,format='PNG')
    t.setdefault('assets',{})[key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}
    item.setdefault('assetIds',[]).append(key)

def source_tables(d,rs,qs):
    files=sorted((ROOT/'source-images'/d).glob('*.png'));results=[]
    for code,p in zip(['VARC','DILR','QA'],files[70:73]):
        ls=lines(ROOT/'extraction/oct13'/d/p.stem/'full.tsv')
        rows=[l for l in ls if len(re.findall(r'\d{1,2}:\d{2}',l['text']))>=2]
        assert len(rows)==(24 if code=='VARC' else 22),(d,code,len(rows))
        # Find the status column from OCR word coordinates, not recognized status glyphs.
        words=list(csv.DictReader((ROOT/'extraction/oct13'/d/p.stem/'full.tsv').open(encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE))
        status=next(w for w in words if w['text']=='Status');sx=(int(status['left'])+int(status['width'])/2)/3
        im=Image.open(p).convert('RGB')
        for n,l in enumerate(rows,1):
            q=qs[code,n];matches=list(re.finditer(r'\d{1,2}:\d{2}',l['text']));secs=lambda s:sum(int(v)*m for v,m in zip(s.split(':'),[60,1]))
            y=round((l['y']+l['bottom'])/2)
            pix=[im.getpixel((xx,yy)) for xx in range(round(sx)-14,round(sx)+15) for yy in range(max(0,y-7),min(im.height,y+8))]
            green=sum(g>r+20 and g>b+10 for r,g,b in pix);red=sum(r>g+35 and r>b+35 for r,g,b in pix)
            outcome='Correct' if green>3 else 'Incorrect' if red>3 else 'Unanswered'
            results.append({'questionId':q['id'],'outcome':outcome,'timeSeconds':secs(matches[0][0])})
            nums=re.findall(r'\d+(?:\.\d+)?',l['text'][matches[1].end():])[:3]
            vals=[float(v) for v in nums]
            for k,v in enumerate(vals):
                if v>100:vals[k]=v/(100 if len(nums[k].split('.')[0])>=4 else 10)
            # Cross-check the table against clearer individual question statistics.
            r=next(r for r in rs if r['section']==code and r['number']==n)
            for label,k in [('Attempt',0),('Accuracy',1),('PValue',2)]:
                row=next((v for v in r['raw'].splitlines() if label in v),'')
                numbers=re.findall(r'\d+(?:\.\d+)?',row.split(label)[-1])
                if len(numbers)==2:
                    v=float(numbers[0])
                    if v<=100 and ('.' in numbers[0] or v in [0,100] or label=='Attempt'):vals[k]=v
            assert len(vals)==3 and all(0<=v<=100 for v in vals),(d,code,n,vals)
            q['benchmark']={'source':'IMS supplied question review and analysis screenshots','sourceImage':p.name,'topperTimeSeconds':secs(matches[1][0]),'topperAttemptPercent':vals[0],'topperAccuracyPercent':vals[1],'topperPValue':vals[2]}
            corrections={('simcat-3','VARC',5):{'topperPValue':47.6},('simcat-3','VARC',14):{'topperPValue':44.8},('simcat-3','VARC',22):{'topperPValue':49.8},('simcat-3','DILR',1):{'topperAttemptPercent':76.4},('simcat-3','DILR',18):{'topperAccuracyPercent':58.88},('take-home-1','VARC',12):{'topperAccuracyPercent':95.89}}
            q['benchmark'].update(corrections.get((d,code,n),{}))
            if (d,code,n)==('take-home-1','DILR',11):q['benchmark']['topperPValue']=86
            cat=re.search(r'Question Type\s+([ABC])',r['raw'])
            q['selectionCategory']=cat[1] if cat else {'8':'B','c':'C'}.get(l['text'][-1],l['text'][-1])
    return results

for j,(d,title) in enumerate([('simcat-3','SimCAT 3 · 2026'),('take-home-1','Take Home 1 · SimCAT 101 · 2026')]):
    rs=records[j*68:(j+1)*68];qs={};t={'schemaVersion':1,'testType':'full','id':'ims-'+d+'-2026','revision':1,'title':title,'description':'68 questions: 24 VARC, 22 DILR and 22 QA. Original set images and supplied analysis preserved.','sections':[{'code':c,'groups':[]} for c in ['VARC','DILR','QA']]}
    for r in rs:
        i=r['index'];q={k:r[k] for k in ['type','prompt','answer']};q.update(id=f'{d}-{r["section"].lower()}-q{r["number"]:02}',sourceNumber=r['number'])
        if i in TITA[j]:
            q['type']='TITA';q['answer']=[TITA[j][i]]
            if j==1 and i in [17,18,23,24]:
                ls=lines(ROOT/'extraction/oct13'/d/Path(r['file']).stem/'right.tsv')
                # These screens omit the keyboard instruction; the fifth/fourth sentence ends before the input.
                end={17:315,18:290,23:350,24:350}[i]
                q['prompt']='\n'.join(l['text'] for l in ls if 35<l['y']<end)
        else:
            q['options']=[{'id':o['id'],'text':clean(o['text'])} for o in r['options']]
            if i in OPTIONS[j]:q['options']=[{'id':chr(65+k),'text':v} for k,v in enumerate(OPTIONS[j][i])]
        if j==0 and i==38:q['answer']='B'
        q['prompt']=clean(PROMPTS[j].get(i,q['prompt']))
        qs[r['section'],r['number']]=q
    specs=([(1,4,'Income inequality and growth'),(8,11,'Language bias in AI'),(12,15,'Space and place in literature'),(16,19,'Postwar economic policy')] if j==0 else [(1,4,'Public opinion and conformity'),(5,8,'Flowering plants and genome size'),(9,12,'Indigenous sovereignty'),(13,16,'Dating Homo naledi')])
    grouped={n for a,b,_ in specs for n in range(a,b+1)}
    allspecs=[('VARC',a,b,'RC · '+label) for a,b,label in specs]+[('VARC',n,n,'Verbal ability · Q'+str(n)) for n in range(1,25) if n not in grouped]
    allspecs.sort(key=lambda s:s[1])
    allspecs+=([('DILR',1,4,'Arcade tournament'),('DILR',5,9,'Madras Music Season'),('DILR',10,14,'Project assignments'),('DILR',15,18,'School theatre productions'),('DILR',19,22,'Reading genres')] if j==0 else [('DILR',1,5,'Friends and toffees'),('DILR',6,9,'Ganga Motors car sales'),('DILR',10,14,'Water supply network'),('DILR',15,18,'Casino betting'),('DILR',19,22,'Employee holiday allocations')])
    allspecs += [('QA',n,n,'Quantitative ability · Q'+str(n)) for n in range(1,23)]
    for code,a,b,label in allspecs:
        g={'id':f'{d}-{code.lower()}-set-{a}','title':label,'questions':[qs[code,n] for n in range(a,b+1)]}
        for q in g['questions']:q['area']='Reading Comprehension' if code=='VARC' and a!=b else 'Verbal Reasoning' if code=='VARC' else 'Logical Reasoning' if code=='DILR' and ((j==0 and a<10) or (j==1 and a in [1,15,19])) else 'Data Interpretation' if code=='DILR' else 'Quantitative Ability';q['topic']=label
        if a!=b:
            r=next(r for r in rs if r['section']==code and r['number']==(14 if j==1 and code=='VARC' and a==13 else a));p=ROOT/'extraction/oct13'/d/Path(r['file']).stem/'left.txt';s=p.read_text(encoding='utf-8')
            if code=='VARC':
                ls=lines(p.with_suffix('.tsv'));deltas=[v['y']-u['y'] for u,v in zip(ls,ls[1:]) if v['y']>u['y']]
                step=statistics.median(deltas);s=''
                for k,l in enumerate(ls):s+=('' if k==0 else '\n\n' if l['y']-ls[k-1]['y']>step*1.3 else '\n')+l['text']
            marker=re.search(r'(?:Refer to the data below.*?follow\.|The passage (?:below|given below).*?question\.|Read the given passage.*?follow:)[^\n]*\n',s)
            if marker:s=s[marker.end():]
            g['stimulus']=clean(s)
            if j==0 and code=='DILR' and a==1:
                for prefix,value in [(1,'In each game, the players are ranked 1st, 2nd, 3rd, and 4th based on their performance.'),(4,'Only Jax and Kael ever achieved a 1st place rank during the tournament.'),(5,'Nova never finished 4th in any of the four games.'),(6,'Kael finished 1st only in Pixel-Quest and Neon-Riders.')]:
                    g['stimulus']=re.sub(r'(?m)^'+str(prefix)+r'\..*',str(prefix)+'. '+value,g['stimulus'])
            # Preserve original tables/graphs and remove their OCR fragments.
            crop_specs=({10:[(10,125,390,255)],15:[(15,174,325,300)],19:[(12,210,345,317),(12,372,285,615)]} if j==0 else {1:[(31,207,438,772)],6:[(18,165,207,351)],10:[(16,171,250,292)],19:[(4,568,410,770)]})
            if code=='DILR' and a in crop_specs:
                # Crop coordinates are reviewed below; keep only text lines outside the figure regions.
                ls=lines(p.with_suffix('.tsv'));filtered=[l['text'] for l in ls if not any(box[1]-3<=l['y']<=box[3]+2 for box in crop_specs[a])]
                s='\n'.join(filtered);marker=re.search(r'(?:Refer to the data below.*?follow\.|Read the given passage.*?follow:)[^\n]*\n',s)
                if marker:s=s[marker.end():]
                g['stimulus']=clean(s)
                if j==0 and a==10:
                    g['stimulus']=g['stimulus'].replace('Bi comprises','B1 comprises')
                    for n,value in enumerate(['Aarav and Diya start working on 3rd March.','Bharat and Esha start working on 5th March.','Chetan starts working on 7th March.','Aarav and Bharat take leave on every 4th day.','Chetan takes leave on every 3rd day.','Diya and Esha take leave on every 2nd day.','A person can work on only one stage in a day.'],1):
                        g['stimulus']=re.sub(r'(?m)^'+str(n)+r'\..*',str(n)+'. '+value,g['stimulus'])
                if j==0 and a==15:g['stimulus']=g['stimulus'].replace('Accultural','A cultural').replace('from 11,','from T1,')
                if j==0 and a==19:g['stimulus']=g['stimulus'].replace('ona particular','on a particular')
                if j==1 and a==19:g['stimulus']=g['stimulus'].removesuffix(' v').replace('Pvt Ltd:', 'Pvt Ltd.’')
                if j==1 and a==10:g['stimulus']=g['stimulus'].replace('{i.e.', '(i.e.')
                for k,box in enumerate(crop_specs[a]):asset(t,g,d,r['file'],box,f'{d}-set-{a}-figure-{k+1}','Original source '+('graph' if (j==0 and a==19 and k==1) or (j==1 and a in [6,10]) else 'table')+' for '+label+'.')
        t['sections'][['VARC','DILR','QA'].index(code)]['groups'].append(g)
    if j==0:
        r=rs[65];asset(t,qs['QA',20],d,r['file'],(30,166,200,328),'simcat-3-qa20-diagram','Original triangle and quadrilateral diagram.')
    results=source_tables(d,rs,qs)
    files=sorted((ROOT/'source-images'/d).glob('*.png'))
    t['sourceAnalysis']={'label':'Original IMS attempt supplied in screenshots','sourceImages':[p.name for p in files[68:]],'reportedScore':[20,22][j],'percentile':[31.32,23.16][j],'questionResults':results,'percentileMapper':[]}
    maps=([[21,28,32,37,49,52],[12,17,20,25,35,38],[16,22,26,32,44,48]] if j==0 else [[24,31,34,39,48,51],[16,21,23,27,33,36],[22,28,31,36,46,48]])
    for code,values in zip(['VARC','DILR','QA'],maps):
        t['sourceAnalysis']['percentileMapper'] += [{'section':code,'percentile':p,'score':v} for p,v in zip([70,85,90,95,99,99.5],values)]
    (ROOT/'samples'/f'{d}.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
    print(d,len(qs),'source outcomes', {c:sum(r['outcome']==c for r in results) for c in ['Correct','Incorrect','Unanswered']})
