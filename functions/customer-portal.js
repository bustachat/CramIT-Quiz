// functions/customer-portal.js — Cloudflare Pages Function (ESM)
// Opens Stripe's hosted billing portal for the AUTHENTICATED user.
// The Stripe customer ID is looked up from the user's own subscription
// row — a customer_id in the request body is ignored.

import Stripe from 'stripe';
import { corsHeaders, requireUser, unauthorized, getSubscriptionRow } from './_lib/auth.js';

const APP_URL = 'https://cramit-quiz.pages.dev';

export async function onRequestOptions(context) {
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const CORS = corsHeaders(request);

  const user = await requireUser(request, env);
  if (!user) return unauthorized(CORS);

  let body = {};
  try { body = await request.json(); } catch { /* return_url optional */ }

  try {
    const sub = await getSubscriptionRow(user.id, env, 'stripe_customer_id');
    if (!sub?.stripe_customer_id) {
      return new Response(
        JSON.stringify({ error: 'No billing account found for your login.' }),
        { status: 404, headers: { 'Content-Type': 'application/json', ...CORS } }
      );
    }

    // Only return to our own origin — never an arbitrary URL from the body.
    const returnUrl = typeof body.return_url === 'string'
      && (body.return_url.startsWith(APP_URL) || /^https:\/\/[a-z0-9-]+\.cramit-quiz\.pages\.dev/.test(body.return_url))
      ? body.return_url
      : APP_URL;

    const stripe = new Stripe(env.STRIPE_SECRET_KEY);
    const session = await stripe.billingPortal.sessions.create({
      customer:   sub.stripe_customer_id,
      return_url: returnUrl,
    });

    return new Response(JSON.stringify({ url: session.url }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });

  } catch (err) {
    console.error('customer-portal error:', err);
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: CORS });
  }
}
