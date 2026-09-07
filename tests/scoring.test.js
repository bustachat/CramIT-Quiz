// tests/scoring.test.js
// The offline (non-AI) marking engine, extracted from index.html on 2026-09-07.
//
// It is loaded here through `vm` rather than `import`, so these tests run the
// EXACT bytes the browser is served — no build step, no re-implementation, and
// no chance of the test drifting from the shipped file. scoring.js is a classic
// script (it must be: index.html loads it before an inline script, and a
// `type="module"` tag is deferred), so it hands its API back through a `module`
// shim placed in the vm context.

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SCORING = path.join(HERE, '..', 'scoring.js');

function loadScoring() {
  const ctx = { module: { exports: {} }, console };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(SCORING, 'utf8'), ctx, { filename: 'scoring.js' });
  // NOTE: values that come back are built by the vm realm's constructors, so
  // assert.deepEqual on an array must compare a host-realm copy ([...arr]).
  // That is a realm artifact of loading the real file, not a product quirk.
  return ctx.module.exports;
}

const S = loadScoring();

describe('scoring.js — module contract', () => {
  test('exports every function index.html calls as a global', () => {
    for (const name of ['keywordHit', 'isMultiPart', 'anyOfConcepts', 'hasAnyOf',
                        'hasScoringData', 'scoreOne', 'bandTextFor', 'scoreAllParts']) {
      assert.equal(typeof S[name], 'function', `${name} missing`);
    }
    assert.equal(typeof S.GENERIC_BAND, 'object');
  });

  test('is loadable as a classic script — no import/export syntax', () => {
    const src = fs.readFileSync(SCORING, 'utf8');
    assert.ok(!/^\s*export\s/m.test(src), 'scoring.js must not use `export` (it is a classic script)');
    assert.ok(!/^\s*import\s/m.test(src), 'scoring.js must not use `import`');
  });

  test('index.html loads it BEFORE its own inline script', () => {
    const html = fs.readFileSync(path.join(HERE, '..', 'index.html'), 'utf8');
    const tag = html.indexOf('<script src="/scoring.js">');
    const inline = html.indexOf('<script>');
    assert.ok(tag !== -1, 'index.html does not load /scoring.js');
    assert.ok(tag < inline, 'scoring.js must be loaded before the inline script');
    assert.ok(!/<script[^>]+src="\/scoring\.js"[^>]*type="module"/.test(html),
      'scoring.js must NOT be type="module" — deferred execution would run it after the inline script');
  });
});

describe('keywordHit', () => {
  test('direct substring, including multi-word keywords', () => {
    assert.equal(S.keywordHit('file size', 'it increases the file size a lot'), true);
    assert.equal(S.keywordHit('file size', 'it gets bigger'), false);
  });

  test('suffix and shared-stem matching', () => {
    assert.equal(S.keywordHit('slow', 'the page is slower'), true);
    assert.equal(S.keywordHit('load', 'it keeps loading'), true);
    assert.equal(S.keywordHit('call to action', 'add calls to action'), true, '4-char shared stem');
  });

  test('short keywords are LOOSE — documented, not a bug', () => {
    // kw.startsWith(word): the bare digit "2" credits "2670".
    assert.equal(S.keywordHit('2670', 'the answer is 2 dollars'), true);
    assert.equal(S.keywordHit('pi', 'lay the pipe'), true);
  });

  test('does not match across an unrelated word', () => {
    assert.equal(S.keywordHit('mitochondria', 'the heart pumps blood'), false);
  });
});

describe('scoreOne — acceptableAnswers', () => {
  const spec = { maxMark: 1, acceptableAnswers: ['rtsp', 'real time streaming protocol'] };
  test('any one match is full marks; anything else is zero', () => {
    assert.equal(S.scoreOne(spec, 'RTSP').marksEarned, 1);
    assert.equal(S.scoreOne(spec, 'Real Time Streaming Protocol').marksEarned, 1);
    assert.equal(S.scoreOne(spec, 'something else').marksEarned, 0);
  });
  test('short-circuits before keywords — keywords beside it are dead data', () => {
    const both = { maxMark: 1, acceptableAnswers: ['rtsp'], keywords: ['never', 'reached'] };
    const res = S.scoreOne(both, 'rtsp');
    assert.equal(res.kind, 'acceptable');
    assert.equal(res.kwResults.length, 0);
  });

  // ── Numeric entries must land on a NUMBER BOUNDARY (added 2026-09-07) ──────
  //
  // A plain includes() let the entry "16" match inside "116" and "160 hours",
  // handing FULL marks to a wrong answer — and because acceptableAnswers
  // short-circuits scoreOne(), it hands over all of them. Measured on the live
  // bank: 45 of the 57 questions using acceptableAnswers accepted a
  // realistically-wrong number. These tests pin the fix in both directions,
  // because a boundary rule that is too strict is just as wrong: requiring one
  // on the right-hand side regressed three real questions whose accepted entry
  // is a legitimate PREFIX of a more precise answer.
  const marks16 = { maxMark: 2, acceptableAnswers: ['16', '16 hours'] };
  test('a bare numeric entry no longer matches inside a longer number', () => {
    assert.equal(S.scoreOne(marks16, '16').marksEarned, 2);
    assert.equal(S.scoreOne(marks16, '16 hours').marksEarned, 2);
    assert.equal(S.scoreOne(marks16, 'the answer is 16').marksEarned, 2);
    assert.equal(S.scoreOne(marks16, '116').marksEarned, 0);
    assert.equal(S.scoreOne(marks16, '160 hours').marksEarned, 0);
    assert.equal(S.scoreOne(marks16, '1.6').marksEarned, 0);
  });
  test('a decimal fragment does not count — "38" is not inside "0.38"', () => {
    const s38 = { maxMark: 4, acceptableAnswers: ['38', 'x = 38'] };
    assert.equal(S.scoreOne(s38, 'x = 38').marksEarned, 4);
    assert.equal(S.scoreOne(s38, '0.38').marksEarned, 0);
    assert.equal(S.scoreOne(s38, '138').marksEarned, 0);
    // the entry itself ends in a digit, so a trailing digit blocks it too
    assert.equal(S.scoreOne(s38, 'x = 380').marksEarned, 0);
  });
  test('a following decimal point is EXTRA PRECISION, not a different number', () => {
    // "$37 158" is the bank's accepted (nearest-dollar) form of "$37 158.72".
    const money = { maxMark: 2, acceptableAnswers: ['$37 158'] };
    assert.equal(S.scoreOne(money, 'fv = $37 158.72').marksEarned, 2);
    assert.equal(S.scoreOne(money, '$37 158').marksEarned, 2);
  });
  test('entries that do not begin or end in a digit are matched as before', () => {
    const prose = { maxMark: 2, acceptableAnswers: ['800 ml', 'not independent'] };
    assert.equal(S.scoreOne(prose, 'about 800 ml of juice').marksEarned, 2);
    assert.equal(S.scoreOne(prose, 'they are not independent').marksEarned, 2);
    assert.equal(S.scoreOne(prose, 'no idea').marksEarned, 0);
  });
  test('a unit suffix still anchors the left-hand side — "4" not inside "0.4"', () => {
    const snails = { maxMark: 2, acceptableAnswers: ['4', '4 snails'] };
    assert.equal(S.scoreOne(snails, '4 snails').marksEarned, 2);
    assert.equal(S.scoreOne(snails, 'about 4').marksEarned, 2);
    assert.equal(S.scoreOne(snails, '0.4').marksEarned, 0);
    assert.equal(S.scoreOne(snails, '14').marksEarned, 0);
    assert.equal(S.scoreOne(snails, '40 snails').marksEarned, 0);
  });
});

describe('scoreOne — keywords', () => {
  const spec = { maxMark: 4, keywords: ['alpha', 'beta', 'gamma', 'delta'], minKeywords: 2 };
  test('marks are proportional to the keywords matched', () => {
    assert.equal(S.scoreOne(spec, 'alpha beta gamma delta').marksEarned, 4);
    assert.equal(S.scoreOne(spec, 'alpha beta').marksEarned, 2);
    assert.equal(S.scoreOne(spec, 'nothing relevant').marksEarned, 0);
  });
  test('minKeywords CAPS at floor(maxMark/2) — it never raises a mark', () => {
    const strict = { maxMark: 4, keywords: ['alpha', 'beta', 'gamma', 'delta'], minKeywords: 4 };
    // 3 of 4 would be 3 marks on the ratio, but the cap pulls it to 2.
    assert.equal(S.scoreOne(strict, 'alpha beta gamma').marksEarned, 2);
  });
  test('returns null when there is nothing to score against', () => {
    assert.equal(S.scoreOne({ maxMark: 3, keywords: [] }, 'x'), null);
    assert.equal(S.scoreOne({ maxMark: 0, keywords: ['a'] }, 'a'), null);
  });
});

describe('scoreOne — anyOf ("choose N from a menu")', () => {
  // The case the proportional grid could not express: VET 2023 Q16(a)(ii),
  // "list TWO items of PPE", 2 marks, six acceptable items.
  const ppe = {
    maxMark: 2,
    anyOf: [{ required: 2, groups: [
      ['safety glasses', 'goggles'],
      ['hearing', 'earmuff', 'earplug'],
      ['face shield'], ['dust mask'], ['footwear'], ['hair'],
    ] }],
  };

  test('two correct items score full — the defect this mechanism fixes', () => {
    assert.equal(S.scoreOne(ppe, 'safety glasses and hearing protection').marksEarned, 2);
  });

  test('a DIFFERENT valid pair also scores full', () => {
    assert.equal(S.scoreOne(ppe, 'a dust mask and protective footwear').marksEarned, 2);
  });

  test('one item scores half, none scores zero', () => {
    assert.equal(S.scoreOne(ppe, 'just safety glasses').marksEarned, 1);
    assert.equal(S.scoreOne(ppe, 'gloves').marksEarned, 0);
  });

  test('naming MORE than asked is capped, never over-rewarded', () => {
    const res = S.scoreOne(ppe, 'goggles, earmuffs, a dust mask, footwear and a face shield');
    assert.equal(res.marksEarned, 2);
    assert.equal(res.matched, 2, 'credited is capped at `required`');
    assert.equal(res.percentage, 100);
  });

  test('a group counts ONCE however many of its synonyms appear', () => {
    // both entries of the same group — one item, not two
    assert.equal(S.scoreOne(ppe, 'safety glasses and goggles').marksEarned, 1);
  });

  // Two pools of one: "identify ONE advantage AND ONE disadvantage".
  const laser = {
    maxMark: 2,
    anyOf: [
      { required: 1, label: 'advantage', groups: [['time'], ['one person'], ['portable']] },
      { required: 1, label: 'disadvantage', groups: [['battery', 'recharge'], ['expensive']] },
    ],
  };

  test('one from each pool scores full', () => {
    assert.equal(S.scoreOne(laser, 'it saves time but the battery needs recharging').marksEarned, 2);
  });

  test('TWO from ONE pool cannot cover the missing other — the reason anyOf is an array', () => {
    const res = S.scoreOne(laser, 'it saves time and it is portable and one person can use it');
    assert.equal(res.marksEarned, 1);
    assert.equal(res.matched, 1);
  });

  test('block labels prefix the checklist rows', () => {
    const res = S.scoreOne(laser, 'time');
    assert.ok(res.kwResults.some(r => r.label === 'advantage: time' && r.hit));
    assert.ok(res.kwResults.some(r => r.label === 'disadvantage: battery' && !r.hit));
  });

  test('a bare object is accepted as a single block', () => {
    const bare = { maxMark: 2, anyOf: { required: 2, groups: [['a'], ['b'], ['c']] } };
    assert.equal(S.scoreOne(bare, 'a and b').marksEarned, 2);
  });

  test('required is clamped into range rather than trusted', () => {
    const silly = { maxMark: 2, anyOf: [{ required: 99, groups: [['a'], ['b']] }] };
    assert.equal(S.scoreOne(silly, 'a and b').marksEarned, 2, 'required clamped to group count');
  });

  test('acceptableAnswers still wins — anyOf sits between it and keywords', () => {
    const both = { maxMark: 2, acceptableAnswers: ['exact'], anyOf: [{ required: 1, groups: [['other']] }] };
    assert.equal(S.scoreOne(both, 'exact').kind, 'acceptable');
  });

  test('anyOf wins over keywords', () => {
    const both = { maxMark: 2, anyOf: [{ required: 1, groups: [['alpha']] }], keywords: ['beta'] };
    assert.equal(S.scoreOne(both, 'alpha').kind, 'anyOf');
  });
});

describe('bandTextFor', () => {
  test('prefers the question’s own NESA-derived wording', () => {
    const spec = { bandDescriptors: { full: 'NESA full.', partial: 'NESA partial.', minimal: 'NESA minimal.' } };
    assert.equal(S.bandTextFor(spec, 'full'), 'NESA full.');
  });
  test('falls back to the generic band when the question has none', () => {
    assert.equal(S.bandTextFor({}, 'full'), S.GENERIC_BAND.full);
  });
});

describe('scoreAllParts', () => {
  const q = { parts: [
    { label: '(a)', marks: 2, keywords: ['alpha', 'beta'], minKeywords: 1,
      bandDescriptors: { full: 'A full.', partial: 'A partial.', minimal: 'A minimal.' } },
    { label: '(b)', marks: 3, keywords: ['gamma', 'delta', 'epsilon'], minKeywords: 1 },
  ] };

  test('totals the parts and reports each part separately', () => {
    const res = S.scoreAllParts(q, { '(a)': 'alpha beta', '(b)': 'gamma' });
    assert.equal(res.maxMark, 5);
    assert.equal(res.marksEarned, 3);            // 2 + 1
    assert.deepEqual([...res.rows].map(r => r.marksEarned), [2, 1]);
  });

  test('an unattempted part scores 0 and says so, without inventing a band', () => {
    const res = S.scoreAllParts(q, { '(a)': 'alpha beta', '(b)': '   ' });
    assert.equal(res.rows[1].attempted, false);
    assert.equal(res.rows[1].marksEarned, 0);
    assert.equal(res.rows[1].note, 'Not attempted — this part scores 0.');
  });

  test('each part is captioned with its own band wording', () => {
    const res = S.scoreAllParts(q, { '(a)': 'alpha beta', '(b)': 'gamma' });
    assert.equal(res.rows[0].note, 'A full.');
    assert.equal(res.rows[1].note, S.GENERIC_BAND.partial, 'part (b) has no bandDescriptors');
  });

  test('a part can use anyOf while its sibling uses keywords', () => {
    const mixed = { parts: [
      { label: '(a)', marks: 2, anyOf: [{ required: 2, groups: [['x'], ['y'], ['z']] }] },
      { label: '(b)', marks: 1, acceptableAnswers: ['zed'] },
    ] };
    const res = S.scoreAllParts(mixed, { '(a)': 'x and y', '(b)': 'zed' });
    assert.equal(res.marksEarned, 3);
  });
});

describe('helpers', () => {
  test('isMultiPart needs two or more parts', () => {
    assert.equal(S.isMultiPart({ parts: [{}, {}] }), true);
    assert.equal(S.isMultiPart({ parts: [{}] }), false);
    assert.equal(S.isMultiPart({}), false);
    assert.equal(S.isMultiPart(null), false);
  });

  test('anyOfConcepts flattens every alternative for the AI prompt, or returns null', () => {
    assert.deepEqual(
      [...S.anyOfConcepts([{ required: 1, groups: [['a', 'b'], ['c']] }])],
      ['a', 'b', 'c']);
    assert.equal(S.anyOfConcepts(undefined), null);
    assert.equal(S.anyOfConcepts([{ required: 1, groups: [] }]), null,
      'null, not [], so the caller’s || chain falls through');
  });

  test('hasScoringData recognises all three mechanisms', () => {
    assert.equal(S.hasScoringData({ keywords: ['a'] }), true);
    assert.equal(S.hasScoringData({ acceptableAnswers: ['a'] }), true);
    assert.equal(S.hasScoringData({ anyOf: [{ required: 1, groups: [['a']] }] }), true);
    assert.equal(S.hasScoringData({}), false);
  });
});
