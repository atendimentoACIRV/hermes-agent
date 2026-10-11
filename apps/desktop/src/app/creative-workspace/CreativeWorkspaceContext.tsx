import { createContext, useContext, useState, useCallback, useMemo } from 'react'
import { atom } from 'nanostores'
import { $workspaceIsPage } from '@/app/routes'
import type {
  CreativeProject,
  CreativeComposition,
  CreativeTrack,
  CreativeClip,
  CreativeLayer,
  CreativeKeyframe,
  CreativeAsset,
  SelectionState,
  WorkspaceMode,
  CreativeWorkspaceContextValue,
} from './types'

export const CREATIVE_WORKSPACE_ROUTE = '/creative'

export const $creativeProject = atom<CreativeProject | null>(null)
export const $creativeSelection = atom<SelectionState>({
  selectedTrackIds: new Set(),
  selectedClipIds: new Set(),
  selectedLayerIds: new Set(),
  selectedKeyframeIds: new Set(),
  playheadTime: 0,
})
export const $creativeWorkspaceMode = atom<WorkspaceMode>('montage')
export const $creativePlayheadTime = atom(0)
export const $creativeIsPlaying = atom(false)
export const $creativePinnedPanels = atom<Set<string>>(new Set())

const CreativeWorkspaceContext = createContext<CreativeWorkspaceContextValue | null>(null)

export function useCreativeWorkspace() {
  const ctx = useContext(CreativeWorkspaceContext)
  if (!ctx) throw new Error('useCreativeWorkspace must be used within CreativeWorkspaceProvider')
  return ctx
}

export function CreativeWorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [project, setProjectState] = useState<CreativeProject | null>(null)
  const [selection, setSelectionState] = useState<SelectionState>({
    selectedTrackIds: new Set(),
    selectedClipIds: new Set(),
    selectedLayerIds: new Set(),
    selectedKeyframeIds: new Set(),
    playheadTime: 0,
  })
  const [workspaceMode, setWorkspaceModeState] = useState<WorkspaceMode>('montage')
  const [playheadTime, setPlayheadTimeState] = useState(0)
  const [isPlaying, setIsPlayingState] = useState(false)
  const [pinnedPanels, setPinnedPanelsState] = useState<Set<string>>(new Set())

  const setProject = useCallback((p: CreativeProject | null) => {
    setProjectState(p)
    $creativeProject.set(p)
  }, [])

  const setSelection = useCallback((partial: Partial<SelectionState>) => {
    setSelectionState(prev => {
      const next = { ...prev, ...partial }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const setWorkspaceMode = useCallback((mode: WorkspaceMode) => {
    setWorkspaceModeState(mode)
    $creativeWorkspaceMode.set(mode)
  }, [])

  const setPlayheadTime = useCallback((time: number) => {
    setPlayheadTimeState(time)
    $creativePlayheadTime.set(time)
    setSelectionState(prev => {
      const next = { ...prev, playheadTime: time }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const setIsPlaying = useCallback((playing: boolean) => {
    setIsPlayingState(playing)
    $creativeIsPlaying.set(playing)
  }, [])

  const togglePinPanel = useCallback((panelId: string) => {
    setPinnedPanelsState(prev => {
      const next = new Set(prev)
      if (next.has(panelId)) next.delete(panelId)
      else next.add(panelId)
      $creativePinnedPanels.set(next)
      return next
    })
  }, [])

  const selectClip = useCallback((clipId: string, multi = false) => {
    setSelectionState(prev => {
      const next = { ...prev }
      if (multi) {
        if (next.selectedClipIds.has(clipId)) next.selectedClipIds.delete(clipId)
        else next.selectedClipIds.add(clipId)
      } else {
        next.selectedClipIds = new Set([clipId])
        next.selectedTrackIds.clear()
        next.selectedLayerIds.clear()
        next.selectedKeyframeIds.clear()
      }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const selectTrack = useCallback((trackId: string, multi = false) => {
    setSelectionState(prev => {
      const next = { ...prev }
      if (multi) {
        if (next.selectedTrackIds.has(trackId)) next.selectedTrackIds.delete(trackId)
        else next.selectedTrackIds.add(trackId)
      } else {
        next.selectedTrackIds = new Set([trackId])
        next.selectedClipIds.clear()
        next.selectedLayerIds.clear()
        next.selectedKeyframeIds.clear()
      }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const selectLayer = useCallback((layerId: string, multi = false) => {
    setSelectionState(prev => {
      const next = { ...prev }
      if (multi) {
        if (next.selectedLayerIds.has(layerId)) next.selectedLayerIds.delete(layerId)
        else next.selectedLayerIds.add(layerId)
      } else {
        next.selectedLayerIds = new Set([layerId])
        next.selectedTrackIds.clear()
        next.selectedClipIds.clear()
        next.selectedKeyframeIds.clear()
      }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const selectKeyframe = useCallback((keyframeId: string, multi = false) => {
    setSelectionState(prev => {
      const next = { ...prev }
      if (multi) {
        if (next.selectedKeyframeIds.has(keyframeId)) next.selectedKeyframeIds.delete(keyframeId)
        else next.selectedKeyframeIds.add(keyframeId)
      } else {
        next.selectedKeyframeIds = new Set([keyframeId])
        next.selectedTrackIds.clear()
        next.selectedClipIds.clear()
        next.selectedLayerIds.clear()
      }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const clearSelection = useCallback(() => {
    setSelectionState(prev => {
      const next: SelectionState = {
        ...prev,
        selectedTrackIds: new Set<string>(),
        selectedClipIds: new Set<string>(),
        selectedLayerIds: new Set<string>(),
        selectedKeyframeIds: new Set<string>(),
      }
      $creativeSelection.set(next)
      return next
    })
  }, [])

  const value = useMemo(() => ({
    project,
    selection,
    workspaceMode,
    playheadTime,
    isPlaying,
    pinnedPanels,
    setProject,
    setSelection,
    setWorkspaceMode,
    setPlayheadTime,
    setIsPlaying,
    togglePinPanel,
    selectClip,
    selectTrack,
    selectLayer,
    selectKeyframe,
    clearSelection,
  }), [project, selection, workspaceMode, playheadTime, isPlaying, pinnedPanels])

  return (
    <CreativeWorkspaceContext.Provider value={value}>
      {children}
    </CreativeWorkspaceContext.Provider>
  )
}

export type {
  CreativeProject,
  CreativeComposition,
  CreativeTrack,
  CreativeClip,
  CreativeLayer,
  CreativeKeyframe,
  CreativeAsset,
  SelectionState,
  WorkspaceMode,
  CreativeWorkspaceContextValue,
} from './types'
