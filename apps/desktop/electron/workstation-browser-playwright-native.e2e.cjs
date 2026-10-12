/* Isolated, actual Electron/WebContentsView Browser runtime contract harness.
 * Pattern adapted from Playwright tests/electron/electron-webcontentsview.spec.ts
 * (Apache-2.0), without copying Playwright source or creating a browser owner.
 */
'use strict'
require('tsx/cjs')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { app, BrowserWindow, WebContentsView } = require('electron')
const temp = process.env.HERMES_C2C_TEST_ROOT || fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-playwright-native-'))
app.setPath('userData', path.join(temp, 'electron'))
Object.assign(process.env, {
  HERMES_TEST_ISOLATION: temp,
  HERMES_WORKSTATION_HOME: path.join(temp, 'workstation'),
  HERMES_WORKSTATION_BROWSER_PROFILE: path.join(temp, 'profile'),
  HERMES_WORKSTATION_BROWSER_CONTROL_FILE: path.join(temp, 'controller.json'),
  HERMES_WORKSTATION_BROWSER_TASK_FILE: path.join(temp, 'tasks.json'),
  HERMES_HOME: path.join(temp, 'hermes')
})
let runtime
let win
async function run() {
  const { WorkstationBrowserRuntime } = require('./workstation-browser-runtime.ts')
  runtime = new WorkstationBrowserRuntime()
  win = new BrowserWindow({ show: false, width: 900, height: 650, webPreferences: { sandbox: true } })
  await win.loadURL('data:text/html,<title>Hermes Test Host</title>')
  const taskId = 'playwright-c2c-offline'
  runtime.createTask({ taskId, sessionHost: 'offline-session', runId: 'offline-run' })
  runtime.showTask(taskId, win, { x: 0, y: 0, width: 800, height: 600 })
  const state = runtime.state()
  const tab = state.tabs.find(t => t.ownerTaskId === taskId)
  assert.ok(tab, 'BrowserTask owns tab')
  const contents = runtime.getWebContents(tab.id)
  assert.ok(contents && !contents.isDestroyed(), 'one native WebContents')
  const matches = win.contentView.children.filter(v => v instanceof WebContentsView && v.webContents === contents)
  assert.equal(matches.length, 1, 'exactly one Hermes-owned WebContentsView attached')
  const html = '<!doctype html><title>Native fixture</title>' +
    '<button id="act" onclick="document.querySelector(\'#status\').textContent=\'clicked\'">Click</button>' +
    '<span id="status">waiting</span>' +
    '<input id="field" placeholder="offline">' +
    '<iframe title="child" srcdoc="<button>Child</button>"></iframe>'
  await contents.loadURL('data:text/html;charset=UTF-8,' + encodeURIComponent(html))
  const before = await runtime.snapshotForEntry(runtime.entries.get(tab.id), true)
  assert.equal(before.success, true, 'real Chromium inventory')
  const button = before.elements.find(e => e.tag === 'button' && e.label === 'Click')
  assert.ok(button, 'snapshot contains clickable ref')
  await runtime.clickRef(runtime.entries.get(tab.id), button.ref)
  const localReadback = await contents.executeJavaScript('document.querySelector("#status").textContent')
  assert.equal(localReadback, 'clicked', 'real renderer proves DOM effect')
  runtime.takeControl(taskId, 'offline-session')
  assert.throws(() => runtime.assertAgentControl(taskId), /USER_CONTROL_ACTIVE|human|control/i)
  const frameCount = await contents.executeJavaScript('document.querySelectorAll("iframe").length')
  assert.equal(frameCount, 1, 'iframe hosted in same browser view')
  process.stdout.write('NATIVE_E2E_PASS pid=' + process.pid + ' tab=' + tab.id + ' viewCount=' + matches.length + '\n')
}
app.whenReady().then(run).then(async () => {
  await runtime?.destroy()
  win?.destroy()
  // Windows keeps Electron's profile files open until the process exits;
  // the external runner owns cleanup after process termination.
  app.quit()
}).catch(async error => {
  process.stderr.write('NATIVE_E2E_FAIL ' + (error?.stack ?? error) + '\n')
  try { await runtime?.destroy() } catch {}
  try { win?.destroy() } catch {}
  app.exit(1)
})
