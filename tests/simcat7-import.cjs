const {chromium}=require('playwright'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:4173');
  await page.click('[data-source-analysis="ims-simcat-7-2026"]');
  await page.waitForSelector('#analysisTabs');await page.click('[data-analysis-tab="questions"]');
  assert.equal(await page.locator('#questionTable tbody tr').count(),68);
  await page.screenshot({path:'test-results/simcat-7-analysis.png',fullPage:true});
  await page.click('[data-analysis-back]');
  await page.click('[data-start="ims-simcat-7-2026"]');
  await page.selectOption('#startMode','DILR');await page.check('#ready');await page.click('#beginBtn');
  await page.waitForSelector('.exam-header');await page.click('[data-question="5"]');
  const imgs=page.locator('.passage-panel img');assert.equal(await imgs.count(),1);
  assert.ok(await imgs.evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0)));
  assert.deepEqual(errors,[]);await page.screenshot({path:'test-results/simcat-7-QA.png',fullPage:true});
  console.log('PASS: SimCAT 7 complete analysis, sectional launch and original DILR image.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
