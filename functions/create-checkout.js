// functions/create-checkout.js — Cloudflare Pages Function (ESM)
// Creates a Stripe Checkout session for the AUTHENTICATED user.
// Identity comes from the verified Supabase JWT — never from the body.
// Plan type is derived server-side from subject_count so a tampered
// client can't buy the base price for an unlimited subject count.

import Stripe from 'stripe';
import { corsHeaders, requireUser, unauthorized } from './_lib/auth.js';

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

export async function onRequestOptions(context) {
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const CORS = corsHeaders(request);

  const user = await requireUser(request, env);
  if (!user) return unauthorized(CORS);

  const stripe = new Stripe(env.STRIPE_SECRET_KEY);

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers: CORS });
  }

  const { subject_count, plan_mode, success_url, cancel_url } = body;
  const nSubjects = parseInt(subject_count, 10);

  if (!nSubjects || nSubjects < 2 || nSubjects > 20) {
    return new Response(JSON.stringify({ error: 'subject_count must be 2–20' }), { status: 400, headers: CORS });
  }

  try {
    // Derive the plan from the count — ignore any client-sent plan_type.
    const planType  = getPlanType(nSubjects, plan_mode);
    const lineItems = buildLineItems(nSubjects, planType);

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
        user_id:        user.id,
        subject_count:  String(nSubjects),
        plan_type:      planType,
        plan_mode:      plan_mode || 'swap',
      },
      subscription_data: {
        metadata: {
          user_id:       user.id,
          subject_count: String(nSubjects),
          plan_mode:     plan_mode || 'swap',
        }
      },
      customer_email: user.email || undefined,
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

function getPlanType(n, mode) {
  const { BASE_INCLUDES, CAP_LIMIT, BASE_PRICE, EXTRA_PRICE, CAP_PRICE } = PRICING;
  if (n <= BASE_INCLUDES) return 'base';
  if (n > CAP_LIMIT)      return 'flex';
  const raw = BASE_PRICE + (n - BASE_INCLUDES) * EXTRA_PRICE;
  if (raw >= CAP_PRICE)   return 'unlimited';
  return 'base_plus';
}

function buildLineItems(nSubjects, planType) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;

  if (planType === 'base') {
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

  // flex — unlimited base + $2.99 per subject above the 7-subject cap
  const flexExtras = nSubjects - CAP_LIMIT;
  return [
    { price: PRICES.flex_base, quantity: 1 },
    { price: PRICES.extra,     quantity: flexExtras },
  ];
}
