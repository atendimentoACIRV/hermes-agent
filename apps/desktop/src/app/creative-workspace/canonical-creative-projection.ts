/** A read-only display projection of a backend-verified CreativeDocument HEAD.
 * Only the canonical backend may assign revision ID/ETag. Neither React nor this
 * module may publish a new revision, execute a renderer or mutate native sources.
 */
import type { CreativeClip, CreativeComposition, CreativeLayer, CreativeProject, CreativeTrack } from './types'

const IDENTIFIER = /^[a-f0-9]{32}$/
// Mirrors CreativeProjectRevision.etag: quoted revision[:16]-source_sha256[:16].
const STRONG_ETAG = /^"[a-f0-9]{16}-[a-f0-9]{16}"$/

type Data = Record<string, unknown>

const asObject = (value: unknown, field: string): Data => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {throw new TypeError(`Invalid ${field}`)}

  return value as Data
}

const asText = (value: unknown, field: string, limit = 2048): string => {
  if (typeof value !== 'string' || value.length > limit) {throw new TypeError(`Invalid ${field}`)}

  return value
}

const asId = (value: unknown, field: string): string => {
  const text = asText(value, field, 32)

  if (!IDENTIFIER.test(text)) {throw new TypeError(`Invalid ${field}`)}

  return text
}

const asArray = (value: unknown, field: string, limit = 2000): unknown[] => {
  if (!Array.isArray(value) || value.length > limit) {throw new TypeError(`Invalid ${field}`)}

  return value
}

const asNumber = (value: unknown, field: string, { min = 0, max = 86400 } = {}): number => {
  if ((typeof value !== 'number' && typeof value !== 'string') || value === '') {
    throw new TypeError(`Invalid ${field}`)
  }

  let number: number

  if (typeof value === 'string') {
    if (value.length > 64) {throw new TypeError(`Invalid ${field}`)}
    const parts = value.split('/')

    if (parts.length === 2) {
      if (!/^-?[0-9]{1,16}$/.test(parts[0]) || !/^[1-9][0-9]{0,15}$/.test(parts[1])) {
        throw new TypeError(`Invalid ${field}`)
      }

      number = Number(parts[0]) / Number(parts[1])
    } else {
      if (parts.length !== 1 || !/^-?[0-9]+([.][0-9]+)?$/.test(value)) {
        throw new TypeError(`Invalid ${field}`)
      }

      number = Number(value)
    }
  } else {
    number = value
  }

  if (!Number.isFinite(number) || number < min || number > max) {throw new TypeError(`Invalid ${field}`)}

  return number
}

const asPositiveInteger = (value: unknown, field: string, max = 65536): number => {
  if (typeof value !== 'number' || !Number.isInteger(value) || value < 1 || value > max) {
    throw new TypeError(`Invalid ${field}`)
  }

  return value
}

const cloneData = (value: unknown): Record<string, unknown> => {
  const obj = asObject(value, 'parameter map')

  return structuredClone(obj)
}

const projectClip = (raw: unknown, trackId: string): CreativeClip => {
  const data = asObject(raw, 'clip')
  const range = asObject(data.timeline_range, 'timeline_range')
  const start = asNumber(range.start, 'timeline start')
  const end = asNumber(range.end, 'timeline end')

  if (end < start) {throw new TypeError('Invalid clip timeline interval')}
  const id = asId(data.track_id, 'clip track_id')

  if (id !== trackId) {throw new TypeError('Clip/track ownership mismatch')}

  return {
    clipId: asId(data.clip_id, 'clip_id'),
    trackId: id,
    assetId: asId(data.asset_id, 'asset_id'),
    name: asText(data.name, 'clip name'),
    timelineRange: { start, end },
    sourceIn: asNumber(data.source_in, 'source_in'),
    speed: asNumber(data.speed, 'speed', { min: 0, max: 100 }),
    reverse: data.reverse === true,
    freeze: data.freeze === true,
    linkedClipIds: asArray(data.linked_clip_ids ?? [], 'linked clip ids').map(id => asId(id, 'linked clip id')),
  }
}

const projectTrack = (raw: unknown): CreativeTrack => {
  const data = asObject(raw, 'track')
  const trackId = asId(data.track_id, 'track_id')
  const kind = asText(data.kind, 'track kind')

  if (!['video', 'audio', 'graphic', 'subtitle'].includes(kind)) {throw new TypeError('Unsupported track kind')}

  return {
    trackId,
    name: asText(data.name, 'track name'),
    kind: kind as CreativeTrack['kind'],
    zIndex: asNumber(data.z_index, 'z_index', { min: -10000, max: 10000 }),
    locked: data.locked === true,
    muted: data.muted === true,
    solo: data.solo === true,
    clips: asArray(data.clips, 'clips').map(clip => projectClip(clip, trackId)),
  }
}

const projectLayer = (raw: unknown): CreativeLayer => {
  const data = asObject(raw, 'layer')
  const kind = asText(data.kind, 'layer kind')

  if (!['vector_svg', 'html_canvas', 'three_js_scene', 'text', 'shape', 'nle_clip'].includes(kind)) {
    throw new TypeError('Unsupported layer kind')
  }

  const transform = asObject(data.transform, 'transform')
  const opaque = data.opaque_code

  return {
    layerId: asId(data.layer_id, 'layer_id'),
    name: asText(data.name, 'layer name'),
    kind: kind as CreativeLayer['kind'],
    declaredParameters: cloneData(data.declared_parameters ?? {}),
    opaqueCode: opaque === null || opaque === undefined ? null : asText(opaque, 'opaque_code', 131072),
    transform: {
      x: asNumber(transform.x, 'transform x', { min: -1000000, max: 1000000 }),
      y: asNumber(transform.y, 'transform y', { min: -1000000, max: 1000000 }),
      opacity: asNumber(transform.opacity, 'transform opacity', { min: 0, max: 1 }),
    },
    keyframes: asArray(data.keyframes, 'keyframes', 10000).map(rawKey => {
      const key = asObject(rawKey, 'keyframe')

      return {
        keyframeId: asId(key.keyframe_id, 'keyframe_id'),
        propertyPath: asText(key.property_path, 'property_path', 512),
        time: asNumber(key.time, 'keyframe time'),
        value: structuredClone(key.value),
        easing: asText(key.easing, 'easing', 128),
      }
    }),
  }
}

const projectComposition = (raw: unknown): CreativeComposition => {
  const data = asObject(raw, 'composition')

  return {
    compositionId: asId(data.composition_id, 'composition_id'),
    name: asText(data.name, 'composition name'),
    tracks: asArray(data.tracks, 'tracks').map(projectTrack),
    layers: asArray(data.layers, 'layers').map(projectLayer),
  }
}

export type CanonicalCreativeProjection = {
  readonly project: CreativeProject
  readonly revisionId: string
  readonly etag: string
}

/** Reject incomplete/foreign data rather than drawing a fictitious local project. */
export function projectFromCanonicalHead(raw: unknown): CanonicalCreativeProjection {
  const head = asObject(raw, 'canonical HEAD')
  const source = asObject(head.source, 'CreativeDocument source')
  const projectId = asId(head.project_id, 'HEAD project_id')
  const revisionId = asId(head.revision_id, 'HEAD revision_id')
  const etag = asText(head.etag, 'HEAD ETag', 35)

  if (!STRONG_ETAG.test(etag)) {throw new TypeError('Invalid canonical HEAD ETag')}

  if (source.schema_version !== 1) {throw new TypeError('Unsupported CreativeDocument schema version')}

  if (asId(source.project_id, 'document project_id') !== projectId) {
    throw new TypeError('CreativeDocument and HEAD project mismatch')
  }

  const compositions = asArray(source.compositions, 'compositions', 128)

  if (compositions.length === 0) {throw new TypeError('CreativeDocument contains no compositions')}
  const primary = asObject(compositions[0], 'primary composition')
  const fps = asObject(primary.fps, 'fps')

  const result: CreativeProject = {
    projectId,
    name: asText(source.name, 'project name'),
    width: asPositiveInteger(primary.width, 'width', 16384),
    height: asPositiveInteger(primary.height, 'height', 16384),
    fps: {
      num: asPositiveInteger(fps.num, 'fps numerator', 1000000),
      den: asPositiveInteger(fps.den, 'fps denominator', 1000000),
    },
    duration: asNumber(primary.duration, 'composition duration'),
    compositions: compositions.map(projectComposition),
  }

  return { project: result, revisionId, etag }
}
