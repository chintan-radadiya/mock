(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CAT = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const ORDER = ['VARC', 'DILR', 'QA'];
  const copy = value => JSON.parse(JSON.stringify(value));
  const filled = value => value !== null && value !== undefined && String(value).trim() !== '';
  function validate(input) {
    const t = copy(input), errors = [];
    const check = (condition, message) => { if (!condition) errors.push(message); };
    check(t && typeof t === 'object' && !Array.isArray(t), 'Expected a test object.');
    if (!t || typeof t !== 'object') throw new Error(errors.join('\n'));
    check(t.schemaVersion === 1, 'schemaVersion must be 1.');
    for (const key of ['id', 'title']) check(typeof t[key] === 'string' && t[key].trim(), key + ' must be a non-empty string.');
    check(Number.isInteger(t.revision) && t.revision > 0, 'revision must be a positive integer.');
    check(Array.isArray(t.sections) && t.sections.length > 0 && t.sections.length <= 3, 'Provide one to three sections.');
    check(t.testType === undefined || ['sectional','full'].includes(t.testType), 'testType must be sectional or full.');
    if (t.testType === 'full') check(Array.isArray(t.sections) && t.sections.length === 3, 'A full mock JSON must include VARC, DILR and QA.');
    if (t.testType === 'sectional') check(Array.isArray(t.sections) && t.sections.length === 1, 'A sectional JSON must include exactly one section.');
    const ids = new Set(), codes = new Set();
    const validId = id => typeof id === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]*$/.test(id) && id !== 'prototype' && !Object.hasOwn(Object.prototype, id);
    check(validId(t.id), 'Test ID must contain only letters, digits, dots, colons, hyphens or underscores and start with a letter or digit.');
    for (const key of ['description']) check(t[key] === undefined || typeof t[key] === 'string', key + ' must be text.');
    function unique(id, label) { check(validId(id) && !ids.has(id), label + ': invalid or duplicate ID.'); ids.add(id); }
    function assetRefs(item, label) { check(item.assetIds === undefined || (Array.isArray(item.assetIds) && item.assetIds.every(aid => typeof aid === 'string' && Object.hasOwn(t.assets || {}, aid))), label + ': assetIds must refer to embedded assets.'); }
    for (const s of Array.isArray(t.sections) ? t.sections : []) {
      if (!s || typeof s !== 'object') { check(false, 'Section must be an object.'); continue; }
      check(ORDER.includes(s.code) && !codes.has(s.code), 'Invalid or duplicate section: ' + s.code); codes.add(s.code);
      check(Array.isArray(s.groups) && s.groups.length > 0, s.code + ': groups cannot be empty.');
      for (const g of Array.isArray(s.groups) ? s.groups : []) {
        if (!g || typeof g !== 'object') { check(false, 'Group must be an object.'); continue; }
        unique(g.id, 'Group');
        check(typeof g.title === 'string', 'Group ' + g.id + ': title is required.');
        check(g.stimulus === undefined || typeof g.stimulus === 'string', g.id + ': stimulus must be text.');
        check(Array.isArray(g.questions) && g.questions.length > 0, g.id + ': questions cannot be empty.');
        for (const q of Array.isArray(g.questions) ? g.questions : []) {
          if (!q || typeof q !== 'object') { check(false, 'Question must be an object.'); continue; }
          unique(q.id, 'Question');
          check(['MCQ', 'TITA'].includes(q.type), q.id + ': type must be MCQ or TITA.');
          check(typeof q.prompt === 'string' && q.prompt.trim(), q.id + ': prompt is required.');
          if (q.type === 'MCQ') {
            const opts = Array.isArray(q.options) ? q.options : [];
            check(opts.length === 4, q.id + ': CAT MCQs require four options.');
            const oi = new Set();
            for (const o of opts) {
              if (!o || typeof o !== 'object') { check(false, q.id + ': option must be an object.'); continue; }
              check(validId(o.id) && !oi.has(o.id) && typeof o.text === 'string' && o.text.trim(), q.id + ': invalid or duplicate option.');
              oi.add(o.id);
            }
            check(oi.has(q.answer), q.id + ': answer must match an option ID.');
          } else if (q.type === 'TITA') {
            check(Array.isArray(q.answer) && q.answer.length > 0 && q.answer.every(a => typeof a === 'string' && /^-?\d+(\.\d+)?$/.test(a)), q.id + ': TITA answer must be an array of numeric strings.');
          }
          for (const key of ['topic', 'explanation', 'area']) check(q[key] === undefined || typeof q[key] === 'string', q.id + ': ' + key + ' must be text.');
          check(q.selectionCategory === undefined || ['A','B','C'].includes(q.selectionCategory), q.id + ': selectionCategory must be source label A, B or C.');
          if (q.benchmark !== undefined) {
            const b = q.benchmark;
            check(b && typeof b === 'object' && typeof b.source === 'string' && b.source.trim(), q.id + ': benchmark needs a source label.');
            if (b && typeof b === 'object') {
              for (const key of ['topperAttemptPercent','topperAccuracyPercent','topperPValue']) check(b[key] === undefined || (Number.isFinite(b[key]) && b[key]>=0 && b[key]<=100), q.id + ': invalid ' + key);
              check(b.topperTimeSeconds === undefined || (Number.isFinite(b.topperTimeSeconds) && b.topperTimeSeconds>=0), q.id + ': invalid topperTimeSeconds.');
            }
          }
          assetRefs(q, q.id);
        }
        assetRefs(g, g.id);
      }
    }
    check(t.assets === undefined || (t.assets && typeof t.assets === 'object' && !Array.isArray(t.assets)), 'assets must be an object.');
    for (const [id, a] of Object.entries(t.assets || {})) {
      check(a && typeof a.alt === 'string' && /^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+$/.test(a.data), id + ': asset must be an embedded PNG/JPEG/WebP with alt text.');
    }
    if (t.sourceAnalysis !== undefined) {
      const a=t.sourceAnalysis;
      check(a && typeof a==='object' && typeof a.label==='string' && a.label.trim() && Array.isArray(a.sourceImages) && a.sourceImages.length && a.sourceImages.every(x=>typeof x==='string'), 'sourceAnalysis needs a label and sourceImages.');
      if (a && typeof a==='object') {
        check(a.percentile===undefined || (Number.isFinite(a.percentile) && a.percentile>=0 && a.percentile<=100), 'Invalid source percentile.');
        check(a.reportedScore===undefined || Number.isFinite(a.reportedScore), 'Invalid source reportedScore.');
        check(Array.isArray(a.questionResults), 'sourceAnalysis.questionResults must be an array.');
        check(a.reportedAreas===undefined || (Array.isArray(a.reportedAreas) && a.reportedAreas.every(r=>r && typeof r.label==='string')), 'Invalid reported areas.');
        const resultIds=new Set();
        const questionIds=new Set((Array.isArray(t.sections)?t.sections:[]).flatMap(s=>(Array.isArray(s?.groups)?s.groups:[]).flatMap(g=>(Array.isArray(g?.questions)?g.questions:[]).map(q=>q?.id))));
        for (const r of Array.isArray(a.questionResults)?a.questionResults:[]) {
          check(r && questionIds.has(r.questionId) && !resultIds.has(r.questionId) && ['Correct','Incorrect','Unanswered'].includes(r.outcome) && Number.isFinite(r.timeSeconds) && r.timeSeconds>=0,'Invalid or duplicate source question result.');
          if(r) resultIds.add(r.questionId);
        }
        check(a.percentileMapper===undefined || (Array.isArray(a.percentileMapper) && a.percentileMapper.every(r=>r && Number.isFinite(r.percentile) && r.percentile>=0 && r.percentile<=100 && Number.isFinite(r.score) && (ORDER.includes(r.section)||r.section==='Overall'))), 'Invalid source percentile mapper.');
        check(a.sectionScores===undefined || (Array.isArray(a.sectionScores) && a.sectionScores.every(r=>r && ORDER.includes(r.section) && Number.isFinite(r.score) && Number.isFinite(r.percentile) && r.percentile>=0 && r.percentile<=100)), 'Invalid source section scores.');
      }
    }
    if (errors.length) throw new Error(errors.join('\n'));
    t.sections.sort((a, b) => ORDER.indexOf(a.code) - ORDER.indexOf(b.code));
    return t;
  }
  function shuffled(items, random = Math.random) {
    const a = [...items];
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  function flatten(section) {
    return section.groups.flatMap(g => g.questions.map(q => ({ ...q, groupId: g.id, groupTitle: g.title, stimulus: g.stimulus || '', groupAssets: g.assetIds || [] })));
  }
  function extractSection(test, code, id, title) {
    const source = validate(test), section = source.sections.find(s => s.code === code);
    if (!section) throw new Error('The source test does not contain ' + code + '.');
    const result = { schemaVersion: 1, testType: 'sectional', id, revision: 1,
      title: title || source.title + ' · ' + code,
      description: code + ' extracted from ' + source.title + ' (revision ' + source.revision + '). Shared sets and answer keys are preserved.',
      sections: [section] };
    if (source.demo) result.demo = true;
    const refs = new Set(section.groups.flatMap(g => [...(g.assetIds || []), ...g.questions.flatMap(q => q.assetIds || [])]));
    if (refs.size) result.assets = Object.fromEntries([...refs].map(key => [key, source.assets[key]]));
    // Whole-mock source percentiles/results do not describe this newly separated test.
    return validate(result);
  }
  function createAttempt(test, options, now, id) {
    const snapshot = validate(test);
    if (!['full', 'sectional'].includes(options.mode)) throw new Error('Choose sectional or full mode.');
    if (options.mode === 'full' && !ORDER.every(code => snapshot.sections.some(s => s.code === code))) throw new Error('A full mock requires VARC, DILR and QA.');
    snapshot.sections = snapshot.sections.filter(s => options.mode === 'full' || s.code === options.section);
    snapshot.testType = options.mode;
    delete snapshot.sourceAnalysis;
    if (!snapshot.sections.length) throw new Error('No questions in the selected section.');
    if (options.shuffle) for (const s of snapshot.sections) s.groups = shuffled(s.groups);
    return { id, testId: test.id, testRevision: test.revision, title: test.title, snapshot, mode: options.mode,
      startedAt: now, lastWall: now, durationMs: 2400000, status: 'active', sectionIndex: 0, current: 0,
      shuffled: !!options.shuffle, responses: {}, events: [], timing: {}, clockWarning: false };
  }
  function pause(a, wall) {
    if (a.status !== 'active' || a.pausedAt != null) return;
    advance(a, wall);
    if (a.status === 'active') a.pausedAt = a.lastWall;
  }
  function resume(a, wall) {
    if (a.status !== 'active' || a.pausedAt == null) return;
    const now = Math.max(wall, a.pausedAt);
    a.pausedMs = (a.pausedMs || 0) + now - a.pausedAt;
    a.lastWall = now;
    delete a.pausedAt;
  }
  function advance(a, wall) {
    if (a.pausedAt != null) return false;
    const now = Math.max(wall, a.lastWall || a.startedAt);
    if (wall < (a.lastWall || a.startedAt) - 2000) a.clockWarning = true;
    a.lastWall = now;
    if (a.status !== 'active') return false;
    const index = Math.floor(Math.max(0, now - a.startedAt - (a.pausedMs || 0)) / a.durationMs);
    if (index >= a.snapshot.sections.length) { a.status = 'completed'; a.finishedAt = a.startedAt + (a.pausedMs || 0) + a.durationMs * a.snapshot.sections.length; return true; }
    if (index !== a.sectionIndex) { a.sectionIndex = index; a.current = 0; return true; }
    return false;
  }
  function deadline(a) { return a.startedAt + (a.pausedMs || 0) + (a.sectionIndex + 1) * a.durationMs; }
  function response(a, id) { return a.responses[id] || { saved: null, draft: null, review: false, visited: false, visits: 0, viewedMs: 0, firstVisitMs: 0 }; }
  function visit(a, index, wall) {
    advance(a, wall);
    if (a.status !== 'active') return false;
    const qs = flatten(a.snapshot.sections[a.sectionIndex]);
    if (!qs[index]) return false;
    a.current = index;
    const r = a.responses[qs[index].id] ||= response(a, qs[index].id);
    r.visited = true; r.visits++;
    r.draft = r.saved;
    a.events.push({ at: a.lastWall, type: 'visit', questionId: qs[index].id });
    return true;
  }
  function save(a, id, value, review, wall) {
    const previousSection = a.sectionIndex;
    advance(a, wall);
    if (a.status !== 'active' || previousSection !== a.sectionIndex) return false;
    const q = flatten(a.snapshot.sections[a.sectionIndex]).find(q => q.id === id);
    if (!q || (q.type === 'MCQ' && filled(value) && !q.options.some(o => o.id === value))) return false;
    if (q.type === 'TITA' && filled(value) && !/^-?\d+(\.\d+)?$/.test(String(value).trim())) throw new Error('Enter a number for TITA.');
    const r = a.responses[id] ||= response(a, id);
    const clean = filled(value) ? String(value).trim() : null;
    a.events.push({ at: a.lastWall, type: 'save', questionId: id, previous: r.saved, value: clean, review: !!review });
    r.saved = clean; r.draft = clean; r.review = !!review; r.visited = true;
    return true;
  }
  function status(r) { return r.review ? (filled(r.saved) ? 'answered-review' : 'review') : filled(r.saved) ? 'answered' : r.visited ? 'unanswered' : 'unvisited'; }
  function verdict(q, r) {
    if (!filled(r.saved)) return { outcome: 'Unanswered', score: 0 };
    const correct = q.type === 'MCQ' ? q.answer === r.saved : q.answer.some(v => Number(v) === Number(r.saved));
    return { outcome: correct ? 'Correct' : 'Incorrect', score: correct ? 3 : q.type === 'MCQ' ? -1 : 0 };
  }
  function report(a) {
    const rows = a.snapshot.sections.flatMap(s => flatten(s).map(q => ({ ...q, section: s.code, ...response(a, q.id), ...verdict(q, response(a, q.id)) })));
    const summarize = values => {
      const correct = values.filter(r => r.outcome === 'Correct').length, attempted = values.filter(r => r.outcome !== 'Unanswered').length;
      return { count: values.length, score: values.reduce((sum, r) => sum + r.score, 0), correct, attempted,
        incorrect: attempted - correct, accuracy: attempted ? Math.round(correct / attempted * 100) : 0, viewedMs: values.reduce((sum, r) => sum + r.viewedMs, 0) };
    };
    return { rows, ...summarize(rows), sections: a.snapshot.sections.map(s => ({ code: s.code, ...summarize(rows.filter(r => r.section === s.code)) })) };
  }
  function validateAttempt(input) {
    const a = copy(input);
    const bad = () => { throw new Error('Invalid attempt in backup.'); };
    if (!a || typeof a !== 'object') bad();
    a.snapshot = validate(a.snapshot);
    if (typeof a.id !== 'string' || !a.id || typeof a.title !== 'string' || typeof a.testId !== 'string' || !Number.isInteger(a.testRevision) || !['full', 'sectional'].includes(a.mode) || !['active', 'completed', 'abandoned'].includes(a.status) || !Number.isFinite(a.startedAt) || !Number.isFinite(a.lastWall) || a.lastWall < a.startedAt || a.durationMs !== 2400000 || !Number.isInteger(a.sectionIndex) || a.sectionIndex < 0 || a.sectionIndex >= a.snapshot.sections.length || !Number.isInteger(a.current) || !flatten(a.snapshot.sections[a.sectionIndex])[a.current] || !Array.isArray(a.events) || !a.responses || typeof a.responses !== 'object' || Array.isArray(a.responses)) bad();
    if ((a.mode === 'full' && a.snapshot.sections.length !== 3) || (a.mode === 'sectional' && a.snapshot.sections.length !== 1)) bad();
    if (a.pausedMs !== undefined && (!Number.isFinite(a.pausedMs) || a.pausedMs < 0)) bad();
    if (a.pausedAt !== undefined && (a.status !== 'active' || !Number.isFinite(a.pausedAt) || a.pausedAt < a.startedAt || a.pausedAt !== a.lastWall)) bad();
    if (a.status !== 'active' && (!Number.isFinite(a.finishedAt) || a.finishedAt < a.startedAt)) bad();
    const questions = a.snapshot.sections.flatMap(flatten);
    for (const [id, r] of Object.entries(a.responses)) {
      const q = questions.find(q => q.id === id);
      if (!q || !r || typeof r !== 'object' || !Number.isFinite(r.viewedMs) || r.viewedMs < 0 || !Number.isFinite(r.firstVisitMs) || r.firstVisitMs < 0 || r.firstVisitMs > r.viewedMs || !Number.isInteger(r.visits) || r.visits < 0 || typeof r.visited !== 'boolean' || typeof r.review !== 'boolean') bad();
      if (r.saved !== null && (typeof r.saved !== 'string' || (q.type === 'MCQ' ? !q.options.some(o => o.id === r.saved) : !/^-?\d+(\.\d+)?$/.test(r.saved)))) bad();
      if (r.draft !== null && typeof r.draft !== 'string') bad();
    }
    for (const e of a.events) if (!e || !Number.isFinite(e.at) || e.at < a.startedAt || typeof e.type !== 'string' || typeof e.questionId !== 'string') bad();
    return a;
  }
  return { ORDER, copy, filled, validate, validateAttempt, shuffled, flatten, extractSection, createAttempt, pause, resume, advance, deadline, response, visit, save, status, verdict, report };
});
