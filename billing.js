  // billing.js
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
//  HSC Quiz â€” Billing & Subject Access Module
//  Drop this alongside index.html and import it.
//
//  Requires:
//    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
//  Set your keys below.
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const SUPABASE_URL  = 'https://YOUR_PROJECT.supabase.co';
const SUPABASE_ANON = 'YOUR_ANON_KEY';

const { createClient } = supabase;
const db = createClient(SUPABASE_URL, SUPABASE_ANON);

// â”€â”€ PRICING CONSTANTS (must match schema pricing_config) â”€â”€â”€â”€â”€â”€
const PRICING = {
  BASE_PRICE:      7.99,
  EXTRA_PRICE:     2.99,
  CAP_PRICE:       19.99,
  CAP_LIMIT:       7,      // max subjects on unlimited plan
  BASE_INCLUDES:   2,
  FREE_SUBJECTS:   1,
};

// â”€â”€ STRIPE PUBLISHABLE KEY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const STRIPE_PK = 'pk_live_YOUR_PUBLISHABLE_KEY';

// â”€â”€ PRICE IDs from your Stripe dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Create these in Stripe â†’ Products â†’ Add product
const STRIPE_PRICES = {
  base:      'price_1TEdRbPvnbx5MPYyExQIlaBK',   // $7.99/mo â€” 2 subjects
  extra:     'price_1TEdUJPvnbx5MPYy6luOiFjv',   // $2.99/mo per unit (metered add-on)
  cap:       'price_1TEdW3Pvnbx5MPYykHvvk7gf',   // $19.99/mo â€” unlimited (up to 7)
  flex_base: 'price_1TEdZRPvnbx5MPYylioNhNQI',   // $19.99/mo â€” flex base
  flex_extra:'price_1TEdUJPvnbx5MPYy6luOiFjv',   // $2.99/mo per unit above 7
};


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  AUTH
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export async function signUp(email, password, fullName) {
  const { data, error } = await db.auth.signUp({
    email, password,
    options: { data: { full_name: fullName } }
  });
  if (error) throw error;
  return data;
}

export async function signIn(email, password) {
  const { data, error } = await db.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

export async function signInWithGoogle() {
  const { data, error } = await db.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin }
  });
  if (error) throw error;
  return data;
}

export async function signOut() {
  const { error } = await db.auth.signOut();
  if (error) throw error;
}

export async function getCurrentUser() {
  const { data: { user } } = await db.auth.getUser();
  return user;
}

export function onAuthStateChange(callback) {
  return db.auth.onAuthStateChange((event, session) => {
    callback(event, session?.user ?? null);
  });
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  SUBSCRIPTION & SUBJECT STATE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export async function getSubscription(userId) {
  const { data, error } = await db
    .from('subscriptions')
    .select('*')
    .eq('user_id', userId)
    .single();

  if (error && error.code !== 'PGRST116') throw error; // PGRST116 = no rows

  // Default free plan if no subscription exists
  return data ?? {
    plan: 'free',
    subject_count: 1,
    status: 'active',
    flex_extras: 0,
  };
}

export async function getSelectedSubjects(userId) {
  const { data, error } = await db
    .from('subject_selections')
    .select('subject_id, added_at')
    .eq('user_id', userId)
    .order('added_at', { ascending: true });

  if (error) throw error;
  return (data ?? []).map(s => s.subject_id);
}

export async function canAccessSubject(userId, subjectId) {
  const { data, error } = await db
    .rpc('can_access_subject', { p_user_id: userId, p_subject: subjectId });
  if (error) throw error;
  return data === true;
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  SUBJECT SELECTION LOGIC (enforces billing rules client-side)
//  Server enforces the same rules via the webhook â€” belt and braces.
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export async function addSubject(userId, subjectId) {
  const sub      = await getSubscription(userId);
  const selected = await getSelectedSubjects(userId);

  if (selected.includes(subjectId)) return { ok: true, alreadySelected: true };

  const newCount = selected.length + 1;
  const result   = validateSubjectAdd(sub, selected.length, newCount);

  if (!result.allowed) {
    return { ok: false, reason: result.reason, action: result.action };
  }

  // Add to subject_selections
  const { error } = await db
    .from('subject_selections')
    .insert({ user_id: userId, subject_id: subjectId });

  if (error) throw error;

  // If this triggers a plan upgrade, update Stripe subscription
  if (result.requiresUpgrade) {
    await updateStripeSubjectCount(userId, newCount, sub);
  }

  return { ok: true, newPrice: result.newPrice, newPlan: result.newPlan };
}

export async function removeSubject(userId, subjectId) {
  const selected = await getSelectedSubjects(userId);

  if (selected.length <= 1) {
    return { ok: false, reason: 'You must keep at least one subject.' };
  }

  const { error } = await db
    .from('subject_selections')
    .delete()
    .eq('user_id', userId)
    .eq('subject_id', subjectId);

  if (error) throw error;

  const newCount = selected.length - 1;
  await updateStripeSubjectCount(userId, newCount, await getSubscription(userId));

  return { ok: true, newPrice: calculatePrice(newCount, 'swap') };
}

export async function swapSubject(userId, removeId, addId) {
  // Atomic swap for unlimited plan â€” price doesn't change
  const { error: delErr } = await db
    .from('subject_selections')
    .delete()
    .eq('user_id', userId)
    .eq('subject_id', removeId);

  if (delErr) throw delErr;

  const { error: addErr } = await db
    .from('subject_selections')
    .insert({ user_id: userId, subject_id: addId });

  if (addErr) {
    // Rollback
    await db.from('subject_selections').insert({ user_id: userId, subject_id: removeId });
    throw addErr;
  }

  return { ok: true };
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  PRICING CALCULATIONS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export function calculatePrice(nSubjects, planMode = 'swap') {
  const { BASE_PRICE, EXTRA_PRICE, CAP_PRICE, CAP_LIMIT, BASE_INCLUDES } = PRICING;

  if (nSubjects <= 1) return { price: 0,         plan: 'free',      breakdown: 'Free' };
  if (nSubjects <= BASE_INCLUDES) return { price: BASE_PRICE, plan: 'base', breakdown: `$${BASE_PRICE} base plan` };

  const raw = BASE_PRICE + (nSubjects - BASE_INCLUDES) * EXTRA_PRICE;

  if (raw < CAP_PRICE) {
    const extras = nSubjects - BASE_INCLUDES;
    return {
      price:     parseFloat(raw.toFixed(2)),
      plan:      'base_plus',
      breakdown: `$${BASE_PRICE} + ${extras} Ã— $${EXTRA_PRICE}`
    };
  }

  if (nSubjects <= CAP_LIMIT || planMode === 'swap') {
    return { price: CAP_PRICE, plan: 'unlimited', breakdown: `$${CAP_PRICE} cap (${nSubjects} subjects)` };
  }

  // Flex plan â€” above cap limit
  const flexExtras = nSubjects - CAP_LIMIT;
  const flexPrice  = parseFloat((CAP_PRICE + flexExtras * EXTRA_PRICE).toFixed(2));
  return {
    price:     flexPrice,
    plan:      'flex',
    breakdown: `$${CAP_PRICE} + ${flexExtras} Ã— $${EXTRA_PRICE} flex`
  };
}

function validateSubjectAdd(sub, currentCount, newCount) {
  const { CAP_LIMIT } = PRICING;
  const planMode = sub.plan === 'flex' ? 'flex' : 'swap';

  // Free â†’ needs upgrade to add 2nd subject
  if (sub.plan === 'free' && newCount > 1) {
    return {
      allowed: true,
      requiresUpgrade: true,
      ...calculatePrice(newCount, planMode)
    };
  }

  // On swap/unlimited plan â€” block above cap limit
  if (sub.plan === 'unlimited' && planMode === 'swap' && newCount > CAP_LIMIT) {
    return {
      allowed: false,
      reason:  `You've reached the 7-subject cap on your unlimited plan.`,
      action:  'swap_or_upgrade_flex'
    };
  }

  // Everything else is allowed, may require price update
  const newPricing = calculatePrice(newCount, planMode);
  const oldPricing = calculatePrice(currentCount, planMode);

  return {
    allowed: true,
    requiresUpgrade: newPricing.price > oldPricing.price,
    ...newPricing
  };
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  STRIPE CHECKOUT
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export async function createCheckoutSession(userId, nSubjects, planMode = 'swap') {
  const pricing = calculatePrice(nSubjects, planMode);

  // Call your Netlify/Supabase function to create a Stripe checkout session
  const res = await fetch('/functions/create-checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id:       userId,
      subject_count: nSubjects,
      plan_type:     pricing.plan,
      plan_mode:     planMode,
      success_url:   `${window.location.origin}?payment=success`,
      cancel_url:    `${window.location.origin}?payment=cancelled`,
    })
  });

  if (!res.ok) throw new Error('Failed to create checkout session');
  const { url } = await res.json();

  // Redirect to Stripe hosted checkout
  window.location.href = url;
}

export async function openCustomerPortal(userId) {
  const sub = await getSubscription(userId);
  if (!sub.stripe_customer_id) throw new Error('No billing account found');

  const res = await fetch('/functions/customer-portal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      customer_id: sub.stripe_customer_id,
      return_url:  window.location.origin,
    })
  });

  const { url } = await res.json();
  window.location.href = url;
}

async function updateStripeSubjectCount(userId, newCount, sub) {
  if (!sub.stripe_subscription_id) return; // Free plan, no Stripe sub yet

  await fetch('/functions/update-subscription', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      subscription_id: sub.stripe_subscription_id,
      subject_count:   newCount,
      plan_mode:       sub.plan === 'flex' ? 'flex' : 'swap',
    })
  });
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
//  UPGRADE TO FLEX PLAN
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export async function upgradeToFlex(userId) {
  const sub = await getSubscription(userId);
  if (!sub.stripe_subscription_id) throw new Error('No active subscription');

  await fetch('/functions/upgrade-flex', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      subscription_id: sub.stripe_subscription_id,
      user_id:         userId,
    })
  });
}

