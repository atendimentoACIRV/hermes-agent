/**
 * HCW P0A — main-process sender identity fenced by a fresh BACKEND attestation.
 *
 * This is a verifier, NOT a source of authority. The supplied attestor MUST
 * use the already-authenticated Hermes backend for the exact connection and
 * profile and must check the live TaskRun plus current human/agent lease.
 *
 * Never inject data supplied by a renderer as readSenderScope or attestBackend.
 * Without a live attestor main.ts must remain deny-all.
 */
import type { TrustedCreativeOwner } from './creative-canonical-ipc'

export interface CreativeSenderScope {
  webContentsId: number
  navigationEpoch: number
  connectionId: string
  profile: string
  sessionId: string
}

export interface CreativeBackendAttestation extends TrustedCreativeOwner {
  connectionId: string
  profile: string
  actorId: string
  authorized: boolean
  humanControlActive: boolean
  expiresAt: number
}

export interface CreativeTaskRunResolverDeps {
  readSenderScope: (senderEvent: unknown) => CreativeSenderScope | null
  attestBackend: (scope: CreativeSenderScope) => Promise<CreativeBackendAttestation | null>
  now?: () => number
}

const MAX_ATTESTATION_AGE_MS = 60_000

function validString(s: unknown, max = 256): s is string {
  return typeof s === 'string' && s.length > 0 && s.length <= max
}

function validScope(value: CreativeSenderScope | null): value is CreativeSenderScope {
  return Boolean(value && Number.isSafeInteger(value.webContentsId)
    && value.webContentsId > 0 && Number.isSafeInteger(value.navigationEpoch)
    && value.navigationEpoch >= 0 && validString(value.connectionId)
    && validString(value.profile) && validString(value.sessionId))
}

function equalScope(a: CreativeSenderScope, b: CreativeSenderScope): boolean {
  return a.webContentsId === b.webContentsId
    && a.navigationEpoch === b.navigationEpoch
    && a.connectionId === b.connectionId
    && a.profile === b.profile && a.sessionId === b.sessionId
}

function validProof(proof: CreativeBackendAttestation | null, scope: CreativeSenderScope, now: number): proof is CreativeBackendAttestation {
  return Boolean(proof && proof.authorized === true && proof.humanControlActive === false
    && proof.connectionId === scope.connectionId && proof.profile === scope.profile
    && proof.sessionId === scope.sessionId
    && validString(proof.taskId) && Number.isSafeInteger(proof.runId) && proof.runId > 0
    && validString(proof.sessionKey) && validString(proof.profileHome, 1024)
    && validString(proof.actorId) && Number.isSafeInteger(proof.expiresAt)
    && proof.expiresAt > now && proof.expiresAt <= now + MAX_ATTESTATION_AGE_MS)
}

export function createCreativeTaskRunOwnerResolver(deps: CreativeTaskRunResolverDeps) {
  return async (senderEvent: unknown): Promise<TrustedCreativeOwner> => {
    // The scope must come from an ELECTRON-MAIN owned registry, not the URL or
    // renderer payload. A missing or old registration cannot start an attestation.
    const captured = deps.readSenderScope(senderEvent)

    if (!validScope(captured)) {
      throw new Error('creative_owner_unavailable')
    }

    const fixed = { ...captured }
    const proof = await deps.attestBackend(fixed)
    const now = (deps.now || Date.now)()

    if (!validProof(proof, fixed, now)) {
      throw new Error('creative_owner_unavailable')
    }

    // Network round-trips can outlive a navigation, session change or rehome.
    const current = deps.readSenderScope(senderEvent)

    if (!validScope(current) || !equalScope(fixed, current)) {
      throw new Error('creative_owner_changed')
    }

    // Do not expose the attestation, actor claim or backend credentials to UI.
    // Existing canonical IPC independently reattests after every async step.
    return {
      taskId: proof.taskId, runId: proof.runId, sessionId: proof.sessionId,
      profileHome: proof.profileHome, sessionKey: proof.sessionKey
    }
  }
}
