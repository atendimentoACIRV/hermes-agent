import { expect, it, vi } from 'vitest'

const electron = vi.hoisted(() => ({
  contextBridge: { exposeInMainWorld: vi.fn() },
  ipcRenderer: {
    invoke: vi.fn(async () => ({ acknowledged: true })),
    on: vi.fn(),
    removeListener: vi.fn(),
    sendSync: vi.fn(() => ({}))
  },
  webFrame: {}, webUtils: {}
}))

vi.mock('electron', () => electron)

it('the preload exposes bounded creative open/apply channels and no generic executor', async () => {
  await import('./preload')
  const bridge = electron.contextBridge.exposeInMainWorld.mock.calls[0][1]
  expect(Object.keys(bridge.creativeCanonical).sort()).toEqual(['apply', 'open'])
  await bridge.creativeCanonical.open({ projectId: 'a'.repeat(32) })
  expect(electron.ipcRenderer.invoke).toHaveBeenCalledWith(
    'hermes:creative:canonical:open', { projectId: 'a'.repeat(32) }
  )
  await bridge.creativeCanonical.apply({ projectId: 'a'.repeat(32) })
  expect(electron.ipcRenderer.invoke).toHaveBeenCalledWith(
    'hermes:creative:canonical:apply', { projectId: 'a'.repeat(32) }
  )
})
