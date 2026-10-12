import assert from 'node:assert/strict'
import vm from 'node:vm'
import { test } from 'vitest'
import { tryAccessibilitySnapshot } from './workstation-browser-snapshot'

function fakePage() {
  return {
    isDestroyed: () => false,
    executeJavaScript: async () => ({
      url: 'https://example.test/app',
      title: 'Fixture',
      bodyText: 'A button'
    })
  } as any
}

test('AX snapshots release their CDP node handles as one object group', async () => {
  const calls: Array<{ method: string; params: Record<string, unknown> }> = []
  const cdp = async (method: string, params: Record<string, unknown> = {}): Promise<any> => {
    calls.push({ method, params })
    if (method === 'Accessibility.getFullAXTree') {
      return {
        nodes: [{ nodeId: '1', role: { value: 'button' }, backendDOMNodeId: 42 }]
      }
    }
    if (method === 'DOM.resolveNode') return { object: { objectId: 'remote-object-42' } }
    if (method === 'Runtime.callFunctionOn') {
      return {
        result: {
          value: {
            ref: '@e1',
            tag: 'button',
            role: 'button',
            label: 'Test',
            disabled: false
          }
        }
      }
    }
    return {}
  }

  const result = await tryAccessibilitySnapshot(fakePage(), cdp, false)
  assert.equal(result?.elements.length, 1)
  const resolved = calls.find(c => c.method === 'DOM.resolveNode')
  const releases = calls.filter(c => c.method === 'Runtime.releaseObjectGroup')
  assert.equal(typeof resolved?.params.objectGroup, 'string')
  assert.ok(resolved?.params.objectGroup)
  assert.equal(releases.length, 1)
  assert.equal(releases[0].params.objectGroup, resolved?.params.objectGroup)
})

test('AX snapshot releases CDP handles when mapping throws and falls back', async () => {
  const calls: Array<{ method: string; params: Record<string, unknown> }> = []
  const cdp = async (method: string, params: Record<string, unknown> = {}): Promise<any> => {
    calls.push({ method, params })
    if (method === 'Accessibility.getFullAXTree') {
      return { nodes: [{ nodeId: '1', role: { value: 'button' }, backendDOMNodeId: 43 }] }
    }
    if (method === 'DOM.resolveNode') return { object: { objectId: 'remote-object-43' } }
    if (method === 'Runtime.callFunctionOn') throw new Error('target removed during mapping')
    return {}
  }

  const result = await tryAccessibilitySnapshot(fakePage(), cdp, false)
  assert.equal(result, null)
  const resolved = calls.find(c => c.method === 'DOM.resolveNode')
  const releases = calls.filter(c => c.method === 'Runtime.releaseObjectGroup')
  assert.equal(releases.length, 1)
  assert.equal(releases[0].params.objectGroup, resolved?.params.objectGroup)
})

test('AX snapshots never reassign an existing ref when dynamic elements replace the inventory', async () => {
  const elements = new Map<number, Record<string, unknown>>(
    [101, 102, 103].map(id => [
      id,
      {
        tagName: 'BUTTON',
        innerText: String(id),
        textContent: String(id),
        disabled: false,
        getAttribute: () => null
      }
    ])
  )
  const pageWindow: Record<string, unknown> = {}
  const url = 'https://example.test/spa'
  let visible = [101, 102]
  const cdp = async (method: string, params: Record<string, any> = {}): Promise<any> => {
    if (method === 'Accessibility.getFullAXTree') {
      return {
        nodes: visible.map(id => ({
          nodeId: String(id),
          role: { value: 'button' },
          backendDOMNodeId: id
        }))
      }
    }
    if (method === 'DOM.resolveNode') return { object: { objectId: String(params.backendNodeId) } }
    if (method === 'Runtime.callFunctionOn') {
      const fn = vm.runInNewContext('(' + params.functionDeclaration + ')', {
        window: pageWindow,
        location: { href: url }
      }) as (ref: string) => unknown
      return { result: { value: fn.call(elements.get(Number(params.objectId))) } }
    }
    return {}
  }

  const first = await tryAccessibilitySnapshot(fakePage(), cdp, false)
  assert.deepEqual(
    first?.elements.map(x => x.ref),
    ['@e1', '@e2']
  )
  visible = [103]
  const next = await tryAccessibilitySnapshot(fakePage(), cdp, false)
  assert.ok(next)
  assert.notEqual(next.elements[0].ref, first?.elements[0].ref)
  assert.notEqual(next.elements[0].ref, first?.elements[1].ref)
  visible = [101]
  const restored = await tryAccessibilitySnapshot(fakePage(), cdp, false)
  assert.equal(restored?.elements[0].ref, first?.elements[0].ref)
  const refMap = (pageWindow.__hermesWorkstationRefs as { byRef: Map<string, unknown> }).byRef
  assert.equal(refMap.get(first!.elements[0].ref), elements.get(101))
})
