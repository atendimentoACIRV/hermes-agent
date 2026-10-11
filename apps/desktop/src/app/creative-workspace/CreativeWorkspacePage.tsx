import { CreativeWorkspaceProvider, useCreativeWorkspace } from './CreativeWorkspaceContext'
import { newCreativeProject, assertCreativeProject } from './creative-mvp-model'
import { useRef, useState } from 'react'
import { CreativeTimeline } from './CreativeTimeline'
import { CreativeInspector } from './CreativeInspector'
import { CreativePreview } from './CreativePreview'
import { CreativeGraphEditor } from './CreativeGraphEditor'
import { CreativeToolbar } from './CreativeToolbar'
import { CreativeWorkspaceSwitcher } from './CreativeWorkspaceSwitcher'

export function CreativeWorkspacePage() {
  return <CreativeWorkspaceProvider><CreativeWorkspaceContent /></CreativeWorkspaceProvider>
}

function CreativeWorkspaceContent() {
  const { project, workspaceMode, pinnedPanels, setProject } = useCreativeWorkspace()
  const fileRef = useRef<HTMLInputElement>(null)
  const [openError, setOpenError] = useState('')
  const openFile = async (file: File | undefined) => {
    if (!file) return
    try {
      if (file.size > 2_000_000) throw new Error('Project file exceeds 2 MB')
      const data: unknown = JSON.parse(await file.text())
      assertCreativeProject(data)
      setProject(data)
      setOpenError('')
    } catch (error) {
      setOpenError(error instanceof Error ? error.message : 'Invalid project')
    }
  }

  const showTimeline = pinnedPanels.has('timeline') || workspaceMode === 'montage' || workspaceMode === 'motion'
  const showGraphEditor = pinnedPanels.has('graph-editor') || workspaceMode === 'motion'
  const showInspector = pinnedPanels.has('inspector') || true
  const showPreview = pinnedPanels.has('preview') || true

  if (!project) {
    return (
      <div className="creative-workspace-empty">
        <div className="creative-workspace-welcome">
          <h2>Creative Workspace</h2>
          <p>Create an editable vector project, or open a previously saved JSON project.</p>
          <button type="button" onClick={() => setProject(newCreativeProject(crypto.randomUUID()))}>New project</button>
          <button type="button" onClick={() => fileRef.current?.click()}>Open project</button>
          <input ref={fileRef} aria-label="Project JSON file" type="file" accept=".json,application/json"
            style={{ display: 'none' }} onChange={event => void openFile(event.target.files?.[0])} />
          {openError && <p role="alert">{openError}</p>}
        </div>
      </div>
    )
  }

  return (
    <div className="creative-workspace-page">
      <CreativeToolbar />
      <button type="button" onClick={() => fileRef.current?.click()}>Open project</button>
      <input ref={fileRef} aria-label="Project JSON file" type="file" accept=".json,application/json"
        style={{ display: 'none' }} onChange={event => void openFile(event.target.files?.[0])} />
      {openError && <p role="alert">{openError}</p>}
      <CreativeWorkspaceSwitcher />

      <div className="creative-workspace-main">
        <div className="creative-workspace-left">
          {showPreview && <CreativePreview />}
        </div>

        <div className="creative-workspace-center">
          {showTimeline && <CreativeTimeline />}
          {showGraphEditor && <CreativeGraphEditor />}
        </div>

        <div className="creative-workspace-right">
          {showInspector && <CreativeInspector />}
        </div>
      </div>
    </div>
  )
}
