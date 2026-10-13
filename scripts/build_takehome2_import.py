"""Build Take Home 2 (SimCAT 102) from reviewed source screenshots and OCR."""
from pathlib import Path
from PIL import Image
import json, re, io, base64
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source-images/take-home-2'
OCR=ROOT/'extraction/take-home-2'
records=json.loads((ROOT/'extraction/take-home-2-records.json').read_text(encoding='utf8'))
ANS={'VARC':'A C D C A C B C A D C C A D A C A C 2431 3142 D D 1 3'.split(),'DILR':'B 6 81 A 21 D 25 C 35 B D A D D B D D D A B D D'.split(),'QA':'A B 14 303104 1374 A 625 D C 25 12 D D C 23 A B D D C 13 B'.split()}
TITA={'VARC':{19,20,23,24},'DILR':{2,3,5,7,9},'QA':{3,4,5,7,10,11,15,21}}
OPTIONS={
 ('DILR',1):['0','1','2','3'],('DILR',4):['24','36','48','96'],('DILR',6):['70','70 5/12','71 7/12','72 11/12'],('DILR',11):['D','E','B','A'],('DILR',12):['AKR-B','BSK-D','CDD-A','ESG-C'],('DILR',13):['A and B','B and D','A and E','D and A'],('DILR',18):['2','3','5','6'],('DILR',19):['C','D','A','Cannot be determined'],
 ('VARC',21):['Option 1','Option 2','Option 3','Option 4'],('VARC',22):['Option 4','Option 1','Option 2','Option 3'],
 ('QA',1):['3','5','9','7'],('QA',6):['9 hours','9 hours and 20 minutes','10 hours','More information is needed to answer this question'],('QA',8):['On the 15th year of that calendar','On the 16th year of that calendar','On the 4th year of that calendar','On the 5th year of that calendar'],('QA',12):['6','±6','12','±12'],('QA',13):['109','113','Either 109 or 113','Either 111 2/3 or 333'],('QA',14):['−1','−2','−2/3','−3'],('QA',16):['4√(4 + 2√2)','2√(4 + 2√2)','4√(4 + 3√2)','2√(4 + 3√2)'],('QA',18):['(5π/2) cm','(21π/5) cm','(15π/4) cm','(25π/3) cm'],('QA',19):['Only I & II','Only I & III','Only II & III','All three']}
PROMPTS={
 ('QA',1):'If f(x) = x + 2x² + 3x³ + 4x⁴ + 5x⁵, where x is a positive integer, f(x) will always be divisible by _____.',
 ('QA',2):'If 3^(3x) − 9 × 3^(2x) + 23 × 3^x = 15, then which of the following is true?',
 ('QA',3):'If ‘a’ and ‘b’ are two positive real numbers and a³b⁴ = 32768 then the minimum possible value of (3a + b) is _____.',
 ('QA',6):'If Vande Bharat Express runs slower than its usual speed by 24 kmph, it reaches its destination later than its usual time by three hours. If it runs faster than its usual speed by 12 kmph, it reaches its destination in 8 hours. What is the usual time taken by Vande Bharat Express to reach its destination?',
 ('QA',9):'China, USA, and India hold the top 3 positions in terms of emitting CO₂. In the year 2016, China emitted 10 billion tons of CO₂ (6 billion tons for industrial activities), USA emitted 5 billion tons of CO₂ (3 billion tons for industrial activities) and India emitted 2.5 billion tons of CO₂ (1.5 billion tons for industrial activities). In 2020, USA and India could reduce their non-industrial emission of CO₂ by 30% but China increased the same by 10%. In 2020, although the emission for industrial activities was reduced by 7 1/7% by these three countries, China alone increased it by 10%. What is the ratio of total emission of CO₂ by these three countries together for industrial to non-industrial activities in 2020?',
 ('QA',11):'How many non-zero integers satisfy the inequality x² − 5|x| − 6 ≤ 0?',
 ('QA',12):'If c = 4x/y + 9y/x for some non-zero real numbers x and y then for what value of c, x/y can take a unique value?',
 ('QA',14):'A function f(x) = ax² + bx + c such that a ≠ 0. f(x) ≤ f(0.75) for all real ‘x’. Further, ‘b’ is an integer. The maximum possible value of ‘a’ is _____.',
 ('QA',15):'If the equation 3x³ − 16x² + mx − 6 = 0 has three positive real roots, out of which two roots are reciprocals of each other, the value of m is _____.',
 ('QA',17):'In a right-angled triangle ABC where AB ⊥ BC, m ∠ACB = x°. The value of x (in degrees) satisfies the equation 9^(sin² x) + 9^(cos² x) = 6. Find the value of x.',
 ('QA',18):'A circle is drawn with PQ as its diameter. A perpendicular is drawn to PQ at C meeting the circle at A and B. If ℓ(AC) = 4 cm and ℓ(PC) = 3 cm, then find the circumference of the circle.',
 ('QA',19):'A triangle ABC has an area of 24 sq. units and its side BC is located on the line 3x + 4y = 24. Which of the following statements can be true at the same time?\n\nS-I: The shortest possible distance between line BC and the origin is 4.8 units.\nS-II: It is possible that the origin can be the coordinates of vertex A.\nS-III: AB ⊥ AC',
 ('QA',21):'Find the number of possible distinct integral values of X in the original expression below.',
 ('QA',22):'Three natural numbers ‘a’, ‘b’, and ‘c’ are in arithmetic progression. Also, the numbers (a − 1), b, and (c + 4) are in geometric progression. If a + b + c = 18, find the value of a² + b² + c².',
 ('DILR',7):'Level-2 assembly starts at least after _____ minutes from the starting of Level-1 assembly.'}
TIMES={'VARC':'0:19 0:07 0:03 0:02 6:29 1:19 0:55 0:16 5:19 0:32 0:27 1:05 0:46 5:47 0:33 2:56 0:09 0:07 1:34 2:41 2:24 1:12 2:04 2:37','DILR':'0:41 0:09 0:02 0:01 0:02 0:15 0:08 0:01 0:07 0:06 3:15 0:47 9:34 1:39 10:48 9:21 1:28 0:45 0:28 0:17 0:18 0:01','QA':'0:47 0:35 0:06 3:06 5:17 2:37 0:52 1:08 2:35 1:45 1:37 4:36 2:30 0:19 2:40 2:05 1:12 1:02 1:35 3:40 0:12 0:09'}
CORRECT={'VARC':{6,7,9,11,12,14,15,19,20,22,24},'DILR':{11,12,13,14},'QA':{6}}
INCORRECT={'VARC':{5,13,16,21,23},'DILR':{15,16,18},'QA':{4,5,11}}
BENCH={
'VARC':'''5:42 80 77.5 62 A
0:57 82 87.8 72 A
0:56 66 69.7 46 B
0:44 56 85.71 48 B
3:31 58 68.97 40 B
0:41 60 90 54 B
0:32 64 96.88 62 A
0:31 58 89.66 52 B
4:02 86 88.37 76 A
1:03 80 77.5 62 A
1:06 82 95.12 78 A
1:38 86 88.37 76 A
4:05 90 48.89 44 B
1:13 80 52.5 42 B
0:45 90 86.67 78 A
1:29 88 47.73 42 B
1:37 54 33.33 18 C
1:30 72 55.56 40 B
1:17 90 88.89 80 A
1:21 84 19.05 16 C
1:33 86 51.16 44 B
0:57 86 74.42 64 A
1:07 94 85.11 80 A
1:33 92 60.87 56 B''',
'DILR':'''8:21 74 89.19 66 A
0:27 82 78.05 64 A
1:13 74 48.65 36 B
0:58 74 100 74 A
0:50 72 75 54 B
1:50 2 0 0 C
0:24 30 13.33 4 C
0:14 2 0 0 C
0:08 22 9.09 2 C
0:18 2 100 2 C
5:27 96 87.5 84 A
0:37 96 91.67 88 A
0:53 96 87.5 84 A
1:30 90 75.56 68 A
4:35 70 62.86 44 B
1:24 50 88 44 B
1:50 46 52.17 24 C
1:10 46 69.57 32 B
3:42 96 87.5 84 A
0:58 92 84.78 78 A
1:17 88 72.73 64 A
2:00 92 73.91 68 A''',
'QA':'''2:59 88 90.91 80 A
1:46 76 73.68 56 B
2:15 80 82.5 66 A
3:00 64 68.75 44 B
2:30 98 87.76 86 A
3:22 84 80.95 68 A
2:08 72 77.78 56 B
0:59 24 41.67 10 C
2:25 46 82.61 38 B
3:02 58 86.21 50 B
1:41 82 75.61 62 A
1:23 58 93.1 54 B
1:51 34 88.24 30 B
1:00 22 81.82 18 C
1:26 72 86.11 62 A
0:55 26 84.62 22 C
0:55 56 92.86 52 B
1:14 30 93.33 28 C
0:49 32 93.75 30 B
1:14 32 81.25 26 C
0:41 42 9.52 4 C
2:34 64 96.88 62 A'''}
def secs(s):
 m,s=map(int,s.split(':'));return 60*m+s
def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 s=re.sub(r'\s+[.|=\-]$','',s)
 s=re.sub(r'\s+(?:g@|g|je|Q|i\)|@)\s*(?:\|)?$','',s)
 s=s.removesuffix(' |').strip()
 for a,b in [(' 2 more',' a more'),('as 2 ','as a '),('towards 2 ','towards a '),('through 2 ','through a '),('a hereditary','a hereditary'),('inits','in its'),('inthe ','in the '),('their g minimal','their minimal'),('ona unified','on a unified'),('lan Watts','Ian Watts'),('Ain ','A in '),('ina day','in a day'),('Awas','A was'),('Acertain','A certain'),('Ajar','A jar'),(' lf ',' If '),('supremacy*','supremacy"'),('best . captures','best captures'),('decide in . which','decide in which'),('Secondary . schools','Secondary schools'),('all three . games','all three games'),('Out of . these','Out of these'),('last, . which','last, which'),('contains . less','contains less'),('the . average','the average')]:s=s.replace(a,b)
 return s

test={'schemaVersion':1,'testType':'full','id':'ims-take-home-2-2026','revision':1,'title':'Take Home 2 · SimCAT 102 · 2026','description':'Full mock: 24 VARC, 22 DILR and 22 QA questions. Original figures, answer keys and supplied IMS attempt analysis included.','sections':[{'code':c,'groups':[]} for c in ANS]}
qm={};rm={};results=[]
for rec in records:
 c,n=rec['section'],rec['number'];key=c,n;rm[key]=rec
 area=('Reading Comprehension' if n<=16 else 'Verbal Reasoning') if c=='VARC' else ('Data Interpretation' if n<=5 or 11<=n<=14 else 'Logical Reasoning') if c=='DILR' else next(a for end,a in [(2,'Numbers'),(10,'Arithmetic'),(15,'Algebra'),(19,'Geometry'),(22,'Modern Math')] if n<=end)
 p=rec['prompt']
 if c=='VARC' and n in (19,20):p=p[:p.rfind('\n(2')];p=re.sub(r'\n4$','',p)
 if c=='VARC' and n in (23,24):p=p.removeprefix('a\n');p=re.split(r'\n(?:eee|\[sacar)',p)[0];p=p.replace(' Al ',' AI ').replace('or dio files','or audio files')
 q={'id':f'take-home-2-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[c] else 'MCQ','prompt':PROMPTS.get(key,clean(p)),'area':area,'answer':[ANS[c][n-1]] if n in TITA[c] else ANS[c][n-1]}
 if q['type']=='MCQ':
  vals=OPTIONS.get(key,[clean(o['text']) for o in rec['options']]);assert len(vals)==4 and all(vals),(key,vals)
  q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(vals)]
 t,at,ac,pv,cat=BENCH[c].splitlines()[n-1].split();q['selectionCategory']=cat
 q['benchmark']={'source':'IMS supplied question-wise analysis screenshot','sourceImage':'Screenshot 2026-10-13 '+{'VARC':'114436','DILR':'114443','QA':'114450'}[c]+'.png','topperTimeSeconds':secs(t),'topperAttemptPercent':float(at),'topperAccuracyPercent':float(ac),'topperPValue':float(pv)}
 if c=='VARC' and n in (19,20,23,24):q['prompt']=re.sub(r' (?=[1-5]\. )','\n\n',q['prompt'])
 if c=='VARC' and n in (17,18):q['prompt']=q['prompt'].replace('essence of the passage. ','essence of the passage.\n\n',1)
 if c=='VARC' and n==21:
  for a,b in [('Paragraph:_ 1 ','Paragraph: ___1___ '),(' 2S. ',' ___2___ '),(' 3_. ',' ___3___ '),(' _4 ',' ___4___ '),('?culture war? This','?culture war?. This')]:q['prompt']=q['prompt'].replace(a,b)
 if c=='VARC' and n==22:
  for a,b in [('Paragraph:_ 1. ','Paragraph: ___1___ '),(' 2 ??- ',' ___2___ '),('.__3___?- ','. ___3___ '),(' _4 _. ',' ___4___ ')]:q['prompt']=q['prompt'].replace(a,b)
 if c=='VARC' and n in (21,22):q['prompt']=q['prompt'].replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:')
 qm[key]=q;results.append({'questionId':q['id'],'outcome':'Correct' if n in CORRECT[c] else 'Incorrect' if n in INCORRECT[c] else 'Unanswered','timeSeconds':secs(TIMES[c].split()[n-1])})
def embed(target,filename,box,key,alt):
 im=Image.open(SRC/filename)
 if box:im=im.crop(box)
 b=io.BytesIO();im.save(b,format='PNG');test.setdefault('assets',{})[key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()};target.setdefault('assetIds',[]).append(key)
def left(c,n):return (OCR/Path(rm[c,n]['file']).stem/'left.txt').read_text(encoding='utf8')
for n,title in [(1,'Jane Austen and feminism'),(5,'Polyphonic assemblages'),(9,'Shyness and civilization'),(13,'War outcomes')]:
 p=re.split(r'Choose the best answer to each question\.',left('VARC',n),maxsplit=1)[1].strip()
 for a,b in [('lan Watts','Ian Watts'),('“community The','“community”. The'),('| first','I first'),('; | was','; I was'),('was 2 revelation','was a revelation'),('for 2 coordinated','for a coordinated'),('have 2 combination','have a combination'),('Acountry','A country'),('Athird','A third')]:p=p.replace(a,b)
 test['sections'][0]['groups'].append({'id':f'take-home-2-varc-group-{n}','title':title,'stimulus':p,'questions':[qm['VARC',i] for i in range(n,n+4)]})
for n in range(17,25):test['sections'][0]['groups'].append({'id':f'take-home-2-varc-group-{n}','title':f'Verbal ability · Q{n}','questions':[qm['VARC',n]]})
for a,b,title in [(1,5,'Village school teachers'),(6,10,'Manufacturing assembly lines'),(11,14,'Cricket bowler rankings'),(15,18,'Talent show teams'),(19,22,'Three-game tournament')]:
 p=left('DILR',a)
 if a==1:p=p.split('questions that follow.',1)[1].strip()
 if a==6:
  p=p[p.index('‘Mahaveer'):];p=p[:p.index('Assembly produced')]+p[p.index('Further it is known'):];p=p.replace('(=0)','(≥0)')
 if a==11:p=p[p.index('In the Cricket'):];p=p[:p.index('= Wickets')]+p[p.index('Also, know that'):]
 if a==15:p=p.split('questions that follow.',1)[1].strip();p=p[:p.index('after each round.')+len('after each round.')]
 if a==19:p=p.split('questions that follow.',1)[1].strip();p=p[:p.index('[Teams')]+p[p.index('The following points'):];p=p.replace('gets O points','gets 0 points')
 g={'id':f'take-home-2-dilr-group-{a}','title':title,'stimulus':p.strip(),'questions':[qm['DILR',i] for i in range(a,b+1)]}
 if a==6:embed(g,'DILR DIagram Q6 to Q10.png',None,'takehome2-assembly-table','Original manufacturing assembly table.')
 if a==11:embed(g,'DILR DIagram Q11 to Q14.png',None,'takehome2-bowling-graph','Original bowler-ranking graph.')
 if a==15:embed(g,rm['DILR',15]['file'],(48,491,414,710),'takehome2-talent-table','Original talent-show points table.')
 if a==19:embed(g,rm['DILR',19]['file'],(49,349,305,466),'takehome2-games-table','Original tournament points table.')
 test['sections'][1]['groups'].append(g)
for n in range(1,23):test['sections'][2]['groups'].append({'id':f'take-home-2-qa-group-{n}','title':f'Quantitative ability · Q{n}','questions':[qm['QA',n]]})
embed(qm['QA',21],rm['QA',21]['file'],(64,73,760,177),'takehome2-qa21-expression','Original expression and question for QA 21.')
test['sourceAnalysis']={'label':'Original IMS attempt supplied in TakeHome 2 screenshots','sourceImages':['Screenshot 2026-10-13 '+x+'.png' for x in ['114416','114425','114436','114443','114450','114459']],'reportedScore':41,'percentile':44.82,'sectionScores':[{'section':c,'score':s,'percentile':p} for c,s,p in [('VARC',29,82.59),('DILR',9,32.32),('QA',3,18.07)]],'questionResults':results,'percentileMapper':[]}
for c,vs in [('VARC',[24,31,34,39,47,50]),('DILR',[21,27,30,34,42,43]),('QA',[17,23,26,30,41,45]),('Overall',[58,71,77,84,91,92])]:test['sourceAnalysis']['percentileMapper'] += [{'section':c,'percentile':p,'score':v} for p,v in zip([70,85,90,95,99,99.5],vs)]
area_data=[('Overall',41,59.26,'02:00',.34,'04:29'),('VARC',29,68.75,'00:39',.73,'02:30'),('Reading Comprehension',18,70,'00:26',.67,'02:42'),('Verbal Reasoning',11,66.67,'00:12',.86,'02:08'),('DILR',9,57.14,'00:40',.22,'05:46'),('Data Interpretation',12,100,'00:16',.74,'04:02'),('Logical Reasoning',-3,0,'00:24',-.12,'08:01'),('QA',3,25,'00:40',.07,'10:08'),('Numbers',0,0,'00:01',0,'00:00'),('Arithmetic',3,33.33,'00:17',.17,'05:49'),('Algebra',0,0,'00:11',0,'11:42'),('Geometry',0,0,'00:05',0,'00:00'),('Modern Math',0,0,'00:04',0,'00:00')]
test['sourceAnalysis']['reportedAreas']=[dict(zip(['label','score','accuracy','timeLabel','marksPerMinute','timePerAttemptLabel'],row)) for row in area_data]
output=ROOT/'samples/take-home-2.json';output.write_text(json.dumps(test,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Wrote {output}: {len(qm)} questions, {len(results)} source results, {len(test["assets"])} original assets')
