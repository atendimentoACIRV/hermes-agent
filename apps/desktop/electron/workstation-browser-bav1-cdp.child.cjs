'use strict'
/* BAV-01 disposable feasibility process. Never use a real user profile. */
require('tsx/cjs')
const path = require('node:path')
const {app, BrowserWindow, WebContentsView} = require('electron')
const root = process.env.BAV_TEMP_ROOT
if (!root || !process.env.BAV_CDP_PORT || !process.env.BAV_FIXTURE_URL) throw new Error('isolated test config required')
if (process.env.BAV_MODE !== 'controller') {
  app.commandLine.appendSwitch('remote-debugging-address', '127.0.0.1')
  app.commandLine.appendSwitch('remote-debugging-port', process.env.BAV_CDP_PORT)
}
app.setPath('userData', path.join(root, 'electron'))
Object.assign(process.env, {
  HERMES_TEST_ISOLATION: root, HERMES_WORKSTATION_HOME: path.join(root,'workstation'),
  HERMES_WORKSTATION_BROWSER_PROFILE: path.join(root,'profile'),
  HERMES_WORKSTATION_BROWSER_CONTROL_FILE: path.join(root,'controller.json'),
  HERMES_WORKSTATION_BROWSER_TASK_FILE: path.join(root,'tasks.json'),
  HERMES_HOME: path.join(root,'hermes'),
})
let win, runtime
async function start() {
  await app.whenReady()
  const {getWorkstationBrowserRuntime} = require('./workstation-browser-runtime.ts')
  // Use the same official singleton in both test modes.
  runtime = getWorkstationBrowserRuntime()
  win = new BrowserWindow({show: true, width: 900, height: 650, webPreferences: {sandbox: true}})
  await win.loadURL('data:text/html,<title>BAV test host</title>')
  runtime.createTask({taskId:'bav-cdp-test',sessionHost:'offline-session',runId:'bav-run'})
  runtime.showTask('bav-cdp-test',win,{x:0,y:0,width:800,height:600})
  const state=runtime.state()
  const tab=state.tabs.find(t=>t.ownerTaskId==='bav-cdp-test')
  const contents=runtime.getWebContents(tab.id)
  if (win.contentView.children.filter(v=>v instanceof WebContentsView&&v.webContents===contents).length!==1) throw new Error('not a native WebContentsView')
  await contents.loadURL(process.env.BAV_FIXTURE_URL)
  contents.focus()
  const snap=await runtime.snapshotForEntry(runtime.entries.get(tab.id),true)
  if (!snap.success) throw new Error('native snapshot failed')
  process.stdout.write('BAV_READY '+JSON.stringify({tabId:tab.id,webContentsId:contents.id,url:contents.getURL(),debugger:contents.debugger.isAttached()})+'\n')
}
process.on('message',msg=>{if(msg?.type==='close') app.quit()})
app.on('window-all-closed',()=>app.quit())
start().catch(err=>{console.error('BAV_CHILD_ERROR',String(err.stack||err));process.exitCode=1;app.quit()})
