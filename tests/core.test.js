const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const CAT = require('../app/core');
const sample = JSON.parse(fs.readFileSync('samples/sample-full-mock.json', 'utf8'));
const create = (mode = 'full') => CAT.createAttempt(sample, { mode, section: 'QA' }, 1000, 'attempt');

test('strict full mock has fixed order and three 40-minute windows', () => {
  const a = create(); assert.deepEqual(a.snapshot.sections.map(s => s.code), ['VARC', 'DILR', 'QA']);
  CAT.advance(a, 2400999); assert.equal(a.sectionIndex, 0);
  CAT.advance(a, 2401000); assert.equal(a.sectionIndex, 1); assert.equal(a.current, 0);
  CAT.advance(a, 4801000); assert.equal(a.sectionIndex, 2);
  CAT.advance(a, 7201000); assert.equal(a.status, 'completed'); assert.equal(a.finishedAt, 7201000);
});
test('recovery skips elapsed sections and never restarts their clocks', () => {
  const a = create(); CAT.advance(a, 6001000); assert.equal(a.sectionIndex, 2); assert.equal(CAT.deadline(a), 7201000);
  CAT.advance(a, 9001000); assert.equal(a.finishedAt, 7201000);
});
test('sectional ends at exactly 40 minutes and rejects a boundary response', () => {
  const a = create('sectional'); CAT.visit(a, 0, 1000);
  assert.equal(CAT.save(a, 'demo-q1', 'B', false, 2401000), false); assert.equal(CAT.report(a).score, 0);
});
test('old-section response at transition cannot leak into the next section', () => {
  const a = create(); CAT.visit(a, 0, 1000);
  assert.equal(CAT.save(a, 'demo-v1', 'C', false, 2401000), false); assert.equal(a.sectionIndex, 1);
});
test('scoring: correct, wrong MCQ, wrong TITA, unattempted, reviewed answers', () => {
  const a = create('sectional'); CAT.visit(a, 0, 1000);
  CAT.save(a, 'demo-q1', 'A', false, 2000); assert.equal(CAT.report(a).score, -1);
  CAT.save(a, 'demo-q1', 'B', true, 3000); assert.equal(CAT.status(a.responses['demo-q1']), 'answered-review');
  CAT.save(a, 'demo-q2', '12', false, 4000); assert.equal(CAT.report(a).score, 3);
  CAT.save(a, 'demo-q2', '09.0', false, 5000); assert.equal(CAT.report(a).score, 6);
  assert.equal(CAT.report(a).attempted, 2); assert.equal(CAT.report(a).accuracy, 100);
});
test('drafts are not scored, revisits restore saved responses, clearing removes score', () => {
  const a = create('sectional'); CAT.visit(a, 0, 1000); a.responses['demo-q1'].draft = 'B';
  assert.equal(CAT.report(a).score, 0); CAT.visit(a, 1, 2000); CAT.visit(a, 0, 3000);
  assert.equal(a.responses['demo-q1'].draft, null); assert.equal(a.responses['demo-q1'].visits, 2);
  CAT.save(a, 'demo-q1', 'B', true, 4000); CAT.save(a, 'demo-q1', null, true, 5000);
  assert.equal(CAT.status(a.responses['demo-q1']), 'review'); assert.equal(CAT.report(a).score, 0);
});
test('test snapshot is immutable relative to subsequent source edits', () => {
  const source = CAT.copy(sample), a = CAT.createAttempt(source, { mode: 'full', shuffle: true }, 1000, 'x');
  source.sections[0].groups[0].questions[0].answer = 'A';
  assert.equal(CAT.flatten(a.snapshot.sections[0]).find(q => q.id === 'demo-v1').answer, 'C');
  const ids = CAT.flatten(a.snapshot.sections[0]).map(q => q.id); assert.equal(ids.indexOf('demo-v2') - ids.indexOf('demo-v1'), 1);
});
test('clock reversal never adds time and is flagged', () => { const a = create(); CAT.advance(a, 5000); CAT.advance(a, 1000); assert.equal(a.lastWall, 5000); assert.equal(a.clockWarning, true); });
test('validator rejects invalid keys, duplicate IDs, empty groups and unknown versions', () => {
  for (const mutate of [t => t.schemaVersion = 2, t => t.sections[0].groups = [], t => t.sections[0].groups[0].questions[0].answer = 'Z', t => t.sections[0].groups[0].questions[1].id = 'demo-v1']) {
    const t = CAT.copy(sample); mutate(t); assert.throws(() => CAT.validate(t));
  }
});
test('full mock requires all three sections', () => { const t = CAT.copy(sample); t.sections.pop(); assert.throws(() => CAT.createAttempt(t, { mode: 'full' }, 1000, 'x')); });
test('malformed structures and reserved IDs are rejected safely', () => {
  for (const mutate of [t => t.sections = {}, t => t.sections[0] = null, t => t.sections[0].groups[0].questions[0].id = 'constructor', t => t.sections[0].groups[0].questions[0].options = [null], t => t.sections[0].groups[0].assetIds = 'missing']) {
    const t = CAT.copy(sample); mutate(t); assert.throws(() => CAT.validate(t));
  }
});
test('attempt backup validation preserves deadlines and rejects corrupt responses', () => {
  const a = create(); CAT.visit(a, 0, 1000); CAT.save(a, 'demo-v1', 'C', true, 2000);
  assert.equal(CAT.validateAttempt(a).startedAt, 1000);
  const bad = CAT.copy(a); bad.responses['demo-v1'].saved = 'Z'; assert.throws(() => CAT.validateAttempt(bad));
  const invalid = CAT.copy(a); invalid.sectionIndex = 4; assert.throws(() => CAT.validateAttempt(invalid));
});
test('real ZIP import has 24 unique questions, four intact RC sets, and 4 TITA keys', () => {
  const t = CAT.validate(JSON.parse(fs.readFileSync('samples/varc-section-6.json', 'utf8'))), qs = CAT.flatten(t.sections[0]);
  assert.equal(qs.length, 24); assert.equal(qs.filter(q => q.type === 'TITA').length, 4);
  assert.equal(t.sections[0].groups.filter(g => g.questions.length === 4).length, 4);
  assert.deepEqual(qs.map(q => q.sourceNumber), Array.from({ length: 24 }, (_, i) => i + 1));
  assert.deepEqual(qs.slice(14, 18).map(q => q.answer[0]), ['3', '2', '3421', '1432']);
  for (const q of qs) assert.equal(CAT.verdict(q, { saved: q.type === 'MCQ' ? q.answer : q.answer[0] }).score, 3);
});

test('paused attempts preserve remaining time across long absences and backup restore', () => {
  const a = create();
  CAT.pause(a, 61000);
  const remaining = CAT.deadline(a) - a.pausedAt;
  CAT.advance(a, 9000000);
  assert.equal(a.sectionIndex, 0);
  const restored = CAT.validateAttempt(a);
  CAT.resume(restored, 9000000);
  assert.equal(CAT.deadline(restored) - 9000000, remaining);
  CAT.pause(restored, 9060000);
  CAT.resume(restored, 19000000);
  assert.equal(CAT.deadline(restored) - 19000000, remaining - 60000);
  CAT.advance(restored, CAT.deadline(restored));
  assert.equal(restored.sectionIndex, 1);
});
