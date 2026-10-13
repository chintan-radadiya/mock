const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const C=require('../app/core'),A=require('../app/analysis');
const t=C.validate(JSON.parse(fs.readFileSync('samples/simcat-6.json','utf8')));
test('SimCAT 6 preserves its 66-question source structure and reviewed notation',()=>{
 assert.deepEqual(t.sections.map(s=>C.flatten(s).length),[24,20,22]);
 assert.deepEqual(t.sections[1].groups.map(g=>g.questions.length),[5,5,5,5]);
 assert.deepEqual(t.sections[0].groups.filter(g=>g.questions.length>1).map(g=>g.questions.map(q=>q.sourceNumber)),[[1,2,3,4],[7,8,9,10],[13,14,15,16],[18,19,20,21]]);
 const qa=C.flatten(t.sections[2]),di=C.flatten(t.sections[1]);
 assert.equal(qa[9].options[1].text,'24,000');
 assert.match(qa[10].prompt,/log₁₀\(7⅕\)/);
 assert.match(qa[12].prompt,/aₙ₊₁ = aₙ\/\(1 \+ 3aₙ\)/);
 assert.deepEqual(qa[14].answer,['2']);
 assert.deepEqual(di[14].answer,['30']);assert.deepEqual(di[17].answer,['17']);assert.deepEqual(di[19].answer,['23']);
 assert.match(t.sections[1].groups[2].stimulus,/All-Rounder bought for ₹25 Lakhs/);
 assert.match(t.sections[1].groups[2].stimulus,/Defenders = ₹5 Lakhs, Raiders = ₹10 Lakhs/);
 assert.equal(qa[11].assetIds.length,1);assert.ok(t.assets[qa[11].assetIds[0]].data.startsWith('data:image/png;base64,'));
});
test('SimCAT 6 partial source analysis excludes missing results and missing benchmarks',()=>{
 const r=A.build(null,t,true);
 assert.equal(r.partialSource,true);assert.equal(r.totalQuestions,66);assert.equal(r.count,13);
 assert.equal(r.score,3);assert.equal(r.attempted,5);assert.equal(r.correct,2);assert.equal(r.skipped,8);
 assert.equal(r.viewedMs,1225000);
 assert.equal(t.sourceAnalysis.percentile,undefined);assert.equal(t.sourceAnalysis.reportedScore,undefined);
 assert.equal(C.flatten(t.sections[0])[12].benchmark.topperPValue,undefined);
 assert.equal(C.flatten(t.sections[1])[14].benchmark.topperTimeSeconds,undefined);
 assert.ok(!r.rows.some(q=>q.id==='simcat-6-dilr-q15'));
 assert.ok(!r.rows.some(q=>q.section==='QA'));
});
test('SimCAT 6 sections remain reusable with grouped shuffling and fresh attempt analysis',()=>{
 for(const s of t.sections){
  const split=C.extractSection(t,s.code,'s6-split-'+s.code);
  assert.deepEqual(split.sections[0],s);
  const a=C.createAttempt(split,{mode:'sectional',section:s.code,shuffle:true},1000,'s6-'+s.code);
  assert.deepEqual(a.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),s.groups.map(g=>g.questions.map(q=>q.id)).sort());
  assert.equal(a.snapshot.sourceAnalysis,undefined);assert.equal(A.build(a,split).score,0);
 }
 const a=C.createAttempt(t,{mode:'full',shuffle:true},1000,'s6-full');
 assert.equal(a.snapshot.sourceAnalysis,undefined);assert.equal(A.build(a,t).count,66);
});
