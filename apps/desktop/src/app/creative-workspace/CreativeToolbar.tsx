import { useCreativeWorkspace } from './CreativeWorkspaceContext'

export function CreativeToolbar() {
  const { project, isPlaying, setIsPlaying, playheadTime, setPlayheadTime, workspaceMode } = useCreativeWorkspace()
  const composition = project?.compositions[0]
  const totalDuration = project?.duration ?? 60

  const handlePlayPause = () => setIsPlaying(!isPlaying)
  const handleStop = () => { setIsPlaying(false); setPlayheadTime(0) }
  const handleStepBack = () => setPlayheadTime(Math.max(0, playheadTime - 1/30))
  const handleStepForward = () => setPlayheadTime(Math.min(totalDuration, playheadTime + 1/30))

  return (
    <div className="creative-toolbar" role="toolbar" aria-label="Creative toolbar">
      <div className="creative-toolbar-group">
        <button
          className="creative-toolbar-btn"
          onClick={handleStop}
          title="Stop (Home)"
          disabled={!isPlaying && playheadTime === 0}
        >
          ⏹
        </button>
        <button
          className="creative-toolbar-btn"
          onClick={handleStepBack}
          title="Step Back (←)"
        >
          ⏮
        </button>
        <button
          className="creative-toolbar-btn"
          onClick={handlePlayPause}
          title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>
        <button
          className="creative-toolbar-btn"
          onClick={handleStepForward}
          title="Step Forward (→)"
        >
          ⏭
        </button>
      </div>

      <div className="creative-toolbar-group">
        <span className="creative-toolbar-time">
          {formatTime(playheadTime)} / {formatTime(totalDuration)}
        </span>
      </div>

      <div className="creative-toolbar-group">
        <select
          className="creative-toolbar-select"
          value={workspaceMode}
          onChange={e => console.log('Mode change:', e.target.value)}
        >
          <option value="montage">Montage</option>
          <option value="motion">Motion</option>
          <option value="design">Design</option>
          <option value="3d">3D</option>
          <option value="transcript">Transcript</option>
        </select>
      </div>

      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" title="Undo (Ctrl+Z)">↶</button>
        <button className="creative-toolbar-btn" title="Redo (Ctrl+Shift+Z)">↷</button>
      </div>

      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" title="Save">💾</button>
        <button className="creative-toolbar-btn" title="Export">📤</button>
      </div>
    </div>
  )
}

function formatTime(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const frames = Math.floor((seconds % 1) * 30)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`
}
