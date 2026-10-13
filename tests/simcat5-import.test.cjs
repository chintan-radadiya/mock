const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),C=require('../app/core'),A=require('../app/analysis');
const complete=fs.existsSync('samples/simcat-5.json');
const t=JSON.parse(fs.readFileSync(complete?'samples/simcat-5.json':'samples/drafts/simcat-5.json'));
test('SimCAT 5 source analysis reconciles scores, categories and section times',()=>{
 const r=A.build(null,t,true);
 assert.deepEqual(t.sections.map(s=>C.flatten(s).length),[24,22,22]);
 assert.deepEqual(t.sections[1].groups.map(g=>g.questions.length),[5,5,4,4,4]);
 assert.deepEqual(t.sections[0].groups.filter(g=>g.questions.length>1).map(g=>g.questions.map(q=>q.sourceNumber)),[[1,2,3,4],[7,8,9,10],[13,14,15,16],[17,18,19,20]]);
 assert.equal(r.score,35);assert.equal(r.attempted,20);assert.equal(r.correct,13);
 assert.deepEqual(r.areas.filter(a=>a.depth===1).map(a=>[a.score,a.viewedMs/1000]),[[30,2382],[5,2407],[0,2417]]);
 assert.deepEqual(r.selection[0].cells.map(c=>[c.correct,c.incorrect,c.skipped]),[[4,1,6],[5,5,30],[4,1,12]]);
 assert.deepEqual(r.areas.filter(a=>a.section==='QA').map(a=>[a.count,a.viewedMs/1000]),[[6,442],[8,1390],[3,378],[2,21],[3,186]]);
 assert.equal(t.sourceAnalysis.percentile,undefined);assert.equal(t.sourceAnalysis.percentileMapper,undefined);
 assert.equal(C.flatten(t.sections[1])[4].answer[0],'0');
 assert.equal(C.flatten(t.sections[2])[0].answer[0],'96');
 assert.equal(C.flatten(t.sections[2])[21].answer[0],'0');
 assert.match(C.flatten(t.sections[2])[12].prompt,/11⅑%/);
 assert.match(C.flatten(t.sections[2])[16].prompt,/withdrew ₹60,000/);
});
test('SimCAT 5 verified sections preserve original assets and groups in new attempts',()=>{
 for(const s of t.sections.slice(1)){
  const section=C.validate({...t,id:'s5-'+s.code,testType:'sectional',sections:[s],sourceAnalysis:undefined});
  const attempt=C.createAttempt(section,{mode:'sectional',section:s.code,shuffle:true},1000,'check-'+s.code);
  assert.deepEqual(attempt.snapshot.sections[0].groups.map(g=>g.questions.map(q=>q.id)).sort(),s.groups.map(g=>g.questions.map(q=>q.id)).sort());
  assert.equal(attempt.snapshot.sourceAnalysis,undefined);assert.equal(A.build(attempt,section).score,0);
 }
 assert.ok(Object.values(t.assets).every(a=>a.data.startsWith('data:image/png;base64,')));
 assert.doesNotMatch(t.sections[1].groups[1].stimulus,/20\.1|24\.6|22\.8/);
});
test('SimCAT 5 cannot enter the library with unconfirmed source fields',()=>{
 if(complete){
  C.validate(t);assert.equal(t.importReview,undefined);
  assert.equal(C.flatten(t.sections[0])[19].answer,'D');
  assert.equal(C.flatten(t.sections[0])[23].options[3].text,'Option 1');
  const a=C.createAttempt(t,{mode:'full',shuffle:true},1000,'s5-full');
  assert.equal(a.snapshot.sourceAnalysis,undefined);assert.equal(A.build(a,t).score,0);
  for(const s of t.sections){const split=C.extractSection(t,s.code,'s5-split-'+s.code);assert.deepEqual(split.sections[0],s);}
  return;
 }
 assert.equal(t.importReview.ready,false);
 assert.equal(C.flatten(t.sections[0])[19].answer,null);
 assert.equal(C.flatten(t.sections[0])[23].options[3].text,null);
 assert.throws(()=>C.validate(t),e=>{
  assert.deepEqual(e.message.split('\n'),['simcat-5-varc-q20: answer must match an option ID.','simcat-5-varc-q24: invalid or duplicate option.']);return true;
 });
});
