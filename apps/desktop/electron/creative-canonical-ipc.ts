/**
 * Strict typed seam for future Electron -> CreativeDocument RPC.
 *
 * The renderer can choose a project and a safe edit, never a session owner,
 * actor identity, command path, executable or host connection.
 * Registration MUST provide a trusted main/backend owner resolver. Without it,
 * the seam refuses even reads. No authority is conferred by this module.
 */
export interface TrustedCreativeOwner {
  taskId: string
  runId: number
  sessionId: string
  profileHome: string
  sessionKey: string
}

export interface CreativeReadRequest { projectId: string }

export interface CreativeEditRequest {
  projectId: string
  expectedRevisionId: string
  etag: string
  transactionId: string
  command: {
    commandId: 'layer.create' | 'layer.setProperty'
    params: Record<string, unknown>
    idempotencyKey: string
  }
}

type CanonicalResult = { project_id: string; revision_id: string; etag: string; source: Record<string, unknown>; [key: string]: unknown }

interface Dependencies {
  resolveTrustedOwner: (senderEvent: unknown) => TrustedCreativeOwner | null | Promise<TrustedCreativeOwner | null>
  open: (owner: TrustedCreativeOwner, projectId: string) => Promise<CanonicalResult>
  apply: (owner: TrustedCreativeOwner, request: CreativeEditRequest) => Promise<unknown>
}

const HEX_ID = /^[a-f0-9]{32}$/
const ALLOWED = new Set(['layer.create', 'layer.setProperty'])

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function hasExactly(value: Record<string, unknown>, keys: readonly string[]): boolean {
  return Object.keys(value).length === keys.length && Object.keys(value).every(key => keys.includes(key))
}

function nonempty(value: unknown, max = 256): value is string {
  return typeof value === 'string' && value.length > 0 && value.length <= max
}

function invalid(): never { throw new Error('creative_invalid_request') }

function readProjectId(value: unknown): string {
  if (!record(value) || !hasExactly(value, ['projectId']) || !HEX_ID.test(String(value.projectId))) {
    return invalid()
  }

  return value.projectId as string
}

function parseEdit(value: unknown): CreativeEditRequest {
  if (!record(value) || !hasExactly(value, [
    'projectId', 'expectedRevisionId', 'etag', 'transactionId', 'command'
  ])) {return invalid()}

  if (![value.projectId, value.expectedRevisionId, value.transactionId]
    .every(item => typeof item === 'string' && HEX_ID.test(item))) {return invalid()}

  if (!nonempty(value.etag, 180)) {return invalid()}

  if (!record(value.command) || !hasExactly(value.command, [
    'commandId', 'params', 'idempotencyKey'
  ])) {return invalid()}

  const command = value.command

  if (!ALLOWED.has(String(command.commandId)) || !nonempty(command.idempotencyKey, 100)
      || !record(command.params)) {return invalid()}

  const params = command.params

  if (command.commandId === 'layer.create') {
    if (!hasExactly(params, ['composition_id', 'layer_id', 'name'])
        || !HEX_ID.test(String(params.composition_id))
        || !HEX_ID.test(String(params.layer_id))
        || !nonempty(params.name, 200)) {return invalid()}
  } else if (command.commandId === 'layer.setProperty') {
    if (!hasExactly(params, ['composition_id', 'layer_id', 'property_path', 'value'])
        || !HEX_ID.test(String(params.composition_id))
        || !HEX_ID.test(String(params.layer_id))
        || !nonempty(params.property_path, 160)
        || !/^declared_parameters\.[a-zA-Z_][\w-]{0,63}$/.test(params.property_path as string)
        || typeof params.value !== 'string' || !nonempty(params.value, 500)) {return invalid()}
  }

  // Force JSON-only, bounded structured data; reject proto/accessor trickery by
  // re-parsing and validating the plain decoded representation.
  let plain: unknown

  try {
    const bytes = JSON.stringify(value)

    if (!bytes || bytes.length > 4096) {return invalid()}
    plain = JSON.parse(bytes)
  } catch { return invalid() }

  return plain as CreativeEditRequest
}

function verifyOwner(owner: TrustedCreativeOwner | null): TrustedCreativeOwner {
  if (!owner || !nonempty(owner.taskId) || !Number.isSafeInteger(owner.runId)
      || owner.runId <= 0 || !nonempty(owner.sessionId)
      || !nonempty(owner.sessionKey) || !nonempty(owner.profileHome, 1024)) {
    throw new Error('creative_owner_unavailable')
  }

  return owner
}

function verifyHead(head: CanonicalResult, projectId: string): CanonicalResult {
  if (!record(head) || head.project_id !== projectId || !HEX_ID.test(String(head.revision_id))
      || !/^"[a-f0-9]{16}-[a-f0-9]{16}"$/.test(String(head.etag))
      || !record(head.source) || head.source.project_id !== projectId
      || head.source.schema_version !== 1) {throw new Error('creative_head_mismatch')}

  return head
}

export function createCreativeCanonicalBridge(deps: Dependencies) {
  async function owner(senderEvent: unknown): Promise<TrustedCreativeOwner> {
    // Resolve against the EXACT IPC sender, not the last active window or a
    // process-global session. Copy the main-owned identity before awaiting IO.
    return { ...verifyOwner(await deps.resolveTrustedOwner(senderEvent)) }
  }

  async function assertSameOwner(senderEvent: unknown, original: TrustedCreativeOwner): Promise<void> {
    const current = await owner(senderEvent)

    if (current.taskId !== original.taskId || current.runId !== original.runId
        || current.sessionId !== original.sessionId || current.sessionKey !== original.sessionKey
        || current.profileHome !== original.profileHome) {
      throw new Error('creative_owner_changed')
    }
  }

  return {
    async open(payload: unknown, senderEvent?: unknown): Promise<CanonicalResult> {
      const projectId = readProjectId(payload)
      const trusted = await owner(senderEvent)
      const result = verifyHead(await deps.open(trusted, projectId), projectId)
      await assertSameOwner(senderEvent, trusted)

      return result
    },
    async apply(payload: unknown, senderEvent?: unknown): Promise<CanonicalResult> {
      const edit = parseEdit(payload)
      const trusted = await owner(senderEvent)
      const receipt = await deps.apply(trusted, edit)
      // Revalidate sender and task before even interpreting a commit receipt.
      await assertSameOwner(senderEvent, trusted)

      // A readback alone is not proof of a commit. Require an actual backend
      // revision receipt, with a new revision matching canonical readback.
      if (!record(receipt) || receipt.project_id !== edit.projectId
          || typeof receipt.revision_id !== 'string'
          || !HEX_ID.test(receipt.revision_id)
          || receipt.revision_id === edit.expectedRevisionId) {
        throw new Error('creative_commit_mismatch')
      }

      // If this renderer was rebound or closed during the edit, do not return
      // an apparently successful HEAD from another task or user.
      await assertSameOwner(senderEvent, trusted)
      const result = verifyHead(await deps.open(trusted, edit.projectId), edit.projectId)
      await assertSameOwner(senderEvent, trusted)

      if (result.revision_id !== receipt.revision_id) {
        throw new Error('creative_commit_mismatch')
      }

      return result
    }
  }
}


/** Register only for sender-bound main-process ownership, never arbitrary JS. */
export function registerCreativeCanonicalHandlers(
  ipc: { handle: (channel: string, handler: (event: unknown, data: unknown) => Promise<unknown>) => void },
  deps: Dependencies,
  allowSender: (event: unknown) => boolean
): void {
  const bridge = createCreativeCanonicalBridge({
    ...deps,
    // Sender admission must be checked on EVERY asynchronous owner resolution,
    // not just once when the IPC call begins; a closed/navigated renderer loses it.
    resolveTrustedOwner: sender => {
      if (!allowSender(sender)) { throw new Error('creative_sender_denied') }

      return deps.resolveTrustedOwner(sender)
    }
  })

  ipc.handle('hermes:creative:canonical:open', (event, data) => {
    if (!allowSender(event)) {return Promise.reject(new Error('creative_sender_denied'))}

    return bridge.open(data, event)
  })
  ipc.handle('hermes:creative:canonical:apply', (event, data) => {
    if (!allowSender(event)) {return Promise.reject(new Error('creative_sender_denied'))}

    return bridge.apply(data, event)
  })
}
