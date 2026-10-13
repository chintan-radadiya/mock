const {chromium}=require('playwright');const assert=require('node:assert/strict');const fs=require('node:fs');
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true});try{
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://localhost:4173');await page.waitForSelector('[data-start="ims-simcat-2-2026"]');
 await page.click('[data-split="ims-simcat-2-2026"]');await page.selectOption('#splitCode','DILR');
 const dp=page.waitForEvent('download');await page.click('[data-split-export]');const download=await dp;await download.saveAs('test-results/separated-dilr.json');
 const extracted=JSON.parse(fs.readFileSync('test-results/separated-dilr.json'));assert.equal(extracted.sections.length,1);assert.equal(extracted.sections[0].code,'DILR');
 await page.fill('#splitTitle','Separated SimCAT DILR');await page.click('[data-split-save]');await page.waitForFunction(()=>document.querySelectorAll('.card').length===7);
 await page.click('[data-action="compose"]');await page.fill('#mockTitle','Real custom mock');
 await page.selectOption('#composeVARC','ims-simcat-2-2026');await page.selectOption('#composeDILR','ims-dilr-section-1-2026');await page.selectOption('#composeQA','ims-simcat-2-2026');
 await page.screenshot({path:'test-results/custom-mock-builder.png',fullPage:true});await page.click('[data-action="create-mock"]');await page.waitForFunction(()=>document.querySelectorAll('.card').length===8);
 const custom=await page.evaluate(async()=>{const t=(await Store.all('tests')).find(t=>t.title==='Real custom mock');return {t,counts:t.sections.map(s=>CAT.flatten(s).length)};});assert.deepEqual(custom.counts,[24,22,22]);assert.equal(custom.t.testType,'full');assert.ok(custom.t.assets['DILR-hockey-table']);
 await page.screenshot({path:'test-results/new-test-library.png',fullPage:true});
 await page.click('[data-start="ims-simcat-2-2026"]');await page.selectOption('#startMode','DILR');await page.check('#ready');await page.click('#beginBtn');await page.waitForSelector('.exam-header');assert.equal(await page.locator('#palette button').count(),22);assert.match(await page.textContent('#main'),/musical instruments/);
 await page.click('[data-question="13"]');assert.equal(await page.locator('.asset').count(),2);await page.screenshot({path:'test-results/simcat-dilr.png',fullPage:true});
 await page.clock.install();await page.clock.fastForward(2400000);await page.waitForSelector('#analysisTabs');
 await page.click('[data-analysis-tab="questions"]');assert.equal(await page.locator('#questionTable tbody tr').count(),22);assert.match(await page.textContent('#questionTable'),/96.2/);assert.doesNotMatch(await page.textContent('#main'),/Source percentile/);
 assert.deepEqual(errors,[]);console.log('PASS: new imports, section download/save, mixed-source real mock, DILR standalone, embedded charts, expiry and benchmark analysis');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
