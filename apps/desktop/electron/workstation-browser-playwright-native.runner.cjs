/* External runner owns the Electron test profile and cleans it after process exit. */
'use strict'
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawnSync } = require('node:child_process')
const electron = require('electron')
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-playwright-native-'))
let code = 1
try {
  const result = spawnSync(electron, [path.join(__dirname, 'workstation-browser-playwright-native.e2e.cjs'), '--no-sandbox'], {
    cwd: path.resolve(__dirname, '..'),
    env: { ...process.env, HERMES_C2C_TEST_ROOT: tmp },
    encoding: 'utf8', windowsHide: true, timeout: 60000
  })
  if (result.stdout) process.stdout.write(result.stdout)
  if (result.stderr) process.stderr.write(result.stderr)
  if (result.error) process.stderr.write(String(result.error) + '\n')
  code = result.status === 0 ? 0 : 1
} finally {
  fs.rmSync(tmp, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 })
}
process.exitCode = code
