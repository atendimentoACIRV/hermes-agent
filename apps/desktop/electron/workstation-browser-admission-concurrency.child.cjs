'use strict'
// Two real OS-level Node processes synchronize immediately before the file
// write to expose a check-then-act admission race deterministically.
require('tsx/cjs')
const fs = require('node:fs')
const path = require('node:path')
const { BrowserSessionStateFilePersistence } = require('./workstation-browser-session-state.ts')
const root = process.argv[2]
const participant = process.argv[3]
if (!root || !['A','B'].includes(participant)) throw Error('fixture_arguments_required')
const file = path.join(root,'browser-session.json')
const store = new BrowserSessionStateFilePersistence(file)
const originalSave = store.save.bind(store)
const pause = new Int32Array(new SharedArrayBuffer(4))
store.save = function(snapshot) {
  fs.writeFileSync(path.join(root, 'ready-' + participant), String(process.pid))
  const deadline = Date.now() + 12000
  while (!fs.existsSync(path.join(root, 'go'))) {
    if (Date.now() > deadline) throw new Error('barrier_timeout')
    Atomics.wait(pause, 0, 0, 20)
  }
  return originalSave(snapshot)
}
const identity = {
  operationId: 'op-concurrent', taskId: 'task-crash-03', sessionId: 'session-crash-03',
  runId: 'run-crash-03', tabId: 'tab-crash-03',
  action: 'browser_click', argumentsDigest: 'a'.repeat(64)
}
try {
  const result = store.admitBrowserMutation(identity)
  console.log('CRASH_03_RESULT ' + JSON.stringify({ participant, pid: process.pid, result }))
} catch (error) {
  console.log('CRASH_03_RESULT ' + JSON.stringify({ participant, pid: process.pid, result: 'rejected', reason: String(error.message) }))
}
