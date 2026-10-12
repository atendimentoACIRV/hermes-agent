import assert from 'node:assert/strict'
import { afterEach, beforeEach, describe, test, vi } from 'vitest'
import {
  hasUsableAXTree,
  isAccessibilitySnapshotEnabled,
  isInteractiveAXNode,
  tryAccessibilitySnapshot,
  type AXNode
} from './workstation-browser-snapshot'

describe('OPT-02 Accessibility Tree Snapshot Provider', () => {
  const originalEnv = process.env.HERMES_BROWSER_AXTREE_ENABLED

  beforeEach(() => {
    delete process.env.HERMES_BROWSER_AXTREE_ENABLED
  })

  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.HERMES_BROWSER_AXTREE_ENABLED = originalEnv
    } else {
      delete process.env.HERMES_BROWSER_AXTREE_ENABLED
    }
  })

  test('feature flag is disabled by default', () => {
    assert.equal(isAccessibilitySnapshotEnabled(), false)
  })

  test('feature flag activates when HERMES_BROWSER_AXTREE_ENABLED is 1 or true', () => {
    process.env.HERMES_BROWSER_AXTREE_ENABLED = '1'
    assert.equal(isAccessibilitySnapshotEnabled(), true)
    process.env.HERMES_BROWSER_AXTREE_ENABLED = 'true'
    assert.equal(isAccessibilitySnapshotEnabled(), true)
    process.env.HERMES_BROWSER_AXTREE_ENABLED = '0'
    assert.equal(isAccessibilitySnapshotEnabled(), false)
  })

  test('identifies interactive AX nodes and filters ignored nodes', () => {
    const buttonNode: AXNode = {
      nodeId: '1',
      role: { value: 'button' },
      name: { value: 'Submit' },
      backendDOMNodeId: 10
    }
    const ignoredButton: AXNode = {
      nodeId: '2',
      role: { value: 'button' },
      ignored: true,
      backendDOMNodeId: 11
    }
    const genericDiv: AXNode = {
      nodeId: '3',
      role: { value: 'generic' },
      backendDOMNodeId: 12
    }
    const textbox: AXNode = {
      nodeId: '4',
      role: { value: 'textbox' },
      backendDOMNodeId: 13
    }

    assert.equal(isInteractiveAXNode(buttonNode), true)
    assert.equal(isInteractiveAXNode(ignoredButton), false)
    assert.equal(isInteractiveAXNode(genericDiv), false)
    assert.equal(isInteractiveAXNode(textbox), true)
  })

  test('hasUsableAXTree requires valid interactive nodes with backendDOMNodeId', () => {
    assert.equal(hasUsableAXTree([]), false)
    assert.equal(
      hasUsableAXTree([
        { nodeId: '1', role: { value: 'generic' } },
        { nodeId: '2', role: { value: 'none' } }
      ]),
      false
    )
    assert.equal(
      hasUsableAXTree([
        { nodeId: '1', role: { value: 'button' }, backendDOMNodeId: 0 }
      ]),
      false
    )
    assert.equal(
      hasUsableAXTree([
        { nodeId: '1', role: { value: 'button' }, backendDOMNodeId: 101 }
      ]),
      true
    )
  })

  test('returns null (falls back) when CDP fails or returns empty tree', async () => {
    const fakeWc = {
      isDestroyed: () => false,
      executeJavaScript: async () => ({})
    } as any

    const cdpFail = async () => {
      throw new Error('CDP session unavailable')
    }

    const res = await tryAccessibilitySnapshot(fakeWc, cdpFail, false, 8000, 100)
    assert.equal(res, null)
  })

  test('returns null (falls back) when WebContents is destroyed', async () => {
    const fakeWc = {
      isDestroyed: () => true,
      executeJavaScript: async () => ({})
    } as any

    const cdp = async () => ({ nodes: [] })
    const res = await tryAccessibilitySnapshot(fakeWc, cdp, false, 8000, 100)
    assert.equal(res, null)
  })

  test('handles shadow DOM, iframe, and editable elements through hybrid mapping', async () => {
    const nodes: AXNode[] = [
      {
        nodeId: 'ax-1',
        role: { value: 'button' },
        name: { value: 'Shadow DOM Button' },
        backendDOMNodeId: 101
      },
      {
        nodeId: 'ax-2',
        role: { value: 'textbox' },
        name: { value: 'Rich Content Editable' },
        backendDOMNodeId: 102
      }
    ]

    const fakeWc = {
      isDestroyed: () => false,
      executeJavaScript: async (script: string) => {
        if (script.includes('bodyText')) {
          return {
            url: 'https://example.com/app',
            title: 'Test App',
            text: 'Hello shadow world',
            totalTextChars: 18,
            documentToken: 'stable-doc'
          }
        }
        return { url: 'https://example.com/app', documentToken: 'stable-doc' }
      }
    } as any

    const cdp = async (method: string, params?: any): Promise<any> => {
      if (method === 'Accessibility.enable') return {}
      if (method === 'Accessibility.getFullAXTree') return { nodes }
      if (method === 'DOM.resolveNode') {
        return { object: { objectId: `obj-${params.backendNodeId}` } }
      }
      if (method === 'Runtime.callFunctionOn') {
        const id = params.objectId
        if (id === 'obj-101') {
          return {
            result: {
              value: {
                ref: '@e1',
                tag: 'button',
                role: 'button',
                label: 'Shadow DOM Button',
                disabled: false
              }
            }
          }
        }
        if (id === 'obj-102') {
          return {
            result: {
              value: {
                ref: '@e2',
                tag: 'div',
                role: 'textbox',
                label: 'Rich Content Editable',
                disabled: false,
                testid: 'rich-editor'
              }
            }
          }
        }
      }
      return {}
    }

    const inventory = await tryAccessibilitySnapshot(fakeWc, cdp, false, 8000, 100)
    assert.ok(inventory)
    assert.equal(inventory.elements.length, 2)
    assert.equal(inventory.elements[0].ref, '@e1')
    assert.equal(inventory.elements[0].label, 'Shadow DOM Button')
    assert.equal(inventory.elements[1].ref, '@e2')
    assert.equal(inventory.elements[1].testid, 'rich-editor')
    assert.equal(inventory.url, 'https://example.com/app')
    assert.equal(inventory.title, 'Test App')
  })

  test('falls back gracefully on canvas / SPA when AX tree has no resolvable interactive elements', async () => {
    // Canvas or WebGL app has a canvas element, but no AX interactive controls
    const canvasNodes: AXNode[] = [
      {
        nodeId: 'ax-canvas',
        role: { value: 'canvas' },
        name: { value: 'WebGL Scene' },
        backendDOMNodeId: 50
      }
    ]

    const fakeWc = {
      isDestroyed: () => false,
      executeJavaScript: async () => ({})
    } as any

    const cdp = async (method: string) => {
      if (method === 'Accessibility.enable') return {}
      if (method === 'Accessibility.getFullAXTree') return { nodes: canvasNodes }
      return {}
    }

    const res = await tryAccessibilitySnapshot(fakeWc, cdp, false, 8000, 100)
    // Canvas node is not interactive role -> hasUsableAXTree returns false -> returns null (triggers fallback)
    assert.equal(res, null)
  })
})
