const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),C=require('../app/core');
const final=fs.existsSync('samples/simcat-5.json');
const t=JSON.parse(fs.readFileSync(final?'samples/simcat-5.json':'samples/drafts/simcat-5.json'));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const review=await browser.newPage();
  await review.goto('http://localhost:4173');
  await review.click('[data-source-analysis="ims-simcat-5-2026"]');
  await review.waitForSelector('#analysisTabs');
  await review.click('[data-analysis-tab="questions"]');
  assert.equal(await review.locator('#questionTable tbody tr').count(),68);
  await review.close();
  for(const code of ['DILR','QA']){
   const section=C.validate({...t,testType:'sectional',id:'simcat-5-check-'+code,sections:t.sections.filter(s=>s.code===code),sourceAnalysis:undefined});
   const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://localhost:4173');await page.waitForSelector('[data-start]');
   await page.evaluate(async data=>{await Store.put('tests',data)},section);await page.reload();
   await page.click('[data-start="'+section.id+'"]');await page.check('#ready');await page.click('#beginBtn');
   await page.waitForSelector('.exam-header');await page.click('[data-question="'+(code==='DILR'?5:14)+'"]');
   const images=page.locator(code==='DILR'?'.passage-panel img':'.answer-panel img');
   assert.equal(await images.count(),1);assert.ok(await images.evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0)));
   assert.deepEqual(errors,[]);await page.screenshot({path:'test-results/simcat-5-'+code+'.png',fullPage:true});await page.close();
  }
  console.log('PASS: verified DILR and QA content, original image assets and exam launch.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
