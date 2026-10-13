const {test}=require('node:test');const assert=require('node:assert/strict');const CAT=require('../app/core');const A=require('../app/analysis');const fs=require('node:fs');const t=JSON.parse(fs.readFileSync('samples/varc-section-6.json'));const mock=JSON.parse(fs.readFileSync('samples/sample-full-mock.json'));
test('Take Home 4 keeps complete keys and figures while source totals remain explicitly partial',()=>{
 const t=CAT.validate(require('../samples/take-home-4.json')),r=A.build(null,t,true);
 assert.deepEqual(t.sections.map(s=>CAT.flatten(s).length),[24,22,22]);
 assert.deepEqual(t.sections[1].groups.map(g=>g.questions.length),[5,5,4,4,4]);
 assert.equal(Object.keys(t.assets).length,9);
 assert.equal(CAT.flatten(t.sections[0])[17].answer[0],'5');
 assert.equal(CAT.flatten(t.sections[1])[2].answer[0],'2177280');
 assert.equal(CAT.flatten(t.sections[2])[17].answer[0],'18430');
 assert.equal(r.partialSource,true);assert.equal(r.totalQuestions,68);assert.equal(r.count,26);
 assert.equal(r.score,18);assert.equal(r.attempted,10);assert.equal(r.correct,7);
 assert.deepEqual(r.areas.filter(a=>a.depth===1).map(a=>a.label),['VARC','DILR']);
 assert.ok(r.sets.every(s=>s.count>0));assert.equal(r.sourceAnalysis.percentile,undefined);
 for(const s of t.sections){
  const split=CAT.extractSection(t,s.code,'th4-'+s.code);
  assert.deepEqual(split.sections[0],s);CAT.validate(split);
  const a=CAT.createAttempt(split,{mode:'sectional',section:s.code,shuffle:true},1000,'th4-attempt-'+s.code);
  assert.deepEqual(a.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),s.groups.map(g=>g.questions.map(q=>q.id)).sort());
  assert.equal(A.build(a,split).partialSource,false);assert.equal(A.build(a,split).count,CAT.flatten(s).length);
 }
 const full=CAT.createAttempt(t,{mode:'full'},1000,'th4-full');
 assert.equal(A.build(full,t).count,68);assert.equal(full.snapshot.sourceAnalysis,undefined);
});
test('October full mocks preserve complete sections, source scorecards and original figures',()=>{
 for(const [name,score,attempted,sectionScores,sets] of [['simcat-3',20,23,[13,2,5],[4,5,5,4,4]],['take-home-1',22,18,[17,3,2],[5,4,5,4,4]]]){
  const t=CAT.validate(JSON.parse(fs.readFileSync('samples/'+name+'.json'))),r=A.build(null,t,true);
  assert.deepEqual(t.sections.map(s=>CAT.flatten(s).length),[24,22,22]);
  assert.deepEqual(t.sections[1].groups.map(g=>g.questions.length),sets);
  assert.equal(t.sections[0].groups.filter(g=>g.questions.length===4).length,4);
  assert.equal(r.score,score);assert.equal(r.attempted,attempted);assert.equal(r.correct,9);
  assert.deepEqual(r.areas.filter(a=>a.depth===1).map(a=>a.score),sectionScores);
  for(const s of t.sections)assert.deepEqual(CAT.flatten(s).map(q=>q.sourceNumber),Array.from({length:CAT.flatten(s).length},(_,i)=>i+1));
  const a=CAT.createAttempt(t,{mode:'full',shuffle:true},1000,'test-'+name);
  assert.equal(a.snapshot.sourceAnalysis,undefined);assert.equal(A.build(a,t).score,0);
  for(const s of t.sections)assert.deepEqual(a.snapshot.sections.find(x=>x.code===s.code).groups.map(g=>g.questions.map(q=>q.id)).sort(),s.groups.map(g=>g.questions.map(q=>q.id)).sort());
  const split=CAT.extractSection(t,'DILR','split-'+name,'DILR');assert.deepEqual(split.sections[0],t.sections[1]);assert.equal(split.sourceAnalysis,undefined);
  const graphs=Object.entries(t.assets).filter(([,a])=>a.alt.includes('graph'));assert.ok(graphs.length);
  for(const [key,a] of graphs){assert.match(a.data,/^data:image\/png;base64,/);assert.ok(split.assets[key]);assert.doesNotMatch(a.alt,/\d/);}
 }
 const s=require('../samples/simcat-3.json'),t=require('../samples/take-home-1.json');
 assert.doesNotMatch(s.sections[1].groups[4].stimulus,/35%|25%|10%/);
 assert.doesNotMatch(t.sections[1].groups[1].stimulus,/\(p%\)|\(q%\)|\(r%\)/);
 assert.match(t.sections[0].groups[3].stimulus,/discovery of a never-before-seen human relative/);
 assert.equal(CAT.flatten(s.sections[2])[4].answer[0],'1540');
 assert.match(CAT.flatten(s.sections[2])[4].prompt,/x ≥ 1/);
});
test('Take Home 6 reconciles source scores, selection, area times and reusable sections',()=>{
 const t=CAT.validate(require('../samples/take-home-6.json')),r=A.build(null,t,true);
 assert.deepEqual(t.sections.map(s=>CAT.flatten(s).length),[24,22,22]);
 assert.deepEqual(t.sections[1].groups.map(g=>g.questions.length),[5,5,4,4,4]);
 assert.equal(r.count,68);assert.equal(r.partialSource,false);
 assert.equal(r.score,45);assert.equal(r.attempted,33);assert.equal(r.correct,18);
 assert.deepEqual(r.areas.filter(a=>a.depth===1).map(a=>a.score),[24,14,7]);
 assert.deepEqual(r.selection[0].cells.map(c=>[c.correct,c.incorrect,c.skipped]),[[15,5,9],[3,5,11],[0,5,15]]);
 assert.deepEqual(r.areas.filter(a=>a.section==='QA').map(a=>[a.count,a.score,a.viewedMs/1000]),[[3,0,260],[8,7,1722],[5,0,291],[4,0,39],[2,0,100]]);
 assert.equal(CAT.flatten(t.sections[0])[17].answer[0],'3');
 assert.equal(CAT.flatten(t.sections[1])[12].answer[0],'1448');
 assert.equal(CAT.flatten(t.sections[2])[14].answer[0],'45');
 assert.equal(Object.keys(t.assets).length,6);
 assert.ok(Object.values(t.assets).every(a=>a.data.startsWith('data:image/png;base64,')));
 for(const s of t.sections){
  const split=CAT.extractSection(t,s.code,'th6-'+s.code);CAT.validate(split);
  assert.deepEqual(split.sections[0],s);assert.equal(split.sourceAnalysis,undefined);
  const attempt=CAT.createAttempt(split,{mode:'sectional',section:s.code,shuffle:true},1000,'th6-'+s.code);
  assert.deepEqual(attempt.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),s.groups.map(g=>g.questions.map(q=>q.id)).sort());
  assert.equal(A.build(attempt,split).score,0);
 }
 const attempt=CAT.createAttempt(t,{mode:'full'},1000,'th6-full');
 assert.equal(attempt.snapshot.sourceAnalysis,undefined);assert.equal(A.build(attempt,t).sourceAnalysis,null);
});

test('screenshot totals and selection matrix reconcile exactly',()=>{const r=A.build(null,CAT.validate(t),true);assert.equal(r.score,1);assert.equal(r.count,24);assert.equal(r.attempted,15);assert.equal(r.correct,3);assert.equal(r.accuracy,20);assert.equal(r.viewedMs,2387000);assert.deepEqual(r.selection[0].cells.map(c=>[c.correct,c.incorrect,c.skipped]),[[2,4,2],[0,6,7],[1,2,0]]);assert.deepEqual(r.areas.filter(a=>a.depth===2).map(a=>[a.count,a.score,a.correct]),[[16,0,2],[8,1,1]]);});
test('new attempts do not inherit source results or percentiles',()=>{const a=CAT.createAttempt(t,{mode:'sectional',section:'VARC'},1000,'a');const r=A.build(a,t);assert.equal(r.score,0);assert.equal(r.attempted,0);assert.equal(r.sourceAnalysis,null);assert.equal(r.accuracy,null);assert.equal(r.timePerAttemptMs,null);assert.equal(a.snapshot.sourceAnalysis,undefined);});
test('historic metadata enriches only unchanged questions',()=>{const a=CAT.createAttempt(t,{mode:'sectional',section:'VARC',shuffle:true},1000,'a');for(const g of a.snapshot.sections[0].groups)for(const q of g.questions){delete q.benchmark;delete q.selectionCategory;}const r=A.build(a,t);assert.ok(r.rows.every(q=>q.benchmark));a.snapshot.sections[0].groups[0].questions[0].prompt+=' changed';assert.equal(A.build(a,t).rows[0].benchmark,undefined);});
test('direct full mock and sectional snapshots validate for backup',()=>{const a=CAT.createAttempt(mock,{mode:'full'},1000,'a');assert.equal(a.snapshot.sections.length,3);const b=CAT.createAttempt(mock,{mode:'sectional',section:'QA'},1000,'b');assert.equal(CAT.validate(b.snapshot).testType,'sectional');assert.equal(A.build(b,mock).pValueAvailable,false);const bad=structuredClone(mock);bad.sections.pop();assert.throws(()=>CAT.validate(bad));});
test('invalid optional source values are rejected',()=>{for(const mutate of [x=>x.sourceAnalysis.percentile=101,x=>x.sourceAnalysis.questionResults.push(x.sourceAnalysis.questionResults[0]),x=>x.sourceAnalysis.reportedAreas=[null],x=>x.sections[0].groups[0].questions[0].benchmark.topperPValue=-1]){const bad=structuredClone(t);mutate(bad);assert.throws(()=>CAT.validate(bad));}});

test('new supplied tests contain complete unique question ranges and intact sets',()=>{
 const dilr=CAT.validate(require('../samples/dilr-section-1.json')),sim=CAT.validate(require('../samples/simcat-2.json'));
 assert.deepEqual(dilr.sections[0].groups.map(g=>g.questions.length),[5,4,4,5,4]);
 assert.deepEqual(sim.sections.map(s=>CAT.flatten(s).length),[24,22,22]);
 for(const t of [dilr,sim])for(const s of t.sections){assert.deepEqual(CAT.flatten(s).map(q=>q.sourceNumber),Array.from({length:CAT.flatten(s).length},(_,i)=>i+1));for(const q of CAT.flatten(s))assert.ok(q.type==='TITA'?q.answer.length:q.options.some(o=>o.id===q.answer));}
 assert.equal(CAT.flatten(sim.sections[0])[0].benchmark.topperAttemptPercent,91.6);
 assert.equal(CAT.flatten(sim.sections[2])[1].answer[0],'20');
 assert.match(CAT.flatten(sim.sections[2])[1].prompt,/\u2265/);
 assert.match(CAT.flatten(sim.sections[2])[18].prompt,/x \u2212 y \u2265 1/);
 assert.equal(sim.sourceAnalysis,undefined);
});
test('separating a section preserves groups, keys and referenced assets without mutating source',()=>{
 const source=require('../samples/simcat-2.json'),before=JSON.stringify(source);
 const s=CAT.extractSection(source,'DILR','separate-dilr','My DILR');
 assert.equal(s.testType,'sectional');assert.equal(s.sections.length,1);assert.deepEqual(s.sections[0],source.sections[1]);assert.equal(Object.keys(s.assets).length,3);
 assert.equal(JSON.stringify(source),before);assert.equal(s.sourceAnalysis,undefined);
 const a=CAT.createAttempt(s,{mode:'sectional',section:'DILR',shuffle:true},1000,'split-attempt');
 assert.equal(CAT.flatten(a.snapshot.sections[0]).length,22);assert.deepEqual(a.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),s.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort());
 assert.throws(()=>CAT.extractSection(s,'QA','bad','Bad'));
});
