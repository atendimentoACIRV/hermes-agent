# 12 — Implementation Roadmap (CW-AUDIT-01)

Ordenado por benefício/custo + dependências. Dívida de duplicação ANTES de features. Nenhum runtime modificado nesta missão. Estimativas: S <1d · M 2-5d · L 1-3 sem (1 IA implementadora + gates H-079/exact-head CI).

## Fase D — Dívida (executar primeiro, BLOCKED_FOR_PROMOTION até fechar)
- D-1 Unificar timeline: `creative_timeline.py` (racional+linked+locks) canônico; `creative_nle.py` vira shim legado ou remove após migrar `creative_operations.py`. Gate: `test_creative_timeline` + `test_creative_nle` verdes + nenhum import float restante. [M]
- D-2 Unificar RenderContext (`float` vs `RationalFps`) + `sanitize_svg ×3` em um owner + MP4 `video vs export` em um pipeline + `load_creative_revision ×2` + `CreativeStudioError` import. Gate: grep zero duplicatas + suites verdes. [S-M]
- D-3 Migrar `creative_operations.py` DOM para `CommandRegistry/Document` (adapters HyperFrames, não autoridade paralela). Gate: ETag/if_match preservado + roundtrip. [M]

## P0 QUICK WIN (ganho concreto, baixo risco)
1. RC-01 schemas + strict reject + `list_commands{filter,enabled_only}` → `creative_commands.py`. Porquê: elimina typos agente. Origem: `commands/mod.rs`. Testes: reject unknown, filter, enabled_reason. Gate: `test_creative_commands` estendido. [S]
2. RC-02 `$N.key` + fold + NOT_IN_BATCH → `creative_transactions.py`. Manter 409. [S]
3. RC-10 `__query vs __exec` + `beginUndoGroup` → capabilities/skills. [S]
4. RC-11 Penpot AI Kit COPY (CC-BY + atribuição) → skills + `creative_edit_plan.py` patterns; Penpot MCP WRAP. [S]
5. RC-22 never-crash policy → `scripts/check` (saturating/clamp/get/nonzero, deny unwrap em novo código). [S]
6. FFmpeg sidecar documentado (flags validadas, `libx264 sem nonfree`) — já implementado, só parity docs. [S]

## P1 HIGH IMPACT (esforço aceitável)
7. RC-03 branching + merge_key + goto → `creative_transactions.py` (feature-flag). [M]
8. RC-04 timeBase + snap → `creative_time/timeline.py`. [S-M]
9. RC-05 `edit` pura + `Sequence::check` → `creative_timeline.py` (ripple_trim_group, lift/extract/insert/overwrite). [M]
10. RC-06 interchange pinado (FCP7/OTIO/EDL) via subprocess. [M]
11. RC-07 graph math → CWN-07 (UI Hermes própria). [M]
12. RC-08 LayerCache + LRU → preview. [M]
13. RC-09 Adjustment/tiles/CMS → pipeline imagem. [M]
14. RC-12 Three.js Scene+History → `scene_adapters/3d.py`. [S-M]
15. Remotion WRAP (`studio/cli/render`) + timeline-utils contract. [M]

## P2 STRATEGIC (arquitetural/complexo)
16. Graphite NodeDefinition → `creative_operations.py` unificado. [M-L]
17. Replicad WASM CAD isolado. [M]
18. NatronRenderer CLI farm (EXTERNAL_PROCESS) — só se VFX nodal justificado. [L]
19. CWN-08 Experience Compiler creative (só transições verificadas + testes +/-). [M]
20. CWN-06 parity player-vs-export com áudio + cancel global. [M]

## P3 OPTIONAL
Tone.js trilha, PixiJS overlay 2D, p5 sketch API, Scribus tipografia ref, n8n intercâmbio.

## BLOCKED
- Qualquer link GPL/AGPL/proprietário (Blender/GIMP/Krita/Natron/Remoção-fork/n8n) — só EXTERNAL_PROCESS/WRAP.
- `.aep` import (py-aep decisão owner — ver gaps.md G4).
- GPU própria antes de B-06/B-07 medidos.

## REJECTED
Inkscape stub / Strudel stub (sem código); OpenReel executor copy; egui embed no Electron; 2º TaskRun/authority/verifier; reimplementar 306 efeitos/codecs.

## Resultado esperado
Com D+P0+P1: mesmo documento + mesmos comandos humano↔IA, descoberta bounded, batch atômico com refs, branching undo, tempo snap, NLE multitrack validada, interchange, preview cacheada, 3D web imediata, design→código via Penpot — com ~2k linhas adaptadas (não 285k reimplementadas) e zero contágio licencial.
