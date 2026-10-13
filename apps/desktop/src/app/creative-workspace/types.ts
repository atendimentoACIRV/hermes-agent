import type { CreativeEdit } from './creative-mvp-model'

export type WorkspaceMode = 'montage' | 'motion' | 'design' | '3d' | 'transcript'

export interface CreativeProject {
  projectId: string
  name: string
  width: number
  height: number
  fps: { num: number; den: number }
  duration: number
  compositions: CreativeComposition[]
}

export interface CreativeComposition {
  compositionId: string
  name: string
  tracks: CreativeTrack[]
  layers: CreativeLayer[]
}

export interface CreativeTrack {
  trackId: string
  name: string
  kind: 'video' | 'audio' | 'graphic' | 'subtitle'
  locked: boolean
  muted: boolean
  solo: boolean
  zIndex: number
  clips: CreativeClip[]
}

export interface CreativeClip {
  clipId: string
  trackId: string
  assetId: string
  name: string
  timelineRange: { start: number; end: number }
  sourceIn: number
  speed: number
  reverse: boolean
  freeze: boolean
  linkedClipIds: string[]
}

export interface CreativeLayer {
  layerId: string
  name: string
  kind: 'vector_svg' | 'html_canvas' | 'three_js_scene' | 'text' | 'shape'
  declaredParameters: Record<string, unknown>
  opaqueCode: string | null
  transform: { x: number; y: number; opacity: number }
  keyframes: CreativeKeyframe[]
}

export interface CreativeKeyframe {
  keyframeId: string
  propertyPath: string
  time: number
  value: unknown
  easing: string
}

export interface CreativeAsset {
  assetId: string
  name: string
  kind: string
  path: string
  sha256: string
  duration?: number
  width?: number
  height?: number
}

export interface SelectionState {
  selectedTrackIds: Set<string>
  selectedClipIds: Set<string>
  selectedLayerIds: Set<string>
  selectedKeyframeIds: Set<string>
  playheadTime: number
}

export interface CreativeWorkspaceContextValue {
  applyEdit: (edit: CreativeEdit) => void
  undo: () => void
  redo: () => void
  canUndo: boolean
  canRedo: boolean

  project: CreativeProject | null
  selection: SelectionState
  workspaceMode: WorkspaceMode
  playheadTime: number
  isPlaying: boolean
  pinnedPanels: Set<string>
  setProject: (project: CreativeProject | null) => void
  setSelection: (selection: Partial<SelectionState>) => void
  setWorkspaceMode: (mode: WorkspaceMode) => void
  setPlayheadTime: (time: number) => void
  setIsPlaying: (playing: boolean) => void
  togglePinPanel: (panelId: string) => void
  selectClip: (clipId: string, multi?: boolean) => void
  selectTrack: (trackId: string, multi?: boolean) => void
  selectLayer: (layerId: string, multi?: boolean) => void
  selectKeyframe: (keyframeId: string, multi?: boolean) => void
  clearSelection: () => void
}