import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { afterEach, test, vi } from 'vitest'

const electron = vi.hoisted(() => {
  type Listener = (...args: unknown[]) => void
  const windows: FakeBrowserWindow[] = []

  class FakeWebContents {
    private destroyed = false
    private readonly listeners = new Map<string, Listener[]>()
    private title = ''
    private url = 'about:blank'
    frameRate = 60
    focused = false
    readonly navigationHistory = {
      canGoBack: () => false,
      canGoForward: () => false,
      goBack: () => undefined,
      goForward: () => undefined
    }
    readonly debugger = {
      isAttached: () => false,
      attach: () => undefined,
      sendCommand: async () => ({})
    }

    on(event: string, listener: Listener): this {
      const current = this.listeners.get(event) ?? []
      current.push(listener)
      this.listeners.set(event, current)
      return this
    }

    private emit(event: string, ...args: unknown[]): void {
      for (const listener of this.listeners.get(event) ?? []) {
        listener(...args)
      }
    }

    setWindowOpenHandler(): void {}
    setFrameRate(rate: number): void {
      this.frameRate = rate
    }

    async loadURL(url: string): Promise<void> {
      this.url = url
      this.emit('did-start-loading')
      this.emit('did-navigate')
      this.emit('did-stop-loading')
    }

    getURL(): string {
      return this.url
    }

    getTitle(): string {
      return this.title
    }

    setTitle(title: string): void {
      this.title = title
      this.emit('page-title-updated')
    }

    isDestroyed(): boolean {
      return this.destroyed
    }

    close(): void {
      if (this.destroyed) return
      this.destroyed = true
      this.emit('destroyed')
    }

    focus(): void {
      this.focused = true
    }

    reload(): void {}
    stop(): void {}

    async executeJavaScript(source: string): Promise<unknown> {
      if (source.includes('__hermesWorkstationRefs')) {
        if (source.includes('byRef.get')) {
          return {
            success: true,
            x: 100,
            y: 100,
            target: {
              ref: '@e1',
              tag: 'input',
              role: 'textbox',
              label: 'Field',
              name: 'field'
            }
          }
        }
      }

      if (source.includes('innerHeight')) {
        return { width: 1280, height: 720 }
      }

      return {
        url: this.url,
        title: this.title || 'Example App',
        text: 'Hello world page content',
        totalTextChars: 24,
        truncated: false,
        elements: [
          {
            ref: '@e1',
            tag: 'input',
            role: 'textbox',
            label: 'Field',
            name: 'field',
            value: '',
            x: 100,
            y: 100,
            w: 200,
            h: 40
          }
        ]
      }
    }
  }

  class FakeWebContentsView {
    readonly webContents = new FakeWebContents()
    private bounds = { x: 0, y: 0, width: 0, height: 0 }
    setBackgroundColor(): void {}
    setBounds(bounds: { x: number; y: number; width: number; height: number }): void {
      this.bounds = bounds
    }
    getBounds(): { x: number; y: number; width: number; height: number } {
      return this.bounds
    }
  }

  class FakeBrowserWindow {
    readonly webContents = {
      send: () => undefined
    }
    readonly views: FakeWebContentsView[] = []
    private bounds = { x: 1280, y: 800, width: 1280, height: 800 }
    constructor() {
      windows.push(this)
    }
    static getAllWindows(): FakeBrowserWindow[] {
      return windows.filter(w => !w.isDestroyed())
    }
    getBounds(): { x: number; y: number; width: number; height: number } {
      return this.bounds
    }
    getContentBounds(): { x: number; y: number; width: number; height: number } {
      return this.bounds
    }
    isDestroyed(): boolean {
      return false
    }
    close(): void {}
    contentView = {
      addChildView: (view: FakeWebContentsView) => {
        this.views.push(view)
      },
      removeChildView: (view: FakeWebContentsView) => {
        const idx = this.views.indexOf(view)
        if (idx >= 0) this.views.splice(idx, 1)
      }
    }
  }

  return {
    windows,
    app: {
      getPath: (name: string) => path.join(os.tmpdir(), `hermes-app-${name}`),
      isPackaged: false,
      getVersion: () => '1.0.0',
      whenReady: () => new Promise<never>(() => undefined),
      on: () => undefined
    },
    BrowserWindow: FakeBrowserWindow,
    WebContentsView: FakeWebContentsView,
    ipcMain: {
      handle: () => undefined,
      removeHandler: () => undefined
    },
    session: {
      defaultSession: {
        clearCache: async () => undefined
      }
    }
  }
})

vi.mock('electron', () => electron)

import { WorkstationBrowserRuntime } from './workstation-browser-runtime'

const tempHomes: string[] = []

function runtimeHome(): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-batch-test-'))
  tempHomes.push(dir)
  process.env.HERMES_HOME = dir
  return dir
}

afterEach(() => {
  delete process.env.HERMES_HOME
  for (const dir of tempHomes.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true })
  }
})

test('browser_batch_actions executes sequential steps and produces receipts', async () => {
  runtimeHome()
  const runtime = new WorkstationBrowserRuntime()
  const executeControlRequest = (
    runtime as unknown as {
      executeControlRequest(request: Record<string, unknown>): Promise<Record<string, unknown>>
    }
  ).executeControlRequest.bind(runtime)

  await executeControlRequest({
    action: 'browser_navigate',
    task_id: 'task-batch-1',
    arguments: { url: 'https://example.com' }
  })

  const batchResponse = await executeControlRequest({
    action: 'browser_batch_actions',
    task_id: 'task-batch-1',
    operation_id: 'op-batch-test-1',
    arguments: {
      steps: [
        { kind: 'click', ref: '@e1' },
        { kind: 'type', ref: '@e1', text: 'typed text', clear: true },
        { kind: 'press', key: 'Enter' },
        { kind: 'scroll', direction: 'down' }
      ]
    }
  })

  assert.equal(batchResponse.status, 'verified')
  assert.equal(batchResponse.completed_steps, 4)
  assert.equal(batchResponse.verified_steps, 4)
  assert.equal(batchResponse.stopped_at, null)
  const receipts = batchResponse.receipts as Array<string | null>
  assert.equal(receipts.length, 4)
  assert.ok(receipts[0]?.startsWith('op-batch-test-1:0:'))
  assert.ok(receipts[1]?.startsWith('op-batch-test-1:1:'))

  await runtime.destroy()
})

test('browser_batch_actions rejects malformed step before executing any operation', async () => {
  runtimeHome()
  const runtime = new WorkstationBrowserRuntime()
  const executeControlRequest = (
    runtime as unknown as {
      executeControlRequest(request: Record<string, unknown>): Promise<Record<string, unknown>>
    }
  ).executeControlRequest.bind(runtime)

  await executeControlRequest({
    action: 'browser_navigate',
    task_id: 'task-batch-bad',
    arguments: { url: 'https://example.com' }
  })

  const res = await executeControlRequest({
    action: 'browser_batch_actions',
    task_id: 'task-batch-bad',
    arguments: {
      steps: [
        { kind: 'click', ref: '@e1' },
        { kind: 'press', key: '' } // malformed press
      ]
    }
  })

  assert.equal(res.status, 'rejected')
  assert.equal(res.completed_steps, 0)
  assert.equal(res.verified_steps, 0)
  assert.equal(res.stopped_at, 1)

  await runtime.destroy()
})

test('browser_batch_actions halts immediately when human takes over during batch', async () => {
  runtimeHome()
  const runtime = new WorkstationBrowserRuntime()
  const executeControlRequest = (
    runtime as unknown as {
      executeControlRequest(request: Record<string, unknown>): Promise<Record<string, unknown>>
    }
  ).executeControlRequest.bind(runtime)

  await executeControlRequest({
    action: 'browser_navigate',
    task_id: 'task-batch-human',
    arguments: { url: 'https://example.com' }
  })

  // Acquire human control lease on the task
  const taskLifecycle = (runtime as unknown as {
    taskLifecycle(): {
      acquireHumanControl(
        taskId: string,
        details: { sessionId: string | null; tabId: string | null; pageId: number | null; profileScope: string | null },
        ttlMs: number
      ): void
    }
  }).taskLifecycle()
  taskLifecycle.acquireHumanControl(
    'task-batch-human',
    { sessionId: null, tabId: null, pageId: null, profileScope: null },
    60_000
  )

  // When human control is active, agent batch execution must be blocked/rejected
  await assert.rejects(async () => {
    await executeControlRequest({
      action: 'browser_batch_actions',
      task_id: 'task-batch-human',
      arguments: {
        steps: [{ kind: 'click', ref: '@e1' }]
      }
    })
  }, /under human control/)

  await runtime.destroy()
})

test('browser_batch_actions rejects batches exceeding maximum limit (20)', async () => {
  runtimeHome()
  const runtime = new WorkstationBrowserRuntime()
  const executeControlRequest = (
    runtime as unknown as {
      executeControlRequest(request: Record<string, unknown>): Promise<Record<string, unknown>>
    }
  ).executeControlRequest.bind(runtime)

  await executeControlRequest({
    action: 'browser_navigate',
    task_id: 'task-batch-oversize',
    arguments: { url: 'https://example.com' }
  })

  const steps = Array.from({ length: 21 }, () => ({ kind: 'press', key: 'Tab' }))
  const res = await executeControlRequest({
    action: 'browser_batch_actions',
    task_id: 'task-batch-oversize',
    arguments: { steps }
  })

  assert.equal(res.status, 'rejected')
  assert.equal(res.completed_steps, 0)
  assert.equal(res.reason, 'invalid_batch_identity_or_size')

  await runtime.destroy()
})
