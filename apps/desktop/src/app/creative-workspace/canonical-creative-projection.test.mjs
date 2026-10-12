import test from 'node:test'
import assert from 'node:assert/strict'
import { projectFromCanonicalHead } from './canonical-creative-projection.ts'

const id = 'a'.repeat(32)
const comp = 'b'.repeat(32)
const layer = 'c'.repeat(32)
const head = {
  project_id: id,
  revision_id: 'd'.repeat(32),
  etag: '"'+ '1'.repeat(16) + '-' + '1'.repeat(16) + '"',
  source: {
    schema_version: 1,
    project_id: id,
    name: 'Hermes Canonical',
    assets: {},
    metadata: {},
    compositions: [{
      composition_id: comp,
      name: 'Main',
      width: 1920, height: 1080,
      duration: '10',
      fps: { num: 30000, den: 1001 },
      tracks: [],
      layers: [{
        layer_id: layer, name: 'Title', kind: 'text',
        declared_parameters: { text: 'Hello' }, opaque_code: null,
        transform: { x: 20, y: 30, opacity: 1 },
        keyframes: [{ keyframe_id: 'e'.repeat(32), property_path: 'transform.x', time: '1.5', value: 60, easing: 'linear' }],
      }],
    }],
  },
}

test('backend canonical HEAD is sole source for view projection and revision/etag', () => {
  const result = projectFromCanonicalHead(head)
  assert.equal(result.project.projectId, id)
  assert.equal(result.project.name, 'Hermes Canonical')
  assert.equal(result.project.compositions[0].layers[0].declaredParameters.text, 'Hello')
  assert.equal(result.project.compositions[0].layers[0].keyframes[0].time, 1.5)
  assert.deepEqual(result.project.fps, { num: 30000, den: 1001 })
  assert.equal(result.revisionId, 'd'.repeat(32))
  assert.equal(result.etag, '"'+ '1'.repeat(16) + '-' + '1'.repeat(16) + '"')
  assert.deepEqual(result.project.compositions[0].layers[0].transform, { x: 20, y: 30, opacity: 1 })
})

test('rejects malformed and mismatched authority/unknown schema before React', () => {
  assert.throws(() => projectFromCanonicalHead({ ...head, project_id: 'other' }))
  assert.throws(() => projectFromCanonicalHead({ ...head, etag: '' }))
  assert.throws(() => projectFromCanonicalHead({ ...head, source: { ...head.source, schema_version: 9 } }))
  assert.throws(() => projectFromCanonicalHead({ ...head, source: { ...head.source, compositions: [{ ...head.source.compositions[0], duration: '-1' }] } }))
})


test('preserves canonical rational-second strings without converting frame rate to a guessed 30fps', () => {
  const fractional = {
    ...head,
    source: {
      ...head.source,
      compositions: [{
        ...head.source.compositions[0],
        duration: '1001/30',
        layers: [{
          ...head.source.compositions[0].layers[0],
          keyframes: [{ ...head.source.compositions[0].layers[0].keyframes[0], time: '1001/30000' }],
        }],
      }],
    },
  }
  const projected = projectFromCanonicalHead(fractional)
  assert.ok(Math.abs(projected.project.duration - 1001 / 30) < 1e-12)
  assert.ok(Math.abs(projected.project.compositions[0].layers[0].keyframes[0].time - 1001 / 30000) < 1e-12)
  assert.deepEqual(projected.project.fps, { num: 30000, den: 1001 })
})

test('accepts an actual Python CreativeProjectRevision ETag and source fixture', async t => {
  const source = process.env.HERMES_CANONICAL_SNAPSHOT
  if (!source) return t.skip('requires explicit real Python backend snapshot')
  const { readFileSync } = await import('node:fs')
  const headFromPython = JSON.parse(readFileSync(source, 'utf8'))
  const projected = projectFromCanonicalHead(headFromPython)
  assert.equal(projected.project.name, 'Backend REAL Canonical')
  assert.equal(projected.etag, headFromPython.etag)
  assert.deepEqual(projected.project.fps, { num: 30000, den: 1001 })
})
