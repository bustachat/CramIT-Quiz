/**
 * Mechanical pre-conditions for committing a written-answer review ledger.
 *
 * Both checks drive the REAL engine (scoring.js, the exact bytes the browser is
 * served) rather than a re-implementation. Every past session that mirrored
 * keywordHit() in Python got a MORE PERMISSIVE matcher and passed questions the
 * engine then failed (docs/HISTORY.md 2026-09-05, 2026-09-06).
 *
 *   (a) SELF-SCORE  — does every question/part score FULL marks when fed its own
 *                     model answer? If not, a student writing the bank's own
 *                     answer is marked down.
 *   (c) DECOY      — what does a fluent but CONTENT-FREE student answer score? This
 *                     is the check that found Standard 2's four full-marks-for-nothing
 *                     questions (2026-09-07): a critical path split into single-letter
 *                     keywords, an acceptableAnswers list leaking another part's bare
 *                     '5', a lone keyword `increase` credited by the word "in", and a
 *                     regex stored as a keyword. Neither (a) nor (b) can see any of them.
 *                     ⚠️ Read its output, do not batch-apply it: most hits are the
 *                     documented kw.startsWith(word) engine looseness paying ONE mark out
 *                     of a long list, which is inherent to a proportional grid. The
 *                     content defects are the ones whose cause is in the data.
 *
 *   (b) THRESHOLD   — what does the engine award at the question's own
 *                     `minKeywords`? round(min/n x marks) == 0 means the question
 *                     scores ZERO for an answer it itself calls sufficient.
 *                     Exactly one of Multimedia's 35 failed this and no other
 *                     gate could see it (CLAUDE.md, 2026-09-06).
 *
 * Usage: node scripts/review_checks.cjs <subject-id> [--year YYYY]
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const REPO = path.dirname(__dirname);

// Load the real engine. scoring.js is a classic script and the repo is ESM
// ("type": "module"), so it goes through vm with a module shim — the same way
// tests/scoring.test.js loads it.
function loadEngine() {
  const src = fs.readFileSync(path.join(REPO, 'scoring.js'), 'utf8');
  const sandbox = { module: { exports: {} } };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, { filename: 'scoring.js' });
  return sandbox.module.exports;
}

/**
 * Strip HTML the way a BROWSER does, not with /<[^>]+>/g.
 *
 * ⚠️ A naive tag regex ate ~500 characters of Maths Advanced 2024 Q30's model
 * answer ("|x| < 1, that is -1 < x < 1") and reported a defect that was purely
 * the measuring instrument (CLAUDE.md, 2026-09-07). The parser only opens a tag
 * when `<` is followed by a letter, `/`, `!` or `?`; anything else is literal
 * text.
 */
function stripHtml(html) {
  let out = '';
  const s = String(html || '');
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '<' && i + 1 < s.length && /[A-Za-z/!?]/.test(s[i + 1])) {
      const gt = s.indexOf('>', i);
      if (gt !== -1) { out += ' '; i = gt; continue; }
    }
    out += s[i];
  }
  return out
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ').trim();
}

const E = loadEngine();
const subject = process.argv[2];
if (!subject) { console.error('usage: node scripts/review_checks.cjs <subject-id> [--year YYYY]'); process.exit(2); }
const yi = process.argv.indexOf('--year');
const onlyYear = yi !== -1 ? process.argv[yi + 1] : null;

const bank = JSON.parse(fs.readFileSync(path.join(REPO, 'subjects', subject + '.json'), 'utf8'));
let questions = bank.writtenQuestions;
if (onlyYear) questions = questions.filter(q => String(q.year) === String(onlyYear));

const selfFail = [], threshFail = [], noMech = [], deadKw = [], decoyFail = [];

// Fluent English with no subject content and NO DIGITS.
//
// ⚠️ Digits are excluded deliberately, and that exclusion is the whole design of this
// check. keywordHit()'s kw.startsWith(word) branch means a bare digit credits ANY
// numeric keyword that begins with it -- so a decoy containing "1 + 2 + 3 + ... + 9"
// scores full marks on essentially every numeric maths question. Measured on
// mathematics-standard-2: 167 of 227 question/part rows. That is a real property of
// the engine (documented in scoring.js and CLAUDE.md as deliberately unfixed, because
// changing it would move marks on live questions), but it is NOT a per-question
// content defect, and including such a decoy here would bury the ones that are.
//
// With prose-only decoys the check is sharp: it flagged 4 of 227 rows on Standard 2,
// and 2 of those were questions paying FULL marks for a wrong answer.
const DECOYS = [
  'I am not sure how to answer this question but I will try my best to explain what I think.',
  'The answer depends on the information given in the diagram above and the method used.',
  'you write down the working and then find the final result carefully',
];

/**
 * Spec for a whole question with no parts[].
 *
 * ⚠️ `q.marks || q.maxMark` -- HMS is the schema outlier and stores `maxMark`
 * (docs/porting-playbook.md). Reading `q.marks` alone makes maxMark 0, scoreOne()
 * return null, and this tool report all 40 HMS questions as "no scoring mechanism".
 * That is the tool being wrong, not the bank.
 */
function questionSpec(q) {
  return {
    maxMark: q.marks || q.maxMark, keywords: q.keywords, minKeywords: q.minKeywords,
    acceptableAnswers: q.acceptableAnswers, anyOf: q.anyOf,
    bandDescriptors: q.bandDescriptors,
  };
}

/** HMS carries no year/qNum either, so fall back to something a human can find. */
function label(q, i) {
  return (q.year !== undefined && q.qNum !== undefined)
    ? `${q.year} Q${q.qNum}`
    : `idx${i}${q.topic ? ' [' + q.topic + ']' : ''}`;
}

/** (b) the threshold check — only meaningful on the keyword path. */
function thresholdMark(spec) {
  if (spec.acceptableAnswers && spec.acceptableAnswers.length) return null; // short-circuits
  if (E.hasAnyOf(spec)) return null;                                        // own formula
  const kws = spec.keywords || [];
  if (!kws.length || !spec.maxMark) return null;
  const min = spec.minKeywords || Math.ceil(kws.length / 2);
  return { min, n: kws.length, mark: Math.round((min / kws.length) * spec.maxMark) };
}

questions.forEach((q, qi) => {
  const tag = label(q, qi);
  const units = E.isMultiPart(q)
    ? q.parts.map(p => ({ label: p.label, spec: {
        maxMark: p.marks, keywords: p.keywords, minKeywords: p.minKeywords,
        acceptableAnswers: p.acceptableAnswers, anyOf: p.anyOf,
        bandDescriptors: p.bandDescriptors }, answer: p.answer }))
    : [{ label: '', spec: questionSpec(q), answer: q.answer || q.modelAnswer || q.sampleAnswer }];

  for (const u of units) {
    const name = tag + (u.label ? ' ' + u.label : '');
    if (!E.hasScoringData(u.spec)) { noMech.push(name); continue; }
    const model = stripHtml(u.answer);
    const res = E.scoreOne(u.spec, model);
    if (!res) { noMech.push(name); continue; }
    if (res.marksEarned < u.spec.maxMark) {
      const misses = (res.kwResults || []).filter(r => !r.hit).map(r => r.label);
      selfFail.push(`${name}: ${res.marksEarned}/${u.spec.maxMark} (${res.kind})` +
        (misses.length ? ` — uncredited: ${JSON.stringify(misses)}` : ''));
    } else if (res.kind === 'keywords') {
      // A keyword the model answer itself cannot credit is dead data even when
      // the part still totals full marks.
      const misses = (res.kwResults || []).filter(r => !r.hit).map(r => r.label);
      if (misses.length) deadKw.push(`${name}: uncredited from own answer ${JSON.stringify(misses)}`);
    }
    let worst = 0, via = '';
    for (const d of DECOYS) {
      const r = E.scoreOne(u.spec, d.toLowerCase());
      if (r && r.marksEarned > worst) { worst = r.marksEarned; via = d; }
    }
    if (worst >= Math.max(1, u.spec.maxMark * 0.5)) {
      decoyFail.push(`${name}: a content-free answer scores ${worst}/${u.spec.maxMark} — via "${via.slice(0, 34)}…"`);
    }

    const t = thresholdMark(u.spec);
    if (t && t.mark === 0) {
      threshFail.push(`${name}: minKeywords=${t.min} of ${t.n} on ${u.spec.maxMark} marks → round(${(t.min / t.n).toFixed(2)} × ${u.spec.maxMark}) = 0`);
    }
  }
});

function report(title, list) {
  console.log(`\n${title}: ${list.length}`);
  list.forEach(l => console.log('   ✗ ' + l));
}
console.log(`${subject}${onlyYear ? ' ' + onlyYear : ''}: ${questions.length} written questions`);
report('(a) does NOT score full from its own model answer', selfFail);
report('(b) awards ZERO at its own minKeywords', threshFail);
report('(c) a CONTENT-FREE answer scores >= 50% of the mark', decoyFail);
report('(d) no scoring mechanism at all', noMech);
report('(e) carries a keyword its own model answer cannot credit (scores full anyway)', deadKw);

// (c) is advisory: some of its hits are engine looseness rather than a data defect,
// so it is reported loudly but does not by itself fail the run.
process.exit(selfFail.length || threshFail.length || noMech.length ? 1 : 0);
