// netlify/functions/update-subscription.js
//
// Called by billing.js whenever a student adds or removes a subject.
// Updates the Stripe subscription quantity so billing adjusts
// automatically — Stripe prorates mid-cycle changes.
//
// Environment variables (Netlify → Site → Environment variables):
//   STRIPE_SECRET_KEY

const Stripe = require('stripe');
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// ── Paste your real Price IDs here ─────────────────────────
const PRICES = {
  base:      'price_1TEdRbPvnbx5MPYyExQIlaBK',   // $7.99/mo — 2 subjects
  extra:     'price_1TEdUJPvnbx5MPYy6luOiFjv',   // $2.99/mo per unit (metered add-on)
  cap:       'price_1TEdW3Pvnbx5MPYykHvvk7gf',   // $19.99/mo — unlimited (up to 7)
  flex_base: 'price_1TEdZRPvnbx5MPYylioNhNQI',   // $19.99/mo — flex base
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
    const { subscription_id, subject_count, plan_mode } = JSON.parse(event.body);

    if (!subscription_id || !subject_count) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing subscription_id or subject_count' }),
      };
    }

    const stripeSub  = await stripe.subscriptions.retrieve(subscription_id);
    const planType   = getPlanType(subject_count, plan_mode);
    const updatedItems = buildUpdatedItems(stripeSub.items.data, subject_count, planType);

    if (updatedItems && updatedItems.length > 0) {
      await stripe.subscriptions.update(subscription_id, {
        items:              updatedItems,
        proration_behavior: 'create_prorations',
        metadata: {
          subject_count: String(subject_count),
          plan_mode:     plan_mode || 'swap',
        },
      });
    } else {
      await stripe.subscriptions.update(subscription_id, {
        metadata: {
          subject_count: String(subject_count),
          plan_mode:     plan_mode || 'swap',
        },
      });
    }

    return {
      statusCode: 200,
      headers:    { 'Content-Type': 'application/json' },
      body:       JSON.stringify({ ok: true, plan: planType, subjects: subject_count }),
    };

  } catch (err) {
    console.error('update-subscription error:', err);
    return {
      statusCode: 500,
      body:       JSON.stringify({ error: err.message }),
    };
  }
};

// ── HELPERS ──────────────────────────────────────────────────

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
  const ids = currentItems.map(i => i.price.id);
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
      if (item.price.id === PRICES.cap)   updated.push({ id: item.id, deleted: true });
      if (item.price.id === PRICES.extra) updated.push({ id: item.id, quantity: flexExtras });
    });
    if (!hasFlexBase) updated.push({ price: PRICES.flex_base, quantity: 1 });
    if (!hasExtra)    updated.push({ price: PRICES.extra,     quantity: flexExtras });
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
