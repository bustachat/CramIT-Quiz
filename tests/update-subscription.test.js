// tests/update-subscription.test.js
// Pure pricing-tier logic from functions/update-subscription.js. This is the
// highest-risk file in billing — it mutates a LIVE Stripe subscription's
// line items on every subject add/remove, across 4 possible tiers. These
// tests pin the tier-transition math (which items get deleted vs added)
// without touching the real Stripe API.

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { getPlanType, buildUpdatedItems, PRICES } from '../functions/update-subscription.js';

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
