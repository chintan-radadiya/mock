"""Build reviewed transcriptions of the two user-supplied ZIPs.

OCR intermediates are local extraction aids, never imported as unchecked text.
Answer labels come from green answer-key markers, not selected-option highlights.
"""
import json, re, base64, io
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT/'extraction/clean-records.json').read_text(encoding='utf-8'))

def clean(s):
    s=re.sub(r'^\d{1,2}/(?:22|24)\s*', '', s.strip())
    s=s.replace(' |', '').replace('corruptinstitutions','corrupt institutions').replace('economicdecline','economic decline').replace('doubtintoanger','doubt into anger').replace('risksthanbefore','risks than before')
    s=s.replace(' a 2 ', ' a ').replace('is 2 distortion','is a distortion').replace('represents 2 transitional','represents a transitional')
    s=s.replace('Asolid','A solid').replace('Ashopkeeper','A shopkeeper').replace('Onan','On an').replace('maintaina','maintain a').replace('inthe vessel willbe.', 'in the vessel will be ______.')
    s=re.sub(r'_{2,}[({](\d)[)}]_{2,}[-.]?',r'___(\1)___.',s)
    paragraphs=[]
    for p in re.split(r'\n\s*\n',s):
        p=re.sub(r'\n(?=\d+[.)]\s)', '\n\n',p)
        paragraphs.extend(' '.join(x.split()) for x in p.split('\n\n'))
    return '\n\n'.join(paragraphs).strip()

def passage(d,n):
    s=(ROOT/f'extraction/structured/{d}/{n}-passage.txt').read_text(encoding='utf-8')
    s=re.sub(r'^(?:Refer to the data below.*?|The passage below.*?)[\r\n]+','',s)
    s=s.replace('1.0n','1. On').replace('Ashipping','A shipping').replace('Ahockey','A hockey').replace('Agroup','A group').replace('Aguitar','A guitar').replace('A5-member','A 5-member')
    s=s.replace('make up 2 genome','make up a genome').replace('possess 2 gene','possess a gene').replace('As 2 result','As a result').replace('resemble 2 mathematical','resemble a mathematical').replace('not ona','not on a').replace('based ona','based on a').replace('for 2 new','for a new')
    s=s.replace('LUCA This strategy','LUCA. This strategy').replace('“ancient*','“ancient”')
    if n==19 and d=='dilr-sectional-1':s=s.replace('\n45.', '\n4.5.')
    if n==53 and d=='simcat-2':
        s=s.replace('humor.\nModern','humor.\n\nModern').replace('AJ.', 'A.I.').replace('AI.', 'A.I.').replace('Al systems','AI systems').replace('A. tools','A.I. tools').replace('A.’s','A.I.’s').replace('drive;*','drive;”').replace('“tank” moving','“tank,” moving')
        s=s.replace('drive;” works', 'drive;’” works')
    if n==78 and d=='simcat-2':s=s.replace('LS.', 'L5.')
    return clean(s)

def options(q, values):
    q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(values)]

def benchmark(d,r):
    text=r['raw']; b={'source':'IMS supplied review screenshots','sourceImage':f'Screenshot ({r["image"]}).png'}
    for label,key in [('Attempt','topperAttemptPercent'),('Accuracy','topperAccuracyPercent')]:
        line=next((x for x in text.splitlines() if label in x and '%' in x), '')
        nums=re.findall(r'(\d+(?:\.\d+)?)%',line)
        if len(nums)==2 and all(float(x)<=100 for x in nums):b[key]=float(nums[0])
    line=next((x for x in text.splitlines() if 'Time Taken' in x),'')
    times=re.findall(r'(\d+):([0-5]\d)',line)
    if len(times)==3:b['topperTimeSeconds']=int(times[1][0])*60+int(times[1][1])
    line=next((x for x in text.splitlines() if re.search('pvalue',x,re.I)), '')
    nums=re.findall(r'\b\d+\.\d+\b',line.split('NA')[-1])
    if len(nums)==2 and all(float(x)<=100 for x in nums):b['topperPValue']=float(nums[0])
    # Visual review of the isolated statistics cells resolves OCR confusions (8/6,
    # clipped leading digits, and decimals). No value is inferred by calculation.
    if d=='simcat-2':
        reviewed={
          45:{'topperAttemptPercent':91.6},52:{'topperAccuracyPercent':84.27},
          53:{'topperAttemptPercent':90.2},
          54:{'topperAttemptPercent':86.2,'topperAccuracyPercent':77.49,'topperTimeSeconds':79,'topperPValue':66.8},
          55:{'topperAccuracyPercent':76.69,'topperPValue':65.8},57:{'topperAttemptPercent':83},
          62:{'topperPValue':65.8},65:{'topperAttemptPercent':61.8},76:{'topperPValue':39.6},
          77:{'topperPValue':45.6},78:{'topperAttemptPercent':31.8},
          80:{'topperAttemptPercent':32.8,'topperPValue':15.2},81:{'topperAttemptPercent':36.4},
          82:{'topperAttemptPercent':34.2,'topperAccuracyPercent':34.5,'topperTimeSeconds':183,'topperPValue':11.8},
          83:{'topperPValue':8},85:{'topperPValue':7.8},
          86:{'topperAttemptPercent':21.8,'topperAccuracyPercent':16.51,'topperPValue':3.6},
          87:{'topperAttemptPercent':98.2,'topperTimeSeconds':242},88:{'topperAttemptPercent':98.4},
          91:{'topperTimeSeconds':110}
        }
        b.update(reviewed.get(r['image'],{}))
    return b if len(b)>2 else None

def question(d,r,code,prefix):
    n=r['image'];q={'id':f'{prefix}-{code.lower()}-q{r["number"]:02}', 'sourceNumber':r['number'],'type':'TITA' if isinstance(r['answer'],list) else 'MCQ','prompt':clean(r['prompt']),'answer':r['answer']}
    if q['type']=='MCQ':q['options']=[{'id':o['id'],'text':clean(o['text']).strip(" |'")} for o in r['options']]
    if r['category']:q['selectionCategory']=r['category']
    b=benchmark(d,r)
    if b:q['benchmark']=b
    if d=='dilr-sectional-1':
        if n==19:q['prompt']+=' ______.'
        if n==23:q['options'][0]['text']='0'
        if n==36:q['options'][2]['text']='IIMC'
        if n==44:q['prompt']='The cap is in the ______ coloured box'
    else:
        if n==52:q['prompt']=q['prompt'].replace('...*?', '...”?' )
        if n in [53,54,55,56]:
            q['prompt']=q['prompt'].replace('Al-generated','AI-generated')
            for o in q.get('options',[]):o['text']=o['text'].replace('Al ', 'AI ').replace('Als humor', "AI’s humor")
        if n==57:q['options'][2]['text']='Excessive attachment to hope can undermine present peace, while letting it go it may bring calm, acceptance, and a more stable form of contentment.'
        if n==67:options(q,['Option 2','Option 3','Option 1','Option 4'])
        if n==78:q['options'][3]['text']='All 4'
        if n==80:q['prompt']=q['prompt'].replace('in LS','in L5')
        if n==83:
            q['prompt']=q['prompt'].replace('by %.','by ______ %.')
            options(q,['12 1/2','14 1/7','16 1/6','Multiple answers are possible'])
        if n==86:q['prompt']=q['prompt'].replace('class Vil','class VII')
        if n in [89,90]:
            q['prompt']='If Supriya is selected in the team, which of the following statements can be true?\n\nI. Sumaya is selected.\nII. Savita is selected.\nIII. Sunita is selected.'
            options(q,['Only I','Only III','Only I and III','All I, II and III'])
        if n==92:q['prompt']=q['prompt'].replace('Fis','F is').replace('cm?', 'cm²')
        if n==93:q['prompt']=q['prompt'].replace('Asq.', 'A sq.').replace('V=10A','V ≥ 10A')
        if n==94:
            q['prompt']='Evaluate √(60 + 12√6 − 12√(25 + 10√6)).'
            options(q,['2√3 + 3√2 − √30','3√2 − 2√3 + √30','2√3 − 3√2 + √30','2√3 − 3√2 − √30'])
        if n==96:q['prompt']='If α, β, θ and π are the four real roots of 120x⁴ − 326x³ + 329x² − 146x + 24 = 0 and\n\nn = [1/(αβθ + βθπ + θπα + παβ)] × [1/(αβθ) + 1/(βθπ) + 1/(θπα) + 1/(παβ)],\n\nthen find the smallest integer larger than or equal to n.'
        if n==97:q['prompt']='If f(x) = max{|x − 2| + 3, 11 − x}, where ‘x’ is a real number. What is the minimum value of f(x)?'
        if n==98:
            q['prompt']='Let f₁(x) = 2x + 1, f₂(x) = x − 4 and f₃(x) = (x + 7)/2. Find the value of f₁(f₂(f₃(f₁(f₂(f₃(2026)))))).'
            options(q,['2027/2','2025/2','2026','4053'])
        if n==99:options(q,['(P² − H²)/4','(P² − 2PH)/4','(P² + 2PH)/2','(P² − 4H²)/8'])
        if n==100:options(q,['3 : 1','2 : 1','(2 + 0.25^99) : 1','(2 + 0.25^49) : 1'])
        if n==101:q['prompt']+=' ______.'
        if n==103:q['prompt']='How many integer values of ‘m’ can be written in the form m = k² − 12k, where the equation x² − (k + 3)x + 4k = 0 has two distinct real roots in the ratio 2 : 1?'
        if n==104:
            q['prompt']='If ‘P’ is a positive real number such Sₘ ≤ P ≤ Sₘ₊₁, where Sₙ is the sum of first ‘n’ terms of the sequence 1, 6/11, 10/11², 14/11³, 18/11⁴, …, the value of P cannot be ______.'
            options(q,['3/2','59/50','71/50','83/50'])
        if n==107:q['prompt']='The last two digits of (6^100 + 7^100) are ______.'
        if n==109:q['prompt']='The coordinates of the vertices of △ABC are A (0, 3), B (0, 0), and C (4, 0). Given BD ⟂ AC such that A-D-C. Find the coordinates of point D.'
        if n==110:q['prompt']='Let ‘x’ and ‘y’ be the integers greater than 1 satisfying 2x + 3y ≤ 12, x − y ≥ 1, x + y ≥ 4. What is the maximum possible value of (3x + 2y)?'
        if n==111:q['prompt']='If 24^n is a factor of (100!)²/(40!)³, the highest value ‘n’ can take is ______.'
    assert q['answer'] and q['prompt'],(d,n)
    assert q['type']=='TITA' or len(q['options'])==4 and all(o['text'] for o in q['options']),(d,n)
    return q

def build(d,tid,title,full):
    t={'schemaVersion':1,'testType':'full' if full else 'sectional','id':tid,'revision':1,'title':title,'description':('68 questions across VARC, DILR and QA.' if full else '22 DILR questions across five intact sets.')+' Transcribed from your IMS images, with supplied question benchmarks.','sections':[]}
    qs={}
    for r in records[d]:
        if r['image'] in ([89] if full else [34]):continue
        code=('VARC' if r['image']<69 else 'DILR' if r['image']<92 else 'QA') if full else 'DILR'
        qs[code,r['number']]=question(d,r,code,tid)
    specs=([('VARC',45,1,4,'RC · Cetacean evolution','Reading Comprehension'),('VARC',49,5,8,'RC · Scientific cultures','Reading Comprehension'),('VARC',53,9,12,'RC · AI and humor','Reading Comprehension'),('VARC',None,13,13,'Summary · Hope','Verbal Reasoning'),('VARC',None,14,14,'Paragraph ordering · Impact investing','Verbal Reasoning'),('VARC',None,15,15,'Sentence placement · Political movements','Verbal Reasoning'),('VARC',None,16,16,'Odd sentence · Aesthetics','Verbal Reasoning'),('VARC',None,17,17,'Summary · Kochi-Muziris Biennale','Verbal Reasoning'),('VARC',62,18,21,'RC · LUCA','Reading Comprehension'),('VARC',None,22,22,'Paragraph ordering · Population','Verbal Reasoning'),('VARC',None,23,23,'Sentence placement · International cooperation','Verbal Reasoning'),('VARC',None,24,24,'Odd sentence · Illusions','Verbal Reasoning'),('DILR',69,1,5,'Music academy','Logical Reasoning'),('DILR',74,6,9,'Eco-Blocks processing plants','Data Interpretation'),('DILR',78,10,13,'Shipping yard loading lanes','Logical Reasoning'),('DILR',82,14,18,'Welham Public School','Data Interpretation'),('DILR',87,19,22,'Hong Kong Super Five team','Logical Reasoning')] if full else [('DILR',19,1,5,'Football tournament starting points','Logical Reasoning'),('DILR',24,6,9,'Spanish game scores','Data Interpretation'),('DILR',31,10,13,'Hockey tournament','Logical Reasoning'),('DILR',36,14,18,'Citibank campus placements','Logical Reasoning'),('DILR',41,19,22,'Coloured boxes and balls','Logical Reasoning')])
    if full:
        topics=['Geometry','Geometry','Algebra','Arithmetic','Algebra','Algebra','Algebra','Geometry','Arithmetic','Number System','Arithmetic','Algebra','Algebra','Modern Mathematics','Arithmetic','Number System','Arithmetic','Geometry','Algebra','Number System','Number System','Arithmetic']
        specs += [('QA',None,i,i,topics[i-1]+' · Q'+str(i),topics[i-1]) for i in range(1,23)]
    for code,pn,start,end,label,area in specs:
        if not t['sections'] or t['sections'][-1]['code']!=code:t['sections'].append({'code':code,'groups':[]})
        g={'id':f'{tid}-{code.lower()}-g{start:02}','title':label,'questions':[]}
        if pn:g['stimulus']=passage(d,pn)
        for i in range(start,end+1):
            q=qs[code,i];q['area']=area;q['topic']=label.split(' · ')[0] if code=='VARC' else label;g['questions'].append(q)
        t['sections'][-1]['groups'].append(g)
    return t

dilr=build('dilr-sectional-1','ims-dilr-section-1-2026','DILR Section Test 1 · 2026',False)
mock=build('simcat-2','ims-simcat-2-2026','SimCAT 2 · 2026',True)

# Tables checked visually against original screenshots; retain actual chart/table crops too.
dg=dilr['sections'][0]['groups'];mg=mock['sections'][1]['groups']
s=dg[1]['stimulus'];a=s.index('Po Rounds');b=s.index("- Chakram",a)
dg[1]['stimulus']=s[:a]+'Rounds: Uno | Dos | Tres | Quatre | Cinco\nAkram: U+31 | D | T+13 | Q+4 | C+19\nBikram: U+24 | D+9 | T | Q+7 | C+29\nChakram: U+19 | D+15 | T+8 | Q | C+34\nDikram: U+32 | D+27 | T+36 | Q+26 | C\nEmram: U+26 | D+12 | T+33 | Q+18 | C+21\nFimram: U | D+8 | T+9 | Q | C+24\n\n'+s[b:]
s=dg[2]['stimulus'];a=s.index('Matches Total');b=s.index('Further following',a)
dg[2]['stimulus']=s[:a].rstrip()+'\n\nTeam | Played | Won | Drawn | Lost | Goals scored | Goals conceded\nAustralia | 5 | 4 | 1 | 0 | 23 | 6\nGermany | 5 | 2 | 3 | 0 | 9 | 4\nPoland | 5 | 2 | 1 | 2 | 8 | 9\nSpain | 5 | 2 | 1 | 2 | 7 | 13\nIndia | 5 | 1 | 1 | 3 | 5 | 10\nCanada | 5 | 0 | 1 | 4 | 3 | 13\n\n'+s[b:]
s=mg[1]['stimulus'];a=s.index('Processing Plant');b=s.index('Additional Information:',a)
mg[1]['stimulus']=s[:a].rstrip()+'\n\nProcessing plant | Plastic content (% of total raw material) | Processing loss (% of total raw material)\nAlpha | 40% | 20%\nBeta | 30% | 25%\nGamma | 50% | 10%\nDelta | 25% | 20%\n\n'+s[b:]
mg[1]['stimulus']=mg[1]['stimulus'].replace('Tota/', 'Total').replace('tosum','to sum').replace('non-plasticraw','non-plastic raw').replace('6.1n','6. In')
s=mg[3]['stimulus'];a=s.index('35');b=s.index('The following facts',a)
mg[3]['stimulus']=s[:a]+'''Fresh admissions (bar graph):
Class VII in 2022: 32
Class VIII in 2023: 25
Class IX in 2024: 20

Number of fresh-admission students who later failed and could not be promoted:
Admission cohort | To class VIII | To class IX | To class X
Class VII in 2022 | 5 | 2 | 0
Class VIII in 2023 | — | 5 | 2
Class IX in 2024 | — | — | 3

'''+s[b:]
mg[3]['stimulus']=mg[3]['stimulus'].replace('10**','10th').replace('10“','10th').replace('10”','10th').replace('10°','10th').replace('33%','33 1/3%').replace('wasn:', 'was n :').replace('where nis','where n is').replace('‘original students.','‘original students’.').replace('years. Fresh admissions','years.\n\nFresh admissions')
mg[1]['stimulus']=mg[1]['stimulus'].replace('used. 6. In Gamma','used.\n\n6. In Gamma')

def add_asset(t,g,d,n,box,key,alt):
    im=Image.open(ROOT/f'source-images/{d}/Screenshot ({n}).png').crop(box);buf=io.BytesIO();im.save(buf,format='PNG')
    t.setdefault('assets',{})[key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}
    g.setdefault('assetIds',[]).append(key)
add_asset(dilr,dg[1],'dilr-sectional-1',24,(49,361,385,488),'spanish-scores','Original Spanish game score table; the values are also transcribed above.')
add_asset(dilr,dg[2],'dilr-sectional-1',31,(57,475,605,615),'hockey-table','Original hockey tournament table; the values are also transcribed above.')
add_asset(mock,mg[1],'simcat-2',74,(38,405,423,480),'eco-blocks-table','Original processing-plant table; the values are also transcribed above.')
add_asset(mock,mg[3],'simcat-2',82,(38,393,317,553),'school-admissions-chart','Fresh admissions: Class VII 2022, 32; Class VIII 2023, 25; Class IX 2024, 20.')
add_asset(mock,mg[3],'simcat-2',82,(38,600,423,697),'school-failures-table','Original table of fresh-admission students failing promotion; the values are transcribed above.')

for name,t in [('dilr-section-1.json',dilr),('simcat-2.json',mock)]:
    (ROOT/'samples'/name).write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,[(s['code'],sum(len(g['questions']) for g in s['groups'])) for s in t['sections']])
