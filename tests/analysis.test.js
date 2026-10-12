const {test}=require('node:test');const assert=require('node:assert/strict');const CAT=require('../app/core');const A=require('../app/analysis');const fs=require('node:fs');const t=JSON.parse(fs.readFileSync('samples/varc-section-6.json'));const mock=JSON.parse(fs.readFileSync('samples/sample-full-mock.json'));
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
