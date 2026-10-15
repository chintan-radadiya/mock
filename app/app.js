/* CAT Studio: browser-local exam workspace. All imported content is rendered as text. */
(() => {
  'use strict';
  const $ = (selector, el = document) => el.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = ms => { const seconds = Math.max(0, Math.ceil(ms / 1000)); return String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0'); };
  const date = ms => new Date(ms).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
  const uid = () => crypto.randomUUID();
  let tests = [], attempts = [], active = null, page = 'library', filter = 'All', query = '', releaseLock = null;
  let attemptKind = 'all', testFilter = '', fromDate = '', toDate = '', trendMetric = 'accuracy';
  let lastPerf = 0, lastWall = 0, lastVisible = false, persistQueue = Promise.resolve(), storageFailed = false, timer, lastPersist = 0, toastTimer;
  const labels = { answered: 'Answered', unanswered: 'Not answered', review: 'Marked for review', 'answered-review': 'Answered & marked', unvisited: 'Not visited' };
  function toast(message) { $('#toast').textContent = message; $('#toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => $('#toast').hidden = true, 4500); }
  function modal(html) { $('#modalContent').innerHTML = html; if (!$('#modal').open) $('#modal').showModal(); }
  function closeModal() { $('#modal').close(); }
  function head(title) { return `<div class="dialog-head"><h2>${title}</h2><button class="close" data-action="close" aria-label="Close dialog">×</button></div>`; }
  function download(value, name) { const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
  function persist() {
    if (!active) return persistQueue;
    const snapshot = CAT.copy(active);
    if ($('#saveStatus') && !storageFailed) $('#saveStatus').textContent = 'Saving progress…';
    persistQueue = persistQueue.then(() => Store.put('attempts', snapshot)).then(() => {
      storageFailed = false;
      if ($('#saveStatus')) $('#saveStatus').textContent = 'Progress saved on this device';
    }).catch(error => {
      if (!storageFailed) toast('Saving failed. Export your attempt now; free browser storage before continuing.');
      storageFailed = true;
      if ($('#saveStatus')) $('#saveStatus').textContent = 'Saving failed — export available';
      console.error('Attempt storage failed', error.name);
    });
    return persistQueue;
  }
  function assets(ids, t) { return (ids || []).map(id => { const a = t.assets?.[id]; return a ? `<img class="asset" src="${esc(a.data)}" alt="${esc(a.alt)}">` : ''; }).join(''); }
  function metric(label, value, note) { return `<div class="metric"><div class="metric-label">${label}</div><strong>${value}</strong><small>${note}</small></div>`; }
  function top() { return `<div class="topline"><span class="mini muted">WORKSPACE / ${page === 'library' ? 'TEST LIBRARY' : page === 'history' ? 'ATTEMPT HISTORY' : 'YOUR PROGRESS'}</span><span class="date">${new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</span></div>`; }
  function completed() { return attempts.filter(a => a.status === 'completed'); }
  async function reload() { [tests, attempts] = await Promise.all([Store.all('tests'), Store.all('attempts')]); tests.sort((a, b) => Number(!!a.demo) - Number(!!b.demo) || a.title.localeCompare(b.title)); attempts.sort((a, b) => b.startedAt - a.startedAt); }
  function navigate(to) { if (active) return; $('#main').onclick=null; $('#main').onchange=null; $('#main').oninput=null; page = to; filter = 'All'; query = ''; document.body.classList.remove('exam-mode'); document.querySelectorAll('[data-nav]').forEach(b => b.classList.toggle('active', b.dataset.nav === page)); render(); }
  function render() { if (page === 'library') library(); else if (page === 'history') history(); else insights(); if (page !== 'library') analysisFilters(); if (page === 'insights') trendControls(); }
  function libraryCategory(t) {
    if (t.demo) return 'Demo';
    if (t.sections.length === 1) return 'Sectionals';
    return /take[\s-]*home/i.test(t.title+' '+t.id) ? 'Take Home' : 'Full Mocks';
  }
  function pendingBanner() {
    const pending = attempts.filter(a => a.status === 'active');
    return pending.length ? `<section class="panel"><h2>Unfinished attempts</h2><p class="mini muted">Resume an attempt below or start any test in the library. Each attempt pauses when you leave and resumes with its remaining time.</p>${pending.map(a => `<div class="notice row between"><span><strong>${esc(a.title)}</strong><br><small>${esc(a.mode === 'full' ? 'Full mock' : a.snapshot.sections[0].code+' sectional')} ? Started ${date(a.startedAt)}</small></span><button data-resume="${esc(a.id)}">Resume attempt ?</button></div>`).join('')}</section>` : '';
  }
  function library() {
    const done = completed(), last = done[0], report = last ? CAT.report(last) : null;
    $('#main').innerHTML = `${top()}<div class="page-head"><div><div class="eyebrow">A little practice. A lot of progress.</div><h1>Ready for your next attempt?</h1><p>Your sectionals and mocks, together in one place.</p></div><button class="primary" data-action="import">＋ Import test</button></div>${pendingBanner()}
    <div class="metrics">${metric('Tests in your library', tests.length, 'Ready when you are')}${metric('Completed attempts', done.length, 'Sectionals + full mocks')}${metric('Latest accuracy', report ? report.accuracy + '%' : '—', report ? esc(last.title) : 'Your first attempt starts here')}${metric('Practice time', Math.round(done.reduce((n, a) => n + CAT.report(a).viewedMs, 0) / 60000) + ' min', 'Active question-viewing time')}</div>
    <div class="welcome"><div><h2>From your questions to exam day.</h2><p>Send your question screenshots as a ZIP in chat. Import the prepared JSON here for a 40-minute sectional or a full 120-minute mock.</p></div><div class="steps"><span>1</span> Import <span>2</span> Attempt <span>3</span> Review</div></div>
    <div class="row between"><h2 style="margin:0">Your test library</h2><button class="text-button" data-action="compose">Build a full mock →</button></div>
    <div class="toolbar"><div class="tabs">${['All', 'Take Home', 'Full Mocks', 'Sectionals', 'VARC', 'DILR', 'QA'].map(f => `<button data-filter="${f}" class="${filter === f ? 'active' : ''}">${f}</button>`).join('')}</div><input class="search" id="search" placeholder="Search your tests…" aria-label="Search tests" value="${esc(query)}"></div><div id="cards"></div>
    <p class="footer-note">CAT-style practice · +3 correct · −1 incorrect MCQ · No penalty for incorrect TITA · Strict section timing</p>`;
    cards(); $('#search').oninput = e => { query = e.target.value; cards(); };
  }
  function cards() {
    const list = tests.filter(t => t.title.toLowerCase().includes(query.toLowerCase()) && (filter === 'All' || (CAT.ORDER.includes(filter) ? t.sections.length === 1 && t.sections[0].code === filter : libraryCategory(t) === filter)));
    $('#cards').innerHTML = list.length ? ['Take Home','Full Mocks','Sectionals','Demo'].filter(category => list.some(t => libraryCategory(t) === category)).map(category => `<section class="library-group"><h2>${category} <span class="mini muted">(${list.filter(t => libraryCategory(t) === category).length})</span></h2><div class="cards">${list.filter(t => libraryCategory(t) === category).map(t => {
      const count = t.sections.reduce((n, s) => n + CAT.flatten(s).length, 0), n = attempts.filter(a => a.testId === t.id).length;
      return `<article class="card ${t.demo ? 'demo' : ''}"><div class="card-top"><span class="badge">${t.sections.length === 3 ? 'FULL MOCK' : esc(t.sections.map(s => s.code).join(' + '))}</span><span class="mini muted">${t.demo ? 'Demo' : 'Imported'}</span></div><h3>${esc(t.title)}</h3><p>${esc(t.description || (t.demo ? 'Short sample content to explore the exam experience.' : 'Your questions, with shared sets kept together.'))}</p><div class="card-detail"><span>◷ ${t.sections.length * 40} minutes</span><span>▤ ${count} questions</span></div><div class="card-foot"><span class="mini muted">${n ? n + ' attempt' + (n > 1 ? 's' : '') : 'Not attempted yet'}</span><button class="text-button" data-start="${esc(t.id)}">Start test →</button></div>${t.sections.length===3 ? `<button class="source-analysis-button" data-split="${esc(t.id)}">Save a section as a separate test &rarr;</button>` : ''}${t.sourceAnalysis ? `<button class="source-analysis-button" data-source-analysis="${esc(t.id)}">View supplied source analysis &rarr;</button>` : ''}</article>`;
    }).join('')}</div></section>`).join('') : '<div class="empty"><h3>No matching tests</h3><p>Import a JSON test or choose another filter.</p></div>';
  }
  function importDialog() { modal(`${head('Import your next test')}<p class="muted mini">Send a ZIP of sectional or full-mock images in chat, then import the prepared JSON here. A full mock uses one JSON containing VARC, DILR and QA; composing sectionals is optional. RC and DILR sets stay together.</p><label class="field">Import type<select id="importType"><option value="auto">Detect from JSON</option><option value="full">Full mock ? all three sections</option><option value="sectional">Single sectional</option></select></label><p class="muted mini">Include answer images and label each section in your ZIP.</p><button class="secondary" data-action="file">Choose JSON file</button><label class="field">Or paste test JSON<textarea id="jsonPaste" placeholder='{"schemaVersion": 1, ...}'></textarea></label><div id="importError" class="error" role="alert"></div><div id="importPreview"></div><div class="dialog-foot"><button data-action="example">Download full-mock sample JSON</button><button class="primary" data-action="validate">Validate & preview</button></div>`); }
  let incoming = null;
  function validateImport(text) {
    try {
      incoming = CAT.validate(JSON.parse(text));
        const kind=$('#importType').value;
        if(kind==='full' && incoming.sections.length!==3)throw new Error('A full mock needs VARC, DILR and QA in the same JSON.');
        if(kind==='sectional' && incoming.sections.length!==1)throw new Error('A sectional must contain exactly one section.');
      if (tests.some(t => t.id === incoming.id && t.revision >= incoming.revision)) throw new Error('This ID and revision already exists. Increase the revision to update it, or use a different test ID.');
      $('#importError').textContent = '';
      const count = incoming.sections.reduce((n, s) => n + CAT.flatten(s).length, 0);
      $('#importPreview').innerHTML = `<div class="notice"><strong>${esc(incoming.title)}</strong><br>${count} questions · ${incoming.sections.map(s => esc(s.code)).join(', ')} · revision ${incoming.revision}<br>Existing attempt results retain their original questions.</div><button class="secondary" data-action="confirm-import">Add to library</button>`;
    } catch (e) { incoming = null; $('#importPreview').innerHTML = ''; $('#importError').textContent = e.message; }
  }
  function startDialog(id) {
    const t = tests.find(t => t.id === id);
    modal(`${head('Set up your attempt')}<h3>${esc(t.title)}</h3><label class="field">Test mode<select id="startMode">${t.sections.length === 3 ? '<option value="full">Full mock · 120 minutes</option>' : ''}${t.sections.map(s => `<option value="${s.code}">${s.code} sectional · 40 minutes</option>`).join('')}</select></label><label class="check"><input id="shuffle" type="checkbox"> Shuffle groups and standalone questions</label><p class="mini muted">Questions within an RC passage or DILR set stay together. Options retain their original order.</p><div class="notice">The clock starts immediately and pauses when you leave, switch tabs or close the browser. Sections cannot be ended early. Use Save & Next or Mark for Review & Next to save an answer. Unsaved selections are not scored.</div>${t.demo ? '<p class="mini muted">This demo has fewer questions than an actual CAT paper. Timing remains 40 minutes per section.</p>' : ''}<label class="check"><input id="ready" type="checkbox"> I have read the instructions and am ready.</label><div class="dialog-foot"><button data-action="close">Cancel</button><button class="primary" id="beginBtn" data-begin="${esc(id)}" disabled>Begin attempt →</button></div>`);
    $('#ready').onchange = e => $('#beginBtn').disabled = !e.target.checked;
  }
  async function acquire() {
    if (!navigator.locks) throw new Error('Open the app at http://localhost:4173 using Start CAT Studio.cmd. This browser needs Web Locks to protect your attempt across tabs.');
    return new Promise((resolve, reject) => navigator.locks.request('cat-studio-exam', { ifAvailable: true }, async lock => {
      if (!lock) { resolve(false); return; }
      await new Promise(release => { releaseLock = release; resolve(true); });
    }).catch(reject));
  }
  async function begin(id) {
    if (!await acquire()) { toast('Your exam is open in another tab. Close it there first.'); return; }
    await reload();
    const selected = $('#startMode').value;
    active = CAT.createAttempt(tests.find(t => t.id === id), { mode: selected === 'full' ? 'full' : 'sectional', section: selected, shuffle: $('#shuffle').checked }, Date.now(), uid());
    CAT.visit(active, 0, active.startedAt); await persist(); closeModal(); enterExam();
  }
  async function resume(id) {
    if (!await acquire()) { toast('Your exam is open in another tab. Close it there first.'); return; }
    await reload(); active = attempts.find(a => a.id === id);
    if (!active || active.status !== 'active') { releaseLock(); releaseLock = null; active = null; render(); return; }
    CAT.resume(active, Date.now());
    CAT.advance(active, Date.now());
    if (active.status !== 'active') { await finish(); return; }
    // Preserve a recovered draft, but do not count it as a saved answer.
    const q = currentQuestion(), r = active.responses[q.id] ||= CAT.response(active, q.id);
    r.visited = true; r.visits++; active.events.push({ type: 'resume', at: Date.now(), questionId: q.id });
    await persist(); enterExam();
  }
  function currentQuestion() { return CAT.flatten(active.snapshot.sections[active.sectionIndex])[active.current]; }
  function enterExam() { document.body.classList.add('exam-mode'); lastPerf = performance.now(); lastWall = Date.now(); lastVisible = !document.hidden; lastPersist = performance.now(); exam(); clearInterval(timer); timer = setInterval(tick, 250); }
  function account() {
    if (!active || active.status !== 'active' || active.pausedAt != null) return;
    const wall = Date.now(), perf = performance.now(), delta = Math.max(0, perf - lastPerf);
    const untilEnd = Math.max(0, CAT.deadline(active) - Math.max(lastWall, active.startedAt));
    // A heartbeat gap may be machine sleep or a suspended browser, not reading time.
    if (lastVisible && delta <= 2500) {
      const elapsed = Math.min(delta, untilEnd), q = currentQuestion(), r = active.responses[q.id] ||= CAT.response(active, q.id);
      r.viewedMs += elapsed; if (r.visits <= 1) r.firstVisitMs += elapsed;
    }
    lastPerf = perf; lastWall = wall; lastVisible = !document.hidden;
  }
  function checkBoundary() {
    if (!active || active.status !== 'active' || active.pausedAt != null) return false;
    account();
    const changed = CAT.advance(active, Date.now());
    if (changed) {
      closeModal();
      if (active.status === 'completed') { finish(); return false; }
      CAT.visit(active, 0, active.lastWall); persist(); exam(); toast('The next section has started.');
      return false;
    }
    return true;
  }
  function tick() {
    if (!checkBoundary()) return;
    const left = Math.max(0, CAT.deadline(active) - Math.max(Date.now(), active.lastWall));
    $('#clock').textContent = fmt(left); $('#clock').classList.toggle('warning', left <= 300000);
    if ($('#qtime')) $('#qtime').textContent = fmt(CAT.response(active, currentQuestion().id).viewedMs);
    if (performance.now() - lastPersist >= 1000) { lastPersist = performance.now(); persist(); }
  }
  function exam() {
    const s = active.snapshot.sections[active.sectionIndex], qs = CAT.flatten(s), q = qs[active.current], r = CAT.response(active, q.id);
    $('#main').innerHTML = `<header class="exam-header"><div class="row"><div class="brand"><span class="brand-icon">C<span>•</span></span> CAT Studio</div><div><strong>${esc(active.title)}</strong><br><small>${active.mode === 'full' ? 'Full mock' : 'Sectional'} · Strict exam mode</small></div></div><div class="exam-tools"><button data-action="calculator">Calculator</button><button data-action="instructions">Instructions</button><div><small>SECTION TIME LEFT</small><div id="clock" class="clock">${fmt(CAT.deadline(active) - active.lastWall)}</div></div></div></header>
    <div class="exam-sectionbar"><div class="section-tabs">${active.snapshot.sections.map((section, i) => `<span class="${i === active.sectionIndex ? 'active' : ''}">${i === active.sectionIndex ? '' : '▣ '}${section.code}</span>`).join('')}</div><span class="saved-status" id="saveStatus">${storageFailed ? 'Saving failed — export below' : 'Progress saved on this device'}</span><span class="mini muted">+3 correct &nbsp; ${q.type === 'MCQ' ? '−1 incorrect' : '0 incorrect'}</span></div>
    <div class="exam-layout"><section class="exam-question"><div class="question-top"><strong>Question ${active.current + 1} <span class="muted">of ${qs.length}</span></strong><span class="muted">${q.type} · Viewed <span id="qtime">${fmt(r.viewedMs)}</span></span></div>
    <div class="question-columns ${q.stimulus || q.groupAssets.length ? '' : 'single'}">${q.stimulus || q.groupAssets.length ? `<div class="passage-panel"><h3>${esc(q.groupTitle)}</h3><div class="content">${esc(q.stimulus)}</div>${assets(q.groupAssets, active.snapshot)}</div>` : ''}<div class="answer-panel"><div class="content">${esc(q.prompt)}</div>${assets(q.assetIds, active.snapshot)}${q.type === 'MCQ' ? `<div class="options">${q.options.map((o, i) => `<label class="option ${r.draft === o.id ? 'selected' : ''}"><input type="radio" name="answer" value="${esc(o.id)}" ${r.draft === o.id ? 'checked' : ''}><span class="option-letter">${String.fromCharCode(65 + i)}.</span><span>${esc(o.text)}</span></label>`).join('')}</div>` : `<label class="field">Type your answer<input class="tita-input" id="tita" inputmode="decimal" autocomplete="off" value="${esc(r.draft || '')}" placeholder="Enter a number"></label>`}<p class="mini muted" style="margin-top:20px">A selection is saved only with Save & Next or Mark for Review & Next.</p></div></div>
    <footer class="question-actions"><div class="row"><button data-action="review">Mark for Review & Next</button><button data-action="clear">Clear Response</button></div><div class="row"><button data-action="previous" ${active.current === 0 ? 'disabled' : ''}>Previous</button><button class="secondary" data-action="save">Save & Next →</button></div></footer></section>
    <aside class="exam-sidebar"><h3>${s.code} question palette</h3><div class="mini muted" id="answeredCount"></div><div class="palette" id="palette"></div><div class="legend">${Object.entries(labels).map(([key, label]) => `<div><span class="swatch ${key}"></span>${label}</div>`).join('')}</div><div class="notice">This section ends automatically at 00:00. Saved answers marked for review are evaluated.</div><button class="ghost" data-action="leave" style="width:100%;font-size:12px">Return to dashboard</button><button class="text-button" data-action="export-active">Export attempt backup</button></aside></div>`;
    palette();
    document.querySelectorAll('input[name="answer"]').forEach(input => input.onchange = e => {
      if (!checkBoundary()) return;
      active.responses[q.id].draft = e.target.value;
      document.querySelectorAll('.option').forEach(o => o.classList.toggle('selected', $('input', o).checked)); persist();
    });
    if ($('#tita')) $('#tita').oninput = e => { if (!checkBoundary()) return; active.responses[q.id].draft = e.target.value; persist(); };
  }
  function palette() { const qs = CAT.flatten(active.snapshot.sections[active.sectionIndex]); $('#palette').innerHTML = qs.map((q, i) => `<button class="${CAT.status(CAT.response(active, q.id))} ${active.current === i ? 'current' : ''}" data-question="${i}" aria-label="Question ${i + 1}, ${labels[CAT.status(CAT.response(active, q.id))]}" ${active.current === i ? 'aria-current="true"' : ''}>${i + 1}</button>`).join(''); $('#answeredCount').textContent = `${qs.filter(q => CAT.filled(CAT.response(active, q.id).saved)).length} of ${qs.length} answered`; }
  function goto(index) { if (!checkBoundary() || index === active.current) return; CAT.visit(active, index, active.lastWall); persist(); exam(); }
  function saveNext(review) {
    if (!checkBoundary()) return;
    const q = currentQuestion(), r = CAT.response(active, q.id);
    if (!CAT.save(active, q.id, r.draft, review, Date.now())) return;
    const count = CAT.flatten(active.snapshot.sections[active.sectionIndex]).length;
    if (active.current < count - 1) CAT.visit(active, active.current + 1, active.lastWall);
    else toast('Response saved. You can review this section until time expires.');
    persist(); exam();
  }
  async function finish() {
    clearInterval(timer); closeModal(); const resultId = active.id, result = CAT.copy(active); await persist();
    if (releaseLock) releaseLock(); releaseLock = null; active = null;
    document.body.classList.remove('exam-mode'); await reload();
    if (storageFailed) { attempts = attempts.filter(a => a.id !== resultId); attempts.unshift(result); }
    showResult(resultId);
  }
  async function leaveExam() {
    if (!checkBoundary()) return; CAT.pause(active, Date.now()); await persist(); clearInterval(timer); active = null;
    if (releaseLock) releaseLock(); releaseLock = null; closeModal(); await reload(); navigate('library');
  }
  function history() {
    const list = selectedAttempts(attempts);
    $('#main').innerHTML = `${top()}<div class="page-head"><div><div class="eyebrow">Learn from every attempt</div><h1>Your attempt history</h1><p>Every response, revisit, and result — ready to review.</p></div></div>${pendingBanner()}<div class="toolbar"><div class="tabs">${['All', ...CAT.ORDER].map(f => `<button data-filter="${f}" class="${filter === f ? 'active' : ''}">${f}</button>`).join('')}</div><span class="mini muted">${list.length} attempts</span></div>${list.length ? `<div class="panel table-wrap"><table><thead><tr><th>Test</th><th>Started</th><th>Score</th><th>Accuracy</th><th>Status</th><th></th></tr></thead><tbody>${list.map(a => { const r = CAT.report(a); return `<tr><td><strong>${esc(a.title)}</strong><br><span class="mini muted">${a.snapshot.sections.map(s => s.code).join(' / ')} · ${a.shuffled ? 'Shuffled' : 'Original order'}</span></td><td>${date(a.startedAt)}</td><td class="score">${a.status === 'active' ? '—' : r.score + ' / ' + r.count * 3}</td><td>${a.status === 'active' ? '—' : r.accuracy + '%'}</td><td><span class="badge ${a.status === 'completed' ? '' : 'neutral'}">${esc(a.status)}</span></td><td><button class="text-button" ${a.status === 'active' ? 'data-resume' : 'data-result'}="${esc(a.id)}">${a.status === 'active' ? 'Resume' : 'Review'} →</button></td></tr>`; }).join('')}</tbody></table></div>` : '<div class="empty"><h3>Your first result belongs here</h3><p>Complete a sectional or mock to begin tracking your progress.</p><button data-nav="library">Browse tests</button></div>'}`;
  }
  function ordinal(a) {
    const key = x => [x.testId, x.testRevision, x.mode, x.snapshot.sections.map(s => s.code).join('-')].join('|');
    return attempts.filter(x => x.status === 'completed' && key(x) === key(a) && x.startedAt < a.startedAt).length + 1;
  }
  function selectedAttempts(values) {
    return values.filter(a => (filter === 'All' || a.snapshot.sections.some(s => s.code === filter)) && (!testFilter || a.testId === testFilter) && (attemptKind === 'all' || (attemptKind === 'first' ? ordinal(a) === 1 : ordinal(a) > 1)) && (!fromDate || a.startedAt >= new Date(fromDate + 'T00:00:00').getTime()) && (!toDate || a.startedAt < new Date(toDate + 'T23:59:59.999').getTime()));
  }
  function analysisFilters() {
    const container = document.createElement('div'); container.className = 'analysis-filters';
    container.innerHTML = `<label class="field">Test<select id="testFilter"><option value="">All tests</option>${tests.map(t => `<option value="${esc(t.id)}" ${testFilter === t.id ? 'selected' : ''}>${esc(t.title)}</option>`).join('')}</select></label><label class="field">Attempt type<select id="attemptKind"><option value="all">All attempts</option><option value="first">First attempts</option><option value="retakes">Retakes</option></select></label><label class="field">From<input type="date" id="fromDate" value="${esc(fromDate)}"></label><label class="field">To<input type="date" id="toDate" value="${esc(toDate)}"></label>`;
    $('.page-head').after(container); $('#attemptKind').value = attemptKind;
    $('#testFilter').onchange = e => { testFilter = e.target.value; render(); };
    $('#attemptKind').onchange = e => { attemptKind = e.target.value; render(); };
    $('#fromDate').onchange = e => { fromDate = e.target.value; render(); };
    $('#toDate').onchange = e => { toDate = e.target.value; render(); };
  }
  function trendControls() {
    const chart = $('.trend'); if (!chart) return;
    const title = $('h2', chart.parentElement); title.textContent = 'Your last 12 attempts';
    const select = document.createElement('select'); select.className = 'search'; select.setAttribute('aria-label', 'Progress chart metric');
    select.innerHTML = '<option value="accuracy">Accuracy (%)</option><option value="score">Raw score</option><option value="time">Average viewing time (seconds)</option>'; select.value = trendMetric; title.after(select);
    const draw = () => {
      const values = selectedAttempts(completed()).slice(0, 12).reverse().map(a => {
        const rows = CAT.report(a).rows.filter(q => filter === 'All' || q.section === filter), attempted = rows.filter(q => q.outcome !== 'Unanswered').length;
        return { a, value: trendMetric === 'accuracy' ? attempted ? Math.round(rows.filter(q => q.outcome === 'Correct').length / attempted * 100) : 0 : trendMetric === 'score' ? rows.reduce((n, q) => n + q.score, 0) : Math.round(rows.reduce((n, q) => n + q.viewedMs, 0) / 1000 / Math.max(1, rows.filter(q => q.visited).length)) };
      });
      const max = Math.max(1, ...values.map(v => Math.abs(v.value)));
      chart.innerHTML = values.map(({ a, value }, i) => `<div class="bar-item" title="${esc(a.title)} · ${date(a.startedAt)} · attempt ${ordinal(a)}: ${value}"><strong class="${value < 0 ? 'danger' : ''}">${value}${trendMetric === 'accuracy' ? '%' : trendMetric === 'time' ? 's' : ''}</strong><div class="bar" style="height:${Math.abs(value) / max * 100}px;${value < 0 ? 'background:#c95548' : ''}"></div><span>${i + 1}</span></div>`).join('');
    };
    select.onchange = e => { trendMetric = e.target.value; draw(); }; draw();
  }
  function showResult(id) {
    const a = attempts.find(a => a.id === id); if (!a || a.status === 'active') return;
    page = 'history'; document.querySelectorAll('[data-nav]').forEach(b => b.classList.toggle('active', b.dataset.nav === page));
    AnalysisView.open({mount:$('#main'),attempt:a,test:tests.find(t=>t.id===a.testId),storageFailed,onBack:()=>navigate('history'),onExport:()=>download({backupVersion:1,tests:[a.snapshot],attempts:[a]},'cat-attempt.json')});
  }
  function showSourceAnalysis(id) {
    const test=tests.find(t=>t.id===id); if(!test?.sourceAnalysis)return;
    AnalysisView.open({mount:$('#main'),test,source:true,onBack:()=>navigate('library'),onExport:()=>download(test,test.id+'.json')});
  }
  function insights() {
    const done = selectedAttempts(completed());
    const rows = done.flatMap(a => CAT.report(a).rows.filter(q => filter === 'All' || q.section === filter));
    const attempted = rows.filter(q => q.outcome !== 'Unanswered').length;
    const topics = [...new Set(rows.map(q => q.topic || 'Untagged'))];
    $('#main').innerHTML = `${top()}<div class="page-head"><div><div class="eyebrow">The bigger picture</div><h1>See your progress.</h1><p>Track accuracy and time. Find what deserves your next practice session.</p></div></div><div class="tabs">${['All', ...CAT.ORDER].map(f => `<button data-filter="${f}" class="${filter === f ? 'active' : ''}">${f}</button>`).join('')}</div>${!done.length ? '<div class="empty" style="margin-top:25px"><h3>Progress starts with one attempt.</h3><p>Complete a test to see your trends here.</p></div>' : `<div class="metrics" style="margin-top:25px">${metric('Completed attempts', done.length, 'Includes retakes')}${metric('Combined accuracy', attempted ? Math.round(rows.filter(q => q.outcome === 'Correct').length / attempted * 100) + '%' : '0%', 'Correct / attempted')}${metric('Questions attempted', attempted, 'Across selected sections')}${metric('Average viewing time', fmt(rows.reduce((n, q) => n + q.viewedMs, 0) / Math.max(1, rows.filter(q => q.visited).length)), 'Per visited question')}</div><div class="panel"><h2>Accuracy over your last 12 attempts</h2><p class="mini muted">Different papers have different difficulty. Repeated attempts include familiarity with the questions.</p><div class="trend">${done.slice(0, 12).reverse().map((a, i) => { const rr = CAT.report(a).rows.filter(q => filter === 'All' || q.section === filter), att = rr.filter(q => q.outcome !== 'Unanswered').length, value = att ? Math.round(rr.filter(q => q.outcome === 'Correct').length / att * 100) : 0; return `<div class="bar-item" title="${esc(a.title)}: ${value}%"><strong>${value}%</strong><div class="bar" style="height:${value}px"></div><span>${i + 1}</span></div>`; }).join('')}</div></div><div class="panel table-wrap"><h2>Topic performance</h2><table><thead><tr><th>Topic</th><th>Attempted</th><th>Accuracy</th><th>Viewing time</th></tr></thead><tbody>${topics.map(topic => { const qs = rows.filter(q => (q.topic || 'Untagged') === topic), att = qs.filter(q => q.outcome !== 'Unanswered').length, correct = qs.filter(q => q.outcome === 'Correct').length; return `<tr><td>${esc(topic)}</td><td>${att} / ${qs.length}</td><td>${att ? Math.round(correct / att * 100) : 0}%</td><td>${fmt(qs.reduce((n, q) => n + q.viewedMs, 0))}</td></tr>`; }).join('')}</tbody></table></div>`}`;
  }
  function splitDialog(id) {
    const t=tests.find(t=>t.id===id); if(!t)return;
    modal(`${head('Save a section')}<p class="mini muted">Create a standalone 40-minute sectional from ${esc(t.title)}. Its passages, sets, answer keys and supplied benchmarks stay intact.</p><label class="field">Section<select id="splitCode">${t.sections.map(s=>`<option value="${s.code}">${s.code} - ${CAT.flatten(s).length} questions</option>`).join('')}</select></label><label class="field">Sectional title<input id="splitTitle" value="${esc(t.title+' - '+t.sections[0].code)}"></label><p class="mini muted">You can also use these sections directly in Build a full mock.</p><div id="splitError" class="error" role="alert"></div><div class="dialog-foot"><button data-split-export="${esc(id)}">Download section JSON</button><button class="primary" data-split-save="${esc(id)}">Save to library</button></div>`);
    $('#splitCode').onchange=()=>$('#splitTitle').value=t.title+' - '+$('#splitCode').value;
  }
  async function splitSection(id,saveToLibrary) {
    try {
      const title=$('#splitTitle').value.trim();if(!title)throw new Error('Enter a sectional title.');
      const t=CAT.extractSection(tests.find(t=>t.id===id),$('#splitCode').value,uid(),title);
      if(saveToLibrary){await Store.put('tests',t);closeModal();await reload();navigate('library');toast('Sectional saved. It is ready to attempt or use in a custom mock.');}
      else download(t,t.id+'.json');
    }catch(e){$('#splitError').textContent=e.message;}
  }
  function compose() {
    modal(`${head('Build a full mock')}<p class="mini muted">Choose each section from any sectional or full mock in your library. You can mix sections from different full mocks; no separate extraction is needed. The mock will run VARC → DILR → QA, 40 minutes each.</p><label class="field">Mock title<input id="mockTitle" value="My full mock"></label>${CAT.ORDER.map(code => `<label class="field">${code}<select id="compose${code}"><option value="">Choose a test…</option>${tests.filter(t => t.sections.some(s => s.code === code)).map(t => `<option value="${esc(t.id)}">${esc(t.title)} - ${CAT.flatten(t.sections.find(s=>s.code===code)).length} questions${t.sections.length===3?' (full mock)':''}${t.demo ? ' (demo)' : ''}</option>`).join('')}</select></label>`).join('')}<div id="composeError" class="error"></div><div class="dialog-foot"><button class="primary" data-action="create-mock">Create full mock</button></div>`);
  }
  async function createMock() {
    try {
      const id = uid();
      const selected = CAT.ORDER.map(code => { const source = tests.find(t => t.id === $('#compose' + code).value); if (!source) throw new Error('Choose a source for ' + code + '.'); return { code, source }; });
      const t = { schemaVersion: 1, testType: 'full', revision: 1, id, title: $('#mockTitle').value.trim(), demo: selected.some(s => s.source.demo), assets: {}, sections: selected.map(({ code, source }) => {
        const section = CAT.copy(source.sections.find(s => s.code === code));
        const prefix = code + '-';
        for (const [key, asset] of Object.entries(source.assets || {})) tPlaceholderAssets.push([prefix + key, asset]);
        for (const g of section.groups) { g.id = prefix + g.id; g.assetIds = (g.assetIds || []).map(a => prefix + a); for (const q of g.questions) { q.id = prefix + q.id; q.assetIds = (q.assetIds || []).map(a => prefix + a); } }
        return section;
      }) };
      for (const [key, asset] of tPlaceholderAssets.splice(0)) t.assets[key] = asset;
      await Store.put('tests', CAT.validate(t)); closeModal(); await reload(); navigate('library'); toast('Full mock added to your library.');
    } catch (e) { tPlaceholderAssets.length = 0; $('#composeError').textContent = e.message; }
  }
  const tPlaceholderAssets = [];
  function calculator() {
    modal(`${head('Calculator')}<input id="calcDisplay" class="calc-display" value="0" readonly aria-label="Calculator display"><div class="calc-grid">${['C','⌫','%','÷','7','8','9','×','4','5','6','−','1','2','3','+','±','0','.','='].map(v => `<button data-calc="${v}">${v}</button>`).join('')}</div><p class="mini muted" style="margin:18px 0 0">The exam clock continues while the calculator is open.</p>`);
    let value = '0', accumulator = null, operator = null, fresh = false;
    $('#modalContent').onclick = e => { const k = e.target.dataset.calc; if (!k) return;
      if (k === 'C') { value = '0'; accumulator = null; operator = null; fresh = false; }
      else if (k === '⌫') value = value.length > 1 ? value.slice(0, -1) : '0';
      else if (k === '±') value = String(-Number(value));
      else if (k === '%') value = String(Number(value) / 100);
      else if ('0123456789.'.includes(k)) { if (fresh || value === '0' || value === 'Error') { value = k === '.' ? '0.' : k; fresh = false; } else if (k !== '.' || !value.includes('.')) value += k; }
      else { const n = Number(value); if (accumulator !== null && operator && !fresh) { const result = operator === '+' ? accumulator + n : operator === '−' ? accumulator - n : operator === '×' ? accumulator * n : accumulator / n; value = Number.isFinite(result) ? String(Number(result.toPrecision(12))) : 'Error'; } accumulator = Number(value); operator = k === '=' ? null : k; fresh = true; }
      $('#calcDisplay').value = value;
    };
  }
  async function exportBackup() { await reload(); download({ backupVersion: 1, exportedAt: new Date().toISOString(), tests, attempts }, 'cat-studio-backup.json'); }
  async function restoreBackup(text) {
    if (active) throw new Error('Return to the dashboard before restoring a backup.');
    const b = JSON.parse(text);
    if (b.backupVersion !== 1 || !Array.isArray(b.tests) || !Array.isArray(b.attempts)) throw new Error('Not a CAT Studio backup.');
    const ts = b.tests.map(CAT.validate), as = b.attempts.map(CAT.validateAttempt);
    if (new Set(ts.map(t => t.id)).size !== ts.length || new Set(as.map(a => a.id)).size !== as.length) throw new Error('Backup contains duplicate records.');
    for (const a of as) if (a.status === 'active') CAT.advance(a, Date.now());
    // Merge only new records. Never overwrite a newer local test or an existing attempt.
    if (!await acquire()) throw new Error('An exam is open in another tab. Close that exam before restoring.');
    try {
      await reload();
      await Store.restore(ts.filter(t => !tests.some(x => x.id === t.id && x.revision >= t.revision)), as.filter(a => !attempts.some(x => x.id === a.id)));
    } finally { releaseLock(); releaseLock = null; }
    await reload(); render(); toast('Backup restored. Existing attempts were kept.');
  }
  document.addEventListener('click', async event => {
    const el = event.target.closest('button'); if (!el) return;
    try {
      if (el.dataset.nav) navigate(el.dataset.nav);
      if (el.dataset.filter) { filter = el.dataset.filter; render(); }
      if (el.dataset.start) startDialog(el.dataset.start);
      if (el.dataset.begin) { el.disabled = true; await begin(el.dataset.begin); }
      if (el.dataset.resume) await resume(el.dataset.resume);
      if (el.dataset.split) splitDialog(el.dataset.split);
      if (el.dataset.splitSave) await splitSection(el.dataset.splitSave,true);
      if (el.dataset.splitExport) await splitSection(el.dataset.splitExport,false);
      if (el.dataset.result) showResult(el.dataset.result);
      if (el.dataset.sourceAnalysis) showSourceAnalysis(el.dataset.sourceAnalysis);
      if (el.dataset.export) { const a = attempts.find(a => a.id === el.dataset.export); download({ backupVersion: 1, tests: [a.snapshot], attempts: [a] }, 'cat-attempt.json'); }
      if (el.dataset.question !== undefined) goto(Number(el.dataset.question));
      switch (el.dataset.action) {
        case 'close': closeModal(); break;
        case 'import': importDialog(); break;
        case 'file': $('#importFile').click(); break;
        case 'validate': validateImport($('#jsonPaste').value); break;
        case 'confirm-import': if (incoming) { await Store.put('tests', incoming); incoming = null; closeModal(); await reload(); library(); toast('Test added to your library.'); } break;
        case 'example': download(window.DEMO_TEST, 'cat-sample-test.json'); break;
        case 'compose': compose(); break;
        case 'create-mock': await createMock(); break;
        case 'save': saveNext(false); break;
        case 'review': saveNext(true); break;
        case 'clear': if (checkBoundary()) { CAT.save(active, currentQuestion().id, null, CAT.response(active, currentQuestion().id).review, Date.now()); persist(); exam(); } break;
        case 'previous': goto(active.current - 1); break;
        case 'calculator': calculator(); break;
        case 'instructions': modal(`${head('Exam instructions')}<p>Each section lasts exactly 40 minutes. A full mock runs VARC, DILR, then QA. You cannot return to an earlier section.</p><p>Save & Next commits your answer. Mark for Review & Next commits and flags it. Palette navigation discards an unsaved selection. Saved answers marked for review are scored.</p><p>Correct: +3. Incorrect MCQ: −1. Incorrect TITA or unanswered: 0. The clock pauses through refreshes, tab changes, and browser closure.</p><p class="mini muted">Question time measures visible viewing time, not thinking time. Long interruptions are recorded as unobserved time.</p><button class="secondary" data-action="close">Return to test</button>`); break;
        case 'leave': modal(`${head('Leave the exam screen?')}<p>Your responses and remaining time will be saved. The clock will pause. You can resume from the dashboard.</p><div class="dialog-foot"><button data-action="close">Keep working</button><button data-action="leave-confirm">Return to dashboard</button></div>`); break;
        case 'leave-confirm': await leaveExam(); break;
        case 'export-active': await persist(); download({ backupVersion: 1, tests: [active.snapshot], attempts: [active] }, 'cat-active-attempt-backup.json'); break;
      }
    } catch (error) { toast(error.message); if (el.dataset.begin) el.disabled = false; }
  });
  $('#modal').addEventListener('close', () => { $('#modalContent').onclick = null; });
  $('#importFile').onchange = async e => { const f = e.target.files[0]; if (f) { if (f.size > 30 * 1024 * 1024) { toast('JSON files must be smaller than 30 MB.'); return; } validateImport(await f.text()); } e.target.value = ''; };
  $('#backupBtn').onclick = exportBackup;
  $('#restoreBtn').onclick = () => $('#restoreFile').click();
  $('#restoreFile').onchange = async e => { try { const f = e.target.files[0]; if (f) await restoreBackup(await f.text()); } catch (error) { toast(error.message); } e.target.value = ''; };
  document.addEventListener('visibilitychange', () => { if (active) { if (document.hidden) { account(); CAT.pause(active, Date.now()); } else { CAT.resume(active, Date.now()); lastPerf = performance.now(); lastWall = Date.now(); } lastVisible = !document.hidden; persist(); } });
  window.addEventListener('pagehide', () => { if (active) { account(); CAT.pause(active, Date.now()); persist(); } });
  window.addEventListener('beforeunload', e => { if (active) { account(); persist(); e.preventDefault(); e.returnValue = ''; } });
  async function boot() {
    try { await Store.open(); await reload();
      for (const t of window.BUNDLED_TESTS || [window.DEMO_TEST]) if (!tests.some(x => x.id === t.id && x.revision >= t.revision)) await Store.put('tests', CAT.validate(t));
      await reload(); render();
    } catch (e) { $('#main').innerHTML = `<div class="empty"><h2>Browser storage is unavailable</h2><p>${esc(e.message)}</p><p>Use a regular browser window and launch Start CAT Studio.cmd.</p></div>`; }
  }
  boot();
})();
