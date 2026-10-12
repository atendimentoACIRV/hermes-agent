import assert from 'node:assert/strict'
import vm from 'node:vm'
import { test } from 'vitest'
import { domRevisionProbeScript } from './workstation-browser-dom-revision'

test('SPA-01: structural observer increments revision for same-node text and attribute changes', () => {
  const records: Array<{ kind: string }> = []
  class Observer {
    constructor(readonly callback: (records: object[]) => void) {}
    observe() {}
    disconnect() {}
    takeRecords() { return records.splice(0) }
  }
  const documentElement = {}
  const elements: Array<{ shadowRoot?: object }> = []
  const ctx = {
    window: {},
    document: { documentElement, getElementsByTagName: () => elements },
    MutationObserver: Observer
  }
  const script = domRevisionProbeScript()
  const a = vm.runInNewContext(script, ctx)
  assert.equal(a.cacheable, true)
  assert.equal(a.revision, 0)
  records.push({kind:'characterData'})
  const b = vm.runInNewContext(script, ctx)
  assert.equal(b.revision, 1)
  assert.equal(b.generation, a.generation)
  records.push({kind:'attributes'})
  assert.equal(vm.runInNewContext(script, ctx).revision, 2)
})

test('SPA-02: new document element invalidates old generation', () => {
  const ctx = {
    window: {},
    document: { documentElement: {}, getElementsByTagName: () => [] },
    MutationObserver: class { observe() {} disconnect() {} takeRecords() { return [] } }
  }
  const before = vm.runInNewContext(domRevisionProbeScript(), ctx)
  ctx.document.documentElement = {}
  const after = vm.runInNewContext(domRevisionProbeScript(), ctx)
  assert.ok(after.generation > before.generation)
  assert.equal(after.revision, 0)
})

test('SPA-03: Shadow DOM and unavailable observer fail closed to no cache', () => {
  const ctx = {
    window: {},
    document: { documentElement: {}, getElementsByTagName: () => [{shadowRoot:{}}] },
    MutationObserver: class { observe() {} disconnect() {} takeRecords() { return [] } }
  }
  assert.equal(vm.runInNewContext(domRevisionProbeScript(), ctx).cacheable, false)
  const without = {...ctx, MutationObserver: undefined }
  assert.equal(vm.runInNewContext(domRevisionProbeScript(), without).cacheable, false)
})
