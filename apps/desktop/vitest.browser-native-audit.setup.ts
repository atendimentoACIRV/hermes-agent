import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { beforeEach, afterEach } from 'vitest'

// Native Browser session files persist independently of HERMES_HOME.
// Isolate them per test to prevent cross-test replay collisions and to ensure
// tests never write to the user's production Hermes Workstation profile.
let temporaryHome: string | null = null
const inherited = process.env.HERMES_WORKSTATION_HOME

beforeEach(() => {
  temporaryHome = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-browser-test-'))
  process.env.HERMES_WORKSTATION_HOME = temporaryHome
})

afterEach(() => {
  if (inherited === undefined) delete process.env.HERMES_WORKSTATION_HOME
  else process.env.HERMES_WORKSTATION_HOME = inherited
  if (temporaryHome) {
    fs.rmSync(temporaryHome, { recursive: true, force: true, maxRetries: 12, retryDelay: 100 })
    temporaryHome = null
  }
})
