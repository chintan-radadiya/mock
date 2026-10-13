"""Build the reviewed SimCAT 4 full-mock JSON from its source screenshots."""
from pathlib import Path
from PIL import Image
import base64, csv, io, json, re, statistics, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_oct13 import lines

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'source-images' / 'simcat-4'
OCR = ROOT / 'extraction' / 'oct13' / 'simcat-4'
records = json.loads((ROOT / 'extraction' / 'simcat-4-records.json').read_text(encoding='utf-8'))

ANSWERS = {
 'VARC': ['C','B','B','D','C','D','C','A','D','3214','D','4','C','C','B','D','C','A','C','C','C','3','4123','C'],
 'DILR': ['D','C','C','B','B','C','C','14','A','D','10','A','B','27','6','3','B','C','B','C','D','A'],
 'QA': ['A','C','D','D','B','53','4','A','44','C','D','1900','C','90','40','175000','D','D','B','C','204','33']
}
TITA = {('VARC',10),('VARC',12),('VARC',22),('VARC',23),('DILR',8),('DILR',11),('DILR',14),('DILR',15),('DILR',16),('QA',6),('QA',7),('QA',9),('QA',12),('QA',14),('QA',15),('QA',16),('QA',21),('QA',22)}
MANUAL_OPTIONS = {
 ('QA',10): ['121','100','36','25'], ('QA',11): ['log₂ 0.7','log₂ 0.5','log₅ 0.2','log₇ 0.2'],
 ('QA',17): ['512','729','1024','1458'], ('QA',18): ['18','20','22','24'], ('QA',19): ['1','2','3','4'],
 ('QA',13): ['10 14/165','12 7/11','22 2/9','25 4/9'],
 ('DILR',1): ['P1','P3','P4','P6'], ('DILR',4): ['P1 and P6','P3 and P6','P4 and P6','P5 and P6'],
 ('DILR',6): ['2','3','4','5'], ('DILR',12): ['7','4','11','14'], ('DILR',17): ['1','2','3','Cannot be determined'],
 ('QA',5): ['22','26','30','36'],
 ('VARC',1): ['Ethical concerns about future superintelligent AI draw attention away from the risks posed by current technologies.','Business profits strongly push companies to use AI for tracking people across digital platforms.','The real ethical problem with AI influencing behavior is persuasion itself, not the hidden and unequal way it is done.','To judge whether AI is ethical, we must look not only at the software but also at the institutions and politics behind it.'],
 ('VARC',5): ['Hierarchy, Prediction, Control, Independence','Emergence, Novelty, Matter, Energy','Autonomous levels, Closure, Explanation, Causation','Patterns, Computation, Simplification, Accuracy'],
 ('VARC',7): ["A weather model that ignores small, local variations but still forecasts tomorrow's weather accurately using climate patterns.",'A factory assembly line where output can be predicted accurately as long as each worker follows fixed, clearly defined tasks.','A moving crowd whose overall direction can be predicted from current movement patterns despite changing individual choices.','A living system that usually behaves healthily but may fail because of small internal changes.'],
 ('VARC',8): ['Traffic control authorities can achieve reliable results by focusing on overall traffic flow during peak hours.','Weather forecasts often fail even when large amounts of atmospheric data are collected.','On platforms like X, trending topics can be anticipated by tracking what influential users will post.','In medicine, small changes inside the body can occasionally lead to sudden, serious health problems.']
}
PROMPT_FIX = {
 ('QA',3): 'Find the number of non-zero terms in the expansion of (8x + 3y)^100 + (8x − 3y)^101.',
 ('QA',6): 'What is the highest possible average of 7 consecutive prime numbers, all less than 100, such that the average is also a prime number?',
 ('QA',7): 'Let A = 1^2 + 4^2 + 7^2 + … + 127^2 + 132^2 + 142^2 + 153^2. Find the remainder when A is divided by 5.',
 ('QA',9): 'If f(x) is defined on non-negative integers by f(x) + f(x + 1) = x², find f(5) + f(0).',
 ('QA',12): 'An investor tracks the value of his stocks over 5 consecutive months. The value increases by a constant amount every month. Additionally, in the fifth month, the value increases by an extra amount equal to half of the first month’s value. The total value over the first 2 months is Rs. 2,400, and over the last 2 months is Rs. 5,300. What is the average monthly value (in Rs.) over the 5 months?',
 ('QA',13): 'Vessels A and B contain 60 litres of alcohol and 60 litres of water, respectively. A 5-litre measuring cup transfers either 5 or 10 litres of alcohol from A to vessel C, then either 5 or 10 litres of water from B to C. This process is repeated once. The remaining alcohol in A is then poured into B. Find the maximum absolute difference between the final alcohol concentrations in B and C, in percentage points.',
 ('QA',14): 'Two ferries, the Albatross and the Pelican, are at opposite ends of a straight shipping channel, starting at Port A and Port B respectively. They depart simultaneously toward each other at constant speeds. They first pass at a point 40 km from Port A. After reaching their opposite ports, they immediately turn back and pass for the second time at a point 30 km from Port B. Find the distance between the ports (in km).',
 ('QA',15): 'In an experiment, two types of bacteria, A and B, are observed in two phases. During the first phase, the total number increases by 16 2/3%. In this phase, A increases by 33 1/3% while B increases by 12.5%. In the second phase, B increases by 11 1/9%. At the end, B is 2.5 times A. What is the overall percentage increase in the total number of bacteria?',
 ('QA',16): 'Trader P invests Rs. 25,000 in scheme A at 20% per annum compounded annually for 2 years and Rs. 20,000 in scheme B at 25% per annum compounded annually for 1 year. Trader Q invests his total amount in schemes C and D in the ratio 3:4 for two years. C offers 10% and D offers 15% per annum, compounded annually. If P’s total interest is one-third of Q’s interest, find Q’s total investment (in Rs.).',
 ('QA',17): 'Find the maximum possible value of a(a + b)² − b(a + b)² − a²b + ab², given that a and b are distinct integers and −10 < a,b < 10.',
 ('QA',18): 'Let P(x) = 2x³ − 3x² + 5x − 7 and Q(x) = x² − 2x + 4. Find the coefficient of x² in P(x + 1) − P(x − 1) + [Q(x)]².',
 ('QA',19): 'For how many integer values of m does x² − mx + (16 − m) = 0 have two distinct real roots, one between 1 and 3 and the other between 5 and 7?',
 ('QA',20): 'The perimeter of a right-angled triangle is 60 units. If all side lengths are integers, which option gives all possible values of its smallest median?',
 ('QA',21): 'In the diagram, ABCD is a quadrilateral with reflex angle BCD. It is given that ∠DAB = 90° + ½∠ABC. Join A to C and extend AC to P so A-C-P; then AC = BC = AD, and ∠BCP = ½∠ADC. Find the reflex angle BCD (in degrees).',
 ('QA',22): 'How many positive integers n, not greater than 100, make n² + n divisible by 12?'
}
PROMPT_FIX[('QA',2)]='Find the minimum value of f(x) = |x − 2| + |x − 5| + |x − 11| + |x − 17|.'
PROMPT_FIX[('QA',3)]='Find the number of non-zero terms in the expansion of (8x + 3y)^100 + (8x − 3y)^100.'
PROMPT_FIX[('QA',7)]='Let A = 1 + 2⁴ + 3⁶ + 4⁸ + 5¹⁰ + 11²² + 12²⁴ + 13²⁶ + 14²⁸ + 15³⁰. Find the remainder when A is divided by 5.'
PROMPT_FIX[('QA',11)]='Find the sum of all real values of x such that 5ˣ · 7^(x²) = 35.'
PROMPT_FIX[('DILR',5)]='If all sachets from all six caddies are mixed together, which option gives the resulting (Consumer Delight Index, selling price per sachet)?'

def fix_text(s):
    s = s.replace('\ufffd', '−').replace('�', '−')
    for a,b in [('Al','AI'),('al systems','AI systems'),('behavioural','behavioural'),('�','−'),('x�','x²'),('log,','log₂'),('Atechnical','A technical'),('Aproblem','A problem'),('Amanagement','A management'),('Asecurity','A security'),('Asix','A six'),('Aweather','A weather'),('Amoving','A moving'),('Asystem','A system'),('sInsome','In some'),('siniiving','In living'),('Cc ','')]: s=s.replace(a,b)
    s=re.sub(r'(?m)^\s*[|=]+\s*','',s)
    s=s.replace('eBusiness','Business').replace('Avalue-based','A value-based').replace('Avalue','A value').replace('Atechnical','A technical').replace('Aproblem','A problem').replace('Amanagement','A management').replace('Aresistance','A resistance').replace('Apolitical','A political').replace('BA factory','A factory').replace('AIiving','A living').replace('Onplatforms','On platforms').replace('Inmedicine','In medicine').replace('sawno','saw no').replace('sInsome','In some').replace('sDevika','Devika').replace('Thesumof','The sum of').replace('R2DxR4Dis','R2D × R4D is').replace('Row 3contains','Row 3 contains').replace('Atleast','At least').replace('annot be determined','Cannot be determined').replace('Morethan7','More than 7').replace('Tojudge','To judge').replace('PS5andP','P5 and P').replace('mainly c highlight','mainly highlight').replace('accumulate A invisibly','accumulate invisibly').replace('least responsible B for','least responsible for').replace('ecologicAI','ecological')
    s=s.replace(' |','').replace('g |','').replace('�','').replace('VOILZ','').replace('Pp4','P4').replace('Pil','P1').replace('PtandP6','P1 and P6').replace('P3andP6','P3 and P6').replace('P4andP6','P4 and P6').replace('PS5andP�6','P5 and P6')
    s=re.sub(r'\s+',' ',s).strip()
    return s

def embed(test, target, path, box, key, alt):
    im=Image.open(path).crop(box)
    b=io.BytesIO(); im.save(b,format='PNG')
    test.setdefault('assets',{})[key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()}
    target.setdefault('assetIds',[]).append(key)

question_map={}
test={'schemaVersion':1,'testType':'full','id':'ims-simcat-4-2026','revision':1,'title':'SimCAT 4 · 2026','description':'Full mock with 24 VARC, 22 DILR and 22 QA questions. Source answer keys, set passages, original DILR charts and supplied analysis are preserved.','sections':[{'code':c,'groups':[]} for c in ['VARC','DILR','QA']]}
for rec in records:
    code,n=rec['section'],rec['number']; key=(code,n)
    q={'id':f'simcat-4-{code.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if key in TITA else 'MCQ','prompt':PROMPT_FIX.get(key,fix_text(rec.get('prompt',''))),'area':'Reading Comprehension' if code=='VARC' and n in set(range(1,5))|set(range(5,9))|set(range(13,17))|set(range(17,21)) else 'Verbal Reasoning' if code=='VARC' else 'Data Interpretation' if code=='DILR' else 'Quantitative Ability','answer':[ANSWERS[code][n-1]] if key in TITA else ANSWERS[code][n-1]}
    if key not in TITA:
        vals=MANUAL_OPTIONS.get(key)
        if vals is None: vals=[fix_text(o['text']) for o in rec.get('options',[])]
        if len(vals)!=4: raise ValueError(f'Missing options: {key}: {vals}')
        q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(vals)]
    if code=='QA' and n==13: q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(MANUAL_OPTIONS[key])]
    question_map[key]=q

rc_specs=[(1,4,'RC · Ethics and artificial intelligence'),(5,8,'RC · Emergence'),(13,16,'RC · Plato and poetry'),(17,20,'RC · Political violence')]
for a,b,title in rc_specs:
    rec=records[a-1]; passage=(OCR/Path(rec['file']).stem/'left.txt').read_text(encoding='utf-8')
    passage=re.sub(r'(?s)^.*?choose the best answer for each question\.?\s*','',passage,flags=re.I)
    # Keep the source passage, normalize common OCR substitutions only.
    passage=passage.replace('�','—').replace('Al ','AI ').replace('Al\'','AI\'').replace('Al-','AI-').replace('�','’')
    g={'id':f'simcat-4-varc-set-{a}','title':title,'stimulus':passage,'questions':[question_map['VARC',n] for n in range(a,b+1)]}
    test['sections'][0]['groups'].append(g)
for n in range(1,25):
    if any(a<=n<=b for a,b,_ in rc_specs): continue
    test['sections'][0]['groups'].append({'id':f'simcat-4-varc-group-q{n}','title':f'Verbal ability · Q{n}','questions':[question_map['VARC',n]]})
test['sections'][0]['groups'].sort(key=lambda g:g['questions'][0]['sourceNumber'])

dilr_specs=[(1,6,'Tea caddies'),(7,10,'Agni Pariksha'),(11,14,'The ancient vault'),(15,18,'Management summit workshops'),(19,22,'Inter-campus innovation showcases')]
for a,b,title in dilr_specs:
    rec=records[24+a-1]; left=(OCR/Path(rec['file']).stem/'left.txt').read_text(encoding='utf-8')
    left=re.sub(r'(?s)^.*?answer the questions that follow\.?\s*','',left,flags=re.I)
    g={'id':f'simcat-4-dilr-set-{a}','title':title,'questions':[question_map['DILR',n] for n in range(a,b+1)]}
    if a==1:
        g['stimulus']=('A specialty tea retailer stores sachets in six caddies. Each sachet weighs 100 grams. The original chart below shows the number of sachets, selling price, and average aroma score for each caddy. The original table below gives the relationship between aroma score and Consumer Delight Index. When caddies are mixed, aroma score is a weighted average based on the numbers of sachets used.')
        embed(test,g,SRC/rec['file'],(16,217,525,553),'simcat-4-dilr-tea-chart','Original source graph for the tea-caddy set.')
        embed(test,g,SRC/rec['file'],(12,639,391,772),'simcat-4-dilr-tea-table','Original source table for the tea-caddy set.')
    elif a==7:
        g['stimulus']=('Professor Iyer at the Chanakya Institute of Management designed a rigorous 10-day evaluation called Agni Pariksha for four CAT scholars: Amit, Bala, Chandan, and Devika. Each student took one 20-question modular test per day. Scoring was +3 for correct, −1 for incorrect, and 0 for unattempted. The original summary table and additional information are shown below.')
        embed(test,g,SRC/rec['file'],(10,258,347,359),'simcat-4-dilr-agni-table','Original source aggregate-results table for Agni Pariksha.')
        # Reproduce only the non-tabular constraints from the source text.
        g['stimulus']+='\n\nAdditional information:\n1. Amit’s score in every module was even and never negative.\n2. Bala answered the same number of questions incorrectly in every module.\n3. Chandan answered exactly 20 correctly in exactly two modules; in the other eight, he answered an equal number correctly.\n4. Devika’s ten unattempted-question counts formed an arithmetic progression with common difference 1.\n5. Devika had exactly one more incorrect than unattempted answer in each module.'
    else:
        g['stimulus']=left.replace('�','−').replace('Ata six','At a six').replace('�','’')
    test['sections'][1]['groups'].append(g)

for n in range(1,23):
    q=question_map['QA',n]
    test['sections'][2]['groups'].append({'id':f'simcat-4-qa-group-q{n}','title':f'Quantitative ability · Q{n}','questions':[q]})
embed(test,question_map['QA',21],SRC/records[66]['file'],(68,109,595,383),'simcat-4-qa-q21-diagram','Original geometry diagram for QA question 21.')

# Capture source question-wise outcomes and time exactly from the supplied analytics screenshots.
analysis_files={'VARC':'Screenshot 2026-10-13 112930.png','DILR':'Screenshot 2026-10-13 112941.png','QA':'Screenshot 2026-10-13 112950.png'}
results=[]
for code,filename in analysis_files.items():
    p=SRC/filename; tsv=OCR/p.stem/'full.tsv'; ls=lines(tsv)
    rows=sorted([l for l in ls if len(re.findall(r'\d{1,2}:\d{2}',l['text']))>=2],key=lambda l:l['y'])
    expected=24 if code=='VARC' else 22
    if len(rows)!=expected: raise ValueError(f'{code}: expected {expected} analytics rows, got {len(rows)}')
    words=list(csv.DictReader(tsv.open(encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE))
    status=next(w for w in words if w['text']=='Status'); sx=round((int(status['left'])+int(status['width'])/2)/3)
    im=Image.open(p).convert('RGB')
    for n,l in enumerate(rows,1):
        matches=list(re.finditer(r'\d{1,2}:\d{2}',l['text']))
        sec=lambda s:sum(int(v)*m for v,m in zip(s.split(':'),[60,1]))
        y=round((l['y']+l['bottom'])/2)
        pix=[im.getpixel((xx,yy)) for xx in range(max(0,sx-12),min(im.width,sx+13)) for yy in range(max(0,y-5),min(im.height,y+6))]
        green=sum(g>r+18 and g>b+8 for r,g,b in pix); red=sum(r>g+30 and r>b+30 for r,g,b in pix)
        gray=sum(abs(r-g)<20 and abs(g-b)<30 and 80<r<220 for r,g,b in pix)
        outcome='Correct' if green>red and green>4 else 'Incorrect' if red>4 else 'Unanswered'
        q=question_map[code,n]
        result={'questionId':q['id'],'outcome':outcome,'timeSeconds':sec(matches[0][0])}
        results.append(result)
        tail=l['text'][matches[1].end():]
        nums=re.findall(r'\d+(?:\.\d+)?',tail)
        if len(nums)>=3:
            vals=[float(x) for x in nums[:3]]
            vals=[v/100 if v>100 else v for v in vals]
            # Analytics tables show topper attempt, accuracy and p-value in this order.
            q['benchmark']={'source':'IMS supplied question-wise analysis screenshot','sourceImage':filename,'topperTimeSeconds':sec(matches[1][0]),'topperAttemptPercent':vals[0],'topperAccuracyPercent':vals[1],'topperPValue':vals[2]}
        category=next((x for x in 'ABC' if re.search(r'Question Type\s*'+x,records[(0 if code=='VARC' else 24 if code=='DILR' else 46)+(n-1)].get('raw',''))),None)
        if category: q['selectionCategory']=category

test['sourceAnalysis']={'label':'Original IMS attempt supplied in screenshots','sourceImages':[analysis_files[c] for c in ['VARC','DILR','QA']]+['Screenshot 2026-10-13 112915.png','Screenshot 2026-10-13 113001.png'],'reportedScore':26,'percentile':30.67,'questionResults':results,'percentileMapper':[],'sectionScores':[{'section':'VARC','score':18,'percentile':53.79},{'section':'DILR','score':5,'percentile':22.23},{'section':'QA','score':3,'percentile':23.22}]}
for code,values in [('VARC',[24,31,35,40,50,54]),('DILR',[19,25,28,32,40,43]),('QA',[15,21,25,30,40,45]),('Overall',[54,70,78,89,110,116])]:
    test['sourceAnalysis']['percentileMapper'] += [{'section':code,'percentile':p,'score':v} for p,v in zip([70,85,90,95,99,99.5],values)]

out=ROOT/'samples'/'simcat-4.json';out.write_text(json.dumps(test,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {out} · {sum(len(g["questions"]) for s in test["sections"] for g in s["groups"])} questions · {len(results)} source results')
