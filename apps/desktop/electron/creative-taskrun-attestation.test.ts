import { describe, expect, it, vi } from 'vitest'

import { createCreativeTaskRunOwnerResolver, type CreativeBackendAttestation, type CreativeSenderScope } from './creative-taskrun-attestation'

const sender = { id: 12 }

const scope: CreativeSenderScope = Object.freeze({
  webContentsId: 12, navigationEpoch: 3, connectionId: 'conn-1',
  profile: 'default', sessionId: 'session-1'
})

const attested: CreativeBackendAttestation = Object.freeze({
  connectionId: 'conn-1', profile: 'default', sessionId: 'session-1',
  taskId: 'task-1', runId: 7, profileHome: 'C:/Hermes/default',
  sessionKey: 'backend-session-secret', actorId: 'authenticated-human',
  authorized: true, humanControlActive: false, expiresAt: 1200
})

function harness(overrides: Partial<typeof attested> = {}) {
  let current = { ...scope }
  let proof = { ...attested, ...overrides }
  const attestBackend = vi.fn(async () => proof)
  const readSenderScope = vi.fn((event: unknown) => event === sender ? { ...current } : null)
  const resolve = createCreativeTaskRunOwnerResolver({ readSenderScope, attestBackend, now: () => 1000 })

  return { resolve, attestBackend, setScope: (next: Partial<typeof scope>) => { current = { ...current, ...next } },
    setProof: (next: Partial<typeof attested>) => { proof = { ...proof, ...next } } }
}

describe('HCW P0A main-owned sender / backend attestation boundary', () => {
  it('admits a live attested sender, never a user supplied actor', async () => {
    const h = harness()
    await expect(h.resolve(sender)).resolves.toEqual({
      taskId: 'task-1', runId: 7, sessionId: 'session-1',
      profileHome: 'C:/Hermes/default', sessionKey: 'backend-session-secret'
    })
    expect(h.attestBackend).toHaveBeenCalledWith(scope)
  })

  it('rejects wrong Electron window before consulting backend', async () => {
    const h = harness()
    await expect(h.resolve({ id: 99 })).rejects.toThrow('creative_owner_unavailable')
    expect(h.attestBackend).not.toHaveBeenCalled()
  })

  it.each([
    ['connection', { connectionId: 'conn-other' }],
    ['profile', { profile: 'other' }],
    ['session', { sessionId: 'session-other' }],
    ['ended TaskRun', { authorized: false }],
    ['human control active', { humanControlActive: true }],
    ['missing actor principal', { actorId: '' }],
    ['expired lease', { expiresAt: 999 }],
    ['overlong lease', { expiresAt: 120_000 }],
    ['noncanonical run', { runId: 0 }]
  ])('rejects invalid backend proof: %s', async (_reason, altered) => {
    const h = harness(altered)
    await expect(h.resolve(sender)).rejects.toThrow('creative_owner_unavailable')
  })

  it('rejects renderer navigation during backend verification', async () => {
    let continueProof!: (value: typeof attested) => void
    const readSenderScope = vi.fn(() => ({ ...scope }))
    const attestBackend = () => new Promise<typeof attested>(resolve => { continueProof = resolve })

    const resolve = createCreativeTaskRunOwnerResolver({
      readSenderScope, attestBackend, now: () => 1000
    })

    const pending = resolve(sender)
    readSenderScope.mockImplementation(() => ({ ...scope, navigationEpoch: 4 }))
    continueProof(attested)
    await expect(pending).rejects.toThrow('creative_owner_changed')
  })

  it('rejects connection rehome during backend verification', async () => {
    let continueProof!: (value: typeof attested) => void
    const h = { current: { ...scope } }

    const resolve = createCreativeTaskRunOwnerResolver({
      readSenderScope: () => ({ ...h.current }),
      attestBackend: () => new Promise<typeof attested>(done => { continueProof = done }),
      now: () => 1000
    })

    const pending = resolve(sender)
    h.current = { ...scope, connectionId: 'conn-2' }
    continueProof(attested)
    await expect(pending).rejects.toThrow('creative_owner_changed')
  })

  it('refuses a backend attestation that has been revoked between operations', async () => {
    const h = harness()
    await h.resolve(sender)
    h.setProof({ authorized: false })
    await expect(h.resolve(sender)).rejects.toThrow('creative_owner_unavailable')
  })
})
