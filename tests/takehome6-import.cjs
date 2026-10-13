const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({channel:'chrome',headless:true});
 try {
  const page = await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:4173');
  await page.click('[data-source-analysis="ims-take-home-6-2026"]');
  await page.waitForSelector('#analysisTabs');
  await page.click('[data-analysis-tab="questions"]');
  assert.equal(await page.locator('#questionTable tbody tr').count(),68);
  await page.click('[data-analysis-back]');
  await page.click('[data-start="ims-take-home-6-2026"]');
  await page.selectOption('#startMode','DILR');
  await page.check('#ready');await page.click('#beginBtn');
  await page.waitForSelector('.exam-header');
  assert.ok(await page.locator('.passage-panel img').count());
  assert.ok(await page.locator('.passage-panel img').evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0)));
  assert.equal(await page.locator('.passage-panel svg,.passage-panel canvas').count(),0);
  await page.screenshot({path:'test-results/take-home-6-dilr.png',fullPage:true});
  // A separate browser context isolates the QA attempt from the running DILR attempt.
  const qa = await browser.newPage();
  await qa.goto('http://localhost:4173');
  await qa.click('[data-start="ims-take-home-6-2026"]');
  await qa.selectOption('#startMode','QA');await qa.check('#ready');await qa.click('#beginBtn');
  await qa.waitForSelector('.exam-header');
  assert.ok(await qa.locator('.answer-panel img').count());
  assert.ok(await qa.locator('.answer-panel img').evaluateAll(xs=>xs.every(x=>x.complete&&x.naturalWidth>0)));
  assert.deepEqual(errors,[]);
  console.log('PASS: 68 source analysis rows, DILR original graph and QA original figure.');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1);});
