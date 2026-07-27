// tests/auth-lib.test.js
// functions/_lib/auth.js is shared by every billing function — this is
// where a bug would compromise ALL of them at once (e.g. trusting an
// invalid token, or leaking CORS to an arbitrary origin). Supabase calls
// are stubbed via a temporary global.fetch override; nothing hits the
// network.
//
// NOTE: mocking global.fetch (rather than a real network doubles) means
// these tests confirm auth.js's OWN logic (parsing the header, handling
// non-OK responses, shaping the 401 body) — they do not confirm the real
// Supabase Auth API still behaves the way we assume. Any change to
// Supabase's /auth/v1/user response shape still needs a manual check.

import { test, describe, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import {
  corsHeaders, requireUser, unauthorized,
  getSubscriptionRow, countSubjectSelections, getSubjectSelectionsWithPending,
} from '../functions/_lib/auth.js';

const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });

function fakeRequest(headers = {}) {
  return { headers: { get: (name) => headers[name] ?? null } };
}

describe('corsHeaders()', () => {
  test('production origin is echoed back', () => {
    const h = corsHeaders(fakeRequest({ Origin: 'https://cramit-quiz.pages.dev' }));
    assert.equal(h['Access-Control-Allow-Origin'], 'https://cramit-quiz.pages.dev');
  });

  test('Cloudflare preview subdomains are allowed', () => {
    const h = corsHeaders(fakeRequest({ Origin: 'https://abc123.cramit-quiz.pages.dev' }));
    assert.equal(h['Access-Control-Allow-Origin'], 'https://abc123.cramit-quiz.pages.dev');
  });

  test('an unrelated/malicious origin falls back to the prod origin, not itself', () => {
    const h = corsHeaders(fakeRequest({ Origin: 'https://evil.example.com' }));
    assert.equal(h['Access-Control-Allow-Origin'], 'https://cramit-quiz.pages.dev');
  });

  test('a lookalike domain (suffix trick) is rejected', () => {
    // "notcramit-quiz.pages.dev" does NOT end with ".cramit-quiz.pages.dev"
    // but a naive .includes() check could be fooled by this.
    const h = corsHeaders(fakeRequest({ Origin: 'https://notcramit-quiz.pages.dev' }));
    assert.equal(h['Access-Control-Allow-Origin'], 'https://cramit-quiz.pages.dev');
  });
});

describe('requireUser()', () => {
  const env = { SUPABASE_URL: 'https://fake.supabase.co', SUPABASE_SERVICE_ROLE_KEY: 'fake-key' };

  test('missing Authorization header -> null (no network call)', async () => {
    let called = false;
    globalThis.fetch = async () => { called = true; return new Response('{}'); };
    const user = await requireUser(fakeRequest(), env);
    assert.equal(user, null);
    assert.equal(called, false);
  });

  test('non-Bearer Authorization header -> null', async () => {
    const user = await requireUser(fakeRequest({ Authorization: 'Basic abc123' }), env);
    assert.equal(user, null);
  });

  test('valid token -> Supabase returns a user object', async () => {
    globalThis.fetch = async () => new Response(JSON.stringify({ id: 'user-123', email: 'a@b.com' }), { status: 200 });
    const user = await requireUser(fakeRequest({ Authorization: 'Bearer valid-token' }), env);
    assert.deepEqual(user, { id: 'user-123', email: 'a@b.com' });
  });

  test('expired/invalid token -> Supabase 401 -> null', async () => {
    globalThis.fetch = async () => new Response('{}', { status: 401 });
    const user = await requireUser(fakeRequest({ Authorization: 'Bearer expired-token' }), env);
    assert.equal(user, null);
  });

  test('Supabase response with no id field -> null (never trust a body without id)', async () => {
    globalThis.fetch = async () => new Response(JSON.stringify({ email: 'a@b.com' }), { status: 200 });
    const user = await requireUser(fakeRequest({ Authorization: 'Bearer weird-token' }), env);
    assert.equal(user, null);
  });

  test('network error talking to Supabase -> null, does not throw', async () => {
    globalThis.fetch = async () => { throw new Error('network down'); };
    const user = await requireUser(fakeRequest({ Authorization: 'Bearer token' }), env);
    assert.equal(user, null);
  });
});

describe('unauthorized()', () => {
  test('returns a 401 with a JSON error body', async () => {
    const res = unauthorized({ 'Access-Control-Allow-Origin': 'https://cramit-quiz.pages.dev' });
    assert.equal(res.status, 401);
    const body = await res.json();
    assert.ok(body.error);
  });
});

describe('getSubscriptionRow() / countSubjectSelections()', () => {
  const env = { SUPABASE_URL: 'https://fake.supabase.co', SUPABASE_SERVICE_ROLE_KEY: 'fake-key' };

  test('getSubscriptionRow returns the first row', async () => {
    globalThis.fetch = async () => new Response(JSON.stringify([{ plan: 'unlimited' }]), { status: 200 });
    const row = await getSubscriptionRow('user-1', env);
    assert.deepEqual(row, { plan: 'unlimited' });
  });

  test('getSubscriptionRow returns null when no row exists', async () => {
    globalThis.fetch = async () => new Response('[]', { status: 200 });
    const row = await getSubscriptionRow('user-1', env);
    assert.equal(row, null);
  });

  test('getSubscriptionRow throws on a non-OK Supabase response (caller must not silently proceed)', async () => {
    globalThis.fetch = async () => new Response('error', { status: 500 });
    await assert.rejects(() => getSubscriptionRow('user-1', env));
  });

  test('countSubjectSelections counts rows', async () => {
    globalThis.fetch = async () => new Response(JSON.stringify([{ subject_id: 'maths' }, { subject_id: 'hms' }]), { status: 200 });
    const count = await countSubjectSelections('user-1', env);
    assert.equal(count, 2);
  });

  test('getSubjectSelectionsWithPending returns rows including pending_removal_at', async () => {
    globalThis.fetch = async () => new Response(JSON.stringify([
      { subject_id: 'maths', pending_removal_at: null },
      { subject_id: 'multimedia', pending_removal_at: '2026-08-29T00:00:00.000Z' },
    ]), { status: 200 });
    const rows = await getSubjectSelectionsWithPending('user-1', env);
    assert.equal(rows.length, 2);
    assert.equal(rows[1].pending_removal_at, '2026-08-29T00:00:00.000Z');
  });
});
