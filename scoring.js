// scoring.js — the offline (non-AI) marking engine.
//
// Extracted from index.html on 2026-09-07 so it can be unit-tested. Everything
// here is PURE: no DOM, no fetch, no app globals. The rendering that wraps these
// results (buildKeywordFeedback / buildPartFeedback) stays in index.html, because
// it builds HTML and reads `currentSubjectKey`.
//
// ⚠️ Loaded as a CLASSIC script, deliberately:
//     <script src="/scoring.js"></script>   before index.html's inline script
// Classic scripts execute synchronously in document order, so every function
// below is defined before the inline script runs. A `type="module"` script is
// DEFERRED and would run *after* it, which would be a real load-order hazard for
// no benefit — there is no build step in this project.
//
// Node loads this same file through `vm` (see tests/scoring.test.js), so the
// tests exercise exactly the bytes the browser gets.

(function (root) {
  'use strict';

  // ── KEYWORD HIT — stem matching ──────────────────────────────────────
  // Handles word variations: "slow" matches "slower", "loading" matches "loads"
  //
  // ⚠️ `\W` is ASCII-only in JavaScript and Unicode-aware in Python. Any script
  // that mirrors this matcher must split on ASCII only, or it credits keywords
  // the engine never would (this cost two bad questions on the Maths Advanced
  // per-part build — see docs/HISTORY.md 2026-09-05).
  //
  // ⚠️ The `kw.startsWith(word)` branch makes SHORT keywords very loose: the bare
  // digit "2" credits the keyword "2670", and "pi" credits "pipe". Known and
  // documented, not fixed here — changing it would move marks on live questions.
  function keywordHit(kw, sa) {
    // Direct substring (catches multi-word keywords like "file size")
    if (sa.includes(kw)) return true;
    // Word-level stem matching — split student answer into words
    const words = sa.split(/\W+/);
    for (const word of words) {
      if (!word) continue;
      // One starts with the other (plural/suffix: slow→slower, load→loading/loads)
      if (word.startsWith(kw) || kw.startsWith(word)) return true;
      // Shared 4-char stem (load/loading/loads all share "load")
      const stemLen = Math.min(4, word.length, kw.length);
      if (stemLen >= 4 && word.substring(0, stemLen) === kw.substring(0, stemLen)) return true;
    }
    return false;
  }

  // A NESA question printed with lettered parts, each with its own answer space
  // and its own marks, is ONE bank entry (CLAUDE.md §10 rule 9) but is answered
  // and marked part by part. A question opts in purely by carrying `parts[]`.
  function isMultiPart(q) {
    return Array.isArray(q?.parts) && q.parts.length > 1;
  }

  // An `anyOf` question has no flat `keywords` list, but the AI marker still wants
  // the concepts. Flatten every alternative — the model reads the question stem,
  // which is where the "list TWO" instruction lives. Returns null (not []) so the
  // callers' `||` chains fall through to the next mechanism.
  function anyOfConcepts(anyOf) {
    const blocks = Array.isArray(anyOf) ? anyOf : (anyOf ? [anyOf] : null);
    if (!blocks) return null;
    const out = blocks.flatMap(b => (b && Array.isArray(b.groups)) ? b.groups.flat() : []);
    return out.length ? out : null;
  }
  function hasAnyOf(o) {
    return !!(o && anyOfConcepts(o.anyOf));
  }
  function hasScoringData(q) {
    return !!(q && (q.keywords || q.acceptableAnswers || hasAnyOf(q)));
  }

  // Scores one answer against one set of expectations. This is the single
  // implementation of the offline (non-AI) marking formula — buildKeywordFeedback()
  // calls it for a whole question, and the per-part renderer calls it per part, so
  // the two can never drift.
  //
  // Precedence: acceptableAnswers → anyOf → keywords. A question carries one
  // mechanism; the order is what keeps `anyOf` additive (CLAUDE.md §10 rule 11).
  // An `acceptableAnswers` entry is matched as a substring. That is right for prose
  // ("800 ml", "not independent") and WRONG for a bare number: plain includes() lets
  // the entry "16" match inside "116" and "160 hours", so a wrong answer takes full
  // marks — and because acceptableAnswers short-circuits scoreOne(), it takes ALL of
  // them. Measured on the live bank 2026-09-07: all 11 short numeric entries were
  // exploitable that way (e.g. 2025 Q24 answer "4", student "14" → 2/2).
  //
  // So a NUMERIC entry must land on a number boundary. Two asymmetric rules, both
  // arrived at by probing real answers rather than by reasoning:
  //   • a digit before, or a decimal point that is itself preceded by a digit,
  //     means the entry is a fragment of a bigger number  → "38" inside "0.38"
  //   • only a bare digit after blocks                    → "16" inside "160"
  // A decimal point AFTER is extra precision, not a different number: the entry
  // "$37 158" is a legitimate prefix of the answer "$37 158.72". Requiring a
  // boundary there regressed three real questions, which is how that was found.
  // The guard keys off the entry's own EDGES, not off whether it contains letters:
  // "x = 38" ends in a digit and so must not match inside "x = 380", while
  // "800 ml" ends in a letter and needs no check on that side.
  function acceptableHit(a, sa) {
    const startsDigit = /^\d/.test(a), endsDigit = /\d$/.test(a);
    if (!startsDigit && !endsDigit) return sa.includes(a);
    let i = -1;
    while ((i = sa.indexOf(a, i + 1)) !== -1) {
      const before = sa[i - 1], after = sa[i + a.length];
      const blockedBefore = startsDigit && before !== undefined &&
        (/\d/.test(before) || (before === '.' && /\d/.test(sa[i - 2] || '')));
      const blockedAfter = endsDigit && after !== undefined && /\d/.test(after);
      if (!blockedBefore && !blockedAfter) return true;
    }
    return false;
  }

  function scoreOne(spec, studentAns) {
    const sa = String(studentAns || '').toLowerCase();
    const maxMark = spec.maxMark || 0;
    if (spec.acceptableAnswers && spec.acceptableAnswers.length) {
      const correct = spec.acceptableAnswers.some(a => acceptableHit(a.toLowerCase(), sa));
      return {
        kind: 'acceptable', correct, maxMark,
        marksEarned: correct ? maxMark : 0,
        tier: correct ? 'full' : 'minimal',
        kwResults: [], matched: 0, percentage: correct ? 100 : 0,
      };
    }
    // "any N of these M items" — the shape a `list TWO items of PPE` question
    // actually has. The proportional keyword formula below cannot express it: a
    // correct two-item answer matches 2 of 9 alternatives and scores
    // round(2/9 x marks), which is 0 on a 2-mark question.
    //
    // `anyOf` is an ARRAY of requirement blocks, because one pool is not always
    // enough: "identify ONE advantage and ONE disadvantage" is two pools of one,
    // and a single pool would pay full marks for two advantages. Within a block
    // each GROUP is one creditable item and its entries are synonyms for that
    // item, so a group counts at most once. Each block's hits are capped at its
    // own `required`, so naming more than asked is neither rewarded nor punished,
    // and over-supplying one pool can never cover a missing other.
    const blocks = Array.isArray(spec.anyOf) ? spec.anyOf : (spec.anyOf ? [spec.anyOf] : null);
    if (blocks && blocks.length && maxMark > 0) {
      const kwResults = [];
      let totalRequired = 0, credited = 0;
      blocks.forEach(block => {
        const groups = (block && Array.isArray(block.groups)) ? block.groups : [];
        if (!groups.length) return;
        const required = Math.max(1, Math.min(Number(block.required) || 1, groups.length));
        totalRequired += required;
        let hits = 0;
        groups.forEach(group => {
          const hit = group.some(alt => keywordHit(String(alt).toLowerCase(), sa));
          if (hit) hits++;
          kwResults.push({ label: (block.label ? block.label + ': ' : '') + group[0], hit });
        });
        credited += Math.min(hits, required);
      });
      if (totalRequired > 0) {
        const marksEarned = Math.round((credited / totalRequired) * maxMark);
        const tier = marksEarned >= maxMark * 0.7 ? 'full' : marksEarned > 0 ? 'partial' : 'minimal';
        return {
          kind: 'anyOf', maxMark, marksEarned, tier, kwResults,
          matched: credited, required: totalRequired,
          percentage: Math.round((credited / totalRequired) * 100),
        };
      }
    }
    const keywords = spec.keywords || [];
    if (!keywords.length || maxMark <= 0) return null;
    const minKw = spec.minKeywords || Math.ceil(keywords.length / 2);
    const kwResults = keywords.map(kw => ({ label: kw, hit: keywordHit(kw.toLowerCase(), sa) }));
    const matched = kwResults.filter(r => r.hit).length;
    let marksEarned = Math.round((matched / keywords.length) * maxMark);
    if (matched < minKw) marksEarned = Math.min(marksEarned, Math.floor(maxMark / 2));
    const tier = marksEarned >= maxMark * 0.7 ? 'full' : marksEarned > 0 ? 'partial' : 'minimal';
    return {
      kind: 'keywords', maxMark, marksEarned, tier, kwResults, matched,
      percentage: Math.round((matched / keywords.length) * 100),
    };
  }

  // Default wording when a part carries no NESA-derived bandDescriptors.
  const GENERIC_BAND = {
    full: 'Excellent — demonstrates detailed knowledge with key terminology.',
    partial: 'Good — solid understanding, could include more specific detail.',
    minimal: 'Developing — key concepts partially covered, review the model answer.',
  };
  function bandTextFor(spec, tier) {
    return (spec.bandDescriptors && spec.bandDescriptors[tier]) || GENERIC_BAND[tier];
  }

  // Offline (no-AI) marking of a whole multi-part question: score each part
  // against its OWN keywords and marks, then total. This is what makes a per-part
  // mark real rather than cosmetic.
  function scoreAllParts(q, ansObj) {
    const rows = q.parts.map(p => {
      const studentAns = (ansObj && ansObj[p.label]) || '';
      const spec = {
        maxMark: p.marks, keywords: p.keywords, minKeywords: p.minKeywords,
        acceptableAnswers: p.acceptableAnswers, anyOf: p.anyOf,
        bandDescriptors: p.bandDescriptors,
      };
      const attempted = String(studentAns).trim() !== '';
      const res = attempted ? scoreOne(spec, studentAns) : null;
      return {
        part: p, studentAns, attempted,
        marksEarned: res ? res.marksEarned : 0,
        tier: res ? res.tier : 'minimal',
        note: attempted
          ? (res ? bandTextFor(spec, res.tier) : '')
          : 'Not attempted — this part scores 0.',
      };
    });
    return {
      rows,
      marksEarned: rows.reduce((t, r) => t + r.marksEarned, 0),
      maxMark: q.parts.reduce((t, p) => t + p.marks, 0),
    };
  }

  const api = {
    keywordHit, isMultiPart, anyOfConcepts, hasAnyOf, hasScoringData,
    scoreOne, GENERIC_BAND, bandTextFor, scoreAllParts,
  };

  // Browser: define them as globals, exactly as the inline script expects.
  Object.assign(root, api);
  // Node (via vm, with a `module` shim in the context): hand back the same object.
  if (typeof module !== 'undefined' && module && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
