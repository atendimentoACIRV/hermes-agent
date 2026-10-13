import { act, render, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { WorkstationBrowserBridge, WorkstationBrowserState } from '@/app/browser/types'
import { PaneVisibleContext } from '@/components/pane-shell/pane-visibility'
import { $activeSessionId, $selectedStoredSessionId, $sessions } from '@/store/session'
import { makeSessionInfo } from '@/test/session-info'

import { WorkstationBrowserPane } from './workstation-browser-pane'

const restoredState: WorkstationBrowserState = {
  runtime: 'electron-chromium',
  ready: true,
  attached: false,
  viewportHost: null,
  backgroundCapable: true,
  paused: false,
  controlOwner: 'agent',
  controlReady: true,
  profilePath: 'test-profile',
  cacheBytes: 0,
  activeTabId: null,
  tabs: [],
  tasks: [
    {
      taskId: 'task-b',
      createdAt: '2026-09-19T00:00:00Z',
      updatedAt: '2026-09-19T00:00:00Z',
      panelHost: null,
      controlHost: null,
      sessionHost: 'session-b',
      kanbanCardId: null,
      runId: null,
      localConnection: null,
      status: 'parked',
      leaseState: null,
      parked: true,
      recoveryState: 'restored'
    }
  ],
  downloads: [],
  lastError: null
}

describe('WorkstationBrowserPane cold attach', () => {
  const originalRect = HTMLElement.prototype.getBoundingClientRect

  beforeEach(() => {
    HTMLElement.prototype.getBoundingClientRect = () =>
      ({ x: 0, y: 0, top: 0, left: 0, right: 900, bottom: 600, width: 900, height: 600, toJSON: () => ({}) }) as DOMRect
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe() {}
        disconnect() {}
      }
    )
    $activeSessionId.set('session-b')
    $selectedStoredSessionId.set(null)
    $sessions.set([makeSessionInfo({ id: 'session-b' })])
  })

  afterEach(() => {
    HTMLElement.prototype.getBoundingClientRect = originalRect
    vi.unstubAllGlobals()
    $activeSessionId.set(null)
    $selectedStoredSessionId.set(null)
    $sessions.set([])
    Reflect.deleteProperty(window, 'hermesDesktop')
  })

  it('discovers restored tasks before the first visual attach and binds that attach to the matching task', async () => {
    const attach = vi.fn(
      async (_bounds: unknown, _host?: string, _preferredTaskId?: string) =>
        ({ ...restoredState, attached: true, viewportHost: 'chat' }) as WorkstationBrowserState
    )

    const bridge = {
      ensure: vi.fn(async () => restoredState),
      attach,
      setBounds: vi.fn(async () => restoredState),
      detach: vi.fn(async () => restoredState),
      setVisible: vi.fn(async () => restoredState),
      onState: vi.fn(() => () => undefined)
    } as unknown as WorkstationBrowserBridge

    Object.defineProperty(window, 'hermesDesktop', {
      configurable: true,
      value: { workstationBrowser: bridge }
    })

    render(<WorkstationBrowserPane />)

    await waitFor(() => expect(bridge.ensure).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(attach).toHaveBeenCalled())

    expect(attach.mock.calls[0]?.[2]).toBe('task-b')
    expect(attach).toHaveBeenCalledTimes(1)

    await act(async () => undefined)
  })

  const paneBridge = (setVisible: ReturnType<typeof vi.fn>, attach: ReturnType<typeof vi.fn>) =>
    ({
      ensure: vi.fn(async () => restoredState),
      attach,
      setBounds: vi.fn(async () => restoredState),
      detach: vi.fn(async () => restoredState),
      setVisible,
      onState: vi.fn(() => () => undefined)
    }) as unknown as WorkstationBrowserBridge

  const chatAttach = () =>
    vi.fn(async () => ({ ...restoredState, attached: true, viewportHost: 'chat' }) as WorkstationBrowserState)

  it('parks the native view while the pane is an inactive keep-alive tab', async () => {
    // A kept-alive tab renders with `visibility: hidden`, which preserves its
    // layout box — so its rect is identical to the visible tab's. The native
    // view is an OS-level child of the window content view: left attached, it
    // paints over that tab and swallows its clicks.
    const setVisible = vi.fn(async () => restoredState)
    const attach = chatAttach()

    Object.defineProperty(window, 'hermesDesktop', {
      configurable: true,
      value: { workstationBrowser: paneBridge(setVisible, attach) }
    })

    render(
      <PaneVisibleContext value={false}>
        <WorkstationBrowserPane />
      </PaneVisibleContext>
    )

    await waitFor(() => expect(setVisible).toHaveBeenCalledWith(false, 'chat'))

    expect(setVisible).not.toHaveBeenCalledWith(true, 'chat')
  })

  it('shows the view again when the pane becomes the visible tab', async () => {
    const setVisible = vi.fn(async () => restoredState)
    const attach = chatAttach()

    Object.defineProperty(window, 'hermesDesktop', {
      configurable: true,
      value: { workstationBrowser: paneBridge(setVisible, attach) }
    })

    const { rerender } = render(
      <PaneVisibleContext value={false}>
        <WorkstationBrowserPane />
      </PaneVisibleContext>
    )

    await waitFor(() => expect(setVisible).toHaveBeenCalledWith(false, 'chat'))

    rerender(
      <PaneVisibleContext value={true}>
        <WorkstationBrowserPane />
      </PaneVisibleContext>
    )

    await waitFor(() => expect(setVisible).toHaveBeenCalledWith(true, 'chat'))
  })

  it('parks the view when the host box collapses instead of leaving it at stale bounds', async () => {
    HTMLElement.prototype.getBoundingClientRect = () =>
      ({ x: 0, y: 0, top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0, toJSON: () => ({}) }) as DOMRect

    const setVisible = vi.fn(async () => restoredState)
    const attach = chatAttach()

    Object.defineProperty(window, 'hermesDesktop', {
      configurable: true,
      value: { workstationBrowser: paneBridge(setVisible, attach) }
    })

    render(<WorkstationBrowserPane />)

    await waitFor(() => expect(setVisible).toHaveBeenCalledWith(false, 'chat'))

    // A zero-area host has no bounds to hand the runtime, so nothing attaches.
    expect(attach).not.toHaveBeenCalled()
  })
})
