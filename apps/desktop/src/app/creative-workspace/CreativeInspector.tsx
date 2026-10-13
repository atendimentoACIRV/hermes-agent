import { useMemo } from 'react'

import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import type { CreativeClip, CreativeKeyframe, CreativeLayer, CreativeTrack } from './types'

export function CreativeInspector() {
  const { project, selection, applyEdit } = useCreativeWorkspace()
  const composition = project?.compositions[0]

  const selectedClip = useMemo(() => {
    if (selection.selectedClipIds.size === 0) {return null}
    const clipId = selection.selectedClipIds.values().next().value

    for (const track of composition?.tracks ?? []) {
      const clip = track.clips.find((c: CreativeClip) => c.clipId === clipId)

      if (clip) {return { clip, track }}
    }

    return null
  }, [selection.selectedClipIds, composition])

  const selectedTrack = useMemo(() => {
    if (selection.selectedTrackIds.size === 0) {return null}
    const trackId = selection.selectedTrackIds.values().next().value

    return composition?.tracks.find((t: CreativeTrack) => t.trackId === trackId) ?? null
  }, [selection.selectedTrackIds, composition])

  const selectedLayer = useMemo(() => {
    if (selection.selectedLayerIds.size === 0) {return null}
    const layerId = selection.selectedLayerIds.values().next().value

    return composition?.layers.find((l: CreativeLayer) => l.layerId === layerId) ?? null
  }, [selection.selectedLayerIds, composition])

  const selectedKeyframe = useMemo(() => {
    if (selection.selectedKeyframeIds.size === 0) {return null}
    const keyframeId = selection.selectedKeyframeIds.values().next().value

    for (const layer of composition?.layers ?? []) {
      const kf = layer.keyframes.find((k: CreativeKeyframe) => k.keyframeId === keyframeId)

      if (kf) {return { keyframe: kf, layer }}
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
    <div aria-label="Inspector" className="creative-inspector" role="region">
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
              onChange={e => console.log('Speed change:', e.target.value)}
              step="0.01"
              type="number"
              value={selectedClip.clip.speed}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Reverse</label>
            <input
              checked={selectedClip.clip.reverse}
              onChange={e => console.log('Reverse change:', e.target.checked)}
              type="checkbox"
            />
          </div>
          <div className="creative-inspector-field">
            <label>Freeze Frame</label>
            <input
              checked={selectedClip.clip.freeze}
              onChange={e => console.log('Freeze change:', e.target.checked)}
              type="checkbox"
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
              checked={selectedTrack.locked}
              onChange={e => console.log('Track lock change:', e.target.checked)}
              type="checkbox"
            />
          </div>
          <div className="creative-inspector-field">
            <label>Muted</label>
            <input
              checked={selectedTrack.muted}
              onChange={e => console.log('Track mute change:', e.target.checked)}
              type="checkbox"
            />
          </div>
          <div className="creative-inspector-field">
            <label>Solo</label>
            <input
              checked={selectedTrack.solo}
              onChange={e => console.log('Track solo change:', e.target.checked)}
              type="checkbox"
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
              max="1"
              min="0"
              onChange={e => applyEdit({ type: 'setTransform', id: selectedLayer.layerId, property: 'opacity', value: Number(e.target.value) })}
              step="0.01"
              type="range"
              value={selectedLayer.transform.opacity}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Position X</label>
            <input
              onChange={e => applyEdit({ type: 'setTransform', id: selectedLayer.layerId, property: 'x', value: Number(e.target.value) })}
              step="1"
              type="number"
              value={selectedLayer.transform.x}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Position Y</label>
            <input
              onChange={e => applyEdit({ type: 'setTransform', id: selectedLayer.layerId, property: 'y', value: Number(e.target.value) })}
              step="1"
              type="number"
              value={selectedLayer.transform.y}
            />
          </div>

          {selectedLayer.kind === 'text' && (
            <div className="creative-inspector-field">
              <label htmlFor="creative-text-value">Text</label>
              <input id="creative-text-value" onChange={e => applyEdit({ type: 'setParameter', id: selectedLayer.layerId,
                  property: 'text', value: e.target.value })}
                type="text"
                value={String(selectedLayer.declaredParameters.text ?? '')} />
            </div>
          )}
          {(selectedLayer.kind === 'text' || selectedLayer.kind === 'shape') && (
            <div className="creative-inspector-field">
              <label htmlFor="creative-color-value">Color</label>
              <input id="creative-color-value" onChange={e => applyEdit({ type: 'setParameter', id: selectedLayer.layerId,
                  property: 'color', value: e.target.value })}
                type="color"
                value={String(selectedLayer.declaredParameters.color ?? '#ffffff')} />
            </div>
          )}
          {selectedLayer.kind === 'shape' && (['width', 'height'] as const).map(property => (
            <div className="creative-inspector-field" key={property}>
              <label htmlFor={'creative-' + property}>{property}</label>
              <input id={'creative-' + property} max={8192} min={0} onChange={e => applyEdit({ type: 'setParameter', id: selectedLayer.layerId,
                  property, value: Number(e.target.value) })}
                type="number"
                value={Number(selectedLayer.declaredParameters[property] ?? 0)} />
            </div>
          ))}
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
              onChange={e => applyEdit({ type: 'editKeyframe', keyframeId: selectedKeyframe.keyframe.keyframeId, time: Number(e.target.value) })}
              step="0.001"
              type="number"
              value={selectedKeyframe.keyframe.time}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Value</label>
            <input
              onChange={e => applyEdit({ type: 'editKeyframe', keyframeId: selectedKeyframe.keyframe.keyframeId, value: Number(e.target.value) })}
              type="text"
              value={String(selectedKeyframe.keyframe.value)}
            />
          </div>
          <div className="creative-inspector-field">
            <label>Easing</label>
            <select
              onChange={e => applyEdit({ type: 'editKeyframe', keyframeId: selectedKeyframe.keyframe.keyframeId, easing: e.target.value })}
              value={selectedKeyframe.keyframe.easing}
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
