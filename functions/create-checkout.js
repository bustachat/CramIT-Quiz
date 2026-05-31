// functions/create-checkout.js — Cloudflare Pages Function (ESM)
// Creates a Stripe Checkout session for a given subject count + plan.
// Called by billing.js → createCheckoutSession()

import Stripe from 'stripe';

const PRICES = {
  base:      'price_1TEdRbPvnbx5MPYyExQIlaBK',
  cap:       'price_1TEdW3Pvnbx5MPYykHvvk7gf',
  flex_base: 'price_1TEdZRPvnbx5MPYylioNhNQI',
  extra:     'price_1TEdUJPvnbx5MPYy6luOiFjv',
};

const PRICING = {
  BASE_PRICE:    7.99,
  EXTRA_PRICE:   2.99,
  CAP_PRICE:     19.99,
  CAP_LIMIT:     7,
  BASE_INCLUDES: 2,
};

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, x-user-email',
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers: CORS });
  }

  const { user_id, subject_count, plan_type, plan_mode, success_url, cancel_url } = body;

  if (!user_id || !subject_count) {
    return new Response(JSON.stringify({ error: 'Missing required fields' }), { status: 400, headers: CORS });
  }

  try {
    const lineItems = buildLineItems(subject_count, plan_type, plan_mode);

    const successUrlWithSession = success_url.includes('?')
      ? success_url + '&session_id={CHECKOUT_SESSION_ID}'
      : success_url + '?session_id={CHECKOUT_SESSION_ID}';

    const session = await stripe.checkout.sessions.create({
      mode:                 'subscription',
      payment_method_types: ['card'],
      line_items:           lineItems,
      success_url:          successUrlWithSession,
      cancel_url:           cancel_url,
      metadata: {
        user_id,
        subject_count:  String(subject_count),
        plan_type,
        plan_mode:      plan_mode || 'swap',
      },
      subscription_data: {
        metadata: {
          user_id,
          subject_count: String(subject_count),
          plan_mode:     plan_mode || 'swap',
        }
      },
      customer_email: request.headers.get('x-user-email') || undefined,
    });

    return new Response(JSON.stringify({ url: session.url }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });

  } catch (err) {
    console.error('create-checkout error:', err);
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS });
  }
}

function buildLineItems(nSubjects, planType, planMode) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;

  if (nSubjects <= BASE_INCLUDES) {
    return [{ price: PRICES.base, quantity: 1 }];
  }

  if (planType === 'base_plus') {
    const extras = nSubjects - BASE_INCLUDES;
    return [
      { price: PRICES.base,  quantity: 1 },
      { price: PRICES.extra, quantity: extras },
    ];
  }

  if (planType === 'unlimited') {
    return [{ price: PRICES.cap, quantity: 1 }];
  }

  if (planType === 'flex') {
    const flexExtras = nSubjects - CAP_LIMIT;
    return [
      { price: PRICES.flex_base, quantity: 1 },
      { price: PRICES.extra,     quantity: flexExtras },
    ];
  }

  return [{ price: PRICES.base, quantity: 1 }];
}
