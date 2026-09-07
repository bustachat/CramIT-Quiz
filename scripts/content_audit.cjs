/**
 * EVERY known content check, across EVERY subject, in one run.
 *
 * WHY THIS EXISTS. Each check below was invented by some past session, run once
 * on one subject, and then never run again anywhere else — so every session
 * "fixed everything" and the next one found more. This runs the lot, everywhere,
 * so the total is knowable in one command instead of one class at a time.
 *
 *     node scripts/content_audit.cjs            all subjects
 *     node scripts/content_audit.cjs --strict    exit 1 on MARK-AFFECTING or UNANSWERABLE
 *
 * --strict is what CI runs (.github/workflows/validate.yml, since 2026-09-07).
 * Before that the workflow ran the bare command, so the audit reported a
 * marking defect and went green anyway.
 *
 * Engine-driven checks load the REAL scoring.js through node:vm — never a
 * re-implementation, which has come out more permissive than the engine every
 * single time it has been tried (docs/HISTORY.md 2026-09-05, 2026-09-06).
 *
 * ⚠️ NOT every finding is a defect, and the report says which is which. Four
 * classes are known to produce false positives and are reported for reading,
 * never for fixing in bulk:
 *   G_regex_kw        maths notation like "(x + 4)(x − 1)" is not a regex
 *   P_missing_picture a part with a declared omittedParts and a visible note is correct
 *   M_scratch_work    "he needed to wait 57 minutes" is legitimate prose
 *   T_leaked_numeric_kw a flagged keyword may still be earning real credit —
 *                     2020 Q11(b) in Maths Advanced measured 2/2 → 1/2 when its
 *                     flagged keyword was dropped. Probe before removing.
 *
 * ADDING A CHECK. The house rule, learned the hard way and applied to T/U/V
 * below: a new check is not trusted until it has been run repo-wide, every hit
 * READ, and its false-positive classes written down here beside it. Three of
 * the checks above turned out to be the instrument rather than the data, and
 * T's first two hits were both false (a coordinate pair, not a leak). Prove a
 * new check BOTH ways — that it reports zero on clean data, and that it fires
 * when the defect it was written for is put back.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const REPO = process.cwd();
const src = fs.readFileSync(path.join(REPO, 'scoring.js'), 'utf8');
const sb = { module: { exports: {} } }; sb.globalThis = sb;
vm.createContext(sb); vm.runInContext(src, sb, { filename: 'scoring.js' });
const E = sb.module.exports;

const SUBJECTS = ['mathematics-standard-2', 'mathematics-advanced', 'vet-construction',
                  'multimedia', 'health-movement-science'];

// Only these move a student's mark. The rest are quality/consistency reports.
const MARK_AFFECTING = ['A_self_score', 'B_zero_at_threshold', 'C_over_credit',
                        'E_no_mechanism', 'F_single_letter_kw', 'H_short_acceptable',
                        'K_band_undefined', 'Q_part_mark_labels', 'R_dollar_damage'];

// These do not change the arithmetic — they make the question impossible or
// wrong to READ, which is worse. Added 2026-09-07 after 14 Maths Advanced
// questions were found asking about a diagram no student had been shown since
// the per-part build two days earlier. --strict fails on these too.
const UNANSWERABLE = ['U_unreachable_image', 'V_attr_angle_bracket'];

/** Browser-faithful HTML strip (a `<` opens a tag only before a letter, / ! ?). */
function strip(h) {
  let o = '', s = String(h || '');
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '<' && /[A-Za-z/!?]/.test(s[i + 1] || '')) {
      const g = s.indexOf('>', i); if (g !== -1) { o += ' '; i = g; continue; }
    }
    o += s[i];
  }
  return o.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&minus;/g, '−')
          .replace(/&deg;/g, '°').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
          .replace(/\s+/g, ' ').trim();
}

const DECOYS = [
  'I am not sure how to answer this question but I will try my best to explain what I think.',
  'The answer depends on the information given in the diagram above and the method used.',
  'you write down the working and then find the final result carefully',
];

/**
 * Digit-group normalisation, mirroring scoring.js's own `normNum`, so that a
 * keyword stored as "34 140" can be LOCATED inside an answer that writes
 * "34140" and vice versa.
 *
 * ⚠️ This is the one place a mirror of engine behaviour is allowed, and only
 * because it decides nothing: it is used to find a substring's POSITION for the
 * structural check below. Every question about whether a keyword actually
 * matches still goes through the real E.keywordHit.
 */
function nn(s) {
  return String(s).replace(/[−–—‒]/g, '-').replace(/\d[\d ,]*\d/g, m => m.replace(/[ ,]/g, ''));
}
/** Does `k` occur in `t` at a position NOT preceded by a digit? */
function hasCleanHit(k, t) {
  let i = -1;
  while ((i = t.indexOf(k, i + 1)) !== -1) if (!/\d/.test(t[i - 1] || '')) return true;
  return false;
}

const SCRATCH = /(\bwait\b|\bActually[:,]\s|\bno\.\s|From MG\b|Actual MG\b|Using MG\b|\bTODO\b|\bFIXME\b)/i;
const REFS_PICTURE = /\b(the (diagram|graph|network diagram|scatterplot|box-?plot|histogram)|shown (below|on the diagram)|on the grid|from the graph|the following diagram)\b/i;

const F = {};                                    // findings by check id
const add = (k, v) => (F[k] = F[k] || []).push(v);

for (const sid of SUBJECTS) {
  const bank = JSON.parse(fs.readFileSync(path.join(REPO, 'subjects', sid + '.json'), 'utf8'));
  const keyPath = path.join(REPO, 'data', 'answer-key', 'written', sid + '.json');
  const hasKey = fs.existsSync(keyPath);
  const ledgerPath = path.join(REPO, 'data', 'answer-key', 'written', 'reviews', sid + '.json');
  const ledger = fs.existsSync(ledgerPath)
    ? JSON.parse(fs.readFileSync(ledgerPath, 'utf8')) : null;

  let reviewed = 0;
  for (const q of bank.writtenQuestions || []) {
    // HMS is the schema outlier: no year/qNum, and `maxMark` instead of `marks`.
    const tag = (q.year !== undefined && q.qNum !== undefined)
      ? `${sid} ${q.year} Q${q.qNum}`
      : `${sid} idx${(bank.writtenQuestions || []).indexOf(q)}${q.topic ? ' [' + q.topic + ']' : ''}`;
    if (ledger && (ledger.reviews[String(q.year)] || {})[String(q.qNum)]) reviewed++;

    const units = E.isMultiPart(q)
      ? q.parts.map(p => ({ n: ' ' + p.label, spec: {
          maxMark: p.marks, keywords: p.keywords, minKeywords: p.minKeywords,
          acceptableAnswers: p.acceptableAnswers, anyOf: p.anyOf,
          bandDescriptors: p.bandDescriptors }, ans: p.answer, prompt: p.q }))
      : [{ n: '', spec: {
          maxMark: q.marks, keywords: q.keywords, minKeywords: q.minKeywords,
          acceptableAnswers: q.acceptableAnswers, anyOf: q.anyOf,
          bandDescriptors: q.bandDescriptors }, ans: q.answer || q.modelAnswer, prompt: q.q }];

    for (const u of units) {
      const name = tag + u.n;
      const max = u.spec.maxMark || q.marks || q.maxMark || 0;
      u.spec.maxMark = max;

      if (!E.hasScoringData(u.spec)) { add('E_no_mechanism', name); continue; }

      // 1 self-score
      const model = strip(u.ans);
      const r = E.scoreOne(u.spec, model.toLowerCase());
      if (!r || r.marksEarned < max) add('A_self_score', `${name}: ${r ? r.marksEarned : 'null'}/${max}`);
      else if (r.kind === 'keywords') {
        const miss = r.kwResults.filter(x => !x.hit).map(x => x.label);
        if (miss.length) add('D_dead_keyword', `${name}: ${JSON.stringify(miss)}`);
      }

      // 2 zero at own threshold
      const kw = u.spec.keywords || [];
      if (kw.length && !(u.spec.acceptableAnswers || []).length && !E.hasAnyOf(u.spec) && max) {
        const min = u.spec.minKeywords || Math.ceil(kw.length / 2);
        if (Math.round(min / kw.length * max) === 0) add('B_zero_at_threshold', name);
      }

      // 3 over-crediting
      let worst = 0;
      for (const d of DECOYS) { const x = E.scoreOne(u.spec, d.toLowerCase()); if (x && x.marksEarned > worst) worst = x.marksEarned; }
      if (worst >= Math.max(1, max * 0.5)) add('C_over_credit', `${name}: ${worst}/${max}`);

      // 4 loose data shapes
      const letters = kw.filter(k => String(k).trim().length === 1 && /[a-z]/i.test(k));
      if (letters.length) add('F_single_letter_kw', `${name}: ${JSON.stringify(letters)}`);
      // Only a real quantifier counts. "(x + 4)(x − 1)" is maths notation, not a
      // regex — flagging brackets produced 5 false positives and nothing else.
      const rx = kw.filter(k => /\.\*|\.\+/.test(String(k)));
      if (rx.length) add('G_regex_kw', `${name}: ${JSON.stringify(rx)}`);
      // Measure the EXPLOIT, not the shape. Since the acceptableAnswers boundary
      // fix (2026-09-07) a short numeric entry is safe, so a length test only
      // cries wolf. Perturb the accepted value the way a student actually gets it
      // wrong — an order of magnitude out, a stray leading digit, a dropped digit
      // — and score it through the real engine.
      const acc = u.spec.acceptableAnswers || [];
      if (acc.length) {
        const wrongs = new Set();
        for (const a of acc) {
          const m = /^(\D*?)(\d[\d ,]*(?:\.\d+)?)(.*)$/.exec(a);
          if (!m) continue;
          const clean = m[2].replace(/[ ,]/g, '');
          wrongs.add(m[1] + clean + '0' + m[3]);
          wrongs.add(m[1] + '1' + clean + m[3]);
          if (!/\./.test(clean) && clean.length > 1) wrongs.add(m[1] + clean.slice(0, -1) + m[3]);
        }
        const taken = [...wrongs]
          .filter(w => !acc.some(a => a.toLowerCase() === w.toLowerCase()))
          .filter(w => E.scoreOne(u.spec, w.toLowerCase()).marksEarned >= max);
        if (taken.length) add('H_short_acceptable', `${name}: accepts ${JSON.stringify(taken.slice(0, 3))} for ${JSON.stringify(acc)}`);
      }

      // 5 band descriptors
      const bd = u.spec.bandDescriptors;
      if (!bd) add('I_no_band', name);
      else {
        for (const t of ['full', 'partial', 'minimal']) {
          if (bd[t] === undefined) add('J_band_missing_tier', `${name}.${t}`);
          else if (/undefined/.test(String(bd[t]))) add('K_band_undefined', `${name}.${t}`);
        }
        if (/^Does not meet the criterion/i.test(String(bd.partial || ''))) add('L_nonattainment_wording', name);
      }

      // 6 student-facing prose problems
      if (SCRATCH.test(strip(u.ans))) add('M_scratch_work', `${name}: ${strip(u.ans).match(SCRATCH)[0]}`);
      if (/\*\*/.test(String(u.ans))) add('N_raw_markdown', name);
    }

    // question-level text checks
    const qtext = strip(q.q) + ' ' + strip(q.stem || '');
    const blobRaw = (q.q || '') + (q.stem || '') + (q.parts || []).map(p => p.q || '').join('');
    if (/\(\s*\d+\s*marks?\s*\)\s*$/i.test(strip(q.q))) add('O_stem_marks_suffix', tag);
    if (!q.image && !/<img/.test(blobRaw) && !/<table/.test(blobRaw) && REFS_PICTURE.test(qtext))
      add('P_missing_picture', tag);
    if (q.parts && q.parts.length > 1) {
      const labels = [...strip(q.q).matchAll(/\((\d+)\s*marks?\)/gi)].map(m => +m[1]);
      const pm = q.parts.map(p => p.marks);
      if (labels.length === pm.length && String(labels) !== String(pm))
        add('Q_part_mark_labels', `${tag}: q says ${JSON.stringify(labels)} vs parts ${JSON.stringify(pm)}`);
    }
    // $1..$9 damage signature
    for (const [f, t] of [['q', strip(q.q)], ['stem', strip(q.stem || '')], ['answer', strip(q.answer || '')]]) {
      for (const m of t.matchAll(/(?<![\d.,°$])0\d{2,}(?!\d*\s*°)/g)) {
        const pre = t.slice(Math.max(0, m.index - 2), m.index);
        if (/\d\s$/.test(pre)) continue;
        add('R_dollar_damage', `${tag} ${f}: …${t.slice(Math.max(0, m.index - 40), m.index + 12)}…`);
      }
    }

    // 7 sibling-part keyword leak (2026-09-07). A NUMERIC keyword whose every
    // match in its OWN model answer is preceded by a digit is a suffix fragment
    // of a longer number — "83" inside 783.7168 — and is really a neighbouring
    // part's answer copied in.
    //
    // ⚠️ The sibling requirement is load-bearing, not decoration. Without it
    // this fires on artefacts of the engine's own digit-group normalisation:
    // "= 18 3x" normalises to "183x", so the keyword "3x = 19" looks preceded
    // by a digit while being perfectly legitimate. Four such false positives
    // were read and discarded before this rule was settled.
    //
    // ⚠️ It also deliberately says nothing about a keyword with a CLEAN match
    // as well. 2020 Q11(b) in Maths Advanced carries part (c)'s "45" and matches
    // it inside its own "450"; dropping it measured 2/2 → 1/2 on a fully correct
    // working. Reported findings must still be probed before anything is removed.
    if (E.isMultiPart(q)) {
      for (const p of q.parts) {
        for (const k of (p.keywords || [])) {
          if (!/^\d/.test(String(k))) continue;
          const kn = nn(String(k).toLowerCase());
          const ownRaw = strip(p.answer).toLowerCase();
          const own = nn(ownRaw);
          if (!own.includes(kn)) continue;
          // ⚠️ Test the RAW text as well as the normalised one. `nn` treats a
          // comma as a digit-group separator, so a coordinate pair "(5, 4977)"
          // normalises to "54977" and makes a perfectly legitimate value look
          // like it is buried inside a longer number. Both of this check's first
          // two hits were exactly that, and both were false. A value that reads
          // cleanly in either form is not a fragment.
          if (hasCleanHit(kn, own) || hasCleanHit(String(k).toLowerCase(), ownRaw)) continue;
          const sibs = q.parts.filter(o => o !== p && hasCleanHit(kn, nn(strip(o.answer).toLowerCase())));
          if (sibs.length) {
            add('T_leaked_numeric_kw',
                `${tag} ${p.label}: '${k}' matches only inside a longer number here; ` +
                `belongs to part ${sibs.map(o => o.label).join('/')}`);
          }
        }
      }
    }

    // 8 a stimulus the accordion can never draw (2026-09-07). A multi-part
    // question renders as `stem` + each part's own prompt; the combined `q` is
    // NOT rendered in the quiz — it feeds CI and the test-mode results
    // breakdown. So an <img> that lives only in `q` reaches no student.
    //
    // This is the shape the per-part build left behind on 14 Maths Advanced
    // questions: it copied the intro TEXT out of `q` into `stem` and left the
    // picture. Nothing static noticed for two days, because every file existed
    // and every path resolved.
    //
    // ⚠️ `parts[].intro` counts. A first version of this check reported VET as
    // broken because it only looked at `parts[].q`.
    if (E.isMultiPart(q)) {
      const nImg = s => (String(s || '').match(/<img\b/g) || []).length;
      const inParts = q.parts.reduce((n, p) => n + nImg(p.q) + nImg(p.intro), 0);
      if (nImg(q.q) && !nImg(q.stem) && !inParts) {
        add('U_unreachable_image', `${tag}: ${nImg(q.q)} image(s) in \`q\` only — the accordion never draws \`q\``);
      }
    }
  }

  // 9 an angle bracket inside a quoted attribute value (2026-09-07). A bare '>'
  // there still closes the tag, so the parser ends the element early and the
  // rest of the attribute renders as visible text. Found once repo-wide, in an
  // img alt reading `alt="Graph of y = c ln x for c > 0, …"`.
  //
  // Detected by parsing the way a browser does rather than by a regex over the
  // attribute: if the span from '<' to the first '>' contains an ODD number of
  // double quotes, that '>' landed inside a quoted value.
  for (const arr of ['writtenQuestions', 'mcQuestions']) {
    (bank[arr] || []).forEach((q, i) => {
      const tag = (q.year !== undefined && q.qNum !== undefined)
        ? `${sid} ${q.year} Q${q.qNum}` : `${sid} ${arr} idx${i}`;
      const fields = [['q', q.q], ['stem', q.stem], ['answer', q.answer || q.modelAnswer],
                      ['solution', q.solution]];
      for (const p of q.parts || []) {
        fields.push([`${p.label}.q`, p.q], [`${p.label}.intro`, p.intro], [`${p.label}.answer`, p.answer]);
      }
      for (const [f, v] of fields) {
        const s = String(v || '');
        for (let j = 0; j < s.length; j++) {
          if (s[j] !== '<' || !/[A-Za-z]/.test(s[j + 1] || '')) continue;
          const g = s.indexOf('>', j);
          if (g === -1) break;
          const quotes = (s.slice(j, g).match(/"/g) || []).length;
          if (quotes % 2 === 1) add('V_attr_angle_bracket', `${tag} ${f}: …${s.slice(j, g + 1).slice(-70)}…`);
          j = g;
        }
      }
    });
  }

  if (ledger) add('S_review_coverage', `${sid}: ${reviewed}/${(bank.writtenQuestions || []).length} reviewed`);
  else add('S_review_coverage', `${sid}: 0/${(bank.writtenQuestions || []).length} — NO LEDGER${hasKey ? '' : ' (no answer key exists)'}`);
}

const TITLES = {
  A_self_score: 'Does not score full marks from its own model answer',
  B_zero_at_threshold: 'Awards ZERO at its own minKeywords',
  C_over_credit: 'A content-free WRONG answer scores >= 50% of the mark',
  D_dead_keyword: 'Carries a keyword its own model answer cannot credit',
  E_no_mechanism: 'No scoring mechanism at all',
  F_single_letter_kw: 'Single-letter keyword (fires on any English text)',
  G_regex_kw: 'A regex quantifier stored as a keyword (never evaluated)',
  H_short_acceptable: 'acceptableAnswers takes FULL marks for a realistically-wrong number',
  I_no_band: 'No bandDescriptors (AI marks against a generic rubric)',
  J_band_missing_tier: 'bandDescriptors missing a tier the engine reads',
  K_band_undefined: 'bandDescriptors text contains the literal word "undefined"',
  L_nonattainment_wording: 'Generated "Does not meet the criterion: …" shown to students',
  M_scratch_work: 'Authoring scratch-work in a student-facing model answer',
  N_raw_markdown: 'Raw ** markdown in a model answer',
  O_stem_marks_suffix: 'Stem ends in a literal "(N marks)" duplicating the badge',
  P_missing_picture: 'Refers to a picture the student is never shown',
  Q_part_mark_labels: 'Stem prints per-part marks that disagree with the key',
  R_dollar_damage: '$1..$9 eaten by a JavaScript String.replace()',
  T_leaked_numeric_kw: "A sibling part's number carried as this part's keyword",
  U_unreachable_image: 'A stimulus image the renderer can never draw',
  V_attr_angle_bracket: 'A bare < or > inside a quoted attribute (closes the tag early)',
  S_review_coverage: 'Written-answer review coverage',
};

const order = Object.keys(TITLES);
const STRICT = process.argv.includes('--strict');
console.log('='.repeat(78));
console.log('FULL CONTENT AUDIT — every known check, all five subjects');
console.log('='.repeat(78));
for (const k of order) {
  const v = F[k] || [];
  console.log(`\n[${k}] ${TITLES[k]} — ${v.length}`);
  const show = k === 'O_stem_marks_suffix' || k === 'L_nonattainment_wording' || k === 'S_review_coverage'
    ? v.slice(0, 8) : v.slice(0, 40);
  show.forEach(x => console.log('    ' + x));
  if (v.length > show.length) console.log(`    … and ${v.length - show.length} more`);
}

const count = ks => ks.reduce((n, k) => n + (F[k] || []).length, 0);
const marky = count(MARK_AFFECTING);
const broken = count(UNANSWERABLE);
console.log('');
console.log('='.repeat(78));
console.log(`MARK-AFFECTING findings: ${marky}   (${MARK_AFFECTING.join(', ')})`);
console.log(`UNANSWERABLE findings:   ${broken}   (${UNANSWERABLE.join(', ')})`);
console.log('Both groups fail --strict. Everything else is a quality or consistency');
console.log('report — read it, do not bulk-fix it.');
console.log('='.repeat(78));
if (STRICT && marky + broken > 0) process.exit(1);
