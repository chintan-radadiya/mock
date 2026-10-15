const {chromium}=require('playwright'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:4173');
  await page.waitForSelector('.library-group');
  for(const category of ['Take Home','Full Mocks','Sectionals']){
   await page.click(`[data-filter="${category}"]`);
   assert.equal(await page.locator('.library-group').count(),1);
   assert.ok((await page.locator('.library-group h2').textContent()).startsWith(category));
  }
  await page.click('[data-filter="All"]');
  async function start(){
   await page.click('[data-start="cat-studio-demo"]');
   await page.check('#ready');await page.click('#beginBtn');
   await page.waitForSelector('.exam-header');
  }
  async function leave(){await page.click('[data-action="leave"]');await page.click('[data-action="leave-confirm"]');await page.waitForSelector('.library-group');}
  await start();await page.check('input[name="answer"][value="C"]');await page.click('[data-action="save"]');await leave();
  const first=await page.evaluate(async()=> (await Store.all('attempts'))[0]);
  assert.ok(Number.isFinite(first.pausedAt));
  await start();await leave();
  assert.equal(await page.locator('[data-resume]').count(),2);
  await page.reload();await page.waitForSelector('[data-resume]');
  assert.equal(await page.locator('[data-resume]').count(),2);
  await page.click(`[data-resume="${first.id}"]`);await page.waitForSelector('.exam-header');
  const saved=await page.evaluate(async id=>(await Store.all('attempts')).find(a=>a.id===id),first.id);
  assert.equal(saved.startedAt,first.startedAt);
  assert.equal(saved.pausedAt,undefined);
  assert.ok(saved.pausedMs > 0);
  assert.equal(saved.responses['demo-v1'].saved,'C');
  await leave();assert.deepEqual(errors,[]);
  console.log('PASS: library categories, multiple unfinished attempts, refresh, preserved responses and resume.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
