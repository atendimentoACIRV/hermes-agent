import { atom } from 'nanostores'
import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'

import { type CanonicalCreativeProjection, projectFromCanonicalHead } from './canonical-creative-projection'
import { applyCreativeEdit, assertCreativeProject } from './creative-mvp-model'
import type { CreativeEdit } from './creative-mvp-model'
import type {
  CreativeProject,
  CreativeWorkspaceContextValue,
  SelectionState,
  WorkspaceMode,
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

  if (!ctx) {throw new Error('useCreativeWorkspace must be used within CreativeWorkspaceProvider')}

  return ctx
}

export function CreativeWorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [projectState, setProjectState] = useState<CreativeProject | null>(null)
  const projectRef = useRef<CreativeProject | null>(null)
  const undoHistory = useRef<CreativeProject[]>([])
  const redoHistory = useRef<CreativeProject[]>([])
  const [historyStamp, setHistoryStamp] = useState(0)

  const [canonicalHead, setCanonicalHead] = useState<CanonicalCreativeProjection | null>(null)
  const project = canonicalHead?.project ?? projectState

  const canonicalRevision = useMemo(
    () => canonicalHead ? { revisionId: canonicalHead.revisionId, etag: canonicalHead.etag } : null,
    [canonicalHead]
  )

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
    if (p) {assertCreativeProject(p)}
    setCanonicalHead(null)
    projectRef.current = p
    undoHistory.current = []
    redoHistory.current = []
    setProjectState(p)
    $creativeProject.set(p)
    setHistoryStamp(v => v + 1)
  }, [])

  const applyEdit = useCallback((edit: CreativeEdit) => {
    const current = projectRef.current ?? project

    if (!current) {throw new Error('Open a project before editing')}
    const next = applyCreativeEdit(current, edit)
    undoHistory.current.push(current)

    if (undoHistory.current.length > 100) {undoHistory.current.shift()}
    redoHistory.current = []
    projectRef.current = next
    setProjectState(next)
    $creativeProject.set(next)
    setHistoryStamp(v => v + 1)
  }, [project])

  const undo = useCallback(() => {
    const previous = undoHistory.current.pop()

    if (!previous) {return}

    const current = projectRef.current ?? project

    if (current) {redoHistory.current.push(current)}
    projectRef.current = previous
    setProjectState(previous)
    $creativeProject.set(previous)
    setHistoryStamp(v => v + 1)
  }, [project])

  const redo = useCallback(() => {
    const next = redoHistory.current.pop()

    if (!next) {return}

    const current = projectRef.current ?? project

    if (current) {redoHistory.current.push(current)}
    projectRef.current = next
    setProjectState(next)
    $creativeProject.set(next)
    setHistoryStamp(v => v + 1)
  }, [project])

  const acceptCanonicalHead = useCallback((head: unknown) => {
    // Validation is performed before the view state changes. There is no
    // optimistic project mutation and no writable React-side project store.
    const projection = projectFromCanonicalHead(head)
    setCanonicalHead(projection)
    projectRef.current = projection.project
    setProjectState(projection.project)
    undoHistory.current = []
    redoHistory.current = []
    $creativeProject.set(projection.project)
    setHistoryStamp(v => v + 1)
  }, [])

  const clearCanonicalHead = useCallback(() => {
    setCanonicalHead(null)
    projectRef.current = null
    setProjectState(null)
    undoHistory.current = []
    redoHistory.current = []
    $creativeProject.set(null)
    setHistoryStamp(v => v + 1)
  }, [])

  const openCanonicalProject = useCallback(async (projectId: string) => {
    const bridge = window.hermesDesktop?.creativeCanonical

    if (!bridge) { throw new Error('creative_canonical_bridge_unavailable') }
    const verified = projectFromCanonicalHead(await bridge.open({ projectId }))

    if (verified.project.projectId !== projectId) { throw new Error('creative_project_mismatch') }
    setCanonicalHead(verified)
    projectRef.current = verified.project
    setProjectState(verified.project)
    undoHistory.current = []
    redoHistory.current = []
    $creativeProject.set(verified.project)
    setHistoryStamp(v => v + 1)
  }, [])

  const submitCanonicalCommand = useCallback(async (command: {
    commandId: 'layer.create' | 'layer.setProperty'
    params: Record<string, unknown>
    idempotencyKey: string
  }) => {
    if (!canonicalHead) { throw new Error('creative_canonical_head_required') }
    const bridge = window.hermesDesktop?.creativeCanonical

    if (!bridge) { throw new Error('creative_canonical_bridge_unavailable') }
    const transactionId = globalThis.crypto?.randomUUID?.().replaceAll('-', '')

    if (!transactionId || !/^[a-f0-9]{32}$/.test(transactionId)) {
      throw new Error('creative_secure_transaction_id_unavailable')
    }

    const next = projectFromCanonicalHead(await bridge.apply({
      projectId: canonicalHead.project.projectId,
      expectedRevisionId: canonicalHead.revisionId,
      etag: canonicalHead.etag,
      transactionId,
      command
    }))

    if (next.project.projectId !== canonicalHead.project.projectId) {
      throw new Error('creative_project_mismatch')
    }

    setCanonicalHead(next)
  }, [canonicalHead])

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

      if (next.has(panelId)) {next.delete(panelId)}
      else {next.add(panelId)}

      $creativePinnedPanels.set(next)

      return next
    })
  }, [])

  const selectClip = useCallback((clipId: string, multi = false) => {
    setSelectionState(prev => {
      const next = { ...prev }

      if (multi) {
        if (next.selectedClipIds.has(clipId)) {next.selectedClipIds.delete(clipId)}
        else {next.selectedClipIds.add(clipId)}
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
        if (next.selectedTrackIds.has(trackId)) {next.selectedTrackIds.delete(trackId)}
        else {next.selectedTrackIds.add(trackId)}
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
        if (next.selectedLayerIds.has(layerId)) {next.selectedLayerIds.delete(layerId)}
        else {next.selectedLayerIds.add(layerId)}
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
        if (next.selectedKeyframeIds.has(keyframeId)) {next.selectedKeyframeIds.delete(keyframeId)}
        else {next.selectedKeyframeIds.add(keyframeId)}
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
    applyEdit, undo, redo,
    canUndo: undoHistory.current.length > 0,
    canRedo: redoHistory.current.length > 0,
    project,
    canonicalRevision,
    acceptCanonicalHead,
    clearCanonicalHead,
    openCanonicalProject,
    submitCanonicalCommand,
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
  }), [
    project, canonicalRevision, selection, workspaceMode, playheadTime, isPlaying,
    pinnedPanels, historyStamp, applyEdit, undo, redo, setProject,
    acceptCanonicalHead, clearCanonicalHead, openCanonicalProject,
    submitCanonicalCommand, setSelection,
    setWorkspaceMode, setPlayheadTime, setIsPlaying, togglePinPanel,
    selectClip, selectTrack, selectLayer, selectKeyframe, clearSelection,
  ])

  return (
    <CreativeWorkspaceContext.Provider value={value}>
      {children}
    </CreativeWorkspaceContext.Provider>
  )
}

export type {
  CreativeAsset,
  CreativeClip,
  CreativeComposition,
  CreativeKeyframe,
  CreativeLayer,
  CreativeProject,
  CreativeTrack,
  CreativeWorkspaceContextValue,
  SelectionState,
  WorkspaceMode,
} from './types'
