"""Transcription of the user's five analysis screenshots (4)-(8), not inferred benchmarks."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
file = root / 'samples/varc-section-6.json'
t = json.loads(file.read_text(encoding='utf-8'))
# Question number, source time, topper time, topper attempt %, accuracy %, p-value, source category.
data = [
 (1,'08:29','04:53',90.77,81.36,73.85,'A'),(2,'02:02','01:16',90.77,47.46,43.08,'B'),
 (3,'01:09','01:03',73.85,12.5,9.23,'C'),(4,'01:08','01:22',80.0,55.77,44.62,'B'),
 (5,'07:22','04:13',87.69,96.49,84.61,'A'),(6,'01:25','01:25',86.15,37.5,32.31,'B'),
 (7,'02:13','01:12',81.54,50.94,41.54,'B'),(8,'01:20','00:58',86.15,21.43,18.46,'C'),
 (9,'00:43','03:25',92.31,100.0,92.31,'A'),(10,'00:19','00:45',87.69,89.47,78.46,'A'),
 (11,'00:02','00:53',84.62,76.36,64.62,'A'),(12,'00:03','01:07',83.08,61.11,50.77,'B'),
 (13,'02:27','01:27',87.69,92.98,81.53,'A'),(14,'00:33','01:46',76.92,50.0,38.46,'B'),
 (15,'01:48','01:46',90.77,72.88,66.15,'A'),(16,'01:30','01:31',92.31,61.67,56.93,'B'),
 (17,'01:48','01:25',83.08,59.26,49.23,'B'),(18,'00:45','01:31',78.46,88.24,69.23,'A'),
 (19,'03:05','01:54',61.54,57.5,35.39,'B'),(20,'01:21','01:01',63.08,7.32,4.62,'C'),
 (21,'00:15','02:51',61.54,55.0,33.85,'B'),(22,'00:00','00:42',61.54,80.0,49.23,'B'),
 (23,'00:00','00:30',58.46,84.21,49.23,'B'),(24,'00:00','00:55',60.0,74.36,44.62,'B')
]
seconds = lambda s: int(s.split(':')[0])*60 + int(s.split(':')[1])
correct = {3,10,13}
skipped = {7,9,11,12,14,21,22,23,24}
questions = {q['sourceNumber']:q for g in t['sections'][0]['groups'] for q in g['questions']}
results = []
for n, own, topper, attempt, accuracy, pvalue, category in data:
    q = questions[n]
    q['area'] = 'Reading Comprehension' if n <= 12 or n >= 21 else 'Verbal Reasoning'
    q['selectionCategory'] = category
    q['benchmark'] = {'source':'IMS supplied analysis screenshots', 'sourceImage':'Screenshot (6).png' if n<=13 else 'Screenshot (7).png', 'topperTimeSeconds':seconds(topper),'topperAttemptPercent':attempt,'topperAccuracyPercent':accuracy,'topperPValue':pvalue}
    results.append({'questionId':q['id'],'outcome':'Correct' if n in correct else 'Unanswered' if n in skipped else 'Incorrect','timeSeconds':seconds(own)})
t['revision'] = 2
t['testType'] = 'sectional'
t['sourceAnalysis'] = {
 'label':'Original IMS attempt · supplied screenshots',
 'sourceImages':[f'Screenshot ({n}).png' for n in range(4,9)],
 'reportedScore':1,'percentile':17.1,
 'percentileMapper':[{'percentile':p,'score':s,'section':'VARC'} for p,s in [(70,16),(85,21),(90,24),(95,29),(99,38),(99.5,40)]],
 'questionResults':results,
 'reportedAreas':[
  {'label':'Overall','score':1,'count':24,'attempted':15,'correct':3,'accuracy':20,'timeLabel':'00:39','marksPerMinute':0.03,'timePerAttemptLabel':'02:40'},
  {'label':'Reading Comprehension','score':0,'count':16,'attempted':8,'correct':2,'accuracy':25,'timeLabel':'00:26','marksPerMinute':0,'timePerAttemptLabel':'03:19'},
  {'label':'Verbal Reasoning','score':1,'count':8,'attempted':7,'correct':1,'accuracy':14.29,'timeLabel':'00:13','marksPerMinute':0.08,'timePerAttemptLabel':'01:54'}
 ],
 'notes':'Source question times are the exact MM:SS values in Screenshots (6) and (7). Screenshot (5) displays rounded/truncated HH:MM totals and provider-calculated averages; retain those reported values separately. Categories A/B/C are source labels, not MCQ option IDs or inferred difficulty. The original response choices and attempt date are not specified by these analysis screenshots.'
}
file.write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
print('Added 24 question benchmarks and source analysis. Question times total:',sum(r['timeSeconds'] for r in results),'seconds')
