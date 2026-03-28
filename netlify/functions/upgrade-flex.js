// netlify/functions/upgrade-flex.js
// ─────────────────────────────────────────────────────────────
//  Upgrades a student from the Unlimited (cap) plan to the Flex plan.
//  Called when a student on the 7-subject cap wants to add an 8th subject.
//
//  What it does:
//    1. Fetches the student's current Stripe subscription
//    2. Swaps the 'cap' price item → 'flex_base' price item
//    3. Stripe immediately invoices/credits the prorated difference
//
//  Required Netlify env vars:
//    STRIPE_SECRET_KEY      — from Stripe → Developers → API keys
//    STRIPE_PRICE_CAP       — price_1TEdW3Pvnbx5MPYykHvvk7gf
//    STRIPE_PRICE_FLEX_BASE — price_1TEdZRPvnbx5MPYylioNhNQI
// ─────────────────────────────────────────────────────────────

const Stripe = require('stripe');

exports.handler = async (event) => {
  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

  // Parse request body
  let body;
  try {
    body = JSON.parse(event.body);
  } catch {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid JSON in request body' }),
    };
  }

  const { subscription_id, user_id } = body;

  if (!subscription_id) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Missing required field: subscription_id' }),
    };
  }

  try {
    // Fetch the current subscription so we know which item to swap
    const subscription = await stripe.subscriptions.retrieve(subscription_id);

    // Find the item that uses the cap price and swap it to flex_base.
    // All other items (e.g. extra add-ons) are left unchanged.
    const updatedItems = subscription.items.data.map((item) => {
      if (item.price.id === process.env.STRIPE_PRICE_CAP) {
        return {
          id:    item.id,
          price: process.env.STRIPE_PRICE_FLEX_BASE,
        };
      }
      // Keep all other items as-is (no price change, just pass the id)
      return { id: item.id };
    });

    // Apply the update — prorate immediately so the student is charged/credited now
    await stripe.subscriptions.update(subscription_id, {
      items:               updatedItems,
      proration_behavior:  'always_invoice',
      metadata: {
        plan:    'flex',
        user_id: user_id ?? '',
      },
    });

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ok: true }),
    };

  } catch (err) {
    console.error('[upgrade-flex] Stripe error:', err.message);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: err.message }),
    };
  }
};
