// tests/mark-written.test.js
// mark-written.js's quota logic (which plan gets how many AI marks/month,
// when the counter resets, what happens if the row is missing) runs BEFORE
// the Claude API is ever called. These tests mock only the two Supabase
// calls (auth verification + subscription row fetch) via global.fetch, and
// assert on the early-return paths — the request never reaches Claude, so
// no ANTHROPIC_API_KEY or real API call is involved.

import { test, describe, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { onRequestPost } from '../functions/mark-written.js';
import { readFileSync } from 'node:fs';

const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });

const ENV = {
  SUPABASE_URL: 'https://fake.supabase.co',
  SUPABASE_SERVICE_ROLE_KEY: 'fake-key',
  ANTHROPIC_API_KEY: 'fake-key',
};

function mockFetchWithSubscriptionRow(subRow) {
  globalThis.fetch = async (url) => {
    const u = String(url);
    if (u.includes('/auth/v1/user')) {
      return new Response(JSON.stringify({ id: 'user-1', email: 'a@b.com' }), { status: 200 });
    }
    if (u.includes('/rest/v1/subscriptions')) {
      return new Response(JSON.stringify(subRow ? [subRow] : []), { status: 200 });
    }
    throw new Error(`Unexpected fetch call in test: ${u}`);
  };
}

function goodRequest(body) {
  return new Request('https://cramit-quiz.pages.dev/mark-written', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer valid-token' },
    body: JSON.stringify(body),
  });
}

const VALID_BODY = { question: 'Explain X.', maxMarks: 4, studentAnswer: 'Because Y.', keywords: ['Y'] };

describe('mark-written.js validation', () => {
  test('missing required fields -> 400', async () => {
    mockFetchWithSubscriptionRow({ plan: 'base', status: 'active', ai_marks_used: 0 });
    const res = await onRequestPost({ request: goodRequest({ question: 'Q only' }), env: ENV });
    assert.equal(res.status, 400);
  });
});

describe('mark-written.js quota logic', () => {
  test('no subscription row found -> sub_not_found, not a misleading upgrade message', async () => {
    mockFetchWithSubscriptionRow(null);
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.equal(res.status, 200);
    assert.equal(body.quotaExceeded, true);
    assert.equal(body.reason, 'sub_not_found');
  });

  test('free plan, no active subscription -> no_plan, quota 0', async () => {
    // status is NOT active/trialing here — the webhook-sync-delay fallback
    // (tested below) only kicks in for active/trialing rows, so this is a
    // genuine free-plan user, not one mid-upgrade.
    mockFetchWithSubscriptionRow({ plan: 'free', status: 'canceled', ai_marks_used: 0 });
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.equal(body.quotaExceeded, true);
    assert.equal(body.reason, 'no_plan');
  });

  test('unrecognised plan but status active -> treated as base (50 marks), webhook-sync-delay fallback', async () => {
    // sub.plan hasn't synced from Stripe yet but status is active — should
    // NOT be treated as no_plan/quota 0.
    mockFetchWithSubscriptionRow({ plan: 'unknown_new_plan', status: 'active', ai_marks_used: 0 });
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.notEqual(body.reason, 'no_plan');
  });

  test('base plan, already used all 50 marks this cycle -> quota_reached', async () => {
    mockFetchWithSubscriptionRow({
      plan: 'base', status: 'active', ai_marks_used: 50,
      ai_marks_reset_at: new Date().toISOString(), // reset just now, so not eligible for a 30-day reset
    });
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.equal(body.quotaExceeded, true);
    assert.equal(body.reason, 'quota_reached');
  });

  test('base plan, quota used up but reset window elapsed (>=30 days) -> allowed through to Claude', async () => {
    const thirtyOneDaysAgo = new Date(Date.now() - 31 * 24 * 60 * 60 * 1000).toISOString();
    mockFetchWithSubscriptionRow({ plan: 'base', status: 'active', ai_marks_used: 50, ai_marks_reset_at: thirtyOneDaysAgo });
    // Claude is not mocked here — its call should be attempted (and fail,
    // since ANTHROPIC_API_KEY is fake), proving the quota gate let it through
    // rather than reporting quotaExceeded.
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.notEqual(body.quotaExceeded, true);
  });
});

// ── Multi-part marking (CLAUDE.md §10 rule 9) ────────────────────────────────
// A multi-part NESA question sends every part in ONE request and gets a mark per
// part back. The student sees those per-part marks, so a malformed or overgenerous
// model response must not be able to hand out marks the part isn't worth.

// Mocks Supabase as above AND the Anthropic call, returning `aiJson` as Claude's reply.
function mockFetchWithClaude(aiJson, capture = {}) {
  globalThis.fetch = async (url, init) => {
    const u = String(url);
    if (u.includes('/auth/v1/user')) {
      return new Response(JSON.stringify({ id: 'user-1', email: 'a@b.com' }), { status: 200 });
    }
    if (u.includes('/rest/v1/subscriptions') || u.includes('/rest/v1/rpc/')) {
      return new Response(JSON.stringify([{ plan: 'base', status: 'active', ai_marks_used: 0 }]), { status: 200 });
    }
    if (u.includes('api.anthropic.com')) {
      capture.body = JSON.parse(init.body);
      return new Response(JSON.stringify({
        content: [{ text: JSON.stringify(aiJson) }],
        usage: { input_tokens: 1, output_tokens: 1 },
      }), { status: 200 });
    }
    throw new Error(`Unexpected fetch call in test: ${u}`);
  };
}

const PARTS = [
  { label: '(a)', question: 'Name the tool.', maxMarks: 1, keywords: ['chisel'], studentAnswer: 'chisel' },
  { label: '(b)', question: 'Describe TWO uses.', maxMarks: 2, keywords: ['pare'], studentAnswer: 'paring' },
  { label: '(c)', question: 'Describe ONE consequence.', maxMarks: 3, keywords: ['blunt'], studentAnswer: '' },
];
const partsBody = (overrides = {}) => ({
  question: 'A tool is shown.', maxMarks: 6, studentAnswer: '(a) chisel', keywords: [],
  parts: PARTS, ...overrides,
});

describe('mark-written.js multi-part marking', () => {
  test('returns a mark per part and totals them', async () => {
    mockFetchWithClaude({
      partResults: [
        { label: '(a)', marksAwarded: 1, feedback: 'Correct.' },
        { label: '(b)', marksAwarded: 1, feedback: 'One use only.' },
        { label: '(c)', marksAwarded: 0, feedback: 'Not attempted.' },
      ],
      feedback: 'Solid start.', improvement: 'Attempt part (c).',
    });
    const res = await onRequestPost({ request: goodRequest(partsBody()), env: ENV });
    const body = await res.json();
    assert.equal(res.status, 200);
    assert.equal(body.partResults.length, 3);
    assert.deepEqual(body.partResults.map(p => p.marksAwarded), [1, 1, 0]);
    assert.equal(body.marksAwarded, 2);   // derived from the parts, not stated separately
    assert.equal(body.maxMarks, 6);
  });

  test('a part awarded more than its own maximum is clamped', async () => {
    mockFetchWithClaude({
      partResults: [
        { label: '(a)', marksAwarded: 99, feedback: 'x' },   // part is worth 1
        { label: '(b)', marksAwarded: -5, feedback: 'x' },   // negative
        { label: '(c)', marksAwarded: 3, feedback: 'x' },
      ],
      feedback: 'f', improvement: 'i',
    });
    const res = await onRequestPost({ request: goodRequest(partsBody()), env: ENV });
    const body = await res.json();
    assert.deepEqual(body.partResults.map(p => p.marksAwarded), [1, 0, 3]);
    assert.equal(body.marksAwarded, 4);
  });

  test('a part the question does not have is discarded', async () => {
    mockFetchWithClaude({
      partResults: [
        { label: '(a)', marksAwarded: 1, feedback: 'x' },
        { label: '(z)', marksAwarded: 5, feedback: 'invented' },
      ],
      feedback: 'f', improvement: 'i',
    });
    const res = await onRequestPost({ request: goodRequest(partsBody()), env: ENV });
    const body = await res.json();
    assert.deepEqual(body.partResults.map(p => p.label), ['(a)']);
    assert.equal(body.marksAwarded, 1);
  });

  test('every part goes in ONE Claude call, so quota cost does not scale with part count', async () => {
    const capture = {};
    mockFetchWithClaude({ partResults: PARTS.map(p => ({ label: p.label, marksAwarded: 0, feedback: '' })), feedback: '', improvement: '' }, capture);
    await onRequestPost({ request: goodRequest(partsBody()), env: ENV });
    const prompt = capture.body.messages[0].content;
    PARTS.forEach(p => assert.ok(prompt.includes(`PART ${p.label} (${p.maxMarks} marks)`), `prompt missing ${p.label}`));
    assert.ok(prompt.includes('Mark EACH PART SEPARATELY'));
  });

  test('a single-part question is unaffected — no partResults, original shape', async () => {
    mockFetchWithClaude({ marksAwarded: 3, grade: 'good', feedback: 'f', improvement: 'i', keyConceptsFound: ['Y'] });
    const res = await onRequestPost({ request: goodRequest(VALID_BODY), env: ENV });
    const body = await res.json();
    assert.equal(body.partResults, undefined);
    assert.equal(body.marksAwarded, 3);
    assert.equal(body.maxMarks, 4);
    assert.deepEqual(body.keyConceptsFound, ['Y']);
  });

  test('a one-element parts array is treated as a single question, not multi-part', async () => {
    mockFetchWithClaude({ marksAwarded: 2, grade: 'good', feedback: 'f', improvement: 'i' });
    const res = await onRequestPost({ request: goodRequest(partsBody({ parts: [PARTS[0]] })), env: ENV });
    const body = await res.json();
    assert.equal(body.partResults, undefined);
  });
});

// ── Section III: the longest response the engine handles ─────────────────────
// Multimedia Q16 is 15 marks in two parts, and 2023 is 3 + 12 — the largest
// single part anywhere in the bank. These drive the REAL bank entry through the
// real handler, so the prompt and the response handling are exercised against
// production data rather than a fixture. (A live Claude call still needs
// ANTHROPIC_API_KEY, which no CI or dev environment here has — see GATE 7.)

const MULTIMEDIA = JSON.parse(
  readFileSync(new URL('../subjects/multimedia.json', import.meta.url), 'utf8')
);
const Q16_2023 = MULTIMEDIA.writtenQuestions.find((q) => q.year === 2023 && q.qNum === 16);

// Mirrors index.html tryAiMarking()'s body for a multi-part question.
function sectionThreeBody(answers) {
  return {
    question: Q16_2023.q,
    maxMarks: Q16_2023.marks,
    keywords: Q16_2023.keywords || [],
    studentAnswer: Q16_2023.parts.map((p) => `${p.label} ${answers[p.label] || ''}`).join('\n\n'),
    bandDescriptors: Q16_2023.bandDescriptors || null,
    subject: 'multimedia',
    parts: Q16_2023.parts.map((p) => ({
      label: p.label,
      question: [p.intro, p.q].filter(Boolean).join(' '),
      maxMarks: p.marks,
      keywords: p.keywords || p.acceptableAnswers || [],
      bandDescriptors: p.bandDescriptors || null,
      studentAnswer: String(answers[p.label] || ''),
    })),
  };
}

describe('mark-written.js — Multimedia Section III (15 marks, 3 + 12)', () => {
  test('the real bank entry is the shape these tests assume', () => {
    assert.ok(Q16_2023, '2023 Q16 missing from subjects/multimedia.json');
    assert.equal(Q16_2023.marks, 15);
    assert.deepEqual(Q16_2023.parts.map((p) => [p.label, p.marks]), [['(a)', 3], ['(b)', 12]]);
  });

  test('both parts reach Claude with their own maximum, keywords and NESA band descriptors', async () => {
    const capture = {};
    mockFetchWithClaude(
      {
        partResults: [
          { label: '(a)', marksAwarded: 3, feedback: 'x' },
          { label: '(b)', marksAwarded: 12, feedback: 'x' },
        ],
        feedback: 'f',
        improvement: 'i',
      },
      capture
    );
    await onRequestPost({ request: goodRequest(sectionThreeBody({ '(a)': 'VR.', '(b)': 'Automation.' })), env: ENV });
    const prompt = capture.body.messages[0].content;

    assert.ok(prompt.includes('PART (a) (3 marks)'), 'part (a) maximum missing');
    assert.ok(prompt.includes('PART (b) (12 marks)'), 'part (b) maximum missing');
    assert.ok(prompt.includes('worth 15 marks in total'), 'total missing');

    // NESA's own criteria wording, not the engine's generic fallback.
    assert.ok(
      prompt.includes(Q16_2023.parts[1].bandDescriptors.full),
      "part (b)'s NESA top-band wording missing from the prompt"
    );
    // and the part's own key concepts
    Q16_2023.parts[1].keywords.slice(0, 3).forEach((kw) => {
      assert.ok(prompt.includes(kw), `keyword ${kw} missing from the prompt`);
    });
    // nothing undefined leaks into a 12-mark prompt
    assert.ok(!prompt.includes('undefined'), 'prompt contains "undefined"');
  });

  test('a 12-mark part can be awarded its full 12, and the total is derived as 15', async () => {
    mockFetchWithClaude({
      partResults: [
        { label: '(a)', marksAwarded: 3, feedback: 'x' },
        { label: '(b)', marksAwarded: 12, feedback: 'x' },
      ],
      feedback: 'f',
      improvement: 'i',
    });
    const res = await onRequestPost({ request: goodRequest(sectionThreeBody({ '(a)': 'a', '(b)': 'b' })), env: ENV });
    const body = await res.json();
    assert.deepEqual(body.partResults.map((p) => p.marksAwarded), [3, 12]);
    assert.equal(body.marksAwarded, 15);
    assert.equal(body.maxMarks, 15);
    assert.equal(body.grade, 'excellent');
  });

  test('an overgenerous mark on the 12-mark part is clamped to 12, not to the question total', async () => {
    mockFetchWithClaude({
      partResults: [
        { label: '(a)', marksAwarded: 15, feedback: 'x' },  // part is worth 3
        { label: '(b)', marksAwarded: 99, feedback: 'x' },  // part is worth 12
      ],
      feedback: 'f',
      improvement: 'i',
    });
    const res = await onRequestPost({ request: goodRequest(sectionThreeBody({ '(a)': 'a', '(b)': 'b' })), env: ENV });
    const body = await res.json();
    assert.deepEqual(body.partResults.map((p) => p.marksAwarded), [3, 12]);
    assert.equal(body.marksAwarded, 15);
  });

  test('a blank 12-mark part is sent as blank and scores 0', async () => {
    const capture = {};
    mockFetchWithClaude(
      {
        partResults: [
          { label: '(a)', marksAwarded: 2, feedback: 'x' },
          { label: '(b)', marksAwarded: 0, feedback: 'Not attempted.' },
        ],
        feedback: 'f',
        improvement: 'i',
      },
      capture
    );
    const res = await onRequestPost({ request: goodRequest(sectionThreeBody({ '(a)': 'VR is immersive.', '(b)': '' })), env: ENV });
    const body = await res.json();
    assert.ok(capture.body.messages[0].content.includes('(left blank — award 0)'));
    assert.equal(body.marksAwarded, 2);
    assert.equal(body.grade, 'developing');
  });

  test('the parts path asks for enough output headroom for a 15-mark response', async () => {
    const capture = {};
    mockFetchWithClaude(
      { partResults: [{ label: '(a)', marksAwarded: 0, feedback: '' }, { label: '(b)', marksAwarded: 0, feedback: '' }], feedback: '', improvement: '' },
      capture
    );
    await onRequestPost({ request: goodRequest(sectionThreeBody({ '(a)': 'a', '(b)': 'b' })), env: ENV });
    assert.equal(capture.body.max_tokens, 1024);
    assert.equal(capture.body.model, 'claude-haiku-4-5');
  });
});
