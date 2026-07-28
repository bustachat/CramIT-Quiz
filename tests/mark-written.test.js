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
