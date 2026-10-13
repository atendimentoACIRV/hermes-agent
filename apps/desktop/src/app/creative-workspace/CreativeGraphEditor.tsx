import { useCallback, useMemo, useState } from 'react'

import { useCreativeWorkspace } from './CreativeWorkspaceContext'
import type { CreativeKeyframe, CreativeLayer } from './types'

export function CreativeGraphEditor() {
  const { project, selection, applyEdit } = useCreativeWorkspace()
  const composition = project?.compositions[0]

  const selectedLayer = useMemo(() => {
    if (selection.selectedLayerIds.size === 0) {return null}
    const layerId = selection.selectedLayerIds.values().next().value

    return composition?.layers.find((l: CreativeLayer) => l.layerId === layerId) ?? null
  }, [selection.selectedLayerIds, composition])

  const [graphType, setGraphType] = useState<'value' | 'velocity'>('value')

  const propertiesWithKeyframes = useMemo(() => {
    const propMap = new Map<string, CreativeKeyframe[]>()

    for (const kf of selectedLayer?.keyframes ?? []) {
      if (!propMap.has(kf.propertyPath)) {propMap.set(kf.propertyPath, [])}
      propMap.get(kf.propertyPath)!.push(kf)
    }

    return Array.from(propMap.entries()).map(([propertyPath, keyframes]) => ({
      propertyPath,
      keyframes: keyframes.slice().sort((a: CreativeKeyframe, b: CreativeKeyframe) => a.time - b.time),
    }))
  }, [selectedLayer])

  const handleKeyframeDrag = useCallback((keyframeId: string, newTime: number, newValue: number) => {
    applyEdit({ type: 'editKeyframe', keyframeId, time: newTime, value: newValue })
  }, [applyEdit])

  const handleEasingChange = useCallback((keyframeId: string, easing: string) => {
    applyEdit({ type: 'editKeyframe', keyframeId, easing })
  }, [applyEdit])

  if (!selectedLayer || selectedLayer.keyframes.length === 0) {
    return (
      <div className="creative-graph-editor empty">
        <h3>Graph Editor</h3>
        <p>Select a layer with keyframes to edit curves</p>
      </div>
    )
  }

  return (
    <div aria-label="Graph Editor" className="creative-graph-editor" role="region">
      <div className="creative-graph-editor-header">
        <h3>Graph Editor</h3>
        <div className="creative-graph-editor-controls">
          <label>
            <input
              checked={graphType === 'value'}
              name="graph-type"
              onChange={() => setGraphType('value')}
              type="radio"
              value="value"
            />
            Value
          </label>
          <label>
            <input
              checked={graphType === 'velocity'}
              name="graph-type"
              onChange={() => setGraphType('velocity')}
              type="radio"
              value="velocity"
            />
            Velocity
          </label>
        </div>
      </div>

      <div className="creative-graph-editor-properties">
        {propertiesWithKeyframes.map(({ propertyPath, keyframes }) => (
          <div className="creative-graph-editor-property" key={propertyPath}>
            <div className="creative-graph-editor-property-label">{propertyPath}</div>
            <CreativeGraphCurve
              graphType={graphType}
              keyframes={keyframes}
              onEasingChange={handleEasingChange}
              onKeyframeDrag={handleKeyframeDrag}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

interface CreativeGraphCurveProps {
  keyframes: Array<{
    keyframeId: string
    propertyPath: string
    time: number
    value: unknown
    easing: string
  }>
  graphType: 'value' | 'velocity'
  onKeyframeDrag: (keyframeId: string, newTime: number, newValue: number) => void
  onEasingChange: (keyframeId: string, easing: string) => void
}

function CreativeGraphCurve({
  keyframes,
  graphType,
  onKeyframeDrag,
  onEasingChange,
}: CreativeGraphCurveProps) {
  const width = 400
  const height = 150
  const padding = 40

  const times = keyframes.map(k => k.time)
  const values = keyframes.map(k => Number(k.value))
  const minTime = Math.min(...times)
  const maxTime = Math.max(...times)
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const timeRange = maxTime - minTime || 1
  const valueRange = maxValue - minValue || 1

  const xScale = (time: number) => padding + ((time - minTime) / timeRange) * (width - 2 * padding)
  const yScale = (value: number) => height - padding - ((value - minValue) / valueRange) * (height - 2 * padding)

  const ordered = keyframes.slice().sort((a, b) => a.time - b.time)

  const pathData = ordered
    .map((kf, i) => {
      const x = xScale(kf.time)
      const y = yScale(Number(kf.value))

      return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`
    })
    .join(' ')

  return (
    <div className="creative-graph-curve">
      <svg className="creative-graph-svg" height={height} width={width}>
        <defs>
          <linearGradient id="graph-gradient" x1="0%" x2="0%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#00ff88" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#00ff88" stopOpacity="0" />
          </linearGradient>
        </defs>

        <rect fill="#1a1a1a" height={height} width={width} x={0} y={0} />
        <rect fill="none" height={height - 2 * padding} stroke="#333" width={width - 2 * padding} x={padding} y={padding} />

        <path
          d={pathData}
          fill="none"
          stroke="#00ff88"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
        />

        <path
          d={`${pathData} L ${xScale(keyframes[keyframes.length - 1].time)} ${height - padding} L ${xScale(keyframes[0].time)} ${height - padding} Z`}
          fill="url(#graph-gradient)"
        />

        {keyframes.map((kf: CreativeKeyframe) => (
          <g className="creative-graph-keyframe" key={kf.keyframeId}>
            <circle
              cx={xScale(kf.time)}
              cy={yScale(Number(kf.value))}
              fill="#00ff88"
              r={6}
              stroke="#fff"
              strokeWidth={2}
            />
            <text
              fill="#fff"
              fontSize={10}
              textAnchor="middle"
              x={xScale(kf.time)}
              y={yScale(Number(kf.value)) - 10}
            >
              {kf.easing}
            </text>
          </g>
        ))}
      </svg>

      <div className="creative-graph-keyframe-list">
        {keyframes.map((kf: CreativeKeyframe) => (
          <div className="creative-graph-keyframe-item" key={kf.keyframeId}>
            <span>@{kf.time.toFixed(3)}s</span>
            <input
              onChange={e => onKeyframeDrag(kf.keyframeId, kf.time, Number(e.target.value))}
              step="0.001"
              type="number"
              value={String(kf.value)}
            />
            <select
              onChange={e => onEasingChange(kf.keyframeId, e.target.value)}
              value={kf.easing}
            >
              <option value="linear">Linear</option>
              <option value="ease_in">Ease In</option>
              <option value="ease_out">Ease Out</option>
              <option value="ease_in_out">Ease In Out</option>
              <option value="ease_out_elastic">Ease Out Elastic</option>
              <option value="ease_out_bounce">Ease Out Bounce</option>
            </select>
          </div>
        ))}
      </div>
    </div>
  )
}
