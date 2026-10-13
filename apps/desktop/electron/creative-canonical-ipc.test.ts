import { describe, expect, it, vi } from 'vitest'

import { createCreativeCanonicalBridge, type TrustedCreativeOwner } from './creative-canonical-ipc'

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
      project_id: request.projectId, revision_id: 'f'.repeat(32),
      etag: request.etag, source: { project_id: request.projectId, schema_version: 1 }
    }))

    const apply = vi.fn(async (_owner: unknown, _submitted: unknown) => ({
      project_id: request.projectId, revision_id: 'f'.repeat(32)
    }))

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
    expect(result).toEqual({ project_id: request.projectId, revision_id: 'f'.repeat(32), etag: request.etag, source: { project_id: request.projectId, schema_version: 1 } })
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
      apply: vi.fn(async () => ({ project_id: request.projectId, revision_id: 'f'.repeat(32) }))
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


it('binds creative owner per admitted renderer event, never to a global window', async () => {
  const handlers = new Map<string, (event: unknown, data: unknown) => Promise<unknown>>()

  const ipc = { handle: (channel: string, handler: (event: unknown, data: unknown) => Promise<unknown>) => {
    handlers.set(channel, handler)
  } }

  const { registerCreativeCanonicalHandlers } = await import('./creative-canonical-ipc')
  const ownerOne = { ...trustedOwner, taskId: 'owner-one', sessionId: 'session-one' }
  const ownerTwo = { ...trustedOwner, taskId: 'owner-two', sessionId: 'session-two' }

  const resolved = vi.fn((event: unknown) => {
    if (event === 'window-one') {return ownerOne}

    if (event === 'window-two') {return ownerTwo}

    return null
  })

  let committed = false

  const open = vi.fn(async (_owner: unknown) => ({
    project_id: request.projectId,
    revision_id: committed ? 'f'.repeat(32) : request.expectedRevisionId,
    etag: request.etag, source: { project_id: request.projectId, schema_version: 1 }
  }))

  const apply = vi.fn(async (_owner: unknown, _request: unknown) => {
    committed = true

    return { project_id: request.projectId, revision_id: 'f'.repeat(32) }
  })

  registerCreativeCanonicalHandlers(ipc, {
    resolveTrustedOwner: resolved, open, apply
  }, event => event === 'window-one' || event === 'window-two')

  const read = handlers.get('hermes:creative:canonical:open')!
  const mutate = handlers.get('hermes:creative:canonical:apply')!
  await read('window-one', { projectId: request.projectId })
  await read('window-two', { projectId: request.projectId })
  await mutate('window-two', request)
  expect(open.mock.calls[0][0]).toEqual(ownerOne)
  expect(open.mock.calls[1][0]).toEqual(ownerTwo)
  expect(apply.mock.calls[0][0]).toEqual(ownerTwo)
  await expect(mutate('other-window', request)).rejects.toThrow('creative_sender_denied')
  // Each async boundary reattests the sender; unauthorized windows never resolve.
  expect(resolved).toHaveBeenCalledTimes(8)
  expect(resolved.mock.calls.every(([event]) => event === 'window-one' || event === 'window-two')).toBe(true)
})

it('does not acknowledge an edit if the trusted window owner changes during apply', async () => {
  let current: TrustedCreativeOwner = { ...trustedOwner }

  const open = vi.fn(async () => ({
    project_id: request.projectId, revision_id: request.expectedRevisionId,
    etag: request.etag, source: { project_id: request.projectId, schema_version: 1 }
  }))

  const bridge = createCreativeCanonicalBridge({
    resolveTrustedOwner: () => current,
    open,
    apply: async () => {
      current = { ...trustedOwner, taskId: 'other-task' }
    }
  })

  await expect(bridge.apply(request, 'renderer-sender'))
    .rejects.toThrow('creative_owner_changed')
  expect(open).not.toHaveBeenCalled()
})


it('refuses an optimistic readback without a matching backend commit receipt', async () => {
  const after = 'f'.repeat(32)

  const response = {
    project_id: request.projectId, revision_id: after, etag: request.etag,
    source: { project_id: request.projectId, schema_version: 1 }
  }

  const noReceipt = createCreativeCanonicalBridge({
    resolveTrustedOwner: () => trustedOwner,
    apply: vi.fn(async () => ({ committed: true })),
    open: vi.fn(async () => response)
  })

  await expect(noReceipt.apply(request, 'first-window')).rejects.toThrow('creative_commit_mismatch')

  const mismatched = createCreativeCanonicalBridge({
    resolveTrustedOwner: () => trustedOwner,
    apply: vi.fn(async () => ({ project_id: request.projectId, revision_id: 'e'.repeat(32) })),
    open: vi.fn(async () => response)
  })

  await expect(mismatched.apply(request, 'first-window')).rejects.toThrow('creative_commit_mismatch')
})

it('rejects IPC acknowledgement when an allowed renderer navigates away while awaiting commit', async () => {
  let admitted = true
  const handles = new Map<string, (event: unknown, data: unknown) => Promise<unknown>>()

  const open = vi.fn(async () => ({
    project_id: request.projectId, revision_id: 'f'.repeat(32), etag: request.etag,
    source: { project_id: request.projectId, schema_version: 1 }
  }))

  const { registerCreativeCanonicalHandlers } = await import('./creative-canonical-ipc')
  registerCreativeCanonicalHandlers({
    handle: (channel, handler) => { handles.set(channel, handler) }
  }, {
    resolveTrustedOwner: () => trustedOwner,
    apply: async () => {
      admitted = false

      return { project_id: request.projectId, revision_id: 'f'.repeat(32) }
    },
    open
  }, () => admitted)
  await expect(handles.get('hermes:creative:canonical:apply')!('renderer', request))
    .rejects.toThrow('creative_sender_denied')
  expect(open).not.toHaveBeenCalled()
})
