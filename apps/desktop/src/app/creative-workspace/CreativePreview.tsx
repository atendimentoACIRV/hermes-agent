import { useCallback } from 'react'

import { sampledTransform } from './creative-mvp-model'
import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import type { CreativeComposition } from './types'

export function CreativePreview() {
  const { project, playheadTime, isPlaying, setIsPlaying } = useCreativeWorkspace()
  const composition = project?.compositions[0]

  const handlePlayPause = () => setIsPlaying(!isPlaying)

  return (
    <div aria-label="Preview" className="creative-preview" role="region">
      <div className="creative-preview-header">
        <h3>Preview</h3>
        <div className="creative-preview-controls">
          <button
            aria-label={isPlaying ? 'Pause' : 'Play'}
            className="creative-preview-btn"
            onClick={handlePlayPause}
          >
            {isPlaying ? '⏸' : '▶'}
          </button>
          <span className="creative-preview-time">{playheadTime.toFixed(3)}s</span>
        </div>
      </div>

      <div className="creative-preview-canvas">
        {composition ? (
          <CreativePreviewRenderer
            composition={composition}
            height={project?.height ?? 1080}
            playheadTime={playheadTime}
            width={project?.width ?? 1920}
          />
        ) : (
          <div className="creative-preview-placeholder">
            <p>No composition to preview</p>
          </div>
        )}
      </div>
    </div>
  )
}

interface CreativePreviewRendererProps {
  composition: CreativeComposition
  playheadTime: number
  width: number
  height: number
}

function CreativePreviewRenderer({
  composition,
  playheadTime,
  width,
  height,
}: CreativePreviewRendererProps) {
  const { selectLayer } = useCreativeWorkspace()
  const onSelect = useCallback((id: string) => selectLayer(id), [selectLayer])
  const aspectRatio = width / height
  const containerWidth = Math.min(800, window.innerWidth * 0.8)
  const containerHeight = containerWidth / aspectRatio

  return (
    <div
      className="creative-preview-renderer"
      style={{
        width: containerWidth,
        height: containerHeight,
        background: '#1a1a1a',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <svg
        height={containerHeight}
        style={{ position: 'absolute', top: 0, left: 0 }}
        viewBox={`0 0 ${width} ${height}`}
        width={containerWidth}
      >
        <rect fill="#000000" height={height} width={width} />

        {composition.layers
          .filter(layer => ['vector_svg', 'text', 'shape'].includes(layer.kind))
          .map(layer => {
            const { opacity, x, y } = sampledTransform(layer, playheadTime)
            const params = layer.declaredParameters

            if (params.text) {
              return (
                <text
                  fill={params.color as string ?? '#ffffff'}
                  fontFamily="sans-serif"
                  fontSize={params.font_size as number ?? 32}
                  key={layer.layerId}
                  onClick={() => onSelect(layer.layerId)}
                  opacity={opacity}
                  style={{ cursor: 'pointer' }}
                  x={x}
                  y={y}
                >
                  {String(params.text)}
                </text>
              )
            }

            if (layer.kind === 'shape') {return (
              <rect fill={String(params.color ?? '#ffffff')} height={Number(params.height ?? 160)} key={layer.layerId}
                onClick={() => onSelect(layer.layerId)} opacity={opacity}
                style={{ cursor: 'pointer' }} width={Number(params.width ?? 240)}
                x={x} y={y} />
            )}

            return null
          })}

        {composition.tracks
          .filter(track => track.kind === 'video')
          .flatMap(track => track.clips)
          .filter(clip => clip.timelineRange.start <= playheadTime && playheadTime < clip.timelineRange.end)
          .map(clip => (
            <rect
              fill="#333"
              height={height}
              key={clip.clipId}
              opacity={0.5}
              width={width}
              x={0}
              y={0}
            />
          ))}
      </svg>

      <div
        className="creative-preview-playhead-indicator"
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 4,
          background: 'linear-gradient(90deg, transparent, #00ff88, transparent)',
          opacity: 0.6,
        }}
      />
    </div>
  )
}
