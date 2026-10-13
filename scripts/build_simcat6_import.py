"""Build SimCAT 6 from reviewed OCR and original image crops (Simcat 6.zip).

Requires ignored source-images/simcat-6 and extraction/simcat-6 intermediates.
Keys, options, mathematical notation and visible statistics were visually checked.
"""
from pathlib import Path
from PIL import Image
import base64
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OCR = ROOT / 'extraction/simcat-6'
SRC = ROOT / 'source-images/simcat-6'
ANS = {
 'VARC':'C A C D D 4132 C A D B B C C D A C 4312 C D B D 2143 C A'.split(),
 'DILR':'B 4 C 110 C C D C A B B B D B 30 B A 17 C 23'.split(),
 'QA':'A 24 4 D B B C D C D A C 137 66 2 A A B C 5 3456 4'.split(),
}
TITA = {'VARC':{6,17,22},'DILR':{2,4,15,18,20},'QA':{2,3,13,14,15,20,21,22}}
V_OPTIONS = {
 5:[
 'Autoimmune diseases lead to failures in the immune self-recognition system due to complex genetic and environmental factors. However, as DNA damage is the main cause of such failures, studying mutational burden and somatic mutagenesis in the context of these diseases can help clarify how they develop and progress.',
 'Autoimmune diseases, widespread and spanning multiple organs and cellular functions arise owing to complex genetic and environmental factors leading to the failure of the autoimmune system. However, study of somatic mutations - the primary cause of DNA damage- could help in understanding the basis of these diseases.',
 'Complex genetic and environmental factors lead to autoimmune diseases when the adaptive immune system fails to distinguish self from non-self-antigens affecting multiple organ systems and cellular functions. Studying DNA damage in immune cells due to mutational burden as a contributing factor can help clarify how these diseases develop and progress.',
 'Autoimmune diseases arise when the adaptive immune system, influenced by complex genetic and environmental factors, fails to distinguish self from non-self-antigens. Studying mutational burden and somatic mutagenesis as contributing factors can help clarify how these diseases develop and progress.'],
 7:['suggesting that social welfare programs can permanently replace economic growth as the foundation of development.','arguing that market-oriented reforms naturally fix the problems created by redistributive political systems.','showing that development is shaped by shifting interactions among historical, political and global forces.','asserting that external remittances are the decisive factor that ultimately determines long-term economic prosperity.'],
 8:['Political institutions supported change by adjusting their ideas to fit new economic realities while still retaining the earlier welfare policies.','Economic change happened independently of political institutions and was mainly driven primarily by remittance inflows from external labour markets.','Political flexibility appeared only after economic change had already been completed through market liberalisation.','Economic change required removing earlier welfare and redistribution policies so that market-led growth could happen.'],
 9:['By restructuring redistributive policies and focusing on fast industrial growth to increase incomes.','By depending on existing welfare achievements to naturally create growth and expansion within the local economy.','By increasing labor activism and stricter regulations to protect social benefits while limiting private business.','By using remittances from overseas to make up for weak local investment and stimulate economic change.'],
 23:['Option 4','Option 3','Option 1','Option 2'],
}
D_OPTIONS = {6:['All 7','5','4','Fewer than 4'],8:['0','1','Either 0 or 1','More than 1'],10:['0','1','2','3'],11:['6','7','8','9']}
Q_OPTIONS = {1:['8√3/3','10√3/3','8√3','10√3'],5:['12.50%','16⅔%','20.00%','33⅓%'],8:['8½','9','9½','10'],17:['13/2','15/2','5/2','Cannot be determined']}
Q_PROMPTS = {
 1:'Two distinct regular hexagons ABCDEF and BGHIDJ do not completely coincide but overlap in common region. If BD = 2 cm, determine the total area covered by the two hexagons, excluding the overlapping portion. Express your answer in cm².',
 7:'At a music festival, 75% of the attendees were students. Among the students, 80% owned a premium pass. Of the students who owned a premium pass, 66⅔% were boys. What is the minimum possible number of girl students who owned a premium pass?',
 11:'‘x’ and ‘y’ are natural numbers such that a = log₁₀x and b = log₁₀y. If log₁₀(7⅕) = 3a + 2b − 1, find the value of log₅(x + y).',
 12:'In ΔABC, DE ∥ BC, AD : BC = 2 : 3. A(ΔADF) = 8 sq. cm, the length of AB = 15 cm and the length of AD = 6 cm. Find A(ΔBDF) : A(ΔDFE).',
 13:'For n ≥ 1, a sequence is defined as aₙ₊₁ = aₙ/(1 + 3aₙ), where a₁ = 5. What is the sum of the reciprocals of the first 10 terms of the sequence?',
 15:'If 4^(x+1) + 2^(2x+1) = 96, the value of ‘x’ is _____.',
 20:'Find the sum of all the positive integer values of ‘x’ for which (x³ − 10x² + 31x − 30) is negative.',
 22:'How many pairs of positive integers (x, y) satisfy the equation y = (3x + 224)/(x − 10)?',
}
# category, outcome, own time, topper time, attempt%, accuracy%, p-value.
# A cropped timing row is missing, never an invented zero.
STATS = {
 ('VARC',13):('B','Correct','7:38','3:09',61,76.72,None),
 ('VARC',14):('C','Incorrect','1:16','0:48',63.8,29.47,18.8),
 ('VARC',15):('B','Incorrect','1:33','0:37',58.8,82.99,48.8),
 ('VARC',16):('B','Incorrect','0:23','0:40',60.6,69.31,42),
 ('DILR',11):('B','Correct','8:25','4:58',63.8,93.1,59.4),
 ('DILR',12):('B','Unanswered','0:31','1:08',61.6,88.96,54.8),
 ('DILR',13):('B','Unanswered','0:02','0:35',61.4,93.16,57.2),
 ('DILR',14):('B','Unanswered','0:07','0:35',58,93.45,54.2),
 ('DILR',15):('B',None,None,None,58.2,70.1,None),
 ('DILR',16):('C','Unanswered','0:22','4:58',33.8,80.47,27.2),
 ('DILR',17):('C','Unanswered','0:08','0:46',31.8,79.87,25.4),
 ('DILR',18):('C','Unanswered','0:00','0:34',37.2,47.31,17.6),
 ('DILR',19):('C','Unanswered','0:00','0:27',26.2,82.44,21.6),
 ('DILR',20):('C','Unanswered','0:00','0:45',35,56,19.6),
}

def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 for a,b in {'EF coli':'E. coli','F. co//bacteria':'E. coli bacteria','change Is':'change is','20" century':'20th century','anincreasingly':'an increasingly','status ina':'status in a','how, ina':'how, in a','change ina':'change in a','de- emphasise':'de-emphasise','large- scale':'large-scale','bothin':'both in','profoundly 2':'profoundly a','ideais':'idea is','toit':'to it','Acompany':'A company','Acontractor':'A contractor','Acontract':'A contract','Anempty':'An empty','In acircle':'In a circle','Ais':'A is','aset':'a set','7/5 kg':'75 kg','are / cm':'are 7 cm','72,500':'₹2,500','24,000':'₹4,000','71,20,000':'₹1,20,000','24,500':'₹4,500','D(O, 7)':'D(0, 7)','2™ April':'2nd April','2ⁿᵈ April':'2nd April','Al':'AI','“the self*':'“the self”','“self*':'“self”','Asense':'A sense'}.items():
  if a=='Al':s=re.sub(r'\bAl\b','AI',s)
  else:s=s.replace(a,b)
 s=re.sub(r'^lf\b','If',s)
 s=re.sub(r'\s+(?:[@g¢]|x\)|\.)$','',s)
 return s.strip()

def paragraphs(s):return '\n\n'.join(clean(p) for p in s.split('\n\n') if p.strip())
def seconds(s):m,n=map(int,s.split(':'));return m*60+n

def build():
 records=json.loads((ROOT/'extraction/simcat-6-records.json').read_text(encoding='utf8'))
 rm={(r['section'],r['number']):r for r in records};qs={};results=[]
 t={'schemaVersion':1,'testType':'full','id':'ims-simcat-6-2026','revision':1,'title':'SimCAT 6 · 2026','description':'66 questions: 24 VARC, 20 DILR and 22 QA. Four intact RC passages, four DILR sets and the original QA figure. Source analysis is partial; new attempts receive complete analysis.','sections':[{'code':c,'groups':[]} for c in ANS],'assets':{}}
 for r in records:
  c,n=r['section'],r['number'];p=r['prompt']
  if c=='VARC' and n in V_OPTIONS:
   p=p.split('\nA ')[0]
   if n==5:p=p.split('\nAutoimmune diseases lead')[0]
  if c=='DILR':p=re.sub(r' [*Ai7]\n','\n',p);p=re.sub(r'\s+[-.]$','',p)
  if c=='QA':
   p=Q_PROMPTS.get(n,p)
   if n==3:p=p.replace('Accompany','A company')
   if n==2:p=p.replace('|b - a]','|b - a|')
   if n==8:p=p.replace('completed days','completed _____ days')
   if n==16:p=p.replace('$1','S1').replace('$2','S2').replace('$3','S3')
   if n==19:p=p.replace('lf a customer','If a customer')
  p=clean(p)
  if c=='DILR':p=re.sub(r'\? [i7]$','?',p)
  if c=='VARC':p=p.replace('energy,’ in','energy,” in').replace('“you” Under','“you”. Under').replace(',”which',',” which').replace('“de-extinction,’','“de-extinction,”')
  if c=='VARC' and n in TITA[c]:p=re.sub(r' (?=[1-4]\. )','\n\n',p)
  if c=='VARC':p=p.replace(' Sentence:','\n\nSentence:').replace(' Paragraph:','\n\nParagraph:').replace('essence of the passage. ','essence of the passage.\n\n')
  area=('Reading Comprehension' if n in set(range(1,5))|set(range(7,11))|set(range(13,17))|set(range(18,22)) else 'Verbal Reasoning') if c=='VARC' else 'Logical Reasoning' if c=='DILR' else next(a for a,ns in {'Geometry':[1,9,12,17],'Numbers':[2,21,22],'Arithmetic':[3,4,5,7,8,14,18,19],'Algebra':[6,11,15,20],'Modern Math':[10,13,16]}.items() if n in ns)
  q={'id':f'simcat-6-{c.lower()}-q{n:02}','sourceNumber':n,'type':'TITA' if n in TITA[c] else 'MCQ','prompt':p,'area':area,'topic':area}
  q['answer']=[ANS[c][n-1]] if q['type']=='TITA' else ANS[c][n-1]
  if q['type']=='MCQ':
   opts=(V_OPTIONS if c=='VARC' else D_OPTIONS if c=='DILR' else Q_OPTIONS).get(n,[clean(o['text']) for o in r['options']])
   if c=='VARC' and n==2:opts[1]=opts[1].replace(' ‘ seen',' seen')
   if c=='DILR' and n==13:opts[3]='Hisar Heroes'
   if c=='DILR' and n==19:opts[2]=opts[2].replace("Deepa'’s","Deepa’s")
   if c=='QA' and n==10:opts[1]='24,000'
   assert len(opts)==4 and all(opts),(c,n,opts)
   q['options']=[{'id':chr(65+i),'text':v} for i,v in enumerate(opts)]
  if (c,n) in STATS:
   cat,outcome,own,top,att,acc,pv=STATS[c,n];q['selectionCategory']=cat
   q['benchmark']={'source':'IMS supplied question statistics (visible fields only)','sourceImage':r['file'],'topperAttemptPercent':att,'topperAccuracyPercent':acc}
   if top is not None:q['benchmark']['topperTimeSeconds']=seconds(top)
   if pv is not None:q['benchmark']['topperPValue']=pv
   if own is not None:results.append({'questionId':q['id'],'outcome':outcome,'timeSeconds':seconds(own)})
  elif c=='DILR' and n in {3,5,8,9}:q['selectionCategory']={3:'B',5:'C',8:'A',9:'A'}[n]
  qs[c,n]=q
 def group(c,a,b,title,p=None):
  g={'id':f'simcat-6-{c.lower()}-group-{a}','title':title,'questions':[qs[c,n] for n in range(a,b+1)]}
  if p:g['stimulus']=paragraphs(p)
  t['sections'][list(ANS).index(c)]['groups'].append(g)
 def read(name,part):return (OCR/name/(part+'.txt')).read_text(encoding='utf8')
 def passage(name):return read(name,'full').split('\n',1)[1].strip()
 group('VARC',1,4,'Aeonophiles: life, time and energy',passage('Q1 to Q4 VARC'))
 for n in [5,6]:group('VARC',n,n,f'Verbal ability · Q{n}')
 group('VARC',7,10,'Kerala and development',passage('VARC Q7 to Q 10'))
 for n in [11,12]:group('VARC',n,n,f'Verbal ability · Q{n}')
 group('VARC',13,16,'Alienation and identity',read('Screenshot 2026-10-13 221552','left').split('\n',1)[1])
 group('VARC',17,17,'Verbal ability · Q17')
 group('VARC',18,21,'Chance and scientific laws',passage('VARC Q18 to Q21'))
 for n in [22,23,24]:group('VARC',n,n,f'Verbal ability · Q{n}')
 for a,name in [(1,'NCAT scores'),(6,'Scholars and presentations'),(11,'Kabaddi player auction'),(16,'Gold coin transfers')]:
  p=read(Path(rm['DILR',a]['file']).stem,'left').split('Refer to the data below and answer the questions that follow.',1)[1].strip()
  if a==11:
   for old,new in {'280 Lakhs':'₹80 Lakhs','less than 80 Lakhs':'less than ₹80 Lakhs','25 Lakhs':'₹5 Lakhs','210 Lakhs':'₹10 Lakhs','215 Lakhs':'₹15 Lakhs','£80 Lakhs':'₹80 Lakhs','total 80 Lakhs':'total ₹80 Lakhs','#₹5 Lakhs':'₹25 Lakhs'}.items():p=p.replace(old,new)
  p=re.sub(r'\n(?=[1-9]\. )','\n\n',p)
  group('DILR',a,a+4,name,p)
 for n in range(1,23):group('QA',n,n,f'Quantitative ability · Q{n}')
 im=Image.open(SRC/rm['QA',12]['file']).crop((14,34,331,267));buf=io.BytesIO();im.save(buf,format='PNG')
 t['assets']['s6-qa12-figure']={'alt':'Original triangle diagram for QA question 12.','data':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()}
 qs['QA',12]['assetIds']=['s6-qa12-figure']
 t['sourceAnalysis']={'label':'Partial original IMS attempt: only the 13 questions with visible outcomes and timing rows are included. Other source timings, totals and percentiles were not supplied.','sourceImages':list(dict.fromkeys(rm[c,n]['file'] for c,n in STATS)),'questionResults':results}
 out=ROOT/'samples/simcat-6.json';out.write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'Built {out.name}: 66 questions, 1 original figure, {len(results)} timed source results.')
 return t

if __name__=='__main__':build()
