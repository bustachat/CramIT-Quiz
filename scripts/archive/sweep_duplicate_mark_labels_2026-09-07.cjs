'use strict';
/**
 * Sweep E — remove a TRAILING "(N marks)" that duplicates the badge the renderer
 * already draws (2026-09-07). Recorded as an open item since 2026-09-01.
 *
 * Scope, decided by what the student actually sees:
 *   • a SINGLE-part question's `q` — this IS the stem on screen, and the pill
 *     above it already reads "3 marks"
 *   • every `parts[].q` prompt — the accordion header already reads
 *     "PART (A) · 2 MARKS"
 *
 * NOT touched: a MULTI-part question's combined `q`. It is not rendered in the
 * quiz at all (the accordion renders `stem` + parts), and it is what the
 * test-mode results breakdown prints, where the per-part mark values are useful
 * context rather than a duplicate.
 *
 * Only a trailing occurrence is removed. A mid-text "(1 mark)" inside a merged
 * (i)/(ii) prompt is load-bearing — it is the only place that sub-part's value
 * appears.
 *
 *   node sweep_e.cjs           report
 *   node sweep_e.cjs --write   apply
 */
const fs = require('fs'), vm = require('vm');
const sb = { module: { exports: {} } }; sb.globalThis = sb;
vm.createContext(sb); vm.runInContext(fs.readFileSync('scoring.js', 'utf8'), sb);
const E = sb.module.exports;

const TRAIL = /(?:\s|&nbsp;|<br\s*\/?>)*(?:<(strong|b|em)>)?(?:\s|&nbsp;)*\(\s*\d+\s*marks?\s*\)(?:\s|&nbsp;)*(?:<\/(?:strong|b|em)>)?(?:\s|&nbsp;|<br\s*\/?>)*$/i;
const SUB = ['mathematics-standard-2', 'mathematics-advanced', 'vet-construction', 'multimedia', 'health-movement-science'];
const WRITE = process.argv.includes('--write');

let stems = 0, prompts = 0, skipped = [];
for (const sid of SUB) {
  const p = 'subjects/' + sid + '.json';
  const raw = fs.readFileSync(p, 'utf8');
  const bank = JSON.parse(raw);
  let touched = 0;
  for (const q of bank.writtenQuestions || []) {
    const isMP = E.isMultiPart(q);
    if (!isMP && TRAIL.test(q.q)) {
      const next = q.q.replace(TRAIL, '');
      if (next.trim().length < 20) { skipped.push(`${sid} ${q.year} Q${q.qNum} (would leave a near-empty stem)`); }
      else { q.q = next; stems++; touched++; }
    }
    for (const pt of q.parts || []) {
      if (pt.q && TRAIL.test(pt.q)) {
        const next = pt.q.replace(TRAIL, '');
        if (next.trim().length < 10) { skipped.push(`${sid} ${q.year} Q${q.qNum}${pt.label} (would leave a near-empty prompt)`); }
        else { pt.q = next; prompts++; touched++; }
      }
    }
  }
  if (WRITE && touched) {
    const out = JSON.stringify(bank, null, 2) + '\n';
    // Guard: this file must round-trip byte-for-byte, or a dump reformats it.
    const check = JSON.stringify(JSON.parse(raw), null, 2) + '\n';
    if (check !== raw) { console.error(`REFUSING to write ${sid}: it does not round-trip through json.dumps`); process.exit(1); }
    fs.writeFileSync(p, out);
  }
  console.log(`${sid.padEnd(26)} ${touched} trailing "(N marks)" removed`);
}
console.log(`\nsingle-part stems: ${stems}   part prompts: ${prompts}   total: ${stems + prompts}`);
if (skipped.length) { console.log('\nskipped:'); skipped.forEach(x => console.log('   ' + x)); }
if (!WRITE) console.log('\n(report only — pass --write to apply)');
