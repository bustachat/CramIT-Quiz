// functions/update-subscription.js — Cloudflare Pages Function (ESM)
// Syncs the AUTHENTICATED user's Stripe subscription with their actual
// subject count. Both the subscription ID and the count are looked up
// server-side — the request body is never trusted for either.

import Stripe from 'stripe';
import {
  corsHeaders, requireUser, unauthorized,
  getSubscriptionRow, countSubjectSelections,
} from './_lib/auth.js';

const PRICES = {
  base:      'price_1TEdRbPvnbx5MPYyExQIlaBK',
  extra:     'price_1TEdUJPvnbx5MPYy6luOiFjv',
  cap:       'price_1TEdW3Pvnbx5MPYykHvvk7gf',
  flex_base: 'price_1TEdZRPvnbx5MPYylioNhNQI',
};

const PRICING = {
  BASE_PRICE:    7.99,
  EXTRA_PRICE:   2.99,
  CAP_PRICE:     19.99,
  CAP_LIMIT:     7,
  BASE_INCLUDES: 2,
};

export async function onRequestOptions(context) {
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const CORS = corsHeaders(request);

  const user = await requireUser(request, env);
  if (!user) return unauthorized(CORS);

  try {
    const sub = await getSubscriptionRow(user.id, env, 'stripe_subscription_id,plan,status');
    if (!sub?.stripe_subscription_id) {
      return new Response(
        JSON.stringify({ error: 'No active subscription found for your login.' }),
        { status: 404, headers: { 'Content-Type': 'application/json', ...CORS } }
      );
    }

    // Source of truth: how many subjects the user actually has selected.
    const subject_count = await countSubjectSelections(user.id, env);
    const plan_mode     = sub.plan === 'flex' ? 'flex' : 'swap';
    const subscription_id = sub.stripe_subscription_id;

    const stripe = new Stripe(env.STRIPE_SECRET_KEY);

    if (subject_count <= 1) {
      await stripe.subscriptions.cancel(subscription_id);
      return new Response(
        JSON.stringify({ ok: true, plan: 'free', subjects: subject_count, cancelled: true }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } }
      );
    }

    const stripeSub    = await stripe.subscriptions.retrieve(subscription_id);
    const planType     = getPlanType(subject_count, plan_mode);
    const updatedItems = buildUpdatedItems(stripeSub.items.data, subject_count, planType);

    if (updatedItems && updatedItems.length > 0) {
      await stripe.subscriptions.update(subscription_id, {
        items:              updatedItems,
        proration_behavior: 'create_prorations',
        metadata: {
          subject_count: String(subject_count),
          plan_mode:     plan_mode,
        },
      });
    } else {
      await stripe.subscriptions.update(subscription_id, {
        metadata: {
          subject_count: String(subject_count),
          plan_mode:     plan_mode,
        },
      });
    }

    return new Response(
      JSON.stringify({ ok: true, plan: planType, subjects: subject_count }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } }
    );

  } catch (err) {
    console.error('update-subscription error:', err);
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS });
  }
}

function getPlanType(n, mode) {
  const { BASE_INCLUDES, CAP_LIMIT, BASE_PRICE, EXTRA_PRICE, CAP_PRICE } = PRICING;
  if (n <= 1)             return 'free';
  if (n <= BASE_INCLUDES) return 'base';
  const raw = BASE_PRICE + (n - BASE_INCLUDES) * EXTRA_PRICE;
  if (raw < CAP_PRICE)    return 'base_plus';
  if (n <= CAP_LIMIT)     return 'unlimited';
  if (mode === 'flex')    return 'flex';
  return 'unlimited';
}

function buildUpdatedItems(currentItems, nSubjects, planType) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;
  const updated = [];
  const ids         = currentItems.map(i => i.price.id);
  const hasBase     = ids.includes(PRICES.base);
  const hasExtra    = ids.includes(PRICES.extra);
  const hasCap      = ids.includes(PRICES.cap);
  const hasFlexBase = ids.includes(PRICES.flex_base);

  if (planType === 'unlimited') {
    currentItems.forEach(item => {
      if ([PRICES.base, PRICES.extra, PRICES.flex_base].includes(item.price.id)) {
        updated.push({ id: item.id, deleted: true });
      }
    });
    if (!hasCap) updated.push({ price: PRICES.cap, quantity: 1 });
    return updated;
  }

  if (planType === 'flex') {
    const flexExtras = nSubjects - CAP_LIMIT;
    currentItems.forEach(item => {
      if (item.price.id === PRICES.cap) {
        updated.push({ id: item.id, deleted: true });
      }
    });
    if (!hasFlexBase) updated.push({ price: PRICES.flex_base, quantity: 1 });
    const extraItem = currentItems.find(i => i.price.id === PRICES.extra);
    if (extraItem) {
      updated.push({ id: extraItem.id, quantity: flexExtras });
    } else {
      updated.push({ price: PRICES.extra, quantity: flexExtras });
    }
    return updated;
  }

  if (planType === 'base' || planType === 'base_plus') {
    const extras = Math.max(0, nSubjects - BASE_INCLUDES);
    currentItems.forEach(item => {
      if ([PRICES.cap, PRICES.flex_base].includes(item.price.id)) {
        updated.push({ id: item.id, deleted: true });
      }
    });
    if (!hasBase) updated.push({ price: PRICES.base, quantity: 1 });
    if (extras > 0) {
      const extraItem = currentItems.find(i => i.price.id === PRICES.extra);
      if (extraItem) {
        updated.push({ id: extraItem.id, quantity: extras });
      } else {
        updated.push({ price: PRICES.extra, quantity: extras });
      }
    } else if (hasExtra) {
      const extraItem = currentItems.find(i => i.price.id === PRICES.extra);
      if (extraItem) updated.push({ id: extraItem.id, deleted: true });
    }
    return updated;
  }

  return [];
}
