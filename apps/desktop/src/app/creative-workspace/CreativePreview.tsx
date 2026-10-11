import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import type { CreativeComposition } from './types'

export function CreativePreview() {
  const { project, playheadTime, isPlaying } = useCreativeWorkspace()
  const composition = project?.compositions[0]

  const handlePlayPause = () => {
    // Would dispatch to backend to toggle playback
    console.log('Play/pause toggled')
  }

  const handleSeek = (time: number) => {
    // Would dispatch to backend to seek
    console.log('Seek to:', time)
  }

  return (
    <div className="creative-preview" role="region" aria-label="Preview">
      <div className="creative-preview-header">
        <h3>Preview</h3>
        <div className="creative-preview-controls">
          <button
            className="creative-preview-btn"
            onClick={handlePlayPause}
            aria-label={isPlaying ? 'Pause' : 'Play'}
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
            playheadTime={playheadTime}
            width={project?.width ?? 1920}
            height={project?.height ?? 1080}
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
        width={containerWidth}
        height={containerHeight}
        viewBox={`0 0 ${width} ${height}`}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <rect width={width} height={height} fill="#000000" />

        {composition.layers
          .filter(layer => layer.kind === 'vector_svg')
          .map(layer => {
            const opacity = layer.transform.opacity
            const x = layer.transform.x
            const y = layer.transform.y
            const params = layer.declaredParameters

            if (params.text) {
              return (
                <text
                  key={layer.layerId}
                  x={x}
                  y={y}
                  fill={params.color as string ?? '#ffffff'}
                  fontSize={params.font_size as number ?? 32}
                  opacity={opacity}
                  fontFamily="sans-serif"
                >
                  {String(params.text)}
                </text>
              )
            }
            return null
          })}

        {composition.tracks
          .filter(track => track.kind === 'video')
          .flatMap(track => track.clips)
          .filter(clip => clip.timelineRange.start <= playheadTime && playheadTime < clip.timelineRange.end)
          .map(clip => (
            <rect
              key={clip.clipId}
              x={0}
              y={0}
              width={width}
              height={height}
              fill="#333"
              opacity={0.5}
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
