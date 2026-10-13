'use strict'
const assert = require('node:assert/strict')
const fs = require('node:fs')
const http = require('node:http')
const os = require('node:os')
const path = require('node:path')
const { spawn } = require('node:child_process')
const electron = require('electron')

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-crash-replay-'))
let effects = 0
const page = "<!doctype html><html><body><button id='effect' onclick='this.textContent=\"Clicked\";fetch(\"/effect\",{method:\"POST\"})'>Effect</button></body></html>"
const server = http.createServer((request, response) => {
  if (request.method === 'GET' && request.url === '/effect') {
    effects += 1
    response.writeHead(200, { 'content-type': 'application/json' })
    response.end(JSON.stringify({ effects }))
  } else if (request.url === '/count') {
    response.writeHead(200, { 'content-type': 'application/json' })
    response.end(JSON.stringify({ effects }))
  } else if (request.url === '/fixture' && request.method === 'GET') {
    response.writeHead(200, { 'content-type': 'text/html; charset=UTF-8' })
    response.end(page)
  } else {
    response.writeHead(404)
    response.end()
  }
})

function execute(phase, origin) {
  return new Promise((resolve, reject) => {
    const child = spawn(electron, [path.join(__dirname, 'workstation-browser-crash-replay-native.e2e.cjs'), '--no-sandbox'], {
      cwd: path.resolve(__dirname, '..'), windowsHide: true,
      env: { ...process.env, HERMES_C2C_CRASH_PHASE: phase,
        HERMES_C2C_CRASH_ROOT: root, HERMES_C2C_FIXTURE_ORIGIN: origin }
    })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', chunk => { stdout += chunk.toString() })
    child.stderr.on('data', chunk => { stderr += chunk.toString() })
    const timer = setTimeout(() => child.kill(), 45000)
    child.on('error', error => { clearTimeout(timer); reject(error) })
    child.on('exit', (code, signal) => {
      clearTimeout(timer)
      if (stdout) process.stdout.write('CHILD_' + phase + ' ' + stdout)
      if (stderr) process.stderr.write('CHILD_' + phase + ' ' + stderr)
      resolve({ code, signal, pid: child.pid })
    })
  })
}
async function main() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  const address = server.address()
  assert.ok(address && typeof address === 'object')
  const origin = 'http://127.0.0.1:' + address.port
  try {
    const first = await execute('A', origin)
    assert.equal(first.code, 86, 'child A must be forcefully terminated after external effect')
    assert.equal(fs.existsSync(path.join(root, 'effect-ack-marker')), true, 'fixture effect reached server')
    assert.equal(effects, 1, 'exactly one HTTP fixture side effect before restart')
    const persistedFile = path.join(root, 'workstation', 'Runtime', 'browser-session.json')
    const persisted = JSON.parse(fs.readFileSync(persistedFile, 'utf8'))
    assert.equal(persisted.operationAdmissions['op-crash-after-effect'].action, 'browser_navigate', 'pre-dispatch admission persisted')
    assert.equal(persisted.receipts?.['crash-task'], undefined, 'crash happened before persistent owner receipt')
    const task = persisted.browserTasks.tasks.find(item => item.taskId === 'crash-task')
    assert.ok(task, 'BrowserTask lineage survived process crash')
    assert.equal(task.lastReceipt, undefined, 'BrowserTask has no terminal receipt yet')
    const second = await execute('B', origin)
    assert.equal(second.code, 0, 'child B should recover and refuse replay')
    assert.notEqual(first.pid, second.pid, 'two separate OS-level Electron processes')
    assert.equal(effects, 1, 'no second POST')
    process.stdout.write('CRASH_REPLAY_NATIVE_PASS effects=1 processes=' + first.pid + ',' + second.pid + '\n')
  } finally {
    await new Promise(resolve => server.close(resolve))
    fs.rmSync(root, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 })
  }
}
main().catch(error => {
  process.stderr.write('CRASH_REPLAY_NATIVE_FAIL ' + String(error?.stack ?? error) + '\n')
  server.close()
  process.exitCode = 1
})
