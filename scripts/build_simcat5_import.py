"""Build SimCAT 5 from reviewed local screenshots and OCR intermediates.

Follow-up screenshots 220536 and 220626 confirm VARC Q20 = D and Q24
option D = Option 1. Default builds include these reviewed corrections.
"""
from pathlib import Path
from PIL import Image
import argparse
import base64
import io
import json
import re

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source-images/simcat-5'
OCR=ROOT/'extraction/simcat-5'
ANS={
 'VARC':'A C D D C D C B D A 2431 B D C C A B A A ? 5 2 4231 A'.split(),
 'DILR':'C A 4 C 0 B 10 B A B A B 4 B A 12 3 2 D C D A'.split(),
 'QA':'96 C B C 8 B 33 582 8 B D D C B C D C B A 12 D 0'.split(),
}
TITA={'VARC':{11,21,22,23},'DILR':{3,5,7,13,16,17,18},'QA':{1,5,7,8,9,20,22}}
CAT={
 'VARC':'A A A A C B B B B B C B B B C B B B A B C C C B'.split(),
 'DILR':'B C C C C B B B B B B C C B B B B B B B C B'.split(),
 'QA':'B A A B B B B C B C A C A A B B A B B B C B'.split(),
}
CORRECT={'VARC':{1,2,3,5,17,18,19,21,22,23,24},'DILR':{19,20},'QA':set()}
INCORRECT={'VARC':{4,7,20},'DILR':{12},'QA':{1,5,9}}
# Clipped option borders defeat automatic extraction; these are read from pixels.
V_OPTIONS={
 6:['In modernity, digital media represents a form of “environmentality,” where power works not through direct control but through data-driven systems that subtly shape behavior.','“Environmentality” is a modern expression of “governmentality,” indirectly influencing people through widespread data systems embedded in digital media.','In modernity, “governmentality” and “environmentality” operate as modes of control that regulate people and their interaction with the environment through data-driven systems.','Digital media enact “environmentality,” a modern form of power that governs people indirectly by managing their environmental relations through data-driven systems.'],
 9:['Ricoeur overlooks the fact that Proust mainly uses figurative language to enrich his storytelling.','Ricoeur fails to recognize that Proust’s novel actually follows a clear and orderly timeline.','Ricoeur underestimates the influence of early twentieth-century industrial and technological change on Proust’s writing.','Ricoeur misses how Proust’s novel shows a deeply personal experience of time that cannot be reduced to narrative structure.'],
 10:['“Grief is a season that returns each year, no matter how carefully one shuts the door.”','“The sunset spilled gold across the river, painting the sky in extravagant colour.”','“The story begins in winter and ends in spring, marking the passage of several months.”','“Her memories were described in rich and beautiful language to heighten the emotional tone.”'],
 13:['Works as a general guide for making decisions, not as a strict rule that tells policymakers what to do.','Clearly puts environmental and human health concerns ahead of economic considerations.','Applies equally to different technologies or policy choices when there is uncertainty.','Mandates adoption of restrictive measures even when proof of risks may be missing.'],
 14:['It replaces scientific uncertainty with legally binding rules and dictates regulatory outcomes.','It derives its authority mainly from ethical philosophy rather than from environmental or legal practice.','It incorporates value judgments about risks and priorities without justification or proof.','It reflects political preferences that conflict with the standards used in conventional risk assessment.'],
 15:['When scientific methods are used correctly, they can completely remove personal values and bias from decisions.','Moral principles are considered reasonable only when they match current economic priorities.','Even methods that are seen as objective in policy making still involve value judgments and choices about how problems are framed.','Using precaution works better than cost-benefit analysis in preventing harm from new technologies.'],
 19:['A process shaped by compromise between law, medicine, and social beliefs.','Defeat of psychiatry over moral and legal ideas about personal responsibility.','A clear definition of mental illness through better medical knowledge.','Firm legal rules that protect criminal law from social and political influence.'],
}
D_OPTIONS={1:['1','2','3','4'],2:['0','1','2','3'],4:['0','1','2','More than 2'],6:['19.5','20','21','21.5'],8:['16.5','17','17.2','17.5'],10:['84%','88%','92%','96%'],15:['1 - 0','2 - 0','3 - 0','2 - 1'],19:['231','232','234','Multiple answers possible'],20:['231','232','235','Multiple answers possible'],21:['1','2','3','Multiple answers possible'],22:['1','2','3','Multiple answers possible']}
Q_OPTIONS={4:['4.4','4.6','4.8','5'],10:['√5 + 1','√5 + 2','2√5','√5 + 3'],12:['(250 + 250√6) cm³','(250 + 550√6) cm³','(125 + 250√6) cm³','(125 + 750√6) cm³'],17:['₹72,480','₹75,600','₹78,120','₹81,900'],21:['0 < x < 1/5','1/5 < x < 1/2','1/2 < x < 3/5','x > 3/5']}
Q_PROMPTS={
 6:'Find the minimum value of logₙ(m²) + logₘ(n²) + logₙ²(m³) + logₘ²(n³), for m, n > 1. (The bases of the last two logarithms are n² and m² respectively.)',
 8:'Find the sum of all two-digit natural numbers a for which (a + 3)! / a! has two trailing zeroes.',
 9:'Let N be the smallest four-digit number such that N/5 is a perfect square and N/8 is a perfect cube. What is the sum of the digits of N?',
 10:'For real values of x, the maximum value that |x² − 6x + 8| / (x² − 10x + 26) can take is _____.',
 12:'The sum of the lengths of one space diagonal and one face diagonal of a cube is 5√(5 + 2√6) cm. If V denotes the volume of the cube and S denotes its total surface area, then find the value of V + S^(3/2).',
 13:'For a specific type of work, Tamannah is 11⅑% more efficient than Pallavi, and Anupriya is 11⅑% more efficient than Tamannah. Tamannah alone takes 900 hours to complete the entire work. Pallavi starts the work and works alone for the first 300 hours. After this, Tamannah works alone for another 300 hours. The remaining work was completed by Anupriya. How many hours does Anupriya take to complete the remaining work?',
 15:'Find the sum of the infinite series shown.',
 17:'A and B started a business with investments of ₹1,20,000 and ₹1,80,000 respectively. After 4 months, A increased his investment by ₹60,000. After 6 months from the start, B withdrew ₹60,000. C joined the business 5 months after it was started, with an investment of ₹2,40,000. At the end of one year, the total profit earned was ₹2,79,000. If 10% of the profit was kept aside as reserve and the remaining profit was distributed among A, B and C, what was C’s share of the profit?',
 19:'Let x and y be two positive real numbers such that x² + y² = 12 and x³ + y³ = 40. The value of xy is _____.',
 21:'Given: x = 1/11 + 1/13 + 1/15 + … + 1/49. Which of the following is definitely true?',
}

def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 for a,b in {'World War ||':'World War II','is 2 particular':'is a particular','Inthe':'In the','Inaseries':'In a series','Ina manufacturing':'In a manufacturing','interest ona':'interest on a','recorded ona':'recorded on a','rooted ina':'rooted in a','/n Search':'In Search','Tria/ by':'Trial by','15t January':'1st January','4st January':'1st January','1°* January':'1st January','On ist January':'On 1st January','On1"* January':'On 1st January','Theratio':'The ratio','Thetotal':'The total','Thenumber':'The number','Is 2 : 9':'is 2 : 9','loss awarded O':'loss awarded 0','conceding O':'conceding 0','dilutes Its':'dilutes its','times Its':'times its'}.items(): s=s.replace(a,b)
 s=re.sub(r'^lf\b','If',s)
 return re.sub(r'\s+(?:[|g@¢<{]|i\)|x\]|xX\) ie|Ps|7)+$','',s).strip()

def paragraphs(s):return '\n\n'.join(clean(p) for p in s.split('\n\n') if p.strip())
def sec(t): a,b=map(int,t.split(':'));return a*60+b

def build(varc20='D',varc24d='Option 1'):
 records=json.loads((ROOT/'extraction/simcat-5-records.json').read_text(encoding='utf8'))
 stats=json.loads((ROOT/'extraction/analysis-simcat5.json').read_text(encoding='utf8'))
 rm={(r['section'],r['number']):r for r in records};qs={};results=[]
 test={'schemaVersion':1,'testType':'full','id':'ims-simcat-5-2026','revision':1,'title':'SimCAT 5 · 2026','description':'68 questions, four intact RC passages, five intact DILR sets and supplied original-attempt analysis.','sections':[{'code':c,'groups':[]} for c in ANS],'assets':{}}
 fixes={4:[41.2,93.2,38.4],6:[60.6,88.45,53.6],9:[58.2,73.88,43],11:[91.4,96.28,88],13:[65.2,93.87,61.2],15:[36.4,93.41,34],16:[44.4,92.34,41],18:[58.2,94.85,55.2],19:[60.4,86.75,52.4],20:[59,60.68,35.8]}
 for r in records:
  c,n=r['section'],r['number'];p=r['prompt']
  if (c=='VARC' and n in [9,10,13,14,15,19,24]) or (c=='DILR' and n==2):p=p.split('\nA ')[0].rstrip('\n< ')
  if c=='VARC' and n==11:p='Arrange the four sentences below into a coherent paragraph. Enter the sequence of the four numbers as your answer.\n'+p.split('\n',1)[1]
  if c=='QA':p=Q_PROMPTS.get(n,p)
  if c=='DILR':p=p.replace(' Ps','').replace('that 7\norder','that\norder').replace('should i\n','should\n')
  p=clean(p)
  if c=='VARC' and n in TITA[c]:p=re.sub(r' (?=[1-5]\. )','\n\n',p)
  if c=='VARC':p=p.replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:')
  area=('Reading Comprehension' if n in set(range(1,5))|set(range(7,11))|set(range(13,21)) else 'Verbal Reasoning') if c=='VARC' else ('Data Interpretation' if n<=10 else 'Logical Reasoning') if c=='DILR' else next(a for a,ns in {'Modern Math':[1,2,6,15,21,22],'Arithmetic':[3,4,13,14,16,17,18,20],'Numbers':[5,8,9],'Geometry':[7,12],'Algebra':[10,11,19]}.items() if n in ns)
  q={'id':f'simcat-5-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[c] else 'MCQ','prompt':p,'area':area,'topic':area,'selectionCategory':CAT[c][n-1]}
  answer=varc20 if c=='VARC' and n==20 else ANS[c][n-1]
  q['answer']=[answer] if q['type']=='TITA' else answer
  if q['type']=='MCQ':
   opts=(Q_OPTIONS if c=='QA' else D_OPTIONS if c=='DILR' else V_OPTIONS).get(n,[clean(o['text']) for o in r['options']])
   if c=='VARC' and n==24:opts=['Option 4','Option 2','Option 3',varc24d]
   if c=='DILR' and n==12:opts[3]='More than one of the above'
   assert len(opts)==4,(c,n,opts)
   q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(opts)]
  st=stats[c][n-1];vals=fixes[n] if c=='QA' and n in fixes else list(map(float,st['values'][:3]))
  assert len(vals)==3 and all(0<=v<=100 for v in vals),(c,n,vals)
  stamp=('214236' if n<=10 else '214244') if c=='VARC' else ('214302' if n<=15 else '214310') if c=='DILR' else '214326'
  q['benchmark']={'source':'IMS supplied question-wise analysis','sourceImage':f'Screenshot 2026-10-13 {stamp}.png','topperTimeSeconds':sec(st['topperTime']),'topperAttemptPercent':vals[0],'topperAccuracyPercent':vals[1],'topperPValue':vals[2]}
  outcome='Correct' if n in CORRECT[c] else 'Incorrect' if n in INCORRECT[c] else 'Unanswered'
  results.append({'questionId':q['id'],'outcome':outcome,'timeSeconds':sec(st['time'])});qs[c,n]=q
 def group(c,a,b,title,p=None):
  g={'id':f'simcat-5-{c.lower()}-group-{a}','title':title,'questions':[qs[c,n] for n in range(a,b+1)]}
  if p:g['stimulus']=paragraphs(p)
  test['sections'][list(ANS).index(c)]['groups'].append(g);return g
 def left(c,n):
  p=(OCR/Path(rm[c,n]['file']).stem/'left.txt').read_text(encoding='utf8')
  if 'Refer to the data below' in p:return p.split('Refer to the data below and answer the questions that follow.',1)[1].strip()
  return p.split('\n',1)[1].strip()
 def full(name):return (OCR/name/'full.txt').read_text(encoding='utf8').split('\n',1)[1].strip()
 def embed(target,filename,key,alt,box=None):
  im=Image.open(SRC/filename)
  if box:im=im.crop(box)
  data=io.BytesIO();im.save(data,format='PNG');test['assets'][key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(data.getvalue()).decode()};target.setdefault('assetIds',[]).append(key)
 group('VARC',1,4,'Technology and evolution',left('VARC',1))
 for n in [5,6]:group('VARC',n,n,f'Verbal ability · Q{n}')
 group('VARC',7,10,'Time and narrative',full('VARC Q7 to 10'))
 for n in [11,12]:group('VARC',n,n,f'Verbal ability · Q{n}')
 group('VARC',13,16,'The precautionary principle',full('VARC Q13 to Q16'))
 group('VARC',17,20,'Legal insanity in Victorian Britain',full('VARC Q 17 to Q20'))
 for n in range(21,25):group('VARC',n,n,f'Verbal ability · Q{n}')
 group('DILR',1,5,'Sharma family ages',left('DILR',1))
 p=left('DILR',6);p=p.split('Average bonus received by male')[0]+'\n\nAdditional Information:\n'+p.split('Additional Information :')[1]
 p=p.replace('e The','• The')
 g=group('DILR',6,10,'Employee bonuses',p)
 embed(g,'DILR Q6 to Q10.png','s5-dilr-bonus','Original department bonus table.')
 group('DILR',11,14,'Mislabelled research kits',left('DILR',11))
 group('DILR',15,18,'Galactic Nexus Cup',left('DILR',15))
 group('DILR',19,22,'Jumbled telephone extensions',left('DILR',19))
 for n in range(1,23):group('QA',n,n,f'Quantitative ability · Q{n}')
 embed(qs['QA',15],rm['QA',15]['file'],'s5-qa-series','Original infinite-series expression.',(5,105,715,160))
 test['sourceAnalysis']={'label':'Original IMS attempt supplied with SimCAT 5. Outcomes and timings use the question-wise analysis screenshots.','sourceImages':[f'Screenshot 2026-10-13 {s}.png' for s in ['214222','214236','214244','214302','214310','214326','214411']],'reportedScore':35,'questionResults':results,'reportedAreas':[dict(zip(['label','score','accuracy','timeLabel','marksPerMinute','timePerAttemptLabel'],v)) for v in [('Overall',35,65,'02:00',.29,'06:02'),('VARC',30,78.57,'00:39',.75,'02:51'),('Reading Comprehension',15,66.67,'00:30',.5,'03:21'),('Verbal Reasoning',15,100,'00:09',1.57,'01:55'),('DILR',5,66.67,'00:40',.12,'13:26'),('Data Interpretation',0,0,'00:05',0,'00:00'),('Logical Reasoning',5,66.67,'00:34',.15,'11:25'),('QA',0,0,'00:40',0,'13:29'),('Modern Math',0,0,'00:07',0,'07:22'),('Arithmetic',0,0,'00:23',0,'00:00'),('Numbers',0,0,'00:06',0,'03:09'),('Geometry',0,0,'00:00',0,'00:00'),('Algebra',0,0,'00:03',0,'00:00')]]}
 complete=bool(varc20 and varc24d)
 if not complete:test['importReview']={'ready':False,'missing':['VARC Q20 correct option','VARC Q24 option D text']}
 path=ROOT/('samples/simcat-5.json' if complete else 'samples/drafts/simcat-5.json')
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(test,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'Built {path.name}: 68 questions, {len(test["assets"])} assets, 68 source results; ready={complete}.')
 return test

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--varc20',choices=list('ABCD'),default='D');parser.add_argument('--varc24-d',default='Option 1');args=parser.parse_args();build(args.varc20,args.varc24_d)
