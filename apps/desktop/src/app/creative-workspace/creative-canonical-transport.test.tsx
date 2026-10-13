import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'

import { CreativeWorkspaceProvider, useCreativeWorkspace } from './CreativeWorkspaceContext'

const projectId = 'a'.repeat(32)
const compositionId = 'b'.repeat(32)

const first = {
  project_id: projectId, revision_id: 'c'.repeat(32),
  etag: '"' + '1'.repeat(16) + '-' + '2'.repeat(16) + '"',
  source: {
    schema_version: 1, project_id: projectId, name: 'Revision one', assets: {}, metadata: {},
    compositions: [{ composition_id: compositionId, name: 'Main', width: 320, height: 180,
      fps: { num: 30, den: 1 }, duration: '2', layers: [], tracks: [] }]
  }
}

const second = {
  ...first, revision_id: 'd'.repeat(32),
  etag: '"' + '3'.repeat(16) + '-' + '4'.repeat(16) + '"',
  source: { ...first.source, name: 'Revision two' }
}

function Harness() {
  const { project, canonicalRevision, openCanonicalProject, submitCanonicalCommand } = useCreativeWorkspace()

  return <div>
    <div data-testid="name">{project?.name ?? 'none'}</div>
    <div data-testid="rev">{canonicalRevision?.revisionId ?? 'none'}</div>
    <button onClick={() => void openCanonicalProject(projectId)}>Open verified project</button>
    <button onClick={() => void submitCanonicalCommand({
      commandId: 'layer.create',
      params: { composition_id: compositionId, layer_id: 'e'.repeat(32), name: 'Human layer' },
      idempotencyKey: 'mouse-first-action'
    })}>Send typed edit</button>
  </div>
}

it('React renders only the read-back after typed IPC edit; no optimistic second project', async () => {
  const open = vi.fn(async () => first)
  const apply = vi.fn(async () => second)
  Object.defineProperty(window, 'hermesDesktop', {
    configurable: true, value: { creativeCanonical: { open, apply } }
  })
  render(<CreativeWorkspaceProvider><Harness /></CreativeWorkspaceProvider>)
  expect(screen.getByTestId('name').textContent).toBe('none')
  fireEvent.click(screen.getByText('Open verified project'))
  await waitFor(() => expect(screen.getByTestId('name').textContent).toBe('Revision one'))
  fireEvent.click(screen.getByText('Send typed edit'))
  await waitFor(() => expect(screen.getByTestId('name').textContent).toBe('Revision two'))
  expect(apply).toHaveBeenCalledWith(expect.objectContaining({
    projectId, expectedRevisionId: first.revision_id, etag: first.etag,
    command: expect.objectContaining({ commandId: 'layer.create' })
  }))
  expect(screen.getByTestId('rev').textContent).toBe(second.revision_id)
})
