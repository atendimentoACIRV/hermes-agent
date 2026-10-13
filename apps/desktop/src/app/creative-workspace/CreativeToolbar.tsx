import { useEffect } from 'react'

import { downloadCreativeFile, renderCreativeSvg } from './creative-mvp-model'
import { useCreativeWorkspace } from './CreativeWorkspaceContext'

export function CreativeToolbar() {
  const {
    project, selection, workspaceMode, setWorkspaceMode, isPlaying, setIsPlaying,
    playheadTime, setPlayheadTime, applyEdit, selectLayer, undo, redo, canUndo, canRedo,
  } = useCreativeWorkspace()

  const fps = project ? project.fps.num / project.fps.den : 30
  const duration = project?.duration ?? 0
  const clampTime = (seconds: number) => Math.round(Math.min(duration, Math.max(0, seconds)) * fps) / fps

  useEffect(() => {
    if (!isPlaying || !project) {return}

    const timer = window.setInterval(() => {
      if (playheadTime + 1 / fps >= duration) {
        setPlayheadTime(duration)
        setIsPlaying(false)
      } else {setPlayheadTime(clampTime(playheadTime + 1 / fps))}
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

    if (!layer) {return}
    applyEdit({ type: 'upsertKeyframe', id: layer.layerId, property: 'opacity',
      time: clampTime(playheadTime), value: layer.transform.opacity, keyframeId: crypto.randomUUID() })
  }

  const save = () => {
    if (!project) {return}
    downloadCreativeFile(`${project.projectId}.json`, JSON.stringify(project, null, 2), 'application/json')
  }

  const exportFrame = () => {
    if (!project) {return}
    downloadCreativeFile(`${project.projectId}-frame.svg`,
      renderCreativeSvg(project, clampTime(playheadTime)), 'image/svg+xml')
  }

  return (
    <div aria-label="Creative toolbar" className="creative-toolbar" role="toolbar">
      <label className="creative-toolbar-time">Project
        <input aria-label="Project name" maxLength={128}
          onChange={e => applyEdit({ type: 'renameProject', name: e.target.value })}
          value={project?.name ?? ''} />
      </label>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" onClick={() => addLayer('text')} title="Add text">+ Text</button>
        <button className="creative-toolbar-btn" onClick={() => addLayer('shape')} title="Add rectangle">+ Rectangle</button>
        <button className="creative-toolbar-btn" disabled={!selection.selectedLayerIds.size}
          onClick={() => {
            const id = selection.selectedLayerIds.values().next().value

            if (id) {applyEdit({ type: 'removeLayer', id })}
          }}
          title="Remove selected layer">Remove layer</button>
        <button className="creative-toolbar-btn" disabled={!selection.selectedLayerIds.size}
          onClick={addKeyframe} title="Add opacity keyframe">+ Keyframe</button>
      </div>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" disabled={!isPlaying && !playheadTime}
          onClick={() => { setIsPlaying(false); setPlayheadTime(0) }} title="Stop">⏹</button>
        <button className="creative-toolbar-btn" onClick={() => setPlayheadTime(clampTime(playheadTime - 1 / fps))}
          title="Previous frame">⏮</button>
        <button className="creative-toolbar-btn" onClick={() => setIsPlaying(!isPlaying)}
          title={isPlaying ? 'Pause' : 'Play'}>{isPlaying ? '⏸' : '▶'}</button>
        <button className="creative-toolbar-btn" onClick={() => setPlayheadTime(clampTime(playheadTime + 1 / fps))}
          title="Next frame">⏭</button>
        <span className="creative-toolbar-time">{playheadTime.toFixed(2)} / {duration}s</span>
        <input aria-label="Seek preview" max={duration} min={0} onChange={e => setPlayheadTime(clampTime(Number(e.target.value)))}
          step={1/fps} type="range" value={playheadTime} />
      </div>
      <div className="creative-toolbar-group">
        <select aria-label="Workspace mode" className="creative-toolbar-select" onChange={e => setWorkspaceMode(e.target.value as typeof workspaceMode)}
          value={workspaceMode}>
          <option value="montage">Montage</option>
          <option value="motion">Motion</option>
          <option value="design">Design</option>
          <option value="3d">3D</option>
          <option value="transcript">Transcript</option>
        </select>
      </div>
      <div className="creative-toolbar-group">
        <button className="creative-toolbar-btn" disabled={!canUndo} onClick={undo} title="Undo">↶</button>
        <button className="creative-toolbar-btn" disabled={!canRedo} onClick={redo} title="Redo">↷</button>
        <button className="creative-toolbar-btn" onClick={save} title="Save editable JSON">💾 Save</button>
        <button className="creative-toolbar-btn" onClick={exportFrame} title="Export current SVG frame">📤 SVG</button>
      </div>
    </div>
  )
}
