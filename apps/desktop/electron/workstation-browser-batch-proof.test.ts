import assert from 'node:assert/strict'
import { describe, test } from 'vitest'
import { hasVerifiedBatchEffect, type BatchObservation } from './workstation-browser-batch-proof'

const baseline: BatchObservation = {
  url: 'https://example.test/form',
  documentToken: 'same-renderer-doc',
  elementToken: 3,
  found: true,
  editable: true,
  value: '',
  checked: null,
  pressed: null,
  expanded: null,
  scrollY: 10
}
const verify = (step: any, after: Partial<BatchObservation>, before = baseline) =>
  hasVerifiedBatchEffect(step, before, { ...baseline, ...after })

describe('BROW-N1 authoritative post-action observation', () => {
  test('ACK without independent observation is never verification', () => {
    assert.equal(hasVerifiedBatchEffect({ kind: 'click', ref: '@e1' }, null, null).verified, false)
    assert.equal(verify({ kind: 'click', ref: '@e1' }, {}).verified, false)
  })
  test('typing is verified only when the target value matches readback', () => {
    assert.equal(verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: 'hello' }).verified, true)
    assert.equal(verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: '' }).verified, false)
    assert.equal(
      verify(
        { kind: 'type', ref: '@e1', text: 'world', append: true },
        { value: 'helloworld' },
        { ...baseline, value: 'hello' }
      ).verified,
      true
    )
    assert.equal(
      verify(
        { kind: 'type', ref: '@e1', text: 'world', append: true },
        { value: 'world' },
        { ...baseline, value: 'hello' }
      ).verified,
      false
    )
  })
  test('same URL is insufficient when document or DOM element changed', () => {
    assert.equal(
      verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: 'hello', documentToken: 'another-document' })
        .verified,
      false
    )
    assert.equal(
      verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: 'hello', elementToken: 4 }).verified,
      false
    )
    assert.equal(verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: 'hello', found: false }).verified, false)
    assert.equal(
      verify({ kind: 'type', ref: '@e1', text: 'hello' }, { value: 'hello', url: 'https://example.test/other' })
        .verified,
      false
    )
  })
  test('click only verifies observable target toggle postcondition', () => {
    assert.equal(
      verify({ kind: 'click', ref: '@e1' }, { checked: true }, { ...baseline, checked: false }).verified,
      true
    )
    assert.equal(
      verify({ kind: 'click', ref: '@e1' }, { pressed: 'true' }, { ...baseline, pressed: 'false' }).verified,
      true
    )
    assert.equal(
      verify({ kind: 'click', ref: '@e1' }, { expanded: 'true' }, { ...baseline, expanded: 'false' }).verified,
      true
    )
    assert.equal(
      verify({ kind: 'click', ref: '@e1' }, { checked: false }, { ...baseline, checked: false }).verified,
      false
    )
  })
  test('scroll requires directional visual movement, not wheel dispatch ACK', () => {
    assert.equal(verify({ kind: 'scroll', direction: 'down' }, { scrollY: 120 }).verified, true)
    assert.equal(verify({ kind: 'scroll', direction: 'up' }, { scrollY: 0 }).verified, true)
    assert.equal(verify({ kind: 'scroll', direction: 'down' }, { scrollY: 10 }).verified, false)
    assert.equal(verify({ kind: 'scroll', direction: 'up' }, { scrollY: 120 }).verified, false)
  })
  test('key dispatch is unverified without semantic postcondition', () => {
    assert.equal(verify({ kind: 'press', key: 'Enter' }, {}).verified, false)
  })
})
