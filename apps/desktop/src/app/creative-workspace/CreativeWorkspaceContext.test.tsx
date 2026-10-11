import { render, screen, fireEvent } from '@testing-library/react'
import { CreativeWorkspaceProvider, useCreativeWorkspace } from '@/app/creative-workspace'
import type { CreativeProject } from '@/app/creative-workspace'

function TestComponent() {
  const { project, selection, selectClip, selectTrack, selectLayer, selectKeyframe, clearSelection } = useCreativeWorkspace()
  return (
    <div>
      <div data-testid="project-name">{project?.name ?? 'none'}</div>
      <div data-testid="selected-clips">{selection.selectedClipIds.size}</div>
      <div data-testid="selected-tracks">{selection.selectedTrackIds.size}</div>
      <div data-testid="selected-layers">{selection.selectedLayerIds.size}</div>
      <div data-testid="selected-keyframes">{selection.selectedKeyframeIds.size}</div>
      <button onClick={() => selectClip('clip-1')}>Select Clip</button>
      <button onClick={() => selectTrack('track-1')}>Select Track</button>
      <button onClick={() => selectLayer('layer-1')}>Select Layer</button>
      <button onClick={() => selectKeyframe('keyframe-1')}>Select Keyframe</button>
      <button onClick={clearSelection}>Clear</button>
    </div>
  )
}

const mockProject: CreativeProject = {
  projectId: 'test-project',
  name: 'Test Project',
  width: 1920,
  height: 1080,
  fps: { num: 30, den: 1 },
  duration: 60,
  compositions: [{
    compositionId: 'comp-1',
    name: 'Main',
    tracks: [{
      trackId: 'track-1',
      name: 'Video 1',
      kind: 'video',
      locked: false,
      muted: false,
      solo: false,
      zIndex: 0,
      clips: [{
        clipId: 'clip-1',
        trackId: 'track-1',
        assetId: 'asset-1',
        name: 'Test Clip',
        timelineRange: { start: 0, end: 10 },
        sourceIn: 0,
        speed: 1,
        reverse: false,
        freeze: false,
        linkedClipIds: [],
      }],
    }],
    layers: [{
      layerId: 'layer-1',
      name: 'Title',
      kind: 'vector_svg',
      declaredParameters: { text: 'Hello' },
      opaqueCode: null,
      transform: { x: 0, y: 0, opacity: 1 },
      keyframes: [{
        keyframeId: 'keyframe-1',
        propertyPath: 'transform.opacity',
        time: 0,
        value: 0,
        easing: 'linear',
      }],
    }],
  }],
}

describe('CreativeWorkspaceContext', () => {
  it('provides project and selection state', () => {
    render(
      <CreativeWorkspaceProvider>
        <TestComponent />
      </CreativeWorkspaceProvider>
    )
    expect(screen.getByTestId('project-name').textContent).toBe('none')
    expect(screen.getByTestId('selected-clips').textContent).toBe('0')
  })

  it('allows selecting clips, tracks, layers, keyframes', () => {
    render(
      <CreativeWorkspaceProvider>
        <TestComponent />
      </CreativeWorkspaceProvider>
    )
    
    fireEvent.click(screen.getByText('Select Clip'))
    expect(screen.getByTestId('selected-clips').textContent).toBe('1')
    
    fireEvent.click(screen.getByText('Select Track'))
    expect(screen.getByTestId('selected-tracks').textContent).toBe('1')
    
    fireEvent.click(screen.getByText('Select Layer'))
    expect(screen.getByTestId('selected-layers').textContent).toBe('1')
    
    fireEvent.click(screen.getByText('Select Keyframe'))
    expect(screen.getByTestId('selected-keyframes').textContent).toBe('1')
    
    fireEvent.click(screen.getByText('Clear'))
    expect(screen.getByTestId('selected-clips').textContent).toBe('0')
    expect(screen.getByTestId('selected-tracks').textContent).toBe('0')
    expect(screen.getByTestId('selected-layers').textContent).toBe('0')
    expect(screen.getByTestId('selected-keyframes').textContent).toBe('0')
  })
})