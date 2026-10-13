"""Build the reviewed SimCAT 104 import from local OCR intermediates and source crops.

Input: TakeHome 4 DONE.zip, extracted to source-images/take-home-4, plus
extraction/take-home-4-records.json and extraction/take-home-4/*/left.txt.
Answer keys, mathematical notation and benchmarks below were visually reviewed.
"""
from pathlib import Path
from PIL import Image
import base64
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'source-images/take-home-4'
OCR = ROOT / 'extraction/take-home-4'
ANS = {
    'VARC': 'D C A C A A D D C B A C A B C D 3 5 C B 2431 4321 C A'.split(),
    'DILR': '18144 362880 2177280 27216 544320 A D A A D A D B D 6 A C 2 D B A C'.split(),
    'QA': 'B B D 138 D B A C B C 1440 A D A B 8 C 18430 A C D D'.split(),
}
TITA = {'VARC': {17, 18, 21, 22}, 'DILR': {1, 2, 3, 4, 5, 15, 18}, 'QA': {4, 11, 16, 18}}
QA_PROMPTS = {
    1: 'If (√2)²¹ × 125ʸ = 25¹⁴ × 10ˣ × ⁵√128 and x and y are real numbers, find x : y.',
    9: 'What can be the minimum value of {(a + b)² + (a + c)² + (a + d)²} if a, b, c, d are integers and a + b + c + d = 15?',
    12: 'A circle of radius 1 is inscribed in a regular hexagon ABCDEF such that it touches all the six sides. Another circle of the largest possible radius r is drawn in the space between the circle and the hexagon as shown. Find r.',
    13: 'A cuboid with maximum possible volume is enclosed in a cylinder of height 7 cm. The volume of the cylinder outside the cuboid is 128 cubic cm. Calculate the total surface area of the cuboid. (Use π = 22/7.)',
    14: 'In the diagram given below, PQRS is a square. Area denoted by region B is also a square. Area of PQRS : Area of square B = 9 : 1. Further, ℓ(PL) = ℓ(PU) = ℓ(MN). Find the ratio of the area of region A to the area of region B.',
    16: 'Find the value of the expression shown.',
    20: 'The number of rational terms in the expansion of (⁴√5 + ⁷√2)¹⁰⁰ is:',
    21: 'Let p, q, r, and s be positive integers such that both p and q exceed 1. If pʳ × qˢ = 108²⁰, then the difference between the largest and smallest possible values of r − s is:',
}
QA_OPTIONS = {
    1: ['3 : 5', '39 : 53', '13 : 19', '9 : 37'],
    7: ['34', '33', '37', '46'], 8: ['3', '4', '5', '6'],
    12: ['7 − 4√3', '3 − 2√3', '2 − √3', '2/√3 − 1'],
    13: ['16(2 + 3√2) sq. cm', '32(2 + 7√2) sq. cm', '16(2 + 9√2) sq. cm', '16(4 + 7√2) sq. cm'],
    15: ['1 : 4', '1 : 8', '1 : 9', '1 : 16'],
    17: ['100', '1/100', '10', '1/10'], 19: ['8', '4(√2 − 1)', '4(√2 + 1)', '4'],
}
DILR_OPTIONS = {
    6: ['2', '3', '4', '8'], 7: ['8', '6', '4', '2'], 8: ['2', '3', '1', '6'],
    9: ['0', '1', '2', '6'], 10: ['2', '4', '6', '8'],
    11: ['NIM Delhi', 'NIM Kolkata', 'NIM Lucknow', 'Cannot be determined'],
    12: ['400', '350', '300', '250'],
    13: ['225 < n < 250', '250 < n < 275', '275 < n < 300', 'n > 300'],
    14: ['Only two', 'Only three', 'Four', 'All five'], 16: ['1910', '1906', '1918', '1922'],
    17: ['2013', '2010', '2006', '1999'], 19: ['L', 'M', 'N', 'None of these'],
    20: ['135', '137', '139', 'Cannot be determined'], 21: ['A', 'L', 'M', 'N'], 22: ['I', 'L', 'M', 'N'],
}
# category, own outcome, own time, topper time, attempt %, accuracy %, p-value.
# Only fully visible timing rows become source questionResults. No invented zeros.
V_STATS = [
    ('A','Correct','8:18','5:10',98.57,95.65,94.29),
    ('A','Correct','1:33','1:13',97.14,95.59,92.86),
    ('A','Correct','1:04','1:22',97.14,86.76,84.29),
    ('B','Correct','1:22','1:19',97.14,55.88,54.29),
    ('B','Unanswered','0:17','3:47',77.14,48.15,37.14),
    ('B','Unanswered','0:02','1:21',64.29,64.44,41.43),
    ('A','Unanswered','0:00','1:03',75.71,90.57,68.57),
    ('B','Unanswered','0:02','1:07',71.43,82,58.57),
    ('A','Correct','4:48','3:37',92.86,81.54,75.71),
    ('A','Correct','1:02','1:12',88.57,85.48,75.71),
    ('B','Incorrect','1:44','1:03',91.43,62.5,57.14),
    ('A','Correct','1:34','0:53',84.29,81.36,68.57),
    ('C','Incorrect','7:11','3:18',65.71,43.48,28.57),
    ('B','Unanswered','1:25','0:53',58.57,90.24,52.86),
    ('B','Incorrect','0:59','0:43',61.43,86.05,52.86),
    ('C','Unanswered','0:40','1:00',45.71,62.5,28.57),
]
D_STATS = {
    6: ('B','Unanswered','3:41','3:36',44.29,80.65,35.71),
    7: ('B','Unanswered','0:33','1:11',42.86,73.33,31.43),
    8: ('B','Unanswered','0:06','0:40',38.57,85.19,32.86),
    9: ('C','Unanswered','0:03','0:34',37.14,65.38,24.29),
    10: ('C','Unanswered','0:06','0:47',37.14,76.92,28.57),
    11: ('B','Unanswered','2:37','4:21',41.43,72.41,30),
    12: ('C','Unanswered','0:17','0:49',40,71.43,28.57),
    14: ('B','Unanswered','0:12','0:45',40,92.86,37.14),
    16: ('B','Unanswered','3:29','1:22',54.29,84.21,45.71),
    17: ('B','Unanswered','0:54','1:20',52.86,83.78,44.29),
}


def clean(text):
    text = re.sub(r'\s+', ' ', text).strip()
    for old, new in {
        'Ashopkeeper':'A shopkeeper', 'Adrum':'A drum', 'Acircle':'A circle',
        'Adirect':'A direct', 'Itis':'It is', 'ofsome':'of some',
        'aestheticexperience':'aesthetic experience', 'lies ina':'lies in a',
        '2 broad spectrum':'a broad spectrum', '2 physical object':'a physical object',
        '2 desire':'a desire', '2 theoretical':'a theoretical', '2 negative':'a negative',
        '2 small amount':'a small amount', 'BMI!':'BMI', 'BMls':'BMIs',
        '18 century':'18th century', 'Bjdnes':'Bjanes', 'Orrespectively':'0 respectively',
        'lf ':'If ', 'Al manipulation':'AI manipulation', 'Al-generated':'AI-generated',
        "Al's":"AI's", 'allfive':'all five', 'tostate-runsocieties':'to state-run societies',
    }.items(): text = text.replace(old, new)
    return text


def paragraphs(text):
    return '\n\n'.join(clean(p) for p in text.strip().split('\n\n') if p.strip())


def seconds(label):
    m, s = map(int, label.split(':'))
    return m * 60 + s


def build():
    records = json.loads((ROOT/'extraction/take-home-4-records.json').read_text(encoding='utf8'))
    rm = {(r['section'],r['number']):r for r in records}
    test = {'schemaVersion':1,'testType':'full','id':'ims-take-home-4-2026','revision':1,
            'title':'Take Home 4 · SimCAT 104 · 2026',
            'description':'68 questions with original figures, four RC passages and five intact DILR sets. Supplied source analysis is partial; new attempts receive complete analysis.',
            'sections':[{'code':c,'groups':[]} for c in ANS], 'assets':{}}
    questions, results = {}, []
    for r in records:
        c, n = r['section'], r['number']
        p = r['prompt'].split('\nSade')[0]
        p = re.sub(r'\s+[.a-]$', '', p) if c == 'DILR' else p
        if c == 'DILR': p = p.replace(' O ', ' 0 ')
        if c == 'QA':
            p = QA_PROMPTS.get(n, p)
            if n == 18: p = p[p.index('A positive'):]
        if c == 'VARC' and n == 20:
            p = p.split('\nIn the debate')[0].replace('17**', '17th')
        p = clean(p)
        if c == 'VARC' and n in TITA[c]: p = re.sub(r' (?=[1-5]\. )', '\n\n', p)
        if c == 'VARC' and n >= 19:
            p = p.replace('essence of the passage. ', 'essence of the passage.\n\n', 1)
            p = p.replace(' Sentence:', '\n\nSentence:').replace(' Paragraph:', '\n\nParagraph:')
        if c == 'VARC' and n == 23:
            p = p[:p.index('Paragraph:')] + 'Paragraph: __(1)__. In the global economy, the ability to innovate and adapt to diverse market needs is crucial for sustained economic growth. __(2)__. However, protectionist attitudes, which focus narrowly on local interests and resist external influences, can severely limit a community\'s or a country\'s economic potential. These attitudes prevent the flow of new ideas and investments, which are essential for innovation and expansion. __(3)__. Moreover, parochialism hinders collaboration and partnership opportunities with other regions or countries, leading to a cycle of economic stagnation and insularity. __(4)__. Overcoming these limiting attitudes can open up new paths for economic development, fostering a more inclusive and dynamic market environment.'
        if c == 'VARC' and n == 24:
            p = p[:p.index('Paragraph:')] + 'Paragraph: Anarchism challenges traditional forms of authority and governance, emphasizing the value of individual liberty and freedom from domination. __(1)__. Advocates argue that true freedom can only be achieved in a society where power is decentralized and individuals collectively manage their own lives without coercive forces. __(2)__. Over the years, these ideals have not only shaped theoretical discussions but also inspired real-world applications in the form of utopian communities and radical political movements. __(3)__. These communities and movements strive to demonstrate that self-management and egalitarian relationships are not only possible but also viable alternatives to state-run societies. __(4)__.'
        area = ('Reading Comprehension' if n<=16 else 'Verbal Reasoning') if c=='VARC' else ('Data Interpretation' if 11<=n<=14 else 'Logical Reasoning') if c=='DILR' else next(a for a,ns in {'Arithmetic':[2,3,4,5,6,7,8,22],'Algebra':[1,9,10,16,17,19],'Modern Math':[11,20],'Geometry':[12,13,14,15],'Numbers':[18,21]}.items() if n in ns)
        q = {'id':f'take-home-4-{c.lower()}-q{n:02}', 'sourceNumber':n, 'type':'TITA' if n in TITA[c] else 'MCQ', 'prompt':p, 'area':area, 'topic':area}
        q['answer'] = [ANS[c][n-1]] if q['type']=='TITA' else ANS[c][n-1]
        if q['type']=='MCQ':
            opts = (QA_OPTIONS if c=='QA' else DILR_OPTIONS if c=='DILR' else {}).get(n, [clean(o['text']) for o in r['options']])
            if c=='VARC' and n==20:
                opts = ["In the debate on mind-body relationship, Princess Elisabeth challenged Descartes' notion of the self which posed the problem of afterlife, highlighting its fundamental tie to the body.", "In the discourse on mind-body relationship, Princess Elisabeth argued that Descartes' view of the self as mere consciousness overlooked its essential connection to the physical body.", 'In the historical mind-body discourse, Princess Elisabeth confronted Descartes and other philosophers, stressing the indivisible link between consciousness and the physical body.', 'Princess Elisabeth disputed philosophers including Descartes, stressing the fundamental unity of consciousness and the physical body within the mind-body debates.']
            assert len(opts)==4 and all(opts), (c,n,opts)
            q['options'] = [{'id':chr(65+i),'text':v} for i,v in enumerate(opts)]
        stats = V_STATS[n-1] if c=='VARC' and n<=16 else D_STATS.get(n) if c=='DILR' else None
        if stats:
            cat, outcome, own, top, att, acc, pv = stats
            q['selectionCategory'] = cat
            q['benchmark'] = {'source':'IMS supplied question statistics','sourceImage':r['file'],'topperTimeSeconds':seconds(top),'topperAttemptPercent':att,'topperAccuracyPercent':acc,'topperPValue':pv}
            results.append({'questionId':q['id'],'outcome':outcome,'timeSeconds':seconds(own)})
        if c=='DILR' and n in [13,15,18]: q['selectionCategory']='C'
        if c=='DILR' and n>=19:
            att, acc = {19:(82.86,67.24),20:(82.86,77.59),21:(84.29,91.53),22:(80,78.57)}[n]
            q['selectionCategory'] = 'B' if n==19 else 'A'
            q['benchmark'] = {'source':'IMS supplied question statistics (visible fields only)','sourceImage':r['file'],'topperAttemptPercent':att,'topperAccuracyPercent':acc}
        questions[c,n] = q

    def left(c,n):
        return (OCR/Path(rm[c,n]['file']).stem/'left.txt').read_text(encoding='utf8').split('\n',1)[1].strip()

    def embed(target,filename,key,alt,box=None):
        im=Image.open(SRC/filename)
        if box: im=im.crop(box)
        stream=io.BytesIO(); im.save(stream,format='PNG')
        test['assets'][key]={'alt':alt,'data':'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()}
        target.setdefault('assetIds',[]).append(key)

    def group(c,a,b,title,stimulus=None):
        g={'id':f'take-home-4-{c.lower()}-group-{a}','title':title,'questions':[questions[c,n] for n in range(a,b+1)]}
        if stimulus: g['stimulus']=paragraphs(stimulus)
        test['sections'][list(ANS).index(c)]['groups'].append(g)
        return g

    for n,title in [(1,'Evolution and climate change'),(5,'Aesthetic experience'),(9,'Antimatter and gravity'),(13,'Brain-machine interfaces')]:
        group('VARC',n,n+3,title,left('VARC',n))
    for n in range(17,25): group('VARC',n,n,f'Verbal ability · Q{n}')
    group('DILR',1,5,'Game of numbers',left('DILR',1))
    p=left('DILR',6); p=p[:p.index('Po\n')]+p[p.index('First ten natural'):]
    g=group('DILR',6,10,'Octagonal die',p)
    embed(g,'DILR Q6 to Q10.png','th4-dilr-die','Original octagonal-prism figure.')
    # Surrounding conditions are text; graph data remains only in the supplied original crops.
    # The whole-set screenshot supplies the final conditions missing from the question captures.
    p='''NAT-2023 for the admission for two years full time MBA program of prestigious National Institutes of Management (NIMs) at Ahmedabad, Bangalore, Kolkata, Lucknow and Delhi was conducted on 26 November 2023. Based on the performance in NAT-2023, the institutes gave calls for WAT-PI for the admission to the MBA program. Some students received calls from only one NIM while some others received calls from multiple NIMs. It is known that in all 100 students received calls from all the five NIMs.

The first graph below shows the number of students getting 3 and 4 calls from different NIMs, including that NIM (all numbers are multiples of 100).

(Interpretation of the graph: Total 200 students got calls from total 3 NIMs, including NIM-Ahmedabad. Similarly, total 600 students got calls from total 4 NIMs, including NIM-Lucknow, and so on.)

The second graph below shows the number of students getting calls from two NIMs.

(Interpretation of the graph: Total 100 students got calls from only NIM Ahmedabad and NIM Bangalore, total 150 students got calls from NIM Kolkata and NIM Lucknow, and so on.)

Total number of WAT-PI calls given out by NIM-Ahmedabad, Bangalore, Kolkata, Lucknow and Delhi are 1200, 1200, 1500, 2000 and 1600 respectively.'''
    g=group('DILR',11,14,'NIM admission calls',p)
    embed(g,'DILR Q11 to Q14 Figure1.png','th4-dilr-calls-1','Original first graph: number of calls.')
    embed(g,'DILR Q11 to Q14 Figure2.png','th4-dilr-calls-2','Original second graph: students getting two calls.')
    p=left('DILR',15); p=p[:p.index('Number of living former')]+p[p.index('Following points are known:'):]
    p=p.replace('Theylivedfor |','They lived for').replace(' ;','')
    g=group('DILR',15,18,'Presidents of Bungaland',p)
    embed(g,'DILR Q15 to Q18.png','th4-dilr-presidents','Original president-tenure table.')
    p=left('DILR',19).split('28 |')[0].replace('H, |, J','H, I, J').replace('- Dand E','- D and E')
    g=group('DILR',19,22,'Sports club teams',p)
    embed(g,'DILR Q19 to Q22.png','th4-dilr-scores','Original player-score table.')
    for n in range(1,23): group('QA',n,n,f'Quantitative ability · Q{n}')
    for n,box in {12:(10,145,239,360),14:(10,120,235,320),15:(10,40,159,128),16:(10,40,495,112)}.items():
        embed(questions['QA',n],rm['QA',n]['file'],f'th4-qa-{n}',f'Original source {"expression" if n==16 else "geometry figure"} for QA question {n}.',box)
    test['sourceAnalysis']={
        'label':'Partial original IMS attempt: 26 of 68 questions have visible outcomes and timings. Totals below cover only those 26 questions, not the full mock.',
        'sourceImages':[r['file'] for r in records if (r['section']=='VARC' and r['number']<=16) or (r['section']=='DILR' and r['number'] in D_STATS)],
        'questionResults':results,
    }
    (ROOT/'samples/take-home-4.json').write_text(json.dumps(test,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'Built Take Home 4: {len(questions)} questions, {len(test["assets"])} original image assets, {len(results)} timed source results.')
    return test


if __name__=='__main__': build()
