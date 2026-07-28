// tests/handlers-auth-gate.test.js
// Every billing/AI Cloudflare Function must reject requests with no (or a
// bad) Authorization header BEFORE touching Stripe/Claude/Supabase. This
// is the single most important invariant in the billing surface — CLAUDE.md
// is explicit that identity must never come from the request body. These
// tests call the real onRequestPost/onRequestOptions handlers with no
// Authorization header; requireUser() returns null without making any
// network call, so no mocking is needed and no secrets are required.
//
// OUT OF SCOPE: the authenticated success paths (creating a real Stripe
// Checkout session, calling the real Claude API) are NOT covered here —
// see docs and the manual Stripe-sandbox checklist in CLAUDE.md §12.

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import * as createCheckout from '../functions/create-checkout.js';
import * as updateSubscription from '../functions/update-subscription.js';
import * as customerPortal from '../functions/customer-portal.js';
import * as markWritten from '../functions/mark-written.js';

const FAKE_ENV = {
  SUPABASE_URL: 'https://fake.supabase.co',
  SUPABASE_SERVICE_ROLE_KEY: 'fake-key',
  STRIPE_SECRET_KEY: 'sk_test_fake',
  ANTHROPIC_API_KEY: 'fake-key',
};

const HANDLERS = {
  'create-checkout':     createCheckout,
  'update-subscription': updateSubscription,
  'customer-portal':     customerPortal,
  'mark-written':        markWritten,
};

for (const [name, mod] of Object.entries(HANDLERS)) {
  describe(`${name}.js auth gate`, () => {
    test('POST with no Authorization header -> 401, no error thrown', async () => {
      const request = new Request(`https://cramit-quiz.pages.dev/${name}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}), // never trusted anyway before the auth check
      });
      const res = await mod.onRequestPost({ request, env: FAKE_ENV });
      assert.equal(res.status, 401);
      const body = await res.json();
      assert.ok(body.error);
    });

    test('OPTIONS preflight -> 204 with CORS headers, no auth required', async () => {
      const request = new Request(`https://cramit-quiz.pages.dev/${name}`, {
        method: 'OPTIONS',
        headers: { Origin: 'https://cramit-quiz.pages.dev' },
      });
      const res = await mod.onRequestOptions({ request, env: FAKE_ENV });
      assert.equal(res.status, 204);
      assert.equal(res.headers.get('Access-Control-Allow-Origin'), 'https://cramit-quiz.pages.dev');
    });
  });
}
