# HWH-001 — binding MVP contract

**Three deliveries**, in order, with TDD and Electron native E2E:
1. **HWH-01:** Hermes Agent recognizes "Abra o Creative Workstation" as a known *internal Desktop application*, opens/focuses the existing React interface without filesystem hunting or confusing the existing loopback `browser_creative_studio_open`. Idempotent, error-aware, authenticated bridge.
2. **HWH-02:** Sidebar label Browser → Workstation (retain route `/browser`); Browser Hub has a one-click Creative Workstation React tab with the correct Provider. Web pages remain actual native Electron Chromium WebContentsViews, with correct occlusion and without page/editor-state destruction on tab switches.
3. **HWH-03:** `Levar para sessão`: on a manually navigated native Browser tab, create a real profile-scoped Gateway session and **adopt the same tab and WebContentsView**, no reload or forged history. Bind BrowserTask↔Session through existing authority, preserve human lease; allow authorized agent continuation only on explicit release. Handle stale/foreign session, double click, partial failure and restart safely.

**Core files:** `apps/desktop/src/app/browser/index.tsx`, `types.ts`, `native-view-occlusion.ts`, `apps/desktop/src/app/chat/sidebar/index.tsx`, `contrib/surfaces.tsx`, `creative-workspace/*`, `electron/preload.ts`, `electron/workstation-browser-runtime.ts`, `electron/workstation-browser-task.ts`, `chat/right-rail/workstation-browser-pane.tsx`, `session/hooks/use-session-actions/session-create-request.ts`, `workstation/integrations/hermes/*` and agent tool registration.

**Proof:** natural-command real Desktop launch; native Web↔Creative tab switch without lost state; native Web→Gateway Session→Chat→human 409→release→agent continuation with same WebContentsView, preserved DOM/JS/form/scroll. TDD RED→GREEN, scope regressions, independent readback, exact-head CI. No native E2E = NOT_VERIFIED_NATIVE.

**Boundaries:** No advanced Creative editor, new Browser/Session/TaskRun stores, separate authentication layer, learned automation, old navigation replay, multiple-session adoption, JavaScript heap resurrection after app restart, broad refactor or main merge.

**Mandatory release prerequisite:** Follow root `AGENTS.md` and `workstation/AGENTS.md`: upstream-first H-079 qualified Stage A and exact-head green baseline before ordinary downstream runtime changes. Historical PASS_WITH_AUTHORIZATION applies to a different scoped operational-speed change, not this HWH mission. See STATE/EVIDENCE.
