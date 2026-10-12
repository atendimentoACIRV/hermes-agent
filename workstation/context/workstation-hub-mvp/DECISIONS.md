# HWH-001 — decisions
- Keep primary dirty checkout untouched; operate in isolated worktrees and do not merge main.
- Preserve strict upstream-first H-079 gate: new HWH runtime cannot be declared qualified while Stage A and exact-head CI are open.
- Separate upstream synchronization (integration/hwh-upstream-20261012-53df274) from feature branch (feat/workstation-hub-creative-session-handoff-20261012).
- Reuse existing Creative React app and Provider, Chromium WebContentsView, BrowserTask Lifecycle, Gateway session.create and human/agent authority; no parallel stores.
- Keep /browser route and rename only visual label to Workstation.
- Do not alias external loopback browser_creative_studio_open to internal Creative route.
- Levar para sessão must preserve the original native WebContentsView; renderer does not grant itself trusted TaskRun/session owner.
- Stage A five merge conflict resolutions are unreviewed candidates. Keep existing downstream release-age policy rather than silently overwriting it; reconcile upstream policy deliberately.
- A missing CI run is not green; a failed offline lock check and a blocked test command are not passing tests.
