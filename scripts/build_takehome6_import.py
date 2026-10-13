"""Build reviewed Take Home 6 from the local ZIP OCR and original image crops.

Inputs: source-images/take-home-6 and extraction/{take-home-6-records,
analysis-takehome6}.json. Keys and benchmark corrections were visually checked.
"""
from pathlib import Path
from PIL import Image
import base64
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'source-images/take-home-6'
OCR = ROOT/'extraction/take-home-6'
ANS = {
    'VARC': 'B D C D A B D D C D B D C D A B 4 3 B C 2143 4132 D B'.split(),
    'DILR': 'C B C A 315 A C A C D 453 3229 1448 B C B B 1 B C A B'.split(),
    'QA': 'A B D 15 2 7 64 A B C B 1630 B A 45 B B 760 B A C D'.split(),
}
TITA = {'VARC': {17,18,21,22}, 'DILR': {5,11,12,13,18}, 'QA': {4,5,6,7,12,15,18}}
CATEGORIES = {
    'VARC': 'A A A A A C A C A B B A B A A B A C B A B B C B'.split(),
    'DILR': 'C C C C C A A A A B C C C C A A A A B B C B'.split(),
    'QA': 'B A A A C B C A A B A C B A A B C B A C C B'.split(),
}
QA_PROMPTS = {
    1: 'In the diagram given below, ∠DAB is an exterior angle of triangle ABC and AE is the bisector of ∠DAB. It is also given that ℓ(AC) = 18 cm, ℓ(AB) = 12 cm and ℓ(BC) = 8 cm. Find ℓ(EB).',
    5: 'If x is an integer, how many values of x are possible in the equation shown?',
    7: 'What is the area (in square units) bounded by the curves |x + y| = 4 and |x − y| = 8?',
    10: 'If a, b, c are positive numbers such that a + b + c = 1, then the minimum value of (1 + a)(1 + b)(1 + c) / [(1 − a)(1 − b)(1 − c)] is:',
    16: 'If one root of the equation x² − 2x + 3 = 0 is p, then the other root is:',
    21: 'Given: f(x) = x² + ax + 3b and g(x) = x² + bx − c. If a, b and c are natural numbers and f(−3) = g(−3) = 0, then what is the value of (a + b + c)?',
}
QA_OPTIONS = {
    1: ['16 cm','18 cm','21 cm','24 cm'], 9: ['3 : 1','2 : 1','3 : 2','5 : 2'],
    11: ['1/4','1/3','1/2','1 or 1/3'], 14: ['132000','66000','88000','None of these'],
    16: ['7/2 − p²/2','1/2 − p²/2','3/2 + p²/2','−1/2 − p²/2'],
}
DILR_OPTIONS = {
    2: ['140','251','258','111'], 3: ['112','85','103','108'],
    6: ['1st September','2nd September','3rd September','5th September'],
    7: ['2nd September - Dayal Bugyal - Special trek','3rd September - Kedarkantha - Special trek','4th September - Deorital Chandrashila - Family trek','5th September - Har ki Dun - Children trek'],
    8: ['Deorital Chandrashila','Tulian lake','Har ki Dun','Either Deorital Chandrashila or Tulian lake'],
    10: ['2nd September','4th September','5th September','6th September'],
    14: ['1','2','3','Never'], 15: ['5 years','12 years','10 years','Cannot be determined'],
    16: ['Vighnesh or Yash','Yash','Suhrud or Yash','Nachiket or Vighnesh'],
    17: ['5 years','17 years','10 years','Cannot be determined'],
    19: ['270','380','450','More than one of the above'], 20: ['B','C','F','Cannot be determined'],
    21: ['20 : 21','120 : 121','70 : 71','1 : 1'], 22: ['370','390','410','400'],
}

def clean(s):
    s = re.sub(r'\s+', ' ', s).strip()
    for a,b in {'Itturns':'It turns','Astationery':'A stationery','anumber':'a number','Asignificant':'A significant','insound':'in sound','toits':'to its','amidst 2 swarm':'amidst a swarm','as 2 standard':'as a standard','is 2 spectrum':'is a spectrum','as 2 spectrum':'as a spectrum','Davies, 2 British':'Davies, a British','for 2 phenomenon':'for a phenomenon','historian lan Morris':'historian Ian Morris','TrainA':'Train A','(0, O)':'(0, 0)','Turtles age':"Turtle’s age",'1° day':'1st day','15* September':'1st September','6" September':'6th September','4" rank':'4th rank'}.items():
        s = s.replace(a,b)
    return re.sub(r'\s+(?:[|g@¢]|i\)|Ps|a)$','',s).strip()

def paragraphs(s):
    return '\n\n'.join(clean(p) for p in s.split('\n\n') if p.strip())

def seconds(s):
    a,b=map(int,s.split(':')); return a*60+b

def build():
    records=json.loads((ROOT/'extraction/take-home-6-records.json').read_text(encoding='utf8'))
    stats=json.loads((ROOT/'extraction/analysis-takehome6.json').read_text(encoding='utf8'))
    fixes={'VARC':{2:{0:100},3:{0:100},4:{0:100},12:{1:89.13},13:{0:86},14:{1:92.68},15:{0:76,1:81.58,2:62},20:{1:91.89},22:{0:84},24:{0:88}},'DILR':{1:{2:12},5:{1:42.86}},'QA':{6:{1:70.59},13:{0:48},17:{1:81.25}}}
    test={'schemaVersion':1,'testType':'full','id':'ims-take-home-6-2026','revision':1,'title':'Take Home 6 · SimCAT 106 · 2026','description':'68 questions with original figures, four RC passages, five intact DILR sets and complete supplied source analysis.','sections':[{'code':c,'groups':[]} for c in ANS],'assets':{}}
    rm={(r['section'],r['number']):r for r in records}; questions={}; results=[]
    for r in records:
        c,n=r['section'],r['number']; p=r['prompt'].split('\nSade')[0].split('\nv\n')[0]
        if (c,n) in [('VARC',23),('QA',14)]: p=p.split('\nA ')[0]
        if c=='QA': p=QA_PROMPTS.get(n,p)
        if c=='DILR': p=p.replace(' Ps','')
        p=clean(p)
        if c=='VARC' and n in TITA[c]: p=re.sub(r' (?=[1-5]\. )','\n\n',p)
        if c=='VARC': p=p.replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:').replace('essence of the passage. ','essence of the passage.\n\n')
        # QA areas reconcile the supplied counts, A/B/C matrix and exact area times.
        area=('Reading Comprehension' if n<=16 else 'Verbal Reasoning') if c=='VARC' else ('Logical Reasoning' if 6<=n<=10 or 15<=n<=18 else 'Data Interpretation') if c=='DILR' else next(a for a,ns in {'Geometry':[1,7,13],'Arithmetic':[2,3,8,9,14,15,19,20],'Algebra':[4,10,16,18,22],'Modern Math':[5,11,17,21],'Numbers':[6,12]}.items() if n in ns)
        q={'id':f'take-home-6-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[c] else 'MCQ','prompt':p,'area':area,'topic':area,'selectionCategory':CATEGORIES[c][n-1]}
        q['answer']=[ANS[c][n-1]] if q['type']=='TITA' else ANS[c][n-1]
        if q['type']=='MCQ':
            opts=(QA_OPTIONS if c=='QA' else DILR_OPTIONS if c=='DILR' else {}).get(n,[clean(o['text']) for o in r['options']])
            if c=='VARC' and n in [23,24]: opts=['Option 4','Option 2','Option 1','Option 3']
            assert len(opts)==4 and all(opts),(c,n,opts)
            q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(opts)]
        st=stats[c][n-1]; vals=list(st['values'])
        while len(vals)<3: vals.append(0)
        for i,v in fixes.get(c,{}).get(n,{}).items(): vals[i]=v
        att,acc,pv=map(float,vals[:3]); assert all(0<=v<=100 for v in (att,acc,pv)),(c,n,vals)
        q['benchmark']={'source':'IMS supplied question-wise analysis','sourceImage':f'Screenshot 2026-10-13 '+{'VARC':'211244','DILR':'211253','QA':'211303'}[c]+'.png','topperTimeSeconds':seconds(st['topperTime']),'topperAttemptPercent':att,'topperAccuracyPercent':acc,'topperPValue':pv}
        results.append({'questionId':q['id'],'outcome':st['outcome'],'timeSeconds':seconds(st['time'])}); questions[c,n]=q

    def left(c,n): return (OCR/Path(rm[c,n]['file']).stem/'left.txt').read_text(encoding='utf8').split('\n',1)[1].strip()
    def group(c,a,b,title,p=None):
        g={'id':f'take-home-6-{c.lower()}-group-{a}','title':title,'questions':[questions[c,n] for n in range(a,b+1)]}
        if p:g['stimulus']=paragraphs(p)
        test['sections'][list(ANS).index(c)]['groups'].append(g); return g
    def embed(target,filename,key,alt,box=None):
        im=Image.open(SRC/filename)
        if box: im=im.crop(box)
        data=io.BytesIO(); im.save(data,format='PNG')
        test['assets'][key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode()}; target.setdefault('assetIds',[]).append(key)
    for n,title in [(1,'Firefly communication'),(5,'Acoustic naturalness'),(9,'Measuring poverty'),(13,'Climate and the Roman Empire')]: group('VARC',n,n+3,title,left('VARC',n))
    for n in range(17,25): group('VARC',n,n,f'Verbal ability · Q{n}')
    g=group('DILR',1,5,'Stationery shop profits',left('DILR',1).split('Cumulative Booked profit')[0])
    embed(g,'Q1 to Q5 DILR.png','th6-dilr-profits','Original cumulative booked and unbooked profit charts.')
    p=left('DILR',6)
    # Dates are superscripts in the source; replace OCR ordinal artifacts explicitly.
    for a,b in {'15*':'1st','1stt':'1st','2"d':'2nd','2™':'2nd','2"':'2nd','3°':'3rd','4\'"':'4th','4"':'4th','5"':'5th','6"':'6th','6%':'6th','5t4':'5th','On 5 September':'On 5th September'}.items(): p=p.replace(a,b)
    group('DILR',6,10,'Trek schedules',p)
    p=(OCR/'Q11 to Q14 Full set/full.txt').read_text(encoding='utf8')
    p=p.split('Public Limited')[0]+'\n\n'+p[p.index('(1) ABCD'):]
    g=group('DILR',11,14,'Share prices',p)
    embed(g,'DILR Q11 to Q14.png','th6-dilr-shares','Original five-day share-price table.')
    group('DILR',15,18,'Friends and pets',left('DILR',15))
    p=left('DILR',19); p=re.sub(r'\npatie[^\n]*','',p).replace('lt’s Christmas','It’s Christmas')
    g=group('DILR',19,22,'Reporters and villages',p)
    for i in [1,2]: embed(g,f'DILR Q19 to Q22 Figure{i}.png',f'th6-dilr-reporters-{i}',f'Original village percentages using {"incorrect" if i==1 else "corrected"} data.')
    for n in range(1,23): group('QA',n,n,f'Quantitative ability · Q{n}')
    embed(questions['QA',1],rm['QA',1]['file'],'th6-qa-1','Original geometry figure for QA question 1.',(8,118,462,311))
    embed(questions['QA',5],rm['QA',5]['file'],'th6-qa-5','Original logarithmic equation for QA question 5.',(502,343,875,390))
    mapper=[]
    for c,ss in {'VARC':[29,35,37,41,47,49],'DILR':[19,24,26,29,34,36],'QA':[22,27,29,33,42,45],'Overall':[64,76,80,86,92,94]}.items():
        mapper.extend({'section':c,'percentile':p,'score':s} for p,s in zip([70,85,90,95,99,99.5],ss))
    test['sourceAnalysis']={'label':'Original IMS attempt supplied with Take Home 6. Question timings and benchmarks are transcribed from the question-wise analysis screenshots.','sourceImages':[f'Screenshot 2026-10-13 {s}.png' for s in ['211223','211231','211244','211253','211303','211326']],'reportedScore':45,'percentile':40.46,'sectionScores':[{'section':c,'score':s,'percentile':p} for c,s,p in [('VARC',24,55.95),('DILR',14,54.81),('QA',7,16.94)]],'questionResults':results,'percentileMapper':mapper,'reportedAreas':[dict(zip(['label','score','accuracy','timeLabel','marksPerMinute','timePerAttemptLabel'],row)) for row in [('Overall',45,54.55,'02:00',.37,'03:40'),('VARC',24,58.82,'00:40',.6,'02:21'),('Reading Comprehension',20,66.67,'00:30',.66,'02:30'),('Verbal Reasoning',4,40,'00:09',.41,'01:56'),('DILR',14,62.5,'00:40',.35,'05:03'),('Data Interpretation',0,0,'00:06',0,'03:20'),('Logical Reasoning',14,83.33,'00:33',.42,'05:37'),('QA',7,37.5,'00:40',.17,'05:03'),('Geometry',0,0,'00:04',0,'00:00'),('Arithmetic',7,60,'00:28',.24,'05:44'),('Algebra',0,0,'00:04',0,'04:51'),('Modern Math',0,0,'00:00',0,'00:39'),('Numbers',0,0,'00:01',0,'01:40')]]}
    (ROOT/'samples/take-home-6.json').write_text(json.dumps(test,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'Built Take Home 6: {len(questions)} questions, {len(test["assets"])} original assets, {len(results)} source results.')

if __name__=='__main__': build()
