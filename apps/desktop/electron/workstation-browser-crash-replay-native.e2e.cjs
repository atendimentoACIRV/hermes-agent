'use strict'
require('tsx/cjs')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { app, BrowserWindow } = require('electron')
const phase = process.env.HERMES_C2C_CRASH_PHASE
const root = process.env.HERMES_C2C_CRASH_ROOT
const base = process.env.HERMES_C2C_FIXTURE_ORIGIN
if (!root || !base || !['A', 'B'].includes(phase)) throw new Error('isolated_test_identity_required')
process.env.HERMES_HOME = path.join(root, 'hermes')
process.env.HERMES_WORKSTATION_HOME = path.join(root, 'workstation')
process.env.HERMES_WORKSTATION_BROWSER_PROFILE = path.join(root, 'profile')
process.env.HERMES_WORKSTATION_BROWSER_CONTROL_FILE = path.join(root, 'control.json')
process.env.HERMES_WORKSTATION_BROWSER_TASK_FILE = path.join(root, 'tasks.json')
process.env.HERMES_TEST_ISOLATION = root
app.setPath('userData', path.join(root, 'electron'))
let runtime
let window
async function execute() {
  const { WorkstationBrowserRuntime } = require('./workstation-browser-runtime.ts')
  runtime = new WorkstationBrowserRuntime()
  const request = {
    action: 'browser_navigate', task_id: 'crash-task',
    session_id: 'crash-session', run_id: 'crash-run',
    operation_id: 'op-crash-after-effect',
    arguments: { url: base + '/effect' }
  }
  if (phase === 'A') {
    window = new BrowserWindow({ show: false, width: 840, height: 640, webPreferences: { sandbox: true } })
    await window.loadURL('data:text/html,<title>Hermes crash harness host</title>')
    runtime.createTask({ taskId: 'crash-task', sessionHost: 'crash-session', runId: 'crash-run' })
    runtime.showTask('crash-task', window, { x: 0, y: 0, width: 800, height: 600 })
    const tab = runtime.state().tabs.find(t => t.ownerTaskId === 'crash-task')
    assert.ok(tab)
    const wc = runtime.getWebContents(tab.id)
    assert.ok(wc && !wc.isDestroyed())
    // Fault injection after real HTTP page load performs an observable local
    // server-side effect, but before BrowserOwnerReceipt is recorded.
    const originalLoadURL = wc.loadURL.bind(wc)
    wc.loadURL = async function (...args) {
      await originalLoadURL(...args)
      for (let i = 0; i < 70; i++) {
        const count = await (await fetch(base + '/count')).json()
        if (count.effects === 1) {
          fs.writeFileSync(path.join(root, 'effect-ack-marker'), 'seen\n')
          process.exit(86)
        }
        await new Promise(resolve => setTimeout(resolve, 40))
      }
      throw new Error('effect_not_observed_before_crash')
    }
    await runtime.executeControlRequest(request)
    throw new Error('failed_to_crash_after_effect')
  }
  const result = await runtime.executeControlRequest(request)
  assert.equal(result.status, 'uncertain')
  assert.equal(result.reason, 'prior_operation_requires_reconciliation')
  assert.equal(result.idempotent_replay, true)
  assert.equal(runtime.entries.size, 0, 'replay must be fenced before lazy BrowserTask view materialization')
  // Restored-tab navigation is asynchronous; observe after it has had time to
  // dispatch rather than only sampling immediately after the replay fence.
  await new Promise(resolve => setTimeout(resolve, 750))
  const check = await (await fetch(base + '/count')).json()
  assert.equal(check.effects, 1, 'do not redispatch HTTP navigation after uncertain effect')
  // A read-only snapshot must not implicitly replay a pending navigation by
  // lazily restoring the old task URL after the owner crashed mid-operation.
  window = new BrowserWindow({ show: false, width: 840, height: 640, webPreferences: { sandbox: true } })
  await window.loadURL('data:text/html,<title>Hermes restored crash fixture host</title>')
  runtime.showTask('crash-task', window, { x: 0, y: 0, width: 800, height: 600 })
  const snapshotTimeout = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('restored_readonly_snapshot_timed_out')), 10000).unref?.()
  })
  const restoredSnapshot = await Promise.race([runtime.executeControlRequest({
    action: 'browser_snapshot', task_id: 'crash-task',
    session_id: 'crash-session', run_id: 'crash-run', arguments: {}
  }), snapshotTimeout])
  assert.equal(restoredSnapshot.success, true, 'blank restored page supports read-only snapshot')
  const restored = runtime.state().tabs.find(tab => tab.ownerTaskId === 'crash-task')
  assert.ok(restored)
  assert.equal(runtime.getWebContents(restored.id).getURL(), 'about:blank', 'uncertain navigation is not restored')
  await new Promise(resolve => setTimeout(resolve, 750))
  const afterSnapshot = await (await fetch(base + '/count')).json()
  assert.equal(afterSnapshot.effects, 1, 'read-only recovery must not cause a second external effect')
  process.stdout.write('CRASH_REPLAY_CHILD_B_PASS effects=' + check.effects + '\n')
}
app.whenReady().then(execute).then(async () => {
  await runtime?.destroy()
  window?.destroy()
  app.quit()
}).catch(async error => {
  process.stderr.write('CRASH_REPLAY_CHILD_FAIL ' + String(error?.stack ?? error) + '\n')
  try { await runtime?.destroy() } catch {}
  try { window?.destroy() } catch {}
  app.exit(1)
})
