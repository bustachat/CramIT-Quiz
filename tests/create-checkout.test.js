// tests/create-checkout.test.js
// Pure pricing-tier logic from functions/create-checkout.js — no network,
// no Stripe/Supabase calls. Pins down the subject-count -> plan -> line-item
// math so a refactor can't silently change what a student gets billed.

import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { getPlanType, buildLineItems, PRICES } from '../functions/create-checkout.js';

describe('create-checkout getPlanType()', () => {
  test('2 subjects -> base', () => {
    assert.equal(getPlanType(2), 'base');
  });

  test('3-6 subjects -> base_plus (below the $19.99 cap)', () => {
    assert.equal(getPlanType(3), 'base_plus');
    assert.equal(getPlanType(6), 'base_plus'); // $19.95 — must stay base_plus, not unlimited
  });

  test('7 subjects -> unlimited (raw price would hit/exceed the cap)', () => {
    assert.equal(getPlanType(7), 'unlimited');
  });

  test('8+ subjects -> flex', () => {
    assert.equal(getPlanType(8), 'flex');
    assert.equal(getPlanType(20), 'flex');
  });
});

describe('create-checkout buildLineItems()', () => {
  test('base: single base price, qty 1', () => {
    assert.deepEqual(buildLineItems(2, 'base'), [
      { price: PRICES.base, quantity: 1 },
    ]);
  });

  test('base_plus: base + correct number of extras', () => {
    assert.deepEqual(buildLineItems(5, 'base_plus'), [
      { price: PRICES.base, quantity: 1 },
      { price: PRICES.extra, quantity: 3 },
    ]);
  });

  test('unlimited: single cap price regardless of exact count', () => {
    assert.deepEqual(buildLineItems(7, 'unlimited'), [
      { price: PRICES.cap, quantity: 1 },
    ]);
  });

  test('flex: flex_base + extras above the 7-subject cap', () => {
    assert.deepEqual(buildLineItems(10, 'flex'), [
      { price: PRICES.flex_base, quantity: 1 },
      { price: PRICES.extra, quantity: 3 },
    ]);
  });
});
