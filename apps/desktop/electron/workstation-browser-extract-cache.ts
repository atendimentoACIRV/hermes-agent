/**
 * Hermes Workstation Browser Extract Cache & Structured Normalization
 *
 * Provides bounded in-memory caching for READ-only structured extraction.
 * Mandatory verified documentFingerprint + epoch + revision prevents stale SPA reads.
 * Automatically sanitizes sensitive keys and passwords.
 */

import crypto from 'node:crypto'

export interface ExtractScope {
  profileId: string
  taskId: string
  tabId: string
  url: string
  documentEpoch: string
  mutationRevision: number
  documentFingerprint: string
  queryDigest: string
}

export class BoundedExtractCache<T> {
  private data = new Map<string, { until: number; value: T }>()

  constructor(
    private readonly maxEntries = 64,
    private readonly ttlMs = 4_000
  ) {}

  private key(s: ExtractScope): string {
    if (
      !s.profileId ||
      !s.taskId ||
      !s.tabId ||
      !s.url ||
      !s.documentEpoch ||
      !s.documentFingerprint ||
      !s.queryDigest ||
      !Number.isSafeInteger(s.mutationRevision) ||
      s.mutationRevision < 0
    ) {
      throw new Error('extract_fingerprint_required')
    }
    return JSON.stringify([
      s.profileId,
      s.taskId,
      s.tabId,
      s.url,
      s.documentEpoch,
      s.mutationRevision,
      s.documentFingerprint,
      s.queryDigest
    ])
  }

  get(scope: ExtractScope): T | null {
    const key = this.key(scope)
    const record = this.data.get(key)
    if (!record) return null
    if (record.until < Date.now()) {
      this.data.delete(key)
      return null
    }
    return record.value
  }

  set(scope: ExtractScope, value: T): void {
    const key = this.key(scope)
    // Cache must only receive previously filtered, non-sensitive read results.
    this.data.delete(key)
    this.data.set(key, { value, until: Date.now() + this.ttlMs })
    while (this.data.size > this.maxEntries) {
      const first = this.data.keys().next().value
      if (!first) break
      this.data.delete(first)
    }
  }

  /** Invalidate entries belonging to a specific tab */
  invalidateTab(tabId: string): void {
    if (!tabId) return
    for (const [key] of this.data.entries()) {
      try {
        const parsed = JSON.parse(key)
        if (Array.isArray(parsed) && parsed[2] === tabId) {
          this.data.delete(key)
        }
      } catch {
        this.data.delete(key)
      }
    }
  }

  /** Call on any navigation, mutation, takeover, uncertainty, auth-wall or profile change. */
  clear(): void {
    this.data.clear()
  }

  /** Invalidate all cached entries for a given task */
  invalidateTask(taskId: string): void {
    if (!taskId) return
    for (const key of Array.from(this.data.keys())) {
      try {
        const parsed = JSON.parse(key)
        if (Array.isArray(parsed) && parsed[1] === taskId) {
          this.data.delete(key)
        }
      } catch {
        this.data.delete(key)
      }
    }
  }

  size(): number {
    return this.data.size
  }
}

/** Compute SHA-256 digest of extraction query parameters */
export function computeQueryDigest(args: Record<string, unknown>): string {
  const normalized = JSON.stringify({
    selector: args.selector ?? null,
    limit: args.limit ?? 20,
    mode: args.mode ?? 'default',
    attributes: args.attributes ?? []
  })
  return crypto.createHash('sha256').update(normalized).digest('hex').slice(0, 16)
}

export const queryDigest = computeQueryDigest

const SENSITIVE_PATTERN = /(?:password|secret|token|bearer|api[_-]?key|auth[_-]?token|credit[_-]?card)/i

/** Normalize and sanitize a single extracted item, optionally filtering by schema properties */
export function normalizeExtractedItem(
  item: unknown,
  schema?: Record<string, unknown> | null
): unknown {
  if (!item || typeof item !== 'object' || Array.isArray(item)) return item
  const record = item as Record<string, unknown>
  const cleaned: Record<string, unknown> = {}

  const schemaProperties =
    schema && typeof schema.properties === 'object' && schema.properties !== null
      ? Object.keys(schema.properties as Record<string, unknown>)
      : null

  for (const [k, v] of Object.entries(record)) {
    if (schemaProperties && !schemaProperties.includes(k)) {
      continue
    }
    if (SENSITIVE_PATTERN.test(k)) {
      cleaned[k] = '[REDACTED]'
    } else if (typeof v === 'string') {
      cleaned[k] = v.slice(0, 20_000)
    } else if (v && typeof v === 'object' && !Array.isArray(v)) {
      cleaned[k] = normalizeExtractedItem(v)
    } else {
      cleaned[k] = v
    }
  }
  return cleaned
}

/** Sanitize an array of extracted items */
export function sanitizeExtractedItems(
  items: unknown[],
  schema?: Record<string, unknown> | null
): unknown[] {
  if (!Array.isArray(items)) return []
  return items.slice(0, 100).map(item => normalizeExtractedItem(item, schema))
}
