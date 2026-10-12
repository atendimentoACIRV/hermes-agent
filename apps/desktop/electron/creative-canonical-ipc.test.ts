import { describe, expect, it, vi } from 'vitest'

import { createCreativeCanonicalBridge } from './creative-canonical-ipc'

const trustedOwner = Object.freeze({
  taskId: 'task-from-main',
  runId: 18,
  sessionId: 'session-from-main',
  profileHome: 'profile-from-main',
  sessionKey: 'secret-from-main'
})

const request = Object.freeze({
  projectId: 'a'.repeat(32),
  expectedRevisionId: 'b'.repeat(32),
  etag: '"' + '1'.repeat(16) + '-' + '2'.repeat(16) + '"',
  transactionId: 'c'.repeat(32),
  command: {
    commandId: 'layer.create',
    params: { composition_id: 'd'.repeat(32), layer_id: 'e'.repeat(32), name: 'By mouse' },
    idempotencyKey: 'mouse-action-1'
  }
})

describe('Creative canonical Electron IPC trust boundary', () => {
  it('denies both reads and writes if main cannot bind an authoritative TaskRun', async () => {
    const open = vi.fn()
    const apply = vi.fn()

    const bridge = createCreativeCanonicalBridge({
      resolveTrustedOwner: () => null,
      open,
      apply
    })

    await expect(bridge.open({ projectId: request.projectId })).rejects.toThrow('creative_owner_unavailable')
    await expect(bridge.apply(request)).rejects.toThrow('creative_owner_unavailable')
    expect(open).not.toHaveBeenCalled()
    expect(apply).not.toHaveBeenCalled()
  })

  it('main forwards only typed edits, binds owner itself and reads back the authoritative head', async () => {
    const open = vi.fn(async () => ({
      project_id: request.projectId, revision_id: request.expectedRevisionId,
      etag: request.etag, source: { project_id: request.projectId, schema_version: 1 }
    }))

    const apply = vi.fn(async (_owner: unknown, _submitted: unknown) => ({ committed: true }))

    const bridge = createCreativeCanonicalBridge({
      resolveTrustedOwner: () => trustedOwner,
      open,
      apply
    })

    const result = await bridge.apply(request)
    expect(apply).toHaveBeenCalledTimes(1)
    const [owner, submitted] = apply.mock.calls[0]
    expect(owner).toEqual(trustedOwner)
    expect(submitted).toEqual(request)
    expect(result).toEqual({ project_id: request.projectId, revision_id: request.expectedRevisionId, etag: request.etag, source: { project_id: request.projectId, schema_version: 1 } })
    expect(open).toHaveBeenCalledWith(trustedOwner, request.projectId)
  })

  it('rejects task/session/actor spoofing and arbitrary command/metadata fields', async () => {
    const apply = vi.fn()

    const bridge = createCreativeCanonicalBridge({
      resolveTrustedOwner: () => trustedOwner, open: vi.fn(), apply
    })

    for (const injected of [
      { ...request, taskId: 'other-task' },
      { ...request, actorId: 'admin' },
      { ...request, sessionKey: 'forged' },
      { ...request, command: { ...request.command, actor: { actor_id: 'admin' } } },
      { ...request, command: { ...request.command, commandId: 'terminal.execute' } },
      { ...request, etag: '' }
    ]) {
      await expect(bridge.apply(injected)).rejects.toThrow('creative_invalid_request')
    }

    expect(apply).not.toHaveBeenCalled()
  })

  it('does not return optimistic UI success when backend rejects 409', async () => {
    const bridge = createCreativeCanonicalBridge({
      resolveTrustedOwner: () => trustedOwner,
      open: vi.fn(),
      apply: vi.fn(async () => { throw new Error('409 Conflict: stale canonical Creative head') })
    })

    await expect(bridge.apply(request)).rejects.toThrow('409 Conflict')
  })

  it('fails closed when the acknowledged head points to the wrong project', async () => {
    const bridge = createCreativeCanonicalBridge({
      resolveTrustedOwner: () => trustedOwner,
      open: vi.fn(async () => ({ project_id: 'f'.repeat(32), revision_id: request.expectedRevisionId, etag: request.etag, source: {} })),
      apply: vi.fn(async () => ({ committed: true }))
    })

    await expect(bridge.apply(request)).rejects.toThrow('creative_head_mismatch')
  })
})


it('IPC registration rejects any renderer that main has not admitted', async () => {
  const handles = new Map<string, (event: unknown, data: unknown) => Promise<unknown>>()

  const ipc = { handle: vi.fn((channel: string, handler: (event: unknown, data: unknown) => Promise<unknown>) => {
    handles.set(channel, handler)
  }) }

  const apply = vi.fn()
  const open = vi.fn()
  const { registerCreativeCanonicalHandlers } = await import('./creative-canonical-ipc')
  registerCreativeCanonicalHandlers(ipc, {
    resolveTrustedOwner: () => trustedOwner,
    open,
    apply
  }, event => event === 'admitted-renderer')
  await expect(handles.get('hermes:creative:canonical:open')!('untrusted-renderer', { projectId: request.projectId }))
    .rejects.toThrow('creative_sender_denied')
  await expect(handles.get('hermes:creative:canonical:apply')!('untrusted-renderer', request))
    .rejects.toThrow('creative_sender_denied')
  expect(open).not.toHaveBeenCalled()
  expect(apply).not.toHaveBeenCalled()
  expect(ipc.handle).toHaveBeenCalledTimes(2)
})
