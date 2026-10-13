/**
 * HCW P0A: in-memory Electron MAIN-owned sender scope, not mutation authority.
 *
 * Only trusted main process call sites may bind/rehome/navigate. Never wire
 * bind() to IPC data or renderer-driven active-route events. Authentication,
 * canonical TaskRun lease, and actor still require independent backend proof.
 */
import type { CreativeSenderScope } from './creative-taskrun-attestation'

interface MainWebContents {
  id: number
  mainFrame: unknown
  isDestroyed(): boolean
}

interface MainOwnedSessionSelector {
  connectionId: string
  profile: string
  sessionId: string
}

interface Entry {
  sender: MainWebContents
  scope: CreativeSenderScope
}

function validId(id: number): boolean {
  return Number.isSafeInteger(id) && id > 0
}

function validString(value: string): boolean {
  return typeof value === 'string' && value.length > 0 && value.length <= 256
}

function isSameSession(a: MainOwnedSessionSelector, b: MainOwnedSessionSelector) {
  return a.connectionId === b.connectionId && a.profile === b.profile
    && a.sessionId === b.sessionId
}

export function createCreativeMainSenderScopeRegistry() {
  const registered = new Map<number, Entry>()
  const epochs = new Map<number, number>()

  const nextEpoch = (id: number) => {
    const next = (epochs.get(id) || 0) + 1

    epochs.set(id, next)

    return next
  }

  return {
    /** Bind ONLY trusted main-side selectors subsequently verified by backend. */
    bind(sender: MainWebContents, selector: MainOwnedSessionSelector): void {
      if (!sender || !validId(sender.id) || sender.isDestroyed()
          || !validString(selector?.connectionId) || !validString(selector?.profile)
          || !validString(selector?.sessionId)) {
        throw new Error('creative_scope_invalid')
      }

      for (const entry of registered.values()) {
        if (entry.sender !== sender && !entry.sender.isDestroyed()
            && isSameSession(entry.scope, selector)) {
          throw new Error('creative_session_already_bound')
        }
      }

      registered.set(sender.id, {
        sender,
        scope: { ...selector, webContentsId: sender.id, navigationEpoch: nextEpoch(sender.id) }
      })
    },
    navigate(sender: MainWebContents): void {
      if (sender && validId(sender.id)) {
        registered.delete(sender.id)
        nextEpoch(sender.id)
      }
    },
    revoke(sender: MainWebContents): void {
      if (sender && validId(sender.id)) {
        registered.delete(sender.id)
        nextEpoch(sender.id)
      }
    },
    /** Only the exact registered WebContents and its primary frame can resolve. */
    read(event: unknown): CreativeSenderScope | null {
      if (!event || typeof event !== 'object') { return null }
      const e = event as { sender?: MainWebContents; senderFrame?: unknown }
      const sender = e.sender

      if (!sender || !validId(sender.id) || sender.isDestroyed()
          || !e.senderFrame || e.senderFrame !== sender.mainFrame) { return null }

      const entry = registered.get(sender.id)

      return entry?.sender === sender ? { ...entry.scope } : null
    }
  }
}
