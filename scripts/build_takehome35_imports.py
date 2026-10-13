"""Reviewed imports for TakeHome 3 / 5; source figures are always embedded crops.
Run after extraction/parse_takehome35.py and extraction/analysis_takehome35.py.
Unrevealed answers remain null in a draft until supplied; no guessed answer keys.
"""
from pathlib import Path
from PIL import Image
import json,re,io,base64,sys
ROOT=Path(__file__).resolve().parents[1]
# TakeHome 5 DILR Q1-4 verified from screenshots 2026-10-13 202909/202915/202921/202929.
# Q21-22 verified from Screenshot (200)/(201).png (correct answers, not entered responses).
ANS={3:{'VARC':'C B D A C A D C A A C D B D D D C A C A 1 3 3142 4312'.split(),'DILR':'5 B A 28800 C 7 4 C A A 5 58 3 340 325 25 A B 6 A 4 76'.split(),'QA':'0 A B 84 C 15 C B C C B 15 429 B C B C 9 B C 5 C'.split()},5:{'VARC':'D D A B C A D C C D A B C A B D 5 4 A D C A 2143 3142'.split(),'DILR':'C 800 1150 B B 27 D 11 D 1 26 2 B B 4 1 A C B 0 C 70'.split(),'QA':'B D D 10 C 77 C 6912 C 300 A C 22 B D A C C C 22 A A'.split()}}
TITA={3:{'VARC':{21,22,23,24},'DILR':{1,4,6,7,11,12,13,14,15,16,19,21,22},'QA':{1,4,6,12,13,18,21}},5:{'VARC':{17,18,23,24},'DILR':{2,3,6,8,10,11,12,15,16,20,22},'QA':{4,6,8,10,13,20}}}
QP={3:{
1:'Find the smallest integer value of ‘x’ when (x + 7)/(|3 − x| + 2) > 1.',
2:'The number of terms present in the expression (1 + 2x + 3x²)⁴ after expansion is _____.',
3:'Which of the following is true if a⁴ + a²b² + b⁴ = M and a² + ab + b² = N?',
4:'If (x² − y²), 3x^(3/2) and (x² + y²) are natural numbers such that they form a Pythagorean triplet. Further, both ‘x’ and ‘y’ are natural numbers and x > y. Find the smallest possible area (in sq. units) of a triangle having sides (x² − y²), 3x^(3/2) and (x² + y²).',
5:'In the expression (46a¹⁰ + Ma⁵ + 90), both ‘a’ and ‘M’ are positive integers. If (ba⁵ + c) is a factor of the given expression, where ‘b’ and ‘c’ are positive integers, then the maximum possible value of ‘M’ is _____.',
7:'In the pentagon PQRST below, QS and RT are perpendicular bisectors of each other and ΔQPT is an isosceles triangle. Find the ratio of area of ΔQPT to that of the pentagon.',
8:'In the diagram below, O is the centre of the circle. It is given that sin x° = 0.8 where 0 < x < 90. Find the area of the shaded region in the given diagram.',
10:'f(x) = sin²x, for all real values of ‘x’ as well as all real values of f(x). ‘x’ is the measure of an angle in degrees. Find the value of f(0) + f(5) + f(10) + … + f(85) + f(90).',
11:'Find the value of ‘m’, if m + log₁₂(3ᵐ − 4) = m log₁₂4 + log₁₂5.',
14:'A traveller embarks on a journey. Each day, he alternates his direction: on the 1st day, he goes north; on the 2nd day, east; on the 3rd day, south; on the 4th day, west; and so on, following this pattern. On the nth day, he travels (n²/2) miles. What is his approximate distance from the starting point at the end of the 20th day?',
19:'If ‘a’ and ‘b’ are positive real numbers such that 2/a + 1/b = 6, what can be the minimum value of (2a + b)?',
20:'Set A and B are defined as follows:\n\nA = {x | x ∈ N, GCD(x, 48) = 1, x < 32}\nB = {y | y ∈ N, GCD(y, 60) = 1, y < 40}\n\nWhich of the following is a value of n(A) + n(B)?',
22:'If ‘x’ is the smallest positive integer such that ‘5000 − x’ is the sum of the squares of the first ‘y’ natural numbers, find the product of x and y.'},5:{
1:'Find the sum of all real roots of the equation: (x + 3)² + 3|x + 3| − 4 = 0.',
3:'ΔABC is a right-angled triangle and it is right-angled at C. If length of the median on hypotenuse is 13 cm and length of one among the other two medians is √601 cm, find the area of ΔABC.',
4:'In the following diagram, ▱ABCD is a trapezium. AB ∥ CD and the base angles A and B are complementary to each other. EF is the median of the trapezium and Q and P are the midpoints AB and CD respectively. If AB = 16 and PQ = 6, then what is the length of EF?',
6:'▱ABCD is a trapezium where AB ∥ CD. It is given that ℓ(AB) = 14 cm and ℓ(CD) = 22 cm. If the two diagonals AC and BD intersect at point O and the area of the trapezium is 324 sq. cm then the area (in sq. cm) of ΔAOD will be _____.',
7:'A function f(x) is defined as (x + 1)f(x + 1) + xf(x) + (x − 1)f(x − 1) = 0 for x ≥ 2. If f(1) = 120 and f(9) = 160, find the value of f(20).',
8:'The sum of three positive real numbers ‘x’, ‘y’ and ‘z’ is 12. Find the maximum value of x²y³z.',
17:'Find the value of ‘x’ given that (162² + 0.1875)² − (162² − 0.1875)² = 27ˣ.',
19:'Which of the following numbers can be expressed in the format of p/q where both ‘p’ and ‘q’ are natural numbers and ‘q’ is a two-digit number formed by the same digit?',
21:'Find the value of (x³ − y³) if (x² − 5y² + 4xy − 31) = 0, where ‘x’ and ‘y’ are non-negative integers.',
22:'‘a’ and ‘b’ are the roots of the equation x² − 3x − p = 0 and a⁴ + b⁴ = 641. Which of the following can be a value of ‘p’?' }}
QO={3:{3:['a² + b² = (M² + N²)/(2N)','a² + b² = (M + N²)/(2N)','ab = (M + N²)/(2M)','ab = (M² − N)/(2N)'],8:['(25π/2)(1 + x/360) − 30','(25π/2)(1 + x/180) − 30','(25π/2)(1 + x/360) − 36','(25π/2)(1 + x/180) − 36'],9:['(106)₇','(56)₇','(126)₇','Cannot be determined'],10:['17/2','21/2','19/2','11/2'],11:['log₅3','log₃5','log₃15','log₅12'],19:['2/3','3/2','3','4/3']},5:{1:['6','−6','0','−2'],5:['26 cm','27 3/7 cm','31 1/5 cm','32 2/3 cm'],16:['√3 : √5','√2 : √3','√3 : √2','√5 : √3'],17:['3/4','4','3','√3/2'],19:['0.0333… (3 recurring)','0.0555… (5 recurring)','0.075757… (75 recurring)','None of these'],21:['91','87','73','69']}}
CATS={3:{'VARC':'B A B A A C B C B C A C A A B B B C C C B A B C','DILR':'B C C C C C C C C C C C C A B C B B B B C B','QA':'A A B B C C B C C B B C C B A A A B B B B A'},5:{'VARC':'A A B A A A B A A A A A A B A A A A B C C C A C','DILR':'B C C B C C C C C B B B C B A A A A B B B B','QA':'A C B C B B C B C A A A B A B B A B B B B A'}}
# Exact manual corrections against the supplied analytics images; values are attempt, accuracy, p-value.
BF={3:{('VARC',11):(78,82.05,64),('VARC',16):(68,44.12,30),('VARC',24):(80,17.5,14),('DILR',2):(32,81.25,26),('DILR',15):(74,78.38,58),('QA',2):(82,92.68,76),('QA',3):(64,90.63,58),('QA',6):(32,31.25,10),('QA',7):(54,85.19,46),('QA',8):(18,55.56,10),('QA',11):(64,90.63,58),('QA',15):(94,93.62,88),('QA',19):(56,89.29,50)},5:{('VARC',3):(92.86,41.54,38.57),('VARC',16):(77.14,85.19,65.72),('VARC',17):(95.71,70.15,67.14),('DILR',1):(55.71,92.31,51.43),('DILR',8):(38.57,44.44,17.14),('DILR',16):(97.14,80.88,78.57),('QA',2):(30,85.71,25.71),('QA',7):(20,85.71,17.14),('QA',12):(77.14,88.89,68.57),('QA',18):(40,85.71,34.28)}}
def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 s=re.sub(r'(?:\s+(?:g|g@|@|i\)|je|ix\]|x\)|Q|Ps|\||a))+$','',s)
 s=re.sub(r'\s+[.\-]$','',s)
 for a,b in [('Asteadfast','A steadfast'),('Adevice','A device'),('Anew form','A new form'),('Aand B','A and B'),('Asolution','A solution'),('Ashopkeeper','A shopkeeper'),('In asurprise','In a surprise'),('In acircle','In a circle'),('lf ','If '),('anc analyzing','and analyzing'),('to 2 ','to a '),('remains 2 ','remains a '),('is 2 stark','is a stark'),('perspective 2 ','perspective a '),('“human*','“human”'),('“stop*','“stop”'),('just 2 small','just a small'),('become 2 winner','become a winner'),('lose 2 powerful','lose a powerful'),('seem 2 subtle','seem a subtle'),('translate 2 goal','translate a goal'),('Itis ','It is '),('Sargon |.','Sargon I.'),('COVID*','COVID'),('"| Have','"I Have'),('to g societal','to societal'),('artis a','art is a'),('tothe future','to the future'),('underscoring 2 @','underscoring a'),('overhaul of ix]','overhaul of'),('moderninternet','modern internet'),('A, DandE','A, D and E'),('Either Bor D','Either B or D'),('a coin','a coin'),('wins acoin','wins a coin'),('There Is','There is'),('best . captures','best captures'),('green.','green.'),(' Ps ',' '),('PQ and R','P, Q and R'),('600 m2','600 m?'),('2? operation','2nd operation'),('3 operation','3rd operation'),('3? operation','3rd operation'),('4" operation','4th operation'),('__{4)__','__(4)__'),('__(3)__-','__(3)__.'),('3.E has','3. E has'),('5.B has','5. B has'),('customers ina','customers in a'),('Acomprehensive','A comprehensive'),('in the . progression','in the progression'),('coins A with F','coins with F'),('coins i with','coins with'),('3 least amount','3rd least amount'),('2? least amount','2nd least amount'),('F3, B6, 16, D8','F3, B6, I6, D8'),(' /5%',' 75%')]:s=s.replace(a,b)
 return s

def sec(s):a,b=map(int,s.split(':'));return a*60+b

def build(mock):
 records=json.loads((ROOT/f'extraction/take-home-{mock}-records.json').read_text(encoding='utf8'));analytics=json.loads((ROOT/f'extraction/analysis-takehome{mock}.json').read_text(encoding='utf8'));src=ROOT/f'source-images/take-home-{mock}';ocr=ROOT/f'extraction/take-home-{mock}';rm={(r['section'],r['number']):r for r in records};qm={};results=[]
 # Optional supplied corrections are text-only answer keys; never fill missing answers by inference.
 answers=json.loads(json.dumps(ANS[mock]));extra=ROOT/f'extraction/take-home-{mock}-supplied-keys.json'
 if extra.exists():
  for key,val in json.loads(extra.read_text()).items():answers['DILR'][int(key)-1]=str(val)
 t={'schemaVersion':1,'testType':'full','id':f'ims-take-home-{mock}-2026','revision':1,'title':f'Take Home {mock} · SimCAT {100+mock} · 2026','description':'Full mock with 24 VARC, 22 DILR and 22 QA questions. Shared sets, original figures and supplied source analysis preserved.','sections':[{'code':c,'groups':[]} for c in ['VARC','DILR','QA']]}
 for r in records:
  c,n=r['section'],r['number'];key=c,n;p=r['prompt']
  if c=='VARC' and n in TITA[mock]['VARC']:
   p=re.split(r'\n(?:Sade|Sasa|9\)|a$|2$)',p)[0];p=re.sub(r'\bAl\b','AI',p)
  if mock==5 and c=='VARC' and n==19:p=p.split('\nA Option3')[0]
  p=clean(p)
  if c=='VARC' and n in TITA[mock]['VARC']:p=re.sub(r' (?=[1-5]\. )','\n\n',p)
  if c=='VARC' and n>=17:p=p.replace('essence of the passage. ','essence of the passage.\n\n',1).replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:')
  if c=='QA':p=QP[mock].get(n,p)
  area=('Reading Comprehension' if n<=16 else 'Verbal Reasoning') if c=='VARC' else ('Data Interpretation' if (n<=4 or (9<=n<=18 if mock==3 else 10<=n<=14)) else 'Logical Reasoning') if c=='DILR' else 'Quantitative Ability'
  if c=='QA':
   areas={3:{'Algebra':range(1,6),'Geometry':range(6,9),'Numbers':[9,20,21,22],'Modern Math':range(10,13),'Arithmetic':range(13,20)},5:{'Algebra':[1,2,7,20,22],'Geometry':range(3,7),'Numbers':[17,19,21],'Modern Math':[8,9,18],'Arithmetic':range(10,17)}}
   area=next(a for a,ns in areas[mock].items() if n in ns)
  q={'id':f'take-home-{mock}-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[mock][c] else 'MCQ','prompt':p,'area':area}
  answer=answers[c][n-1];q['answer']=([answer] if q['type']=='TITA' else answer) if answer is not None else None
  if q['type']=='MCQ':
   vals=QO[mock].get(n) if c=='QA' else None
   if mock==5 and c=='VARC' and n in (19,20):vals=['Option 3','Option 1','Option 2','Option 4'] if n==19 else ['Option 3','Option 4','Option 2','Option 1']
   if vals is None:vals=[clean(o['text']) for o in r['options']]
   assert len(vals)==4 and all(vals),(mock,key,vals)
   q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(vals)]
  ar=analytics[c][n-1];vals=BF[mock].get(key,[float(x) for x in ar['values'][:3]]);assert len(vals)==3 and all(0<=v<=100 for v in vals),(mock,key,vals)
  q['selectionCategory']=CATS[mock][c].split()[n-1]
  q['benchmark']={'source':'IMS supplied question-wise analysis screenshot','sourceImage':f"Screenshot 2026-10-13 {dict(zip(['VARC','DILR','QA'],['201220','201235','201251'] if mock==3 else ['200006','200022','200031']))[c]}.png",'topperTimeSeconds':sec(ar['topperTime']),'topperAttemptPercent':vals[0],'topperAccuracyPercent':vals[1],'topperPValue':vals[2]}
  time=ar['time']
  if mock==3 and key==('VARC',2):time='02:41'
  if mock==3 and key==('DILR',22):time='00:01'
  results.append({'questionId':q['id'],'outcome':ar['outcome'],'timeSeconds':sec(time)});qm[key]=q
 def embed(target,filename,key,alt,box=None):
  im=Image.open(src/filename)
  if box:im=im.crop(box)
  b=io.BytesIO();im.save(b,format='PNG');t.setdefault('assets',{})[key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()};target.setdefault('assetIds',[]).append(key)
 def left(c,n):return (ocr/Path(rm[c,n]['file']).stem/'left.txt').read_text(encoding='utf8')
 def paragraphs(p):return '\n\n'.join(clean(x) for x in p.strip().split('\n\n'))
 for n,title in zip([1,5,9,13],['Ecological resilience','Fundamentalism and modernity','Scientific falsification','Learning from failure'] if mock==3 else ['The experience economy','Hammurabi’s code','Digital bioacoustics','The brain’s stopping mechanism']):
  p=left('VARC',n);p=p.split('\n',1)[1] if mock==5 and n in (9,13) else p.split('each question.',1)[1]
  g={'id':f'take-home-{mock}-varc-group-{n}','title':title,'stimulus':paragraphs(p),'questions':[qm['VARC',i] for i in range(n,n+4)]};t['sections'][0]['groups'].append(g)
 for n in range(17,25):t['sections'][0]['groups'].append({'id':f'take-home-{mock}-varc-group-{n}','title':f'Verbal ability · Q{n}','questions':[qm['VARC',n]]})
 specs=[(1,4,'Ladoo shop'),(5,8,'Four families at a show'),(9,13,'Pentathlon selection'),(14,18,'Coin collections'),(19,22,'Modified chess queen')] if mock==3 else [(1,4,'Coloured material sheets'),(5,9,'Bikers visiting cities'),(10,14,'Number chit game'),(15,18,'Kittens at a cattery'),(19,22,'Mini Casino')]
 for a,b,title in specs:
  p=left('DILR',a)
  if 'questions that follow' in p:p=re.split(r'questions that follow[.:]',p,maxsplit=1)[1]
  g={'id':f'take-home-{mock}-dilr-group-{a}','title':title,'questions':[qm['DILR',i] for i in range(a,b+1)]}
  if mock==3 and a in (1,5,9):
   start,end={1:('Dink Ladoo Besan','Some more facts'),5:('Husband Wife','Additional information'),9:('Fencing Swimming','The following points')}[a];p=p[:p.index(start)]+p[p.index(end):]
   filename={1:'Q1 to Q4 DILR.png',5:'Q-5 to Q8 DILR .png',9:'Q9 to Q13 DILR.png'}[a];embed(g,filename,f'takehome{mock}-dilr-{a}-table','Original source table for this DILR set.')
  if mock==5 and a==1:
   p=p[p.index('Ashopkeeper'):];p=p[:p.index('\nBlack')]+p[p.index('¢ The stock'):];p=p.rstrip('%\n ');p=p.replace('1* of','1st of').replace('¢ ','• ').replace('@ ','• ')
   embed(g,'DILR Q1 to Q 4.png','takehome5-dilr-1-graphs','Original bar and pie graphs for the sheets set.')
  if mock==5 and a==10:
   p=p[:p.index('ee es')]+p[p.index('Further, It is known'):];p=p.replace('Ré:','R6:')
   embed(g,'DILR Q10 to Q14.png','takehome5-dilr-10-table','Original number-chit table.')
  if mock==3 and a==5:
   for x,y in [('2" column','2nd column'),('15* row','1st row'),('3 column','3rd column'),('4" row','4th row'),('4 row','4th row')]:p=p.replace(x,y)
  g['stimulus']=paragraphs(p);t['sections'][1]['groups'].append(g)
 for n in range(1,23):t['sections'][2]['groups'].append({'id':f'take-home-{mock}-qa-group-{n}','title':f'Quantitative ability · Q{n}','questions':[qm['QA',n]]})
 # Original geometry figures only: no SVG, drawing, OCR figure labels, or reconstructed visualization.
 for n,box in ([(7,(15,110,195,278)),(8,(10,100,185,270))] if mock==3 else [(4,(44,150,317,302))]):
  embed(qm['QA',n],rm['QA',n]['file'],f'takehome{mock}-qa-{n}-figure',f'Original source geometry figure for QA question {n}.',box)
 score,percentile,ss,maps=(13,23.15,[('VARC',11,47.3),('DILR',3,33.84),('QA',-1,9.16)],[[19,24,27,30,37,40],[10,14,16,18,24,27],[16,21,24,27,36,42],[40,51,56,62,70,71]]) if mock==3 else (47,39.43,[('VARC',40,80.11),('DILR',-1,6.93),('QA',8,31.29)],[[36,43,46,50,57,59],[18,23,25,29,36,39],[19,25,28,32,41,50],[68,81,86,93,101,103]])
 stamps=['201153','201202','201220','201235','201251','201302'] if mock==3 else ['195927','195937','200006','200022','200031','200050']
 t['sourceAnalysis']={'label':f'Original IMS attempt supplied in TakeHome {mock} screenshots','sourceImages':[f'Screenshot 2026-10-13 {s}.png' for s in stamps],'reportedScore':score,'percentile':percentile,'sectionScores':[{'section':c,'score':s,'percentile':p} for c,s,p in ss],'questionResults':results,'percentileMapper':[{'section':c,'percentile':p,'score':s} for c,vs in zip(['VARC','DILR','QA','Overall'],maps) for p,s in zip([70,85,90,95,99,99.5],vs)]}
 reported={3:[('Overall',13,29.63,'02:00',.11,'04:29'),('VARC',11,42.86,'00:40',.28,'02:51'),('Reading Comprehension',13,54.55,'00:33',.38,'03:05'),('Verbal Reasoning',-2,0,'00:05',-.34,'01:59'),('DILR',3,25,'00:40',.07,'10:07'),('Data Interpretation',3,50,'00:08',.35,'04:15'),('Logical Reasoning',0,0,'00:31',0,'15:54'),('QA',-1,11.11,'00:40',-.02,'04:30'),('Algebra',3,50,'00:09',.33,'04:32'),('Geometry',0,0,'00:04',0,'04:35'),('Numbers',-1,0,'00:07',-.14,'03:38'),('Modern Math',0,0,'00:01',0,'00:00'),('Arithmetic',-3,0,'00:18',-.16,'04:34')],5:[('Overall',47,41.86,'02:00',.39,'02:49'),('VARC',40,68.18,'00:39',1,'01:49'),('Reading Comprehension',40,87.5,'00:33',1.2,'02:05'),('Verbal Reasoning',0,16.67,'00:06',0,'01:05'),('DILR',-1,0,'00:40',-.02,'03:22'),('Data Interpretation',0,0,'00:11',0,'02:23'),('Logical Reasoning',-1,0,'00:28',-.04,'04:02'),('QA',8,33.33,'00:40',.2,'04:30'),('Algebra',6,100,'00:06',.88,'03:26'),('Geometry',0,0,'00:00',0,'00:26'),('Modern Math',0,0,'00:07',0,'07:15'),('Arithmetic',2,25,'00:22',.09,'05:39'),('Numbers',0,0,'00:02',0,'00:00')]}
 t['sourceAnalysis']['reportedAreas']=[dict(zip(['label','score','accuracy','timeLabel','marksPerMinute','timePerAttemptLabel'],v)) for v in reported[mock]]
 missing=[q['id'] for q in qm.values() if q['answer'] is None]
 output=ROOT/(f'drafts/take-home-{mock}.pending.json' if missing else f'samples/take-home-{mock}.json')
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'{output}: {len(qm)} questions; missing source answers: {missing}')
 return t
if __name__=='__main__':
 for mock in [3,5]:build(mock)
