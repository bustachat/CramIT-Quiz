// netlify/functions/create-checkout.js
//
// Creates a Stripe Checkout session for a given subject count + plan.
// Called by billing.js → createCheckoutSession()
//
// Deploy: push to GitHub, Netlify auto-deploys.
// Set env vars in Netlify dashboard → Site → Environment variables:
//   STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

const Stripe = require('stripe');

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// Must match billing.js STRIPE_PRICES
const PRICES = {
  base:      'price_1TEdRbPvnbx5MPYyExQIlaBK',   // $7.99/mo — 2 subjects
  cap:       'price_1TEdW3Pvnbx5MPYykHvvk7gf',   // $19.99/mo — unlimited (up to 7)
  flex_base: 'price_1TEdZRPvnbx5MPYylioNhNQI',   // $19.99/mo — flex base
  extra:     'price_1TEdUJPvnbx5MPYy6luOiFjv',   // $2.99/mo per unit (metered add-on)
};

const PRICING = {
  BASE_PRICE:    7.99,
  EXTRA_PRICE:   2.99,
  CAP_PRICE:     19.99,
  CAP_LIMIT:     7,
  BASE_INCLUDES: 2,
};

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  try {
    const { user_id, subject_count, plan_type, plan_mode, success_url, cancel_url } = JSON.parse(event.body);

    if (!user_id || !subject_count) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing required fields' }) };
    }

    // Build line items based on subject count + plan
    const lineItems = buildLineItems(subject_count, plan_type, plan_mode);

    const session = await stripe.checkout.sessions.create({
      mode:             'subscription',
      payment_method_types: ['card'],
      line_items:       lineItems,
      success_url:      success_url + '&session_id={CHECKOUT_SESSION_ID}',
      cancel_url:       cancel_url,
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
      // Pre-fill email if available
      customer_email: event.headers['x-user-email'] || undefined,
    });

    return {
      statusCode: 200,
      headers:    { 'Content-Type': 'application/json' },
      body:       JSON.stringify({ url: session.url }),
    };

  } catch (err) {
    console.error('create-checkout error:', err);
    return {
      statusCode: 500,
      body:       JSON.stringify({ error: err.message }),
    };
  }
};

function buildLineItems(nSubjects, planType, planMode) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;

  // Free → base (2 subjects)
  if (nSubjects <= BASE_INCLUDES) {
    return [{ price: PRICES.base, quantity: 1 }];
  }

  // Base + extras (below cap)
  if (planType === 'base_plus') {
    const extras = nSubjects - BASE_INCLUDES;
    return [
      { price: PRICES.base,  quantity: 1 },
      { price: PRICES.extra, quantity: extras },
    ];
  }

  // Unlimited cap (up to 7 subjects, swap mode)
  if (planType === 'unlimited') {
    return [{ price: PRICES.cap, quantity: 1 }];
  }

  // Flex plan (above 7 subjects)
  if (planType === 'flex') {
    const flexExtras = nSubjects - CAP_LIMIT;
    return [
      { price: PRICES.flex_base, quantity: 1 },
      { price: PRICES.extra,     quantity: flexExtras },
    ];
  }

  // Fallback — base plan
  return [{ price: PRICES.base, quantity: 1 }];
}
