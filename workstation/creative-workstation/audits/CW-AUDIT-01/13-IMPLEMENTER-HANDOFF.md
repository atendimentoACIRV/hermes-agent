# 13 — Implementer Handoff (CW-AUDIT-01)

Prompt técnico para IA implementadora. Só oportunidades aprováveis e comprovadas. Hipóteses marcadas HYP. Ler antes: root `AGENTS.md`, `workstation/AGENTS.md`, `workstation/context/README.md` (ordem canônica) + H-079 gate + `ENGINE_NEUTRAL_ARCHITECTURE_2026-10-10.md` + `ENGINE_NEUTRAL_IMPLEMENTER_HANDOFF_2026-10-10.md`. NÃO modificar runtime sem branch H-079 + RED→GREEN + exact-head CI. Preservar checkout sujo.

## Sequência (D antes de P0 antes de P1)
1. D-1/D-2: unificar `creative_timeline.py` (canônico) + RenderContext + sanitize + MP4 + `load_creative_revision` dup + `CreativeStudioError` import. Verificar: `grep -rn "from workstation.creative_nle import" workstation/`, `grep -n "def load_creative_revision" workstation/creative_project_store.py` (2 defs), `grep -rn "RenderContext" workstation/creative_*.py`, `grep -rn "CreativeStudioError" workstation/`.
2. P0-1 (RC-01): estender `workstation/creative_commands.py:CommandRegistry` com `label/menu/shortcut/params_doc/json_schema/enabled_reason` + `execute_checked` (strict reject, erro lista accepted keys) + `list_commands(filter,enabled_only)`. Ref: `referências/01-Criacao-Visual-Video-3D/effectcraft-main/crates/engine/src/commands/mod.rs:93-359`. RED: unknown param rejeita; `enabled_only` filtra; schemas validam. DoD: `workstation/tests/test_creative_commands.py` estendido verde.
3. P0-2 (RC-02): `workstation/creative_transactions.py` — refs `$N.key` + `fold()` 1 undo + `NOT_IN_BATCH=[batch]` + rollback nomeando step. Manter `expected_revision` 409 + idempotência. Ref: `.../commands/batch.rs:1-118`.
4. P0-3 (RC-10): separar leitura (`__query`-like snapshot) vs escrita (só via comando journaled) em skills/capabilities; `begin/end_undo_group` para scripts multi-step. Ref: `.../crates/script/src/runtime.rs`, `prelude.js:4-5`.
5. P0-4 (RC-11): copiar `referências/.../penpot--penpot-ai-kit/skills/penpot-*/SKILL.md` (CC-BY-4.0, MANTER atribuição) como skills Hermes; WRAP Penpot MCP (`mcp/packages/common/src/index.ts`) via `creative_apps.py` probe (nunca linkar Clojure).
6. P1 (ordem): RC-03 branching (`history.rs:1-346`, feature-flag) → RC-04 timeBase+snap (`time/src/lib.rs`, `prop.rs:84-117`) → RC-05 edit pura (`filmcraft-main/crates/edit/src/lib.rs`, HYP paths — confirmar no snapshot, sem .git) → RC-07 keyframe math (`keyframe/src/lib.rs:21-560`, UI própria) → RC-08 cache (`render/src/cache.rs`) → RC-12 Three.js (`src/scenes/Scene.js`, `editor/js/History.js`, MIT) → RC-09 PhotoCraft (`doc/src/lib.rs`, `raster/src/lib.rs`, `cms/`) → Remotion WRAP (`npx remotion studio/render`, nunca fork).

## Paths/símbolos exatos (Hermes)
- `workstation/creative_commands.py:Actor,CreativeCommand,CommandResult,CommandRegistry,execute_command` (19 cmds)
- `workstation/creative_transactions.py:CreativeTransaction{expected_revision},CreativeHistory{current_revision,undo/redo,seen_idempotency}`
- `workstation/creative_time.py:RationalFps,CanonicalTime,TimeRange,MediaTimeMap` · `creative_timeline.py:split/trim/ripple_delete/slip/slide/roll/set_clip_speed_op` · `creative_document.py:CreativeDocument,...`
- `workstation/creative_project_store.py` (corrigir dup L69/L114) · `creative_render_adapters.py:RenderAdapter{prepare/seek/ready/snapshot/render/cancel/dispose}` · `creative_scene_adapters.py:CompositeScene{from_composition,seek}` · `creative_export.py:export_composition_to_video` · `creative_video*.py` · `creative_3d.py:inspect_glb_bytes`
- Testes: `workstation/tests/test_creative*.py` (22 suites / 98 testes)

## Dependências/interfaces/testes/aceite
- Deps novas: NENHUMA obrigatória (adapters usam binários existentes: ffmpeg/ffprobe/node). WASM/Replicad e Remotion opt-in, nunca auto-install. Fixar filmcraft pin `2c5ba7a` se usar interchange.
- Interfaces: `CommandRegistry.execute_checked`, `list_commands`, `engine.batch`-like, `history.goto`, `timeBase`, `capabilities()` manifesto. Descoberta bounded — nunca 300 tools no prompt.
- Testes por slice: RED (comportamento real + negativo owner/safety) → GREEN focado → regressões afetadas → E2E GUI/headless quando aplicável → exact-SHA CI → journal+rollback. `scripts/run_tests.sh`, nunca bare pytest.
- Aceite: mouse≡agente mutação serializada; falha passo 3 sem mutação; undo byte-eq; 409 em conflito; preview sem mutar; PARTIAL nunca DONE; cancel sem órfãos; ffprobe + preview hash; sem traversal; licença/atribuição verificada.
- Proteções: H-079 upstream-first + SHA pinado; sem 2º TaskRun/BrowserTask/SessionDB/ArtifactStore/verifier/Experience Compiler; ScopedPolicy + ETag/if_match + actor; File sandbox; sem link GPL/AGPL/proprietário; sem merge drafts #57-64 sem reconciliação; D-041 superseded (motor), D-042 gates intactos.
- HYP (não instrução obrigatória): números parity 99% Craft (auto-avaliados), perf estimativas §10, paths filmcraft sem .git (confirmar no snapshot antes de codar).
