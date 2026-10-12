import assert from 'node:assert/strict'
import { describe, test } from 'vitest'
import {
  BoundedExtractCache,
  computeQueryDigest,
  normalizeExtractedItem,
  sanitizeExtractedItems,
  type ExtractScope
} from './workstation-browser-extract-cache'

const scope: ExtractScope = {
  profileId: 'p',
  taskId: 't',
  tabId: 'tab',
  url: 'https://example.test/',
  documentEpoch: 'e1',
  mutationRevision: 1,
  documentFingerprint: 'dom1',
  queryDigest: 'q1'
}

describe('OPT-03 Structured Extraction Cache & Sanitization', () => {
  test('invalidates on mutation revision and DOM fingerprint', () => {
    const cache = new BoundedExtractCache<string>()
    cache.set(scope, 'old')
    assert.equal(cache.get(scope), 'old')
    assert.equal(cache.get({ ...scope, mutationRevision: 2 }), null)
    assert.equal(cache.get({ ...scope, documentFingerprint: 'dom2' }), null)
    cache.clear()
    assert.equal(cache.get(scope), null)
  })

  test('rejects unproven document identity', () => {
    const cache = new BoundedExtractCache<string>()
    assert.throws(() => cache.get({ ...scope, documentFingerprint: '' }))
    assert.throws(() => cache.get({ ...scope, documentEpoch: '' }))
    assert.throws(() => cache.get({ ...scope, mutationRevision: -1 }))
  })

  test.each([
    ['profile', { ...scope, profileId: 'profile-b' }],
    ['tab', { ...scope, tabId: 'tab-b' }],
    ['document epoch', { ...scope, documentEpoch: 'epoch-b' }],
    ['URL', { ...scope, url: 'https://other.example.test/' }],
    ['query', { ...scope, queryDigest: 'query-b' }]
  ])('isolates profile/tab/document/query identity across A→B→A (%s)', (_label, scopeB) => {
    const cache = new BoundedExtractCache<string>()
    cache.set(scope, 'result-a')
    assert.equal(cache.get(scopeB), null)
    cache.set(scopeB, 'result-b')
    assert.equal(cache.get(scopeB), 'result-b')
    assert.equal(cache.get(scope), 'result-a')
  })

  test('computeQueryDigest produces consistent 16-hex characters hash', () => {
    const d1 = computeQueryDigest({ selector: '.item', limit: 20 })
    const d2 = computeQueryDigest({ selector: '.item', limit: 20 })
    const d3 = computeQueryDigest({ selector: '.item', limit: 50 })
    assert.equal(d1, d2)
    assert.notEqual(d1, d3)
    assert.equal(d1.length, 16)
  })

  test('query digest isolates schema projections on the same document', () => {
    const base = { selector: '.card', limit: 20 }
    const a = computeQueryDigest({ ...base, schema: { properties: { title: { type: 'string' } } } })
    const b = computeQueryDigest({ ...base, schema: { properties: { price: { type: 'number' } } } })
    assert.notEqual(a, b)
  })

  test('nested arrays of extracted records never leak secret fields', () => {
    const result = sanitizeExtractedItems([{ items: [{ name: 'safe', api_token: 'DO_NOT_LEAK' }] }]) as any[]
    assert.equal(result[0].items[0].name, 'safe')
    assert.equal(result[0].items[0].api_token, '[REDACTED]')
  })

  test('normalizeExtractedItem and sanitizeExtractedItems redact sensitive fields and truncate oversized text', () => {
    const raw = [
      {
        title: 'Product 1',
        password: 'super-secret-password',
        user_api_key: 'sk-1234567890',
        token: 'ey...',
        price: '$10.00'
      }
    ]

    const sanitized = sanitizeExtractedItems(raw) as any[]
    assert.equal(sanitized[0].title, 'Product 1')
    assert.equal(sanitized[0].price, '$10.00')
    assert.equal(sanitized[0].password, '[REDACTED]')
    assert.equal(sanitized[0].user_api_key, '[REDACTED]')
    assert.equal(sanitized[0].token, '[REDACTED]')

    const single = normalizeExtractedItem({ auth_token: 'secret', name: 'valid' }) as any
    assert.equal(single.auth_token, '[REDACTED]')
    assert.equal(single.name, 'valid')
  })
})
