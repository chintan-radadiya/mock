const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const C=require('../app/core'),A=require('../app/analysis');
const t=C.validate(JSON.parse(fs.readFileSync('samples/simcat-7.json','utf8')));

test('SimCAT 7 includes all 68 questions and the verified follow-up answers',()=>{
 assert.equal(t.importReview,undefined);
 assert.deepEqual(t.sections.map(s=>C.flatten(s).length),[24,22,22]);
 const qs=C.flatten(t.sections[0]).slice(6,10);
 assert.deepEqual(qs.map(q=>q.answer),['D','C','D','B']);
 assert.ok(qs.every(q=>q.prompt && q.options.length===4));
 assert.deepEqual(t.sections[0].groups.find(g=>g.questions[0].sourceNumber===7).questions.map(q=>q.sourceNumber),[7,8,9,10]);
 const attempt=C.createAttempt(t,{mode:'full',shuffle:true},1000,'s7-full');
 assert.equal(attempt.snapshot.sourceAnalysis,undefined);
 assert.equal(A.build(attempt,t).count,68);
});

test('SimCAT 7 supplied analysis reconciles to the scorecard and area totals',()=>{
 const r=A.build(null,t,true);
 assert.equal(r.count,68);assert.equal(r.score,29);
 assert.equal(r.attempted,23);assert.equal(r.correct,11);assert.equal(r.skipped,45);
 assert.deepEqual(r.areas.filter(x=>x.depth===1).map(x=>x.score),[20,3,6]);
 for(const reported of t.sourceAnalysis.reportedAreas){
  const row=r.areas.find(x=>x.label===reported.label);
  assert.equal(row.score,reported.score,reported.label);
 }
 assert.equal(t.sourceAnalysis.percentileMapper.length,24);
 assert.equal(t.sourceAnalysis.percentile,46.46);
});

test('SimCAT 7 complete DILR and QA sections validate and preserve original images',()=>{
 for(const section of t.sections.slice(1)){
  const split={...t,testType:'sectional',id:'s7-check-'+section.code,sections:[section]};
  delete split.sourceAnalysis;delete split.importReview;
  C.validate(split);
  const a=C.createAttempt(split,{mode:'sectional',section:section.code,shuffle:true},1000,'s7-'+section.code);
  assert.equal(A.build(a,split).score,0);
  assert.deepEqual(a.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),section.groups.map(g=>g.questions.map(q=>q.id)).sort());
 }
 const groups=t.sections[1].groups;
 assert.deepEqual(groups.map(g=>g.questions.length),[5,5,4,4,4]);
 assert.equal(groups[1].stimulus,undefined);
 for(const g of [groups[1],groups[2]]){
  assert.equal(g.assetIds.length,1);
  assert.ok(t.assets[g.assetIds[0]].data.startsWith('data:image/png;base64,'));
 }
});
