import type { CreativeLayer, CreativeProject } from './types'

/** Renderer-only, explicit portable file MVP. Native shared document admission is a separate release gate. */
export type CreativeEdit =
  | { type: 'renameProject'; name: string }
  | { type: 'addLayer'; layerKind: 'text' | 'shape'; id: string }
  | { type: 'removeLayer'; id: string }
  | { type: 'setTransform'; id: string; property: 'x' | 'y' | 'opacity'; value: number }
  | { type: 'setParameter'; id: string; property: 'text' | 'color' | 'width' | 'height'; value: string | number }
  | { type: 'upsertKeyframe'; id: string; property: 'x' | 'y' | 'opacity'; time: number; value: number; keyframeId: string }
  | { type: 'editKeyframe'; keyframeId: string; time?: number; value?: number; easing?: string }
  | { type: 'removeKeyframe'; keyframeId: string }

export function newCreativeProject(id: string): CreativeProject {
  return {
    projectId: id, name: 'Untitled creative project', width: 1280, height: 720,
    fps: { num: 30, den: 1 }, duration: 10,
    compositions: [{ compositionId: 'main', name: 'Main', tracks: [], layers: [] }],
  }
}

export function assertCreativeProject(value: unknown): asserts value is CreativeProject {
  if (!value || typeof value !== 'object') {throw new Error('Invalid project file')}
  const project = value as CreativeProject

  if (!/^[\w-]{1,128}$/.test(project.projectId) || typeof project.name !== 'string'
    || !Number.isSafeInteger(project.width) || project.width < 1 || project.width > 8192
    || !Number.isSafeInteger(project.height) || project.height < 1 || project.height > 8192
    || !project.fps || !Number.isSafeInteger(project.fps.num) || !Number.isSafeInteger(project.fps.den)
    || project.fps.num < 1 || project.fps.den < 1 || project.fps.num / project.fps.den > 120
    || !Number.isFinite(project.duration) || project.duration <= 0 || project.duration > 36000
    || !Array.isArray(project.compositions) || project.compositions.length !== 1
    || !Array.isArray(project.compositions[0]?.layers) || !Array.isArray(project.compositions[0]?.tracks)
    || project.compositions[0].layers.length > 1000) {throw new Error('Invalid project schema or limits')}

  const ids = new Set<string>()

  for (const layer of project.compositions[0].layers) {
    if (!layer || typeof layer !== 'object' || !/^[\w-]{1,128}$/.test(layer.layerId)
      || ids.has(layer.layerId) || !['vector_svg', 'text', 'shape'].includes(layer.kind)
      || !layer.transform || !Number.isFinite(layer.transform.x)
      || !Number.isFinite(layer.transform.y) || !Number.isFinite(layer.transform.opacity)
      || layer.transform.opacity < 0 || layer.transform.opacity > 1
      || !layer.declaredParameters || typeof layer.declaredParameters !== 'object'
      || !Array.isArray(layer.keyframes) || layer.keyframes.length > 1000
      || layer.opaqueCode) {throw new Error('Unsupported or malformed editable layer')}

    ids.add(layer.layerId)

    for (const frame of layer.keyframes) {
      if (!frame || !/^[\w-]{1,128}$/.test(frame.keyframeId)
        || ids.has(frame.keyframeId)
        || !['transform.x', 'transform.y', 'transform.opacity'].includes(frame.propertyPath)
        || !Number.isFinite(frame.time) || frame.time < 0 || frame.time > project.duration
        || !Number.isFinite(frame.value)) {throw new Error('Invalid keyframe')}

      ids.add(frame.keyframeId)
    }
  }

  // This MVP supports editable vector-only projects, never silently discards media.
  if (project.compositions[0].tracks.length !== 0) {throw new Error('Media tracks require the native creative backend')}
}

export function applyCreativeEdit(project: CreativeProject, edit: CreativeEdit): CreativeProject {
  assertCreativeProject(project)
  const next: CreativeProject = structuredClone(project)
  const layers = next.compositions[0].layers

  if (edit.type === 'renameProject') {
    if (edit.name.length > 128) {throw new Error('Project name exceeds 128 characters')}
    next.name = edit.name
  } else if (edit.type === 'addLayer') {
    if (layers.some(layer => layer.layerId === edit.id)) {throw new Error('Layer already exists')}
    layers.push({
      layerId: edit.id, name: edit.layerKind === 'text' ? 'Text' : 'Rectangle',
      kind: edit.layerKind, opaqueCode: null,
      declaredParameters: edit.layerKind === 'text'
        ? { text: 'Your text', font_size: 60, color: '#ffffff' }
        : { width: 240, height: 160, color: '#00aaff' },
      transform: { x: 150, y: 160, opacity: 1 }, keyframes: [],
    })
  } else if (edit.type === 'removeLayer') {
    const i = layers.findIndex(layer => layer.layerId === edit.id)

    if (i < 0) {throw new Error('Layer not found')}
    layers.splice(i, 1)
  } else if (edit.type === 'editKeyframe' || edit.type === 'removeKeyframe') {
    const keyframe = layers.flatMap(layer => layer.keyframes).find(frame => frame.keyframeId === edit.keyframeId)

    if (!keyframe) {throw new Error('Keyframe not found')}

    if (edit.type === 'removeKeyframe') {
      for (const layer of layers) {layer.keyframes = layer.keyframes.filter(frame => frame.keyframeId !== edit.keyframeId)}
    } else {
      if (edit.time !== undefined) {keyframe.time = edit.time}

      if (edit.value !== undefined) {keyframe.value = edit.value}

      if (edit.easing !== undefined) {keyframe.easing = edit.easing}
    }
  } else {
    const layer = layers.find(layer => layer.layerId === edit.id)

    if (!layer) {throw new Error('Layer not found')}

    if (edit.type === 'setTransform') {
      layer.transform[edit.property] = edit.value
    } else if (edit.type === 'setParameter') {
      layer.declaredParameters[edit.property] = edit.value
    } else if (edit.type === 'upsertKeyframe') {
      const path = 'transform.' + edit.property
      const frame = layer.keyframes.find(k => k.propertyPath === path && k.time === edit.time)

      if (frame) {frame.value = edit.value}
      else {layer.keyframes.push({
        keyframeId: edit.keyframeId, propertyPath: path,
        time: edit.time, value: edit.value, easing: 'linear',
      })}
    }
  }

  assertCreativeProject(next)

  return next
}

export function sampledTransform(layer: CreativeLayer, time: number): CreativeLayer['transform'] {
  const transform = { ...layer.transform }

  for (const property of ['x', 'y', 'opacity'] as const) {
    const frames = layer.keyframes
      .filter(k => k.propertyPath === 'transform.' + property)
      .slice().sort((a, b) => a.time - b.time)

    if (!frames.length) {continue}
    const before = [...frames].reverse().find(k => k.time <= time) ?? frames[0]
    const after = frames.find(k => k.time >= time) ?? frames[frames.length - 1]
    const a = Number(before.value), b = Number(after.value)
    const t = before.time === after.time ? 0 : Math.max(0, Math.min(1, (time - before.time) / (after.time - before.time)))
    const eased = before.easing === 'ease_in' ? t*t : before.easing === 'ease_out' ? 1-(1-t)*(1-t) : t
    transform[property] = a + (b-a)*eased
  }

  return transform
}

function escapeXml(value: unknown): string {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;')
}

function safeColor(value: unknown): string {
  return typeof value === 'string' && /^#[\da-fA-F]{3}(?:[\da-fA-F]{3})?$/.test(value) ? value : '#ffffff'
}

function finiteRange(value: unknown, max: number, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= max ? value : fallback
}

export function renderCreativeSvg(project: CreativeProject, time: number): string {
  assertCreativeProject(project)

  if (!Number.isFinite(time) || time < 0 || time > project.duration) {throw new Error('Invalid frame time')}

  const shapes = project.compositions[0].layers.map(layer => {
    const { x, y, opacity } = sampledTransform(layer, time)
    const color = safeColor(layer.declaredParameters.color)

    if (layer.kind === 'shape') {
      const w = finiteRange(layer.declaredParameters.width, 8192, 240)
      const h = finiteRange(layer.declaredParameters.height, 8192, 160)

      return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${color}" opacity="${opacity}"/>`
    }

    const size = finiteRange(layer.declaredParameters.font_size, 512, 60)

    return `<text x="${x}" y="${y}" font-size="${size}" font-family="sans-serif" fill="${color}" opacity="${opacity}">${escapeXml(layer.declaredParameters.text ?? '')}</text>`
  }).join('')

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${project.width}" height="${project.height}" viewBox="0 0 ${project.width} ${project.height}"><rect width="100%" height="100%" fill="#17171d"/>${shapes}</svg>`
}

export function downloadCreativeFile(name: string, content: string, type: string): void {
  const link = document.createElement('a')
  const url = URL.createObjectURL(new Blob([content], { type }))

  try {
    link.href = url
    link.download = name.replace(/[^\w.-]/g, '_')
    document.body.appendChild(link)
    link.click()
  } finally {
    link.remove()
    // Delayed cleanup preserves browser/Electron download completion.
    setTimeout(() => URL.revokeObjectURL(url), 30000)
  }
}
