// functions/update-subscription.js — Cloudflare Pages Function (ESM)
// Syncs the AUTHENTICATED user's Stripe subscription with their actual
// subject count. Both the subscription ID and the count are looked up
// server-side — the request body is never trusted for identity, only for
// which subject_id the client wants to add/remove.
//
// Upgrades (more subjects) are applied immediately, same as before.
// Downgrades (fewer subjects) are DEFERRED to the end of the current
// billing period via a Stripe Subscription Schedule — no immediate
// proration/credit, access continues until the period ends, and the
// price only drops at the natural renewal boundary. This mirrors common
// SaaS practice (upgrade now, downgrade at renewal) and avoids crediting
// back money the student already paid for this cycle.
//
// A same-tier swap (remove one subject, add a different one, net
// subject count unchanged) results in ZERO Stripe calls — see
// compareTiers() below — while the removed subject's own access still
// naturally lapses at the period end it was already stamped with.

import Stripe from 'stripe';
import {
  corsHeaders, requireUser, unauthorized,
  getSubscriptionRow, getSubjectSelectionsWithPending,
} from './_lib/auth.js';

export const PRICES = {
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

const TIER_RANK = { free: 0, base: 1, base_plus: 2, unlimited: 3, flex: 4 };

export async function onRequestOptions(context) {
  return new Response(null, { status: 204, headers: corsHeaders(context.request) });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const CORS = corsHeaders(request);

  const user = await requireUser(request, env);
  if (!user) return unauthorized(CORS);

  let body = {};
  try { body = await request.json(); } catch { /* legacy bare calls send no body */ }
  const { action, subject_id } = body; // action: 'add' | 'remove' | undefined

  try {
    const sub = await getSubscriptionRow(user.id, env, 'stripe_subscription_id,plan,status,stripe_schedule_id');
    if (!sub?.stripe_subscription_id) {
      return new Response(
        JSON.stringify({ error: 'No active subscription found for your login.' }),
        { status: 404, headers: { 'Content-Type': 'application/json', ...CORS } }
      );
    }

    const subscription_id = sub.stripe_subscription_id;
    const plan_mode        = sub.plan === 'flex' ? 'flex' : 'swap';
    const stripe            = new Stripe(env.STRIPE_SECRET_KEY);

    // ── Apply the client's add/remove intent to subject_selections first ──
    // (Both writes use the service-role key so no new RLS grant is needed
    // client-side, and the server can stamp the authoritative period end.)
    if (action === 'remove' && subject_id) {
      const stripeSubForStamp = await stripe.subscriptions.retrieve(subscription_id);
      const periodEndIso = new Date(stripeSubForStamp.current_period_end * 1000).toISOString();
      await stampPendingRemoval(user.id, subject_id, periodEndIso, env);
    } else if (action === 'add' && subject_id) {
      await ensureSubjectSelected(user.id, subject_id, env);
    }

    // ── Recompute the TARGET subject count/tier from scratch ──
    // A row with pending_removal_at set is on its way out — it still
    // grants access (checked client-side against the timestamp) but no
    // longer counts toward what the plan should be priced for.
    const rows = await getSubjectSelectionsWithPending(user.id, env);
    const targetSubjectIds = rows.filter(r => !r.pending_removal_at).map(r => r.subject_id);
    const targetCount = targetSubjectIds.length;

    if (targetCount <= 1) {
      if (sub.stripe_schedule_id) {
        await safeCancelSchedule(stripe, sub.stripe_schedule_id);
      } else {
        await stripe.subscriptions.cancel(subscription_id);
      }
      await setScheduleId(user.id, null, env);
      return new Response(
        JSON.stringify({ ok: true, plan: 'free', subjects: targetCount, cancelled: true }),
        { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } }
      );
    }

    const stripeSub = await stripe.subscriptions.retrieve(subscription_id);
    const targetPlanType = getPlanType(targetCount, plan_mode);
    const currentTier     = getCurrentTierInfo(stripeSub.items.data);
    const targetTier      = { planType: targetPlanType, extraQty: getExtraQty(targetCount, targetPlanType) };
    const change          = compareTiers(currentTier, targetTier);

    let activeScheduleId = sub.stripe_schedule_id || null;
    if (activeScheduleId && !(await scheduleIsActive(stripe, activeScheduleId))) {
      activeScheduleId = null; // a previous downgrade already completed and released itself
    }

    if (change === 'upgrade') {
      if (activeScheduleId) {
        await safeReleaseSchedule(stripe, activeScheduleId);
        activeScheduleId = null;
      }
      const updatedItems = buildUpdatedItems(stripeSub.items.data, targetCount, targetPlanType);
      if (updatedItems.length > 0) {
        await stripe.subscriptions.update(subscription_id, {
          items:              updatedItems,
          proration_behavior: 'create_prorations',
          metadata:           { subject_count: String(targetCount), plan_mode },
        });
      }
      await setScheduleId(user.id, null, env);

    } else if (change === 'downgrade') {
      const phaseItems = buildPhaseItems(targetCount, targetPlanType);
      if (activeScheduleId) {
        await updateDowngradeSchedule(stripe, activeScheduleId, phaseItems);
      } else {
        const schedule = await createDowngradeSchedule(stripe, subscription_id, phaseItems);
        activeScheduleId = schedule.id;
      }
      await setScheduleId(user.id, activeScheduleId, env);

    } else {
      // 'same' — e.g. a like-for-like subject swap. No Stripe billing
      // change needed; release any now-unnecessary pending downgrade.
      if (activeScheduleId) {
        await safeReleaseSchedule(stripe, activeScheduleId);
        activeScheduleId = null;
        await setScheduleId(user.id, null, env);
      }
    }

    return new Response(
      JSON.stringify({ ok: true, plan: targetPlanType, subjects: targetCount, deferred: change === 'downgrade' }),
      { status: 200, headers: { 'Content-Type': 'application/json', ...CORS } }
    );

  } catch (err) {
    console.error('update-subscription error:', err);
    // TEMPORARY (remove once the Subscription Schedule path is proven live):
    // surface Stripe's own diagnostic fields, not just err.message, so a
    // schedule-API failure is actually readable from the client alert
    // instead of needing Cloudflare log access this session doesn't have.
    return new Response(JSON.stringify({
      error:       err.message,
      stripeType:  err.type || null,
      stripeCode:  err.code || null,
      stripeParam: err.param || null,
    }), { status: 500, headers: CORS });
  }
}

export function getPlanType(n, mode) {
  const { BASE_INCLUDES, CAP_LIMIT, BASE_PRICE, EXTRA_PRICE, CAP_PRICE } = PRICING;
  if (n <= 1)             return 'free';
  if (n <= BASE_INCLUDES) return 'base';
  const raw = BASE_PRICE + (n - BASE_INCLUDES) * EXTRA_PRICE;
  if (raw < CAP_PRICE)    return 'base_plus';
  if (n <= CAP_LIMIT)     return 'unlimited';
  if (mode === 'flex')    return 'flex';
  return 'unlimited';
}

// How many `extra` units a given target count/planType needs — used only
// to compare against the currently-billed extra quantity in compareTiers().
export function getExtraQty(n, planType) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;
  if (planType === 'base_plus') return Math.max(0, n - BASE_INCLUDES);
  if (planType === 'flex')      return Math.max(0, n - CAP_LIMIT);
  return 0;
}

// Reverse-derive the currently-billed tier from live Stripe subscription
// items — used to decide upgrade vs downgrade vs no-change.
export function getCurrentTierInfo(currentItems) {
  const ids = currentItems.map(i => i.price.id);
  const extraItem = currentItems.find(i => i.price.id === PRICES.extra);
  const extraQty  = extraItem ? extraItem.quantity : 0;
  let planType;
  if (ids.includes(PRICES.flex_base))               planType = 'flex';
  else if (ids.includes(PRICES.cap))                planType = 'unlimited';
  else if (ids.includes(PRICES.base) && extraQty > 0) planType = 'base_plus';
  else if (ids.includes(PRICES.base))                planType = 'base';
  else                                                planType = 'free';
  return { planType, extraQty };
}

export function compareTiers(current, target) {
  const rankDiff = TIER_RANK[target.planType] - TIER_RANK[current.planType];
  if (rankDiff !== 0) return rankDiff > 0 ? 'upgrade' : 'downgrade';
  if (target.extraQty === current.extraQty) return 'same';
  return target.extraQty > current.extraQty ? 'upgrade' : 'downgrade';
}

// Diff-based item changes for an IMMEDIATE update (upgrades only now).
export function buildUpdatedItems(currentItems, nSubjects, planType) {
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

// Canonical FULL item list for a given target tier — used for the second
// (future) phase of a downgrade schedule, which needs a complete list, not
// a diff. Mirrors create-checkout.js's buildLineItems() (duplicated
// deliberately, same convention as the duplicated PRICES/PRICING constants
// above — the two functions are kept independent per-file in this codebase).
export function buildPhaseItems(nSubjects, planType) {
  const { BASE_INCLUDES, CAP_LIMIT } = PRICING;

  if (planType === 'base') {
    return [{ price: PRICES.base, quantity: 1 }];
  }
  if (planType === 'base_plus') {
    return [
      { price: PRICES.base,  quantity: 1 },
      { price: PRICES.extra, quantity: nSubjects - BASE_INCLUDES },
    ];
  }
  if (planType === 'unlimited') {
    return [{ price: PRICES.cap, quantity: 1 }];
  }
  // flex
  return [
    { price: PRICES.flex_base, quantity: 1 },
    { price: PRICES.extra,     quantity: nSubjects - CAP_LIMIT },
  ];
}

// ── Stripe Subscription Schedule helpers ──────────────────────────────
// NOTE: these calls need a live Stripe Sandbox run to confirm the exact
// wire behavior (phase field shapes, release semantics) — see
// docs/HISTORY.md for the explicit scope boundary on this feature.

async function scheduleIsActive(stripe, scheduleId) {
  try {
    const schedule = await stripe.subscriptionSchedules.retrieve(scheduleId);
    return schedule.status === 'active' || schedule.status === 'not_started';
  } catch {
    return false; // stale/deleted schedule ID — treat as no active schedule
  }
}

async function createDowngradeSchedule(stripe, subscriptionId, phase2Items) {
  const schedule = await stripe.subscriptionSchedules.create({ from_subscription: subscriptionId });
  const phase1 = schedule.phases[0];
  return stripe.subscriptionSchedules.update(schedule.id, {
    end_behavior: 'release',
    phases: [
      {
        items:      phase1.items.map(i => ({ price: typeof i.price === 'string' ? i.price : i.price.id, quantity: i.quantity })),
        start_date: phase1.start_date,
        end_date:   phase1.end_date,
      },
      {
        items:      phase2Items,
        iterations: 1,
      },
    ],
  });
}

async function updateDowngradeSchedule(stripe, scheduleId, phase2Items) {
  const schedule = await stripe.subscriptionSchedules.retrieve(scheduleId);
  const phase1 = schedule.phases[0];
  return stripe.subscriptionSchedules.update(scheduleId, {
    end_behavior: 'release',
    phases: [
      {
        items:      phase1.items.map(i => ({ price: typeof i.price === 'string' ? i.price : i.price.id, quantity: i.quantity })),
        start_date: phase1.start_date,
        end_date:   phase1.end_date,
      },
      {
        items:      phase2Items,
        iterations: 1,
      },
    ],
  });
}

async function safeReleaseSchedule(stripe, scheduleId) {
  try { await stripe.subscriptionSchedules.release(scheduleId); } catch (e) { console.warn('[update-subscription] release schedule failed:', e.message); }
}

async function safeCancelSchedule(stripe, scheduleId) {
  try { await stripe.subscriptionSchedules.cancel(scheduleId); } catch (e) { console.warn('[update-subscription] cancel schedule failed:', e.message); }
}

// ── Supabase writes (service-role, no client RLS grant needed) ────────

async function stampPendingRemoval(userId, subjectId, periodEndIsoOrNull, env) {
  const url = `${env.SUPABASE_URL}/rest/v1/subject_selections?user_id=eq.${encodeURIComponent(userId)}&subject_id=eq.${encodeURIComponent(subjectId)}`;
  await fetch(url, {
    method:  'PATCH',
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
      'Content-Type':  'application/json',
      'Prefer':        'return=minimal',
    },
    body: JSON.stringify({ pending_removal_at: periodEndIsoOrNull }),
  });
}

// Clears any pending removal on the row (undo), inserting it if it
// doesn't exist at all (fallback safety net — the client normally inserts
// new subjects itself).
async function ensureSubjectSelected(userId, subjectId, env) {
  const patchUrl = `${env.SUPABASE_URL}/rest/v1/subject_selections?user_id=eq.${encodeURIComponent(userId)}&subject_id=eq.${encodeURIComponent(subjectId)}`;
  const patchRes = await fetch(patchUrl, {
    method:  'PATCH',
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
      'Content-Type':  'application/json',
      'Prefer':        'return=representation',
    },
    body: JSON.stringify({ pending_removal_at: null }),
  });
  const patched = await patchRes.json().catch(() => []);
  if (Array.isArray(patched) && patched.length > 0) return; // row existed, cleared

  await fetch(`${env.SUPABASE_URL}/rest/v1/subject_selections`, {
    method:  'POST',
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
      'Content-Type':  'application/json',
      'Prefer':        'resolution=ignore-duplicates',
    },
    body: JSON.stringify({ user_id: userId, subject_id: subjectId }),
  });
}

async function setScheduleId(userId, scheduleIdOrNull, env) {
  await fetch(`${env.SUPABASE_URL}/rest/v1/subscriptions?user_id=eq.${encodeURIComponent(userId)}`, {
    method:  'PATCH',
    headers: {
      'apikey':        env.SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
      'Content-Type':  'application/json',
      'Prefer':        'return=minimal',
    },
    body: JSON.stringify({ stripe_schedule_id: scheduleIdOrNull }),
  });
}
