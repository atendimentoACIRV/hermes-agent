import { useEffect } from 'react'
import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import { downloadCreativeFile, renderCreativeSvg } from './creative-mvp-model'

export function CreativeToolbar() {
  const {
    project, selection, workspaceMode, setWorkspaceMode, isPlaying, setIsPlaying,
    playheadTime, setPlayheadTime, applyEdit, selectLayer, undo, redo, canUndo, canRedo,
  } = useCreativeWorkspace()
  const fps = project ? project.fps.num / project.fps.den : 30
  const duration = project?.duration ?? 0
  const clampTime = (seconds: number) => Math.round(Math.min(duration, Math.max(0, seconds)) * fps) / fps

  useEffect(() => {
    if (!isPlaying || !project) return
    const timer = window.setInterval(() => {
      if (playheadTime + 1 / fps >= duration) {
        setPlayheadTime(duration)
        setIsPlaying(false)
      } else setPlayheadTime(clampTime(playheadTime + 1 / fps))
    }, 1000 / fps)
    return () => window.clearInterval(timer)
  }, [isPlaying, playheadTime, fps, duration, setPlayheadTime, setIsPlaying, project])

  const addLayer = (layerKind: 'text' | 'shape') => {
    const id = crypto.randomUUID()
    applyEdit({ type: 'addLayer', layerKind, id })
    selectLayer(id)
  }
  const addKeyframe = () => {
    const layerId = selection.selectedLayerIds.values().next().value
    const layer = project?.compositions[0].layers.find(item => item.layerId === layerId)
    if (!layer) return
    applyEdit({ type: 'upsertKeyframe', id: layer.layerId, property: 'opacity',
      time: clampTime(playheadTime), value: layer.transform.opacity, keyframeId: crypto.randomUUID() })
  }
  const save = () => {
    if (!project) return
    downloadCreativeFile(`${project.projectId}.json`, JSON.stringify(project, null, 2), 'application/json')
  }
  const exportFrame = () => {
    if (!project) return
    downloadCreativeFile(`${project.projectId}-frame.svg`,
      renderCreativeSvg(project, clampTime(playheadTime)), 'image/svg+xml')
  }
  return (
    <div className="creative-toolbar" role="toolbar" aria-label="Creative toolbar">
      <label className="creative-toolbar-time">Project
        <input aria-label="Project name" value={project?.name ?? ''}
          maxLength={128}
          onChange={e => applyEdit({ type: 'renameProject', name: e.target.value })} />
      </label>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" title="Add text" onClick={() => addLayer('text')}>+ Text</button>
        <button className="creative-toolbar-btn" title="Add rectangle" onClick={() => addLayer('shape')}>+ Rectangle</button>
        <button className="creative-toolbar-btn" title="Remove selected layer"
          disabled={!selection.selectedLayerIds.size}
          onClick={() => {
            const id = selection.selectedLayerIds.values().next().value
            if (id) applyEdit({ type: 'removeLayer', id })
          }}>Remove layer</button>
        <button className="creative-toolbar-btn" title="Add opacity keyframe"
          disabled={!selection.selectedLayerIds.size} onClick={addKeyframe}>+ Keyframe</button>
      </div>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" onClick={() => { setIsPlaying(false); setPlayheadTime(0) }}
          title="Stop" disabled={!isPlaying && !playheadTime}>⏹</button>
        <button className="creative-toolbar-btn" onClick={() => setPlayheadTime(clampTime(playheadTime - 1 / fps))}
          title="Previous frame">⏮</button>
        <button className="creative-toolbar-btn" onClick={() => setIsPlaying(!isPlaying)}
          title={isPlaying ? 'Pause' : 'Play'}>{isPlaying ? '⏸' : '▶'}</button>
        <button className="creative-toolbar-btn" onClick={() => setPlayheadTime(clampTime(playheadTime + 1 / fps))}
          title="Next frame">⏭</button>
        <span className="creative-toolbar-time">{playheadTime.toFixed(2)} / {duration}s</span>
        <input aria-label="Seek preview" type="range" min={0} max={duration}
          step={1/fps} value={playheadTime} onChange={e => setPlayheadTime(clampTime(Number(e.target.value)))} />
      </div>
      <div className="creative-toolbar-group">
        <select className="creative-toolbar-select" aria-label="Workspace mode" value={workspaceMode}
          onChange={e => setWorkspaceMode(e.target.value as typeof workspaceMode)}>
          <option value="montage">Montage</option>
          <option value="motion">Motion</option>
          <option value="design">Design</option>
          <option value="3d">3D</option>
          <option value="transcript">Transcript</option>
        </select>
      </div>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" title="Undo" onClick={undo} disabled={!canUndo}>↶</button>
        <button className="creative-toolbar-btn" title="Redo" onClick={redo} disabled={!canRedo}>↷</button>
        <button className="creative-toolbar-btn" title="Save editable JSON" onClick={save}>💾 Save</button>
        <button className="creative-toolbar-btn" title="Export current SVG frame" onClick={exportFrame}>📤 SVG</button>
      </div>
    </div>
  )
}
