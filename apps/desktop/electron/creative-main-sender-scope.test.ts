import { describe, expect, it } from 'vitest'

import { createCreativeMainSenderScopeRegistry } from './creative-main-sender-scope'

function sender(id: number) {
  const mainFrame = {}
  let destroyed = false

  return {
    id, mainFrame, isDestroyed: () => destroyed,
    destroy: () => { destroyed = true }
  }
}

const session = { connectionId: 'conn-1', profile: 'default', sessionId: 'session-1' }

describe('HCW P0A main-owned sender scope registry', () => {
  it('returns a scope only to the exact registered Electron WebContents object and main frame', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    const owner = sender(10)
    registry.bind(owner, session)
    expect(registry.read({ sender: owner, senderFrame: owner.mainFrame })).toMatchObject({
      webContentsId: 10, connectionId: 'conn-1', profile: 'default', sessionId: 'session-1'
    })
    expect(registry.read({ sender: sender(10), senderFrame: owner.mainFrame })).toBeNull()
    expect(registry.read({ sender: owner, senderFrame: {} })).toBeNull()
  })

  it('refuses ambiguous concurrent windows for the same mutation session', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    registry.bind(sender(10), session)
    expect(() => registry.bind(sender(11), session)).toThrow('creative_session_already_bound')
  })

  it('invalidates old proof on navigation and does not silently rebind', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    const owner = sender(10)
    registry.bind(owner, session)
    const previous = registry.read({ sender: owner, senderFrame: owner.mainFrame })
    registry.navigate(owner)
    expect(registry.read({ sender: owner, senderFrame: owner.mainFrame })).toBeNull()
    registry.bind(owner, session)
    const current = registry.read({ sender: owner, senderFrame: owner.mainFrame })
    expect(current?.navigationEpoch).toBeGreaterThan(previous!.navigationEpoch)
  })

  it('rehome revokes the prior scope even if a backend request is in flight', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    const owner = sender(10)
    registry.bind(owner, session)
    const previous = registry.read({ sender: owner, senderFrame: owner.mainFrame })
    registry.bind(owner, { ...session, connectionId: 'conn-2' })
    const current = registry.read({ sender: owner, senderFrame: owner.mainFrame })
    expect(current?.connectionId).toBe('conn-2')
    expect(current?.navigationEpoch).toBeGreaterThan(previous!.navigationEpoch)
  })

  it('rejects revocation, destroyed window and incomplete owner selector', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    const owner = sender(10)
    expect(() => registry.bind(owner, { ...session, sessionId: '' })).toThrow('creative_scope_invalid')
    registry.bind(owner, session)
    registry.revoke(owner)
    expect(registry.read({ sender: owner, senderFrame: owner.mainFrame })).toBeNull()
    registry.bind(owner, session)
    owner.destroy()
    expect(registry.read({ sender: owner, senderFrame: owner.mainFrame })).toBeNull()
  })

  it('returns an immutable copy, never exposing registry state', () => {
    const registry = createCreativeMainSenderScopeRegistry()
    const owner = sender(10)
    registry.bind(owner, session)
    const first = registry.read({ sender: owner, senderFrame: owner.mainFrame })!
    first.sessionId = 'forged'
    expect(registry.read({ sender: owner, senderFrame: owner.mainFrame })?.sessionId)
      .toBe('session-1')
  })
})
