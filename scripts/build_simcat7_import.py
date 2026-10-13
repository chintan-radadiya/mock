"""Reviewed SimCAT 7 import. VARC 7–10 await supplied questions/options/keys.

Builds an explicitly incomplete draft until extraction/simcat-7-missing.json
contains four records with number, prompt, options [{id,text}], and answer.
Source analysis is transcribed from the supplied question-wise scorecards.
"""
from pathlib import Path
from PIL import Image
import base64, io, json, re

ROOT=Path(__file__).resolve().parents[1]
OCR=ROOT/'extraction/simcat-7';SRC=ROOT/'source-images/simcat-7'
ANS={'VARC':'D C B A C 2431 ? ? ? ? C C C B A A 4231 C C A D D 3 5'.split(),
 'DILR':'C B C C B 114 C D A 5 4 D B C 6 C 6 D B A D C'.split(),
 'QA':'550 C 720 C 24000 B 1 36000 D 75264 B C A B C B B D A 30 C 1'.split()}
TITA={'VARC':{6,17,23,24},'DILR':{6,10,11,15,17},'QA':{1,3,5,7,8,10,20,22}}
CAT={'VARC':'B B B A B A B A C B A B A A A B C B A B A B A C'.split(),
 'DILR':'C C C C C B B B B B A A A B C C C C B B B B'.split(),
 'QA':'A B B C A A B A B A B B B B C B B C B B C B'.split()}
# All triples checked against the images: topper attempt%, accuracy%, p-value.
BENCH={
 'VARC':[(83,61.45,51),(81.8,47.43,38.8),(84.6,45.15,38.2),(84,77.86,65.4),(72.4,65.47,47.4),(89,75.51,67.2),(68.4,52.92,36.2),(73.2,93.72,68.6),(64.8,33.64,21.8),(65.6,84.45,55.4),(88.8,91.44,81.2),(60,55.67,33.4),(76.2,92.39,70.4),(71.8,91.64,65.8),(69.4,86.74,60.2),(70.4,68.47,48.2),(83.2,5.05,4.2),(84,54.52,45.8),(66.6,91.59,61),(62.6,69.01,43.2),(68,95.29,64.8),(60.8,75.66,46),(89,69.66,62),(81.6,29.17,23.8)],
 'DILR':[(28,82.14,23),(29.8,82.55,24.6),(25.4,81.1,20.6),(25.4,89.76,22.8),(22.8,79.82,18.2),(70.4,76.99,54.2),(64.4,92.55,59.6),(59.4,87.54,52),(57.2,80.77,46.2),(60.6,76.9,46.6),(85.2,74.18,63.2),(83.2,93.51,77.8),(79.8,93.98,75),(61.6,65.26,40.2),(33.8,45.56,15.4),(15.4,70.13,10.8),(29.6,45.95,13.6),(13.8,82.61,11.4),(65.2,85.28,55.6),(65.4,90.21,59),(62.2,91,56.6),(62,79.03,49)],
 'QA':[(77.6,78.87,61.2),(47.4,87.76,41.6),(60,82,49.2),(31.8,86.79,27.6),(96,93.54,89.8),(87.4,95.19,83.2),(64.4,66.46,42.8),(85.6,93.46,80),(49.8,87.55,43.6),(85.2,79.81,68),(43.8,97.72,42.8),(52.4,80.15,42),(34.6,86.71,30),(59.8,91.97,55),(32,88.13,28.2),(65.4,89.6,58.6),(43.2,85.65,37),(23.8,73.11,17.4),(55.6,88.85,49.4),(53.2,73.68,39.2),(23.8,74.79,17.8),(53,73.96,39.2)]}
V_OPTIONS={
 1:['The interpretation of silence in literature depends on the readers’ imagination rather than that of the writer.','The presence of silence in literature primarily indicates the breakdown or inadequacy of language as a communication system.','Non-verbal textual elements such as spacing and punctuation play a role in shaping meaning independently of spoken or written language.','Literary silence operates as an expressive strategy that can convey meanings which explicit language fails to adequately convey.'],
 2:['Silence in literature reflects the absence of speech, yet often relies on linguistic context to become noticeable and acquire meaning.','Silence in literature eliminates verbal expression, yet enhances the emotional intensity experienced by readers.','Silence in literature emerges from the limitations of language, yet exceeds it in communication of meanings.','Silence in literature disrupts conventional communication, yet depends on structural elements of writing to produce meaning.'],
 3:['Absence in literature primarily is a withholding of expression when language reaches its limits.','Absence in literature is as a literary device that generates meaning by influencing how language is interpreted.','Absence in literature is used to intensify emotional effects by reducing the density of verbal expression.','Absence in literature is the form of writing by drawing attention to non-verbal elements such as spacing and layout.'],
 19:['Small perturbations can help a system adjust or adapt if the system is already near a tipping point where it can react to changes around it.','Perturbations can be dangerous in noisy environments because the system might react strongly to random signals that actually don’t mean anything important.','Perturbations necessarily produce large-scale systemic transformations whenever a system approaches a critical point.','Small perturbations can actually keep a system stable by releasing pressure gradually, preventing bigger problems later.']}
D_OPTIONS={1:['₹110','₹120','₹130','₹140'],3:['₹140','₹150','₹160','₹170'],4:['Stock Z lost exactly ₹30 on Day 2.','Stock W triggered the Upper Circuit on Day 2.','The combined value of the four stocks on Day 3 was ₹550.','The price of Stock X on Day 4 was ₹150.'],7:['8.5','9','9.5','10']}
Q_OPTIONS={4:['78 cm²','90 cm²','84 cm²','72 cm²'],11:['30√3 m, 60 m','30√3 m, 30(√3 + 1) m','30 m, 30√3 m','45 m, 30(2 + √3) m'],12:['5/364','1/364','3/364','None of the above'],13:['1584/7','1464/7','1466/7','None of these'],15:['15√5','12√5','10√5','20√5']}
Q_PROMPTS={
 2:'Find the value of (|x| + |y|) given that ‘x’ and ‘y’ are integers, and (x + xy + y + 38) = 0.',
 3:'If n is a natural number greater than 1 such that (n − 2)! × (n − 1)! = (n − 1)! + n!, then find the value of (n + 1)!.',
 8:'A, B and C entered into a partnership. A invested ₹60,000 at the beginning of the year and increased his investment by ₹30,000 after 4 months. B invested ₹75,000 at the beginning of the year and withdrew ₹15,000 after 6 months. C joined the business after 3 months with an investment of ₹80,000. If the total profit at the end of the year was ₹1,24,500, what was C’s share of the profit (in ₹)?',
 9:'Find the sum of all real roots of the equation: (x² − 4x)(x² − 4x + 1)(x² − 4x + 2) + 6 = 0.',
 16:'Let α and β be the roots of the quadratic equation x² − (k + 3)x + (2k + 1) = 0. If α² + β² = 25, then the sum of all possible values of ‘k’ is _____.',
 19:'Given equation: |x − 3|² + 7|x − 3| − 8 = 0. The sum of all the positive roots of the given equation is _____.',
 22:'Three types of coffee, Arabica, Robusta, and Liberica cost ₹800/kg, ₹500/kg, and ₹1200/kg respectively. Blend Alpha contains them in the ratio x : y : 1 respectively and costs ₹700/kg. Blend Omega contains them in the ratio y : x : 3 respectively and costs ₹830/kg. Find the difference between x and y.'}

def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 for a,b in {' ¢ ':' ','butin':'but in','Atthe':'At the','insome':'in some','A“culture':'A “culture','may be 2 real':'may be a real','non- coding':'non-coding','half full*':'half full”','“junk DNA’':'“junk DNA”','“junk DNA?':'“junk DNA,”','culture*':'culture”','overtime.':'over time.','intheworld.':'in the world.','___-(2)__—.':'___(2)___.','_(4)__«.':'___(4)___.','Ashop':'A shop','Awildlife':'A wildlife','Achocolate':'A chocolate','Asquad':'A squad','7.Asquad':'7. A squad','1/7 candidates':'17 candidates','Operations Is':'Operations is','Agastya Is':'Agastya is','tangent Is':'tangent is','premium Ingredients':'premium ingredients'}.items():s=s.replace(a,b)
 s=re.sub(r'^lf\b','If',s)
 return re.sub(r'\s+(?:g|@|¢|<|i\)|Ps|a|\.|-)$','',s).strip()
def paras(s):return '\n\n'.join(clean(p) for p in s.split('\n\n') if p.strip())
def sec(s):a,b=map(int,s.split(':'));return 60*a+b

def build():
 records=json.loads((ROOT/'extraction/simcat-7-records.json').read_text(encoding='utf8'))
 stats=json.loads((ROOT/'extraction/analysis-simcat7.json').read_text(encoding='utf8'))
 missing_path=ROOT/'scripts/simcat7-followup.json'
 supplied=json.loads(missing_path.read_text(encoding='utf8')) if missing_path.exists() else []
 supplied={r['number']:r for r in supplied};qs={};results=[]
 t={'schemaVersion':1,'testType':'full','id':'ims-simcat-7-2026','revision':1,'title':'SimCAT 7 · 2026','description':'68-question full mock with four RC passages, five intact DILR sets, original graphs and supplied source analysis.','sections':[{'code':c,'groups':[]} for c in ANS],'assets':{}}
 rm={(r['section'],r['number']):r for r in records}
 for c in ANS:
  for n in range(1,len(ANS[c])+1):
   r=rm.get((c,n));answer=ANS[c][n-1]
   if r is None:
    r=supplied.get(n,{'prompt':None,'options':[],'answer':None});answer=r['answer']
   p=r['prompt']
   if p is not None:
    if c=='VARC' and n in V_OPTIONS:p=p.split('\nA ')[0]
    if c=='VARC' and n==23:p=p.removeprefix('a\n')
    if c=='QA':
     p=Q_PROMPTS.get(n,p).replace('APQR','ΔPQR').replace('720"','720th')
     if n==6:p=p.replace('2180','₹180').replace('2240','₹240').replace('2630','₹630')
     if n==13:p=p.split('\n(take')[0]+' (Take π = 22/7.)'
    if c=='DILR':p=p.replace('(+250)','(+₹50)').replace(' Ps','').replace('2024- a\n25','2024-25')
    p=clean(p)
    if c=='VARC' and n in TITA[c]:p=re.sub(r' (?=[1-5]\. )','\n\n',p)
    if c=='VARC':p=p.replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:').replace('essence of the passage. ','essence of the passage.\n\n')
   area=('Reading Comprehension' if n in set(range(1,5))|set(range(7,11))|set(range(13,17))|set(range(19,23)) else 'Verbal Reasoning') if c=='VARC' else ('Logical Reasoning' if n<=5 or 15<=n<=18 else 'Data Interpretation') if c=='DILR' else next(a for a,ns in {'Arithmetic':[1,5,8,10,14,18,22],'Algebra':[2,6,9,16,19],'Numbers':[3,20],'Geometry':[4,7,11,13,15],'Modern Math':[12,17,21]}.items() if n in ns)
   q={'id':f'simcat-7-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[c] else 'MCQ','prompt':p,'area':area,'topic':area,'selectionCategory':CAT[c][n-1]}
   q['answer']=[answer] if q['type']=='TITA' else answer
   if q['type']=='MCQ':
    opts=(V_OPTIONS if c=='VARC' else D_OPTIONS if c=='DILR' else Q_OPTIONS).get(n,[clean(o['text']) for o in r['options']])
    q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(opts)]
    assert len(opts)==4 or (c=='VARC' and n in range(7,11)),(c,n,opts)
   st=stats[c][n-1];att,acc,pv=BENCH[c][n-1];stamp={'VARC':'223604','DILR':'223617','QA':'223626'}[c]
   q['benchmark']={'source':'IMS supplied question-wise analysis','sourceImage':f'Screenshot 2026-10-13 {stamp}.png','topperTimeSeconds':sec(st['topperTime']),'topperAttemptPercent':att,'topperAccuracyPercent':acc,'topperPValue':pv}
   results.append({'questionId':q['id'],'outcome':st['outcome'],'timeSeconds':sec(st['time'])});qs[c,n]=q
 def read(name,part='full'):return (OCR/name/(part+'.txt')).read_text(encoding='utf8')
 def group(c,a,b,title,p=None):
  g={'id':f'simcat-7-{c.lower()}-group-{a}','title':title,'questions':[qs[c,n] for n in range(a,b+1)]}
  if p:g['stimulus']=paras(p)
  t['sections'][list(ANS).index(c)]['groups'].append(g);return g
 def left(n):return read(f'Screenshot ({n+303})','left').split('Refer to the data below and answer the questions that follow.',1)[1].strip()
 def embed(g,filename,key,alt,box=None):
  im=Image.open(SRC/filename)
  if box:im=im.crop(box)
  stream=io.BytesIO();im.save(stream,format='PNG');t['assets'][key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()};g.setdefault('assetIds',[]).append(key)
 rc={1:('Silence in literature','VARC Q1 to Q4'),7:('Complexity and economics','VARC Q7 to Q10'),13:('Genetic variation','VARCQ 13 to Q16'),19:('Critical points and perturbations','VARC Q19 to Q22')}
 for n in range(1,25):
  if n in rc:
   title,name=rc[n];group('VARC',n,n+3,title,read(name).split('\n',1)[1])
  elif not any(a<n<=a+3 for a in rc):group('VARC',n,n,f'Verbal ability · Q{n}')
 p=left(1)
 for a,b in {'250':'₹50','230':'₹30','210':'₹10','2510':'₹510','2110':'₹110','exactly 20 higher':'exactly ₹20 higher','was ona':'was on a'}.items():p=p.replace(a,b)
 group('DILR',1,5,'Stock prices',p)
 g=group('DILR',6,10,'Refinery production');embed(g,'DILR Q6 to Q 10 Set .png','s7-refineries','Original refinery set with bar chart, table and instructions.')
 p=left(11).split('% of students')[0]
 g=group('DILR',11,14,'Regions and specializations',p);embed(g,'Screenshot 2026-10-13 224800.png','s7-regions','Original region and specialization pie charts.')
 group('DILR',15,18,'Training programme squads',left(15))
 group('DILR',19,22,'Virtual creators',left(19))
 for n in range(1,23):group('QA',n,n,f'Quantitative ability · Q{n}')
 t['sourceAnalysis']={'label':'Original IMS SimCAT 7 attempt. Outcomes and timings use the supplied question-wise analysis; scorecard percentiles are source-only.','sourceImages':[f'Screenshot 2026-10-13 {s}.png' for s in ['223538','223547','223604','223617','223626']],'reportedScore':29,'percentile':46.46,'sectionScores':[{'section':c,'score':score,'percentile':pct} for c,score,pct in [('VARC',20,70.5),('DILR',3,29.39),('QA',6,29.68)]],'questionResults':results,'percentileMapper':[{'percentile':v[0],'section':c,'score':v[i+1]} for v in [(70,20,13,17,47),(85,27,20,24,64),(90,31,23,28,72),(95,36,28,33,84),(99,45,38,43,106),(99.5,49,41,47,116)] for i,c in enumerate(['VARC','DILR','QA','Overall'])],'reportedAreas':[dict(zip(['label','score','accuracy','timeLabel','marksPerMinute','timePerAttemptLabel'],v)) for v in [('Overall',29,47.83,'02:00',.24,'05:15'),('VARC',20,57.14,'00:39',.5,'02:51'),('Reading Comprehension',14,60,'00:33',.42,'03:21'),('Verbal Reasoning',6,50,'00:06',.95,'01:35'),('DILR',3,25,'00:40',.07,'10:05'),('Logical Reasoning',0,0,'00:02',0,'01:04'),('Data Interpretation',3,50,'00:38',.08,'19:00'),('QA',6,40,'00:40',.15,'08:05'),('Arithmetic',3,33.33,'00:19',.15,'06:31'),('Algebra',3,100,'00:06',.5,'06:03'),('Numbers',0,0,'00:02',0,'00:00'),('Geometry',0,0,'00:11',0,'11:20'),('Modern Math',0,0,'00:00',0,'00:00')]]}
 missing=[n for n in range(7,11) if not qs['VARC',n]['prompt'] or not qs['VARC',n]['answer'] or len(qs['VARC',n]['options'])!=4]
 if missing:t['importReview']={'ready':False,'missing':[f'VARC Q{n}: question, options and correct answer' for n in missing]}
 out=ROOT/('samples/drafts/simcat-7.json' if missing else 'samples/simcat-7.json');out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'Built {out}: {68-len(missing)} complete questions, {len(missing)} awaiting source, 68 source results.');return t

if __name__=='__main__':build()
