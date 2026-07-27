// tests/update-subscription.test.js
// Pure pricing-tier logic from functions/update-subscription.js. This is the
// highest-risk file in billing — it mutates a LIVE Stripe subscription's
// line items on every subject add/remove, across 4 possible tiers. These
// tests pin the tier-transition math (which items get deleted vs added)
// without touching the real Stripe API.

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  getPlanType, buildUpdatedItems, PRICES,
  getCurrentTierInfo, compareTiers, buildPhaseItems, getExtraQty,
} from '../functions/update-subscription.js';

describe('update-subscription getPlanType()', () => {
  test('0-1 subjects -> free (cancel path)', () => {
    assert.equal(getPlanType(0), 'free');
    assert.equal(getPlanType(1), 'free');
  });

  test('2 subjects -> base', () => {
    assert.equal(getPlanType(2), 'base');
  });

  test('6 subjects -> base_plus, never forced to unlimited', () => {
    assert.equal(getPlanType(6), 'base_plus');
  });

  test('7 subjects, mode=swap -> unlimited', () => {
    assert.equal(getPlanType(7, 'swap'), 'unlimited');
  });

  test('8 subjects, mode=flex -> flex', () => {
    assert.equal(getPlanType(8, 'flex'), 'flex');
  });

  test('8 subjects, mode=swap (no flex opt-in) -> stays unlimited', () => {
    assert.equal(getPlanType(8, 'swap'), 'unlimited');
  });
});

describe('update-subscription buildUpdatedItems() tier transitions', () => {
  test('base_plus -> unlimited: removes base+extra, adds cap', () => {
    const currentItems = [
      { id: 'si_base',  price: { id: PRICES.base } },
      { id: 'si_extra', price: { id: PRICES.extra } },
    ];
    const result = buildUpdatedItems(currentItems, 7, 'unlimited');
    assert.deepEqual(result, [
      { id: 'si_base', deleted: true },
      { id: 'si_extra', deleted: true },
      { price: PRICES.cap, quantity: 1 },
    ]);
  });

  test('unlimited -> flex: removes cap, adds flex_base + extras', () => {
    const currentItems = [
      { id: 'si_cap', price: { id: PRICES.cap } },
    ];
    const result = buildUpdatedItems(currentItems, 9, 'flex');
    assert.deepEqual(result, [
      { id: 'si_cap', deleted: true },
      { price: PRICES.flex_base, quantity: 1 },
      { price: PRICES.extra, quantity: 2 }, // 9 - 7 cap limit
    ]);
  });

  test('flex -> base_plus: removes cap/flex_base, adds base, updates extra qty', () => {
    const currentItems = [
      { id: 'si_flexbase', price: { id: PRICES.flex_base } },
      { id: 'si_extra',    price: { id: PRICES.extra } },
    ];
    const result = buildUpdatedItems(currentItems, 4, 'base_plus');
    assert.deepEqual(result, [
      { id: 'si_flexbase', deleted: true },
      { price: PRICES.base, quantity: 1 },
      { id: 'si_extra', quantity: 2 }, // reuses existing line item, updates qty
    ]);
  });

  test('base_plus -> base: drops the extra line item entirely when subjects fall to 2', () => {
    const currentItems = [
      { id: 'si_base',  price: { id: PRICES.base } },
      { id: 'si_extra', price: { id: PRICES.extra } },
    ];
    const result = buildUpdatedItems(currentItems, 2, 'base');
    assert.deepEqual(result, [
      { id: 'si_extra', deleted: true },
    ]);
  });

  test('already on the target tier: no redundant base item re-added', () => {
    const currentItems = [
      { id: 'si_base', price: { id: PRICES.base } },
    ];
    const result = buildUpdatedItems(currentItems, 2, 'base');
    assert.deepEqual(result, []); // nothing to change
  });
});

describe('getCurrentTierInfo() — reverse-derives tier from live Stripe items', () => {
  test('base only -> base, 0 extras', () => {
    const info = getCurrentTierInfo([{ price: { id: PRICES.base } }]);
    assert.deepEqual(info, { planType: 'base', extraQty: 0 });
  });

  test('base + extra qty 2 -> base_plus, 2 extras', () => {
    const info = getCurrentTierInfo([
      { price: { id: PRICES.base } },
      { price: { id: PRICES.extra }, quantity: 2 },
    ]);
    assert.deepEqual(info, { planType: 'base_plus', extraQty: 2 });
  });

  test('cap present -> unlimited regardless of other items', () => {
    const info = getCurrentTierInfo([{ price: { id: PRICES.cap } }]);
    assert.equal(info.planType, 'unlimited');
  });

  test('flex_base present -> flex', () => {
    const info = getCurrentTierInfo([
      { price: { id: PRICES.flex_base } },
      { price: { id: PRICES.extra }, quantity: 3 },
    ]);
    assert.deepEqual(info, { planType: 'flex', extraQty: 3 });
  });

  test('no recognised items -> free', () => {
    assert.equal(getCurrentTierInfo([]).planType, 'free');
  });
});

describe('compareTiers() — decides upgrade vs downgrade vs same', () => {
  test('base -> base_plus is an upgrade', () => {
    assert.equal(compareTiers({ planType: 'base', extraQty: 0 }, { planType: 'base_plus', extraQty: 1 }), 'upgrade');
  });

  test('unlimited -> base_plus is a downgrade', () => {
    assert.equal(compareTiers({ planType: 'unlimited', extraQty: 0 }, { planType: 'base_plus', extraQty: 4 }), 'downgrade');
  });

  test('same planType, fewer extras -> downgrade', () => {
    assert.equal(compareTiers({ planType: 'base_plus', extraQty: 3 }, { planType: 'base_plus', extraQty: 1 }), 'downgrade');
  });

  test('same planType, more extras -> upgrade', () => {
    assert.equal(compareTiers({ planType: 'base_plus', extraQty: 1 }, { planType: 'base_plus', extraQty: 3 }), 'upgrade');
  });

  test('identical tier and extras -> same (the net-neutral swap case)', () => {
    // This is the exact scenario: remove Multimedia (3 subjects -> 2,
    // base_plus with 0 extras dropping toward base) then immediately add
    // VET back (2 -> 3 again). By the time update-subscription.js
    // recomputes from scratch, target should land back on the SAME tier
    // it started from, so no Stripe call should happen at all.
    assert.equal(compareTiers({ planType: 'base_plus', extraQty: 1 }, { planType: 'base_plus', extraQty: 1 }), 'same');
    assert.equal(compareTiers({ planType: 'unlimited', extraQty: 0 }, { planType: 'unlimited', extraQty: 0 }), 'same');
  });
});

describe('buildPhaseItems() — canonical full item list for a schedule phase', () => {
  test('base_plus: base + correct extras', () => {
    assert.deepEqual(buildPhaseItems(5, 'base_plus'), [
      { price: PRICES.base, quantity: 1 },
      { price: PRICES.extra, quantity: 3 },
    ]);
  });

  test('unlimited: single cap item', () => {
    assert.deepEqual(buildPhaseItems(7, 'unlimited'), [{ price: PRICES.cap, quantity: 1 }]);
  });

  test('flex: flex_base + extras above the 7-subject cap', () => {
    assert.deepEqual(buildPhaseItems(10, 'flex'), [
      { price: PRICES.flex_base, quantity: 1 },
      { price: PRICES.extra, quantity: 3 },
    ]);
  });
});

describe('getExtraQty()', () => {
  test('base_plus at 5 subjects -> 3 extras', () => {
    assert.equal(getExtraQty(5, 'base_plus'), 3);
  });
  test('flex at 10 subjects -> 3 extras above the cap', () => {
    assert.equal(getExtraQty(10, 'flex'), 3);
  });
  test('base/unlimited -> 0 extras', () => {
    assert.equal(getExtraQty(2, 'base'), 0);
    assert.equal(getExtraQty(7, 'unlimited'), 0);
  });
});

describe('End-to-end tier reconciliation — the net-neutral swap scenario', () => {
  test('3 subjects (base_plus) -> remove one (target 2, base) -> downgrade detected', () => {
    const currentItems = [
      { price: { id: PRICES.base } },
      { price: { id: PRICES.extra }, quantity: 1 },
    ];
    const current = getCurrentTierInfo(currentItems);
    const targetCount = 2;
    const targetPlanType = getPlanType(targetCount, 'swap');
    const target = { planType: targetPlanType, extraQty: getExtraQty(targetCount, targetPlanType) };
    assert.equal(compareTiers(current, target), 'downgrade');
  });

  test('...then add a different subject back (target 3 again, base_plus) -> same, zero Stripe change', () => {
    // Same starting Stripe state as above (still billed for 3 subjects —
    // nothing was ever applied to Stripe for the pending downgrade).
    const currentItems = [
      { price: { id: PRICES.base } },
      { price: { id: PRICES.extra }, quantity: 1 },
    ];
    const current = getCurrentTierInfo(currentItems);
    const targetCount = 3; // Multimedia excluded (pending removal), VET added
    const targetPlanType = getPlanType(targetCount, 'swap');
    const target = { planType: targetPlanType, extraQty: getExtraQty(targetCount, targetPlanType) };
    assert.equal(compareTiers(current, target), 'same');
  });
});
