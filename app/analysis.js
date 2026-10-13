(function(root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./core'));
  else root.CATAnalysis = factory(root.CAT);
})(globalThis, function(CAT) {
  'use strict';
  const round = n => Math.round(n * 100) / 100;
  function summarize(rows) {
    const count = rows.length, correct = rows.filter(q => q.outcome === 'Correct').length;
    const incorrect = rows.filter(q => q.outcome === 'Incorrect').length, attempted = correct + incorrect;
    const score = rows.reduce((n,q) => n + q.score, 0), viewedMs = rows.reduce((n,q) => n + q.viewedMs, 0);
    return { count, correct, incorrect, attempted, skipped: count-attempted, score, viewedMs,
      accuracy: attempted ? round(correct/attempted*100) : null,
      marksPerMinute: viewedMs > 0 ? round(score/(viewedMs/60000)) : null,
      timePerAttemptMs: attempted ? viewedMs/attempted : null };
  }
  function compatible(q, ref) {
    return ref && q.id === ref.id && q.prompt === ref.prompt && q.type === ref.type && q.stimulus === ref.stimulus &&
      JSON.stringify(q.options) === JSON.stringify(ref.options) && JSON.stringify(q.answer) === JSON.stringify(ref.answer);
  }
  function area(q) {
    if (q.area) return q.area;
    if (q.section === 'VARC') return /reading comprehension/i.test(q.topic || '') || q.stimulus ? 'Reading Comprehension' : 'Verbal Reasoning';
    return q.topic || 'Unclassified';
  }
  function build(attempt, test, source = false) {
    const snapshot = source ? test : attempt.snapshot;
    let rows;
    if (source) {
      const results = new Map((test.sourceAnalysis?.questionResults || []).map(r => [r.questionId,r]));
      rows = test.sections.flatMap(s => CAT.flatten(s).map(q => {
        const result = results.get(q.id);
        if (!result) return null;
        return { ...q, section:s.code, outcome:result.outcome, score:result.outcome === 'Correct' ? 3 : result.outcome === 'Incorrect' && q.type === 'MCQ' ? -1 : 0, viewedMs:result.timeSeconds*1000, saved:null, sourceResult:true, visits:null, firstVisitMs:null };
      })).filter(Boolean);
    } else {
      rows = CAT.report(attempt).rows;
      // Add reference metadata only to identical questions; never rewrite an attempt or its score.
      const refs = new Map((test?.id === attempt.testId ? test.sections : []).flatMap(s => CAT.flatten(s).map(q => [s.code+'|'+q.id,q])));
      rows = rows.map(q => { const ref = refs.get(q.section+'|'+q.id); return compatible(q,ref) ? { ...q, area:q.area || ref.area, selectionCategory:q.selectionCategory || ref.selectionCategory, benchmark:q.benchmark || ref.benchmark } : q; });
    }
    rows = rows.map((q,i) => ({ ...q, displayNumber:i+1, area:area(q), selectionCategory:q.selectionCategory || 'Unclassified' }));
    const groups = [{key:'overall',label:'Overall',depth:0,rows}];
    for (const s of snapshot.sections) {
      const selected = rows.filter(q => q.section === s.code);
      if (source && !selected.length) continue;
      groups.push({key:s.code,label:s.code,depth:1,rows:selected});
      for (const label of new Set(selected.map(q => q.area))) groups.push({key:s.code+'|'+label,label,section:s.code,depth:2,rows:selected.filter(q => q.area === label)});
    }
    const categoryOrder = ['A','B','C','Unclassified'];
    const categories = categoryOrder.filter(c => rows.some(q => q.selectionCategory === c));
    const areas = groups.map(g => ({...g, ...summarize(g.rows)}));
    const sets = snapshot.sections.flatMap(s => s.groups.filter(g => g.questions.length>1).map(g => {
      const selected = rows.filter(q => q.section===s.code && q.groupId===g.id);
      const complete = selected.length===g.questions.length && selected.every(q => Number.isFinite(q.benchmark?.topperTimeSeconds));
      return {id:g.id,section:s.code,title:g.title,...summarize(selected),topperTimeMs:complete ? selected.reduce((n,q)=>n+q.benchmark.topperTimeSeconds*1000,0) : null};
    }));
    const totalQuestions = snapshot.sections.reduce((n,s)=>n+CAT.flatten(s).length,0);
    return {source, snapshot, rows, ...summarize(rows), areas, sets:source?sets.filter(s=>s.count):sets, categories,
      totalQuestions, partialSource:source && rows.length<totalQuestions,
      selection:groups.map(g=>({...g, cells:categories.map(c=>({category:c,...summarize(g.rows.filter(q=>q.selectionCategory===c))}))})),
      sourceAnalysis:source ? test.sourceAnalysis : null,
      benchmarkAvailable:rows.some(q=>q.benchmark), pValueAvailable:rows.some(q=>Number.isFinite(q.benchmark?.topperPValue))};
  }
  return {build,summarize,compatible};
});
