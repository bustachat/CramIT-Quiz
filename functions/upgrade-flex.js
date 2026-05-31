// functions/upgrade-flex.js — Cloudflare Pages Function (ESM)
// Upgrades a student from the Unlimited (cap) plan to the Flex plan.
// Swaps the 'cap' price item → 'flex_base' price item on the subscription.

import Stripe from 'stripe';

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
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
    return new Response(JSON.stringify({ error: 'Invalid JSON in request body' }), { status: 400, headers: CORS });
  }

  const { subscription_id, user_id } = body;

  if (!subscription_id) {
    return new Response(
      JSON.stringify({ error: 'Missing required field: subscription_id' }),
      { status: 400, headers: CORS }
    );
  }

  try {
    const subscription = await stripe.subscriptions.retrieve(subscription_id);

    const updatedItems = subscription.items.data.map((item) => {
      if (item.price.id === env.STRIPE_PRICE_CAP) {
        return { id: item.id, price: env.STRIPE_PRICE_FLEX_BASE };
      }
      return { id: item.id };
    });

    await stripe.subscriptions.update(subscription_id, {
      items:              updatedItems,
      proration_behavior: 'always_invoice',
      metadata: {
        plan:    'flex',
        user_id: user_id ?? '',
      },
    });

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });

  } catch (err) {
    console.error('[upgrade-flex] Stripe error:', err.message);
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS });
  }
}
