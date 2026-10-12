import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { afterEach, test } from 'vitest'
import { BrowserSessionStateFilePersistence } from './workstation-browser-session-state'

const roots: string[] = []
afterEach(() => { for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true }) })

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-admission-'))
  roots.push(root)
  const file = path.join(root, 'session-state.json')
  const owner = new BrowserSessionStateFilePersistence(file)
  const identity = {
    operationId: 'op-a', taskId: 'task-1', sessionId: 'session-1', runId: 'run-1',
    tabId: 'tab-1', action: 'browser_click', argumentsDigest: 'a'.repeat(64)
  }
  return { file, owner, identity }
}

test('CRASH-01/07: admission persists before effect and blocks replay after a fresh process', () => {
  const { file, owner, identity } = fixture()
  assert.equal(owner.admitBrowserMutation(identity), 'admitted')
  const fromRestart = new BrowserSessionStateFilePersistence(file)
  assert.equal(fromRestart.admitBrowserMutation(identity), 'reconciliation_required')
  const persisted = fs.readFileSync(file, 'utf-8')
  assert.equal(persisted.includes('op-a'), true)
  assert.equal(persisted.includes('argumentsDigest'), true)
})

test('CRASH-02: operation A cannot replay after B is admitted', () => {
  const { file, owner, identity } = fixture()
  assert.equal(owner.admitBrowserMutation(identity), 'admitted')
  assert.equal(owner.admitBrowserMutation({ ...identity, operationId: 'op-b' }), 'admitted')
  assert.equal(new BrowserSessionStateFilePersistence(file).admitBrowserMutation(identity), 'reconciliation_required')
})

test('CRASH-03/04: repeated operation ID is fail-closed for concurrent and conflicting ownership', () => {
  const { owner, identity } = fixture()
  assert.equal(owner.admitBrowserMutation(identity), 'admitted')
  assert.equal(owner.admitBrowserMutation(identity), 'reconciliation_required')
  for (const changed of [
    { taskId: 'task-2' }, { runId: 'run-2' }, { tabId: 'tab-2' },
    { action: 'browser_type' }, { argumentsDigest: 'b'.repeat(64) }
  ]) assert.throws(() => owner.admitBrowserMutation({ ...identity, ...changed }), /operation_identity_collision/)
})

test('CRASH-08: corrupted persisted state cannot be treated as fresh empty admission', () => {
  const { file, identity } = fixture()
  fs.writeFileSync(file, '{ incomplete')
  assert.throws(
    () => new BrowserSessionStateFilePersistence(file).admitBrowserMutation(identity),
    /browser_admission_state_unavailable/
  )
})

test('CRASH-03: a lock from an unknown writer is never stolen or removed', () => {
  const { file, owner, identity } = fixture()
  const lock = file + '.admission.lock'
  fs.writeFileSync(lock, 'unowned-lock-marker')
  assert.throws(() => owner.admitBrowserMutation(identity), /browser_admission_concurrent_reconciliation_required/)
  assert.equal(fs.readFileSync(lock, 'utf8'), 'unowned-lock-marker', 'foreign lock remains untouched')
  assert.equal(fs.existsSync(file), false, 'no admission dispatched without lock')
})

test('CRASH-03: an owner with a stale cached snapshot rereads history under exclusive lock', () => {
  const { file, owner, identity } = fixture()
  const stale = new BrowserSessionStateFilePersistence(file)
  stale.load()
  assert.equal(owner.admitBrowserMutation(identity), 'admitted')
  assert.equal(stale.admitBrowserMutation(identity), 'reconciliation_required')
  assert.throws(() => stale.admitBrowserMutation({ ...identity, argumentsDigest: 'b'.repeat(64) }), /operation_identity_collision/)
})

test('CRASH-03: a stale session projection must not erase a different process admission', () => {
  const { file, owner, identity } = fixture()
  const staleOwner = new BrowserSessionStateFilePersistence(file)
  staleOwner.load()
  assert.equal(owner.admitBrowserMutation(identity), 'admitted')
  staleOwner.saveSession([], null)
  assert.equal(
    new BrowserSessionStateFilePersistence(file).admitBrowserMutation(identity),
    'reconciliation_required',
    'a stale session save cannot permit a prior operation to be admitted again'
  )
})
