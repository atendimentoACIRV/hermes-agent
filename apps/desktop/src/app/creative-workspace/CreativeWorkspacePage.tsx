import { CreativeGraphEditor } from './CreativeGraphEditor'
import { CreativeInspector } from './CreativeInspector'
import { CreativePreview } from './CreativePreview'
import { CreativeTimeline } from './CreativeTimeline'
import { CreativeToolbar } from './CreativeToolbar'
import { CreativeWorkspaceProvider, useCreativeWorkspace } from './CreativeWorkspaceContext'
import { CreativeWorkspaceSwitcher } from './CreativeWorkspaceSwitcher'

export function CreativeWorkspacePage() {
  return (
    <CreativeWorkspaceProvider>
      <CreativeWorkspaceBody />
    </CreativeWorkspaceProvider>
  )
}

function CreativeWorkspaceBody() {
  const { project, workspaceMode, pinnedPanels } = useCreativeWorkspace()

  const showTimeline = pinnedPanels.has('timeline') || workspaceMode === 'montage' || workspaceMode === 'motion'
  const showGraphEditor = pinnedPanels.has('graph-editor') || workspaceMode === 'motion'
  const showInspector = pinnedPanels.has('inspector') || true
  const showPreview = pinnedPanels.has('preview') || true

  if (!project) {
    return (
      <div className="creative-workspace-empty">
        <div className="creative-workspace-welcome">
          <h2>Creative Workspace</h2>
          <p>Open or create a project to start editing</p>
        </div>
      </div>
    )
  }

  return (
    <div className="creative-workspace-page">
      <CreativeToolbar />
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
