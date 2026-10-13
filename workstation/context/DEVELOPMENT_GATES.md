<!-- Extracted verbatim from AGENTS.md; the hub retains mandatory reading links. -->

## Downstream Workstation context

This downstream fork contains a first-class Hermes Workstation product layer. If a task touches `workstation/`, the Desktop Workstation Browser, `browser_*` Workstation routing, or another Workstation-owned integration point, **read `workstation/context/README.md` and follow its required reading order before editing code**. The root rules in this file remain authoritative; the Workstation context adds current downstream state, settled decisions, constraints, tests, known issues, and the maintained upstream delta. Always verify those documents against current `main` implementation and tests rather than relying on old plans or conversation state.

### PRIMARY DOWNSTREAM RULE — Upstream-first change gate

Before **any downstream runtime implementation, bug fix, refactor, behavioral adjustment or
new feature**, do not start coding from whatever `main` happens to contain.

Read and execute
`workstation/context/UPSTREAM_FIRST_CHANGE_GATE_2026-09-20.md` first.

Mandatory sequence:

```text
refresh upstream
-> select/pin one exact upstream SHA
-> establish a qualified upstream-aligned baseline
-> reconcile/reclassify affected Workstation seams
-> only then implement the target downstream change
-> final upstream drift snapshot before promotion
```

The synchronization/baseline work and the target implementation must remain independently
inspectable. Do not hide a feature inside an upstream merge and do not defer upstream drift
until after the feature is built.

### One-pin promotion closure

Each downstream promotion cycle adopts **one immutable upstream SHA**. Once Stage A has
merged and qualified that pin, do not start a second upstream merge merely because
`upstream/main` advanced while the PR was being prepared. The final fetch is an observation:
record the new tip, compare it with the fixed pin, classify it for the next cycle, and keep
the candidate reproducible. It does not change the candidate's ancestry or restart
qualification. Merge the approved PR, then fast-forward local `main` from `origin/main`.

The only exception is a separately documented release hold for a confirmed defect in
the candidate or a required GitHub check failure. A moving upstream tip alone is never a
reason to consume the current promotion cycle with another sync.

A coding agent may skip the physical upstream merge only when the pre-change gate proves
that the selected upstream pin is already contained in the qualified baseline and no newer
relevant upstream delta needs adoption. If upstream moved, classify the delta before
editing target code.

If required exact-head baseline CI is red, ordinary feature work is blocked until the
baseline failure is closed or an explicit documented exception exists.

This rule has priority over convenience, historical patch locations and local feature
urgency.

### Workstation upstream-sync / first-party seam rule

When touching an upstream integration point, conflict, rebase, or migration for Hermes
Workstation, read both:

- `workstation/context/UPSTREAM_MIGRATION_AS_DECOUPLING_2026-09-19.md`
- `workstation/context/FIRST_PARTY_SEAM_POLICY.md`

The goal is **minimum necessary first-party seams**, not zero seams and not preservation of
every historical patch.

Core direction:

- the LLM/Reasoner MUST NOT need to remember to use Workstation;
- generic Hermes core SHOULD use generic lifecycle/middleware/provider/plugin contracts
  when those contracts preserve full semantics;
- the first-party Hermes Work distribution MAY deliberately keep narrow source-level
  integration when extension surfaces cannot preserve equivalent capability, lifecycle,
  authority, native UI/UX or correctness;
- never regress a proven Workstation capability merely to reduce the downstream diff.

For every upstream overlap, classify:
`ADOPT_UPSTREAM | KEEP_WORKSTATION | SEMANTIC_PORT | EXTRACT_BOUNDARY`.

For every remaining source seam, classify:
`REMOVE | UPSTREAM_ABSTRACT | PRESERVE_FIRST_PARTY`.

Use this order:
1. REMOVE when a current generic surface preserves all required behavior.
2. UPSTREAM_ABSTRACT when a small generic upstream-compatible boundary can preserve it.
3. PRESERVE_FIRST_PARTY when privileged first-party lifecycle is materially required.

A preserved seam must satisfy the seam budget: no equivalent generic surface, material
product capability, minimum blast radius, behavioral contract/E2E evidence,
`UPSTREAM_DELTA.md` + `workstation/first_party_seams.json` registration, and
re-evaluation on the next upstream cycle.

The Workstation Browser is the reference constraint. Upstream plugin/pane APIs may replace
presentation seams when parity is proven, but they are not presumed equivalent to native
Electron `WebContentsView` lifecycle, BrowserTask ownership, background continuity,
human-control fencing, native IPC or recovery.

Never remove an existing seam until the replacement path has run in shadow/parity and
proves the same relevant lineage, authority, ordering, uncertainty, verification,
BrowserTask/handoff, UX placement/background behavior and learning semantics.

Use `python workstation/scripts/audit_hermes_seams.py` when planning/reviewing the
migration. New **unclassified** Hermes-core -> Workstation seams are forbidden. New
deliberate first-party seams require explicit classification and justification.

