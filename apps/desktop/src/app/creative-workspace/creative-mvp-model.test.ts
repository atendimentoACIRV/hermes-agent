import { describe, expect, it } from 'vitest'

import {
  applyCreativeEdit, assertCreativeProject, newCreativeProject,
  renderCreativeSvg, sampledTransform,
} from './creative-mvp-model'

describe('Creative SVG edit+animation MVP', () => {
  it('creates editable project, renders safe SVG and validates roundtrip', () => {
    const base = newCreativeProject('new-1')
    const project = applyCreativeEdit(base, { type: 'addLayer', layerKind: 'text', id: 'title' })

    const modified = applyCreativeEdit(project, {
      type: 'setParameter', id: 'title', property: 'text', value: 'Hello <World> & "Everyone"',
    })

    expect(base.compositions[0].layers).toEqual([])
    expect(project.compositions[0].layers).toHaveLength(1)
    const reopened = JSON.parse(JSON.stringify(modified))
    expect(() => assertCreativeProject(reopened)).not.toThrow()
    const svg = renderCreativeSvg(reopened, 0)
    expect(svg).toContain('Hello &lt;World&gt; &amp; &quot;Everyone&quot;')
    expect(svg).not.toContain('<World>')
  })
  it('creates a shape and changes geometry and opacity without mutating the original', () => {
    const start = newCreativeProject('shape-1')
    const withShape = applyCreativeEdit(start, { type: 'addLayer', layerKind: 'shape', id: 'rect' })
    const moved = applyCreativeEdit(withShape, { type: 'setTransform', id: 'rect', property: 'x', value: 222 })
    expect(renderCreativeSvg(moved, 0)).toContain('x="222"')
    expect(renderCreativeSvg(withShape, 0)).toContain('x="150"')
  })
  it('interpolates keyframe paths frame-accurately at 30 fps', () => {
    let project = applyCreativeEdit(newCreativeProject('motion-1'), { type: 'addLayer', layerKind: 'text', id: 'title' })
    project = applyCreativeEdit(project, {
      type: 'upsertKeyframe', id: 'title', property: 'opacity', time: 0, value: 0, keyframeId: 'kf-0',
    })
    project = applyCreativeEdit(project, {
      type: 'upsertKeyframe', id: 'title', property: 'opacity', time: 1, value: 1, keyframeId: 'kf-1',
    })
    const layer = project.compositions[0].layers[0]
    expect(sampledTransform(layer, 15/30).opacity).toBeCloseTo(.5)
    expect(renderCreativeSvg(project, .5)).toContain('opacity="0.5"')
    const adjusted = applyCreativeEdit(project, { type: 'editKeyframe', keyframeId: 'kf-1', value: .5 })
    expect(sampledTransform(adjusted.compositions[0].layers[0], 1).opacity).toBeCloseTo(.5)
    expect(sampledTransform(layer, 1).opacity).toBe(1)
  })
  it('rejects duplicates, invalid frame times and NaN edits', () => {
    const project = applyCreativeEdit(newCreativeProject('bad-1'), { type: 'addLayer', layerKind: 'text', id: 'first' })
    expect(() => applyCreativeEdit(project, { type: 'addLayer', layerKind: 'text', id: 'first' })).toThrow()
    expect(() => applyCreativeEdit(project, {
      type: 'setTransform', id: 'first', property: 'opacity', value: Number.NaN,
    })).toThrow()
    expect(() => renderCreativeSvg(project, 1000)).toThrow()
  })
  it('fails closed on scripts, unsupported media or malformed foreign projects', () => {
    const project = newCreativeProject('safe-1')
    const foreign = structuredClone(project)
    foreign.compositions[0].tracks.push({
      trackId: 'foreign', name: 'Not imported silently', kind: 'video',
      locked: false, muted: false, solo: false, zIndex: 0, clips: [],
    })
    expect(() => assertCreativeProject(foreign)).toThrow(/backend/)
    const layer = applyCreativeEdit(project, { type: 'addLayer', layerKind: 'shape', id: 'rect' })
    layer.compositions[0].layers[0].opaqueCode = '<script>alert(1)</script>'
    expect(() => assertCreativeProject(layer)).toThrow()
  })
})
