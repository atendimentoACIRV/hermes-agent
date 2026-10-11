import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import { useMemo } from 'react'
import type { CreativeTrack, CreativeClip, CreativeLayer, CreativeKeyframe } from './types'

export function CreativeInspector() {
  const { project, selection } = useCreativeWorkspace()
  const composition = project?.compositions[0]

  const selectedClip = useMemo(() => {
    if (selection.selectedClipIds.size === 0) return null
    const clipId = selection.selectedClipIds.values().next().value
    for (const track of composition?.tracks ?? []) {
      const clip = track.clips.find((c: CreativeClip) => c.clipId === clipId)
      if (clip) return { clip, track }
    }
    return null
  }, [selection.selectedClipIds, composition])

  const selectedTrack = useMemo(() => {
    if (selection.selectedTrackIds.size === 0) return null
    const trackId = selection.selectedTrackIds.values().next().value
    return composition?.tracks.find((t: CreativeTrack) => t.trackId === trackId) ?? null
  }, [selection.selectedTrackIds, composition])

  const selectedLayer = useMemo(() => {
    if (selection.selectedLayerIds.size === 0) return null
    const layerId = selection.selectedLayerIds.values().next().value
    return composition?.layers.find((l: CreativeLayer) => l.layerId === layerId) ?? null
  }, [selection.selectedLayerIds, composition])

  const selectedKeyframe = useMemo(() => {
    if (selection.selectedKeyframeIds.size === 0) return null
    const keyframeId = selection.selectedKeyframeIds.values().next().value
    for (const layer of composition?.layers ?? []) {
      const kf = layer.keyframes.find((k: CreativeKeyframe) => k.keyframeId === keyframeId)
      if (kf) return { keyframe: kf, layer }
    }
    return null
  }, [selection.selectedKeyframeIds, composition])

  if (!selectedClip && !selectedTrack && !selectedLayer && !selectedKeyframe) {
    return (
      <div className="creative-inspector empty">
        <h3>Inspector</h3>
        <p>Select a clip, track, layer, or keyframe to inspect</p>
      </div>
    )
  }

  return (
    <div className="creative-inspector" role="region" aria-label="Inspector">
      <h3>Inspector</h3>

      {selectedClip && (
        <div className="creative-inspector-section">
          <h4>Clip: {selectedClip.clip.name}</h4>
          <div className="creative-inspector-field">
            <label>Clip ID</label>
            <code>{selectedClip.clip.clipId}</code>
          </div>
          <div className="creative-inspector-field">
            <label>Track</label>
            <span>{selectedClip.track.name}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Asset ID</label>
            <code>{selectedClip.clip.assetId}</code>
          </div>
          <div className="creative-inspector-field">
            <label>Timeline Range</label>
            <span>{selectedClip.clip.timelineRange.start.toFixed(3)}s - {selectedClip.clip.timelineRange.end.toFixed(3)}s</span>
          </div>
          <div className="creative-inspector-field">
            <label>Duration</label>
            <span>{(selectedClip.clip.timelineRange.end - selectedClip.clip.timelineRange.start).toFixed(3)}s</span>
          </div>
          <div className="creative-inspector-field">
            <label>Source In</label>
            <span>{selectedClip.clip.sourceIn.toFixed(3)}s</span>
          </div>
          <div className="creative-inspector-field">
            <label>Speed</label>
            <input
              type="number"
              step="0.01"
              value={selectedClip.clip.speed}
              onChange={e => console.log('Speed change:', e.target.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Reverse</label>
            <input
              type="checkbox"
              checked={selectedClip.clip.reverse}
              onChange={e => console.log('Reverse change:', e.target.checked)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Freeze Frame</label>
            <input
              type="checkbox"
              checked={selectedClip.clip.freeze}
              onChange={e => console.log('Freeze change:', e.target.checked)}
            />
          </div>
          {selectedClip.clip.linkedClipIds.length > 0 && (
            <div className="creative-inspector-field">
              <label>Linked Clips</label>
              <ul>
                {selectedClip.clip.linkedClipIds.map((id: string) => <li key={id}>{id}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {selectedTrack && (
        <div className="creative-inspector-section">
          <h4>Track: {selectedTrack.name}</h4>
          <div className="creative-inspector-field">
            <label>Track ID</label>
            <code>{selectedTrack.trackId}</code>
          </div>
          <div className="creative-inspector-field">
            <label>Kind</label>
            <span>{selectedTrack.kind}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Z-Index</label>
            <span>{selectedTrack.zIndex}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Locked</label>
            <input
              type="checkbox"
              checked={selectedTrack.locked}
              onChange={e => console.log('Track lock change:', e.target.checked)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Muted</label>
            <input
              type="checkbox"
              checked={selectedTrack.muted}
              onChange={e => console.log('Track mute change:', e.target.checked)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Solo</label>
            <input
              type="checkbox"
              checked={selectedTrack.solo}
              onChange={e => console.log('Track solo change:', e.target.checked)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Clips</label>
            <span>{selectedTrack.clips.length}</span>
          </div>
        </div>
      )}

      {selectedLayer && (
        <div className="creative-inspector-section">
          <h4>Layer: {selectedLayer.name}</h4>
          <div className="creative-inspector-field">
            <label>Layer ID</label>
            <code>{selectedLayer.layerId}</code>
          </div>
          <div className="creative-inspector-field">
            <label>Kind</label>
            <span>{selectedLayer.kind}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Opacity</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={selectedLayer.transform.opacity}
              onChange={e => console.log('Opacity change:', e.target.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Position X</label>
            <input
              type="number"
              step="1"
              value={selectedLayer.transform.x}
              onChange={e => console.log('X change:', e.target.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Position Y</label>
            <input
              type="number"
              step="1"
              value={selectedLayer.transform.y}
              onChange={e => console.log('Y change:', e.target.value)}
            />
          </div>

          {Object.keys(selectedLayer.declaredParameters).length > 0 && (
            <div className="creative-inspector-field">
              <label>Declared Parameters</label>
              <dl>
                {Object.entries(selectedLayer.declaredParameters).map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd><code>{String(value)}</code></dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {selectedLayer.opaqueCode && (
            <div className="creative-inspector-field">
              <label>Opaque Code</label>
              <pre>{selectedLayer.opaqueCode}</pre>
            </div>
          )}

          {selectedLayer.keyframes.length > 0 && (
            <div className="creative-inspector-field">
              <label>Keyframes</label>
              <ul>
                {selectedLayer.keyframes.map((kf: CreativeKeyframe) => (
                  <li key={kf.keyframeId}>
                    {kf.propertyPath} @ {kf.time.toFixed(3)}s = <code>{String(kf.value)}</code> ({kf.easing})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {selectedKeyframe && (
        <div className="creative-inspector-section">
          <h4>Keyframe</h4>
          <div className="creative-inspector-field">
            <label>Keyframe ID</label>
            <code>{selectedKeyframe.keyframe.keyframeId}</code>
          </div>
          <div className="creative-inspector-field">
            <label>Layer</label>
            <span>{selectedKeyframe.layer.name}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Property</label>
            <span>{selectedKeyframe.keyframe.propertyPath}</span>
          </div>
          <div className="creative-inspector-field">
            <label>Time</label>
            <input
              type="number"
              step="0.001"
              value={selectedKeyframe.keyframe.time}
              onChange={e => console.log('Keyframe time change:', e.target.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Value</label>
            <input
              type="text"
              value={String(selectedKeyframe.keyframe.value)}
              onChange={e => console.log('Keyframe value change:', e.target.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Easing</label>
            <select
              value={selectedKeyframe.keyframe.easing}
              onChange={e => console.log('Easing change:', e.target.value)}
            >
              <option value="linear">Linear</option>
              <option value="ease_in">Ease In</option>
              <option value="ease_out">Ease Out</option>
              <option value="ease_in_out">Ease In Out</option>
              <option value="ease_out_elastic">Ease Out Elastic</option>
              <option value="ease_out_bounce">Ease Out Bounce</option>
            </select>
          </div>
        </div>
      )}
    </div>
  )
}
