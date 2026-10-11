# 00 — Executive Summary (CW-AUDIT-01)

**Missão:** auditoria code-to-code categoria 01 + 5 manuais · **HEAD:** `80e3a0724b` (`feat/workstation-browser-optimization-c2c`) · **Pin D-043:** `f21e803b` · **Data:** 2026-10-11 · **Runtime inalterado** (read-only + docs auditoria).

## 10 melhores oportunidades
1. **RC-01 Schemas + strict reject + descoberta bounded** (EffectCraft `commands/mod.rs`) → `creative_commands.py` · P0 · ADAPT_CONTRACT — elimina typos agente.
2. **RC-02 Batch `$N.key` + fold 1 undo** (`batch.rs`) → `creative_transactions.py` · P0 — manter 409 Hermes.
3. **RC-10 `__query` vs `__exec` + undo-group** (`script/runtime.rs`) → skills/capabilities · P0 — escrita só journaled.
4. **RC-11 Penpot AI Kit COPY (CC-BY) + MCP WRAP (MPL)** → skills + `creative_apps.py` · P0 — maior ROI produto.
5. **RC-22 Never-crash policy** (`deny unwrap + guarded`) → `scripts/check` · P0.
6. **RC-03 Branching + merge_key + goto** (`history.rs`) → history · P1 — manter revision Hermes.
7. **RC-05 `edit` pura + `Sequence::check`** (FilmCraft) → `creative_timeline.py` · P1 — multitrack validada.
8. **RC-07 Keyframe math** (ease/bezier/roving/velocity) → CWN-07 UI própria · P1 — sem egui.
9. **RC-12 Three.js Scene+History (MIT)** → `scene_adapters/3d.py` · P1 — 3D web imediata.
10. **RC-09 Adjustment + tiles CoW + CMS ICC** (PhotoCraft) → pipeline imagem · P1 — sem 2º editor.

## O que começar a reaproveitar (P0, dias, sem risco legal)
Schemas/strict, batch refs, query/exec split, Penpot skills, never-crash — todos MIT/Apache/CC-BY, zero deps, testes existentes estendíveis.

## Referência mais promissora
**Família Craft como contrato, não como editor:** FilmCraft (Tick + `edit` + interchange) + EffectCraft (registry + batch + history + keyframe) + PhotoCraft (doc + CMS + tiles) — todas MIT/Apache, pin `2c5ba7a`, mesma base. Hermes mantém TaskRun/authority/verifier (que nenhuma tem). Motores pesados sempre WRAP/EXTERNAL_PROCESS.

## Conclusão EffectCraft
Melhor referência MoGraph para **contrato humano+IA** (registry único ~2000 ids, batch atômico, branching, timeBase+snap, graph 626 linhas, 306 effects, MCP/CLI/control mesmo dispatch, WASM). NÃO eleger motor central: renderer/efeitos/GPU/egui nunca reimplementar (WRAP); Tick não substitui Fraction sem prova; `.aep 0%`, behavior 60-80% não medido, parity 99% auto-avaliado — não benchmark. Portar ~2k linhas contrato/math, não 285k.

## Integrar HW+HCW
**Confirmar E (Hybrid Creative Kernel = D-043):** documento+comandos+política+histórico compartilhados (owners Hermes); renderers isolados. BrowserOS transfere 5 princípios (broker único, recibo como prova, visual≠automação, sessão owned, descoberta bounded) — não fork Chromium. Pagar dívida D-1/D-2/D-3 (timeline×2, commands×2, MP4×2, RenderContext×2, sanitize×3) antes de features.

## Erros arquiteturais a evitar
Embedar egui no Electron; linkar GPL/AGPL/proprietário (Natron/Blender/GIMP/Krita/Remotion-fork/n8n); copiar executor float OpenReel ou registry 228 tools; 2º TaskRun/authority/verifier; trocar Fraction por Tick por preferência; reimplementar codecs/306 efeitos; WASM como authority; auto-install engines; merge drafts sem reconciliação.

## Estado Hermes (para roadmap)
CWN-00..06 base IMPLEMENTADA local (22 suites/98 testes) mas NÃO QUALIFIED exact-head; duplicações críticas; CWN-07/08/09 ausentes; Electron mínimo; 2 defeitos (dup `load_creative_revision`, `CreativeStudioError` sem import). Detalhes: `02`, `06`, `12`, `13`.
