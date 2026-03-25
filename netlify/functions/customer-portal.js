// netlify/functions/customer-portal.js
//
// Opens Stripe's hosted billing portal — students can:
//   - Update their card
//   - Cancel their subscription
//   - View invoice history

const Stripe = require('stripe');
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method not allowed' };

  try {
    const { customer_id, return_url } = JSON.parse(event.body);

    const session = await stripe.billingPortal.sessions.create({
      customer:   customer_id,
      return_url: return_url,
    });

    return {
      statusCode: 200,
      headers:    { 'Content-Type': 'application/json' },
      body:       JSON.stringify({ url: session.url }),
    };

  } catch (err) {
    console.error('customer-portal error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};
