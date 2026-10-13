const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  for(const [id,graphQuestion,expectedScore] of [['ims-simcat-3-2026',18,20],['ims-take-home-1-2026',5,22]]){
   const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://localhost:4173');await page.waitForSelector('[data-start="'+id+'"]');
   await page.click('[data-source-analysis="'+id+'"]');await page.waitForSelector('#analysisTabs');
   assert.ok((await page.textContent('#main')).includes(String(expectedScore)));
   await page.click('[data-analysis-tab="questions"]');assert.equal(await page.locator('#questionTable tbody tr').count(),68);
   await page.click('[data-analysis-back]');
   await page.click('[data-start="'+id+'"]');await page.selectOption('#startMode','DILR');await page.check('#ready');await page.click('#beginBtn');
   await page.waitForSelector('.exam-header');assert.equal(await page.locator('#palette button').count(),22);
   await page.click('[data-question="'+graphQuestion+'"]');
   const imgs=page.locator('.passage-panel img');assert.ok(await imgs.count()>0);
   assert.ok(await imgs.evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0)));
   assert.equal(await page.locator('.passage-panel svg,.passage-panel canvas').count(),0);
   await page.screenshot({path:'test-results/'+id+'-graph.png',fullPage:true});
   await page.clock.install();await page.clock.fastForward(2400000);await page.waitForSelector('#analysisTabs');
   await page.click('[data-analysis-tab="questions"]');assert.equal(await page.locator('#questionTable tbody tr').count(),22);
   assert.deepEqual(errors,[]);await context.close();
  }
  console.log('PASS: both full mocks, 68-row supplied analysis, DILR graph images, 40-minute expiry and new-attempt analysis');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
