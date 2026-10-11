# 09 — Feature Parity Matrix (CW-AUDIT-01)

Funcionalidade anunciada ≠ implementada. Status: ✅ verificado código+teste · 🟡 parcial · ❌ ausente · NV não verificado. AE = workflow referência (não auditado código, só comportamento público documentado nos Crafts).

| Capacidade | AE (ref) | EffectCraft | FilmCraft | PhotoCraft | OpenReel | Natron | Hermes CW |
|---|---|---|---|---|---|---|---|
| Command Registry único UI/CLI/MCP | ✅ | ✅ (~2000 ids, batch, schemas) | ✅ (650+, enabled Result) | ✅ (500+) | 🟡 (executor + overlay bypass) | ❌ (Python callbacks, sem registry) | 🟡 (19 cmds, sem schemas) |
| Batch atômico 1 undo + rollback | ✅ | ✅ (`engine.batch`+fold) | ✅ (`edit`+undo 200) | ✅ | 🟡 (txn cara, JSON snapshot) | ❌ | ✅ (CoW+409, sem $refs) |
| Branching history + goto | ✅ | ✅ | 🟡 (linear 200) | 🟡 | ❌ (fragmentada) | ❌ | ❌ (linear) |
| Tempo exato NTSC/drop-frame | ✅ | ✅ (Tick) | ✅ (Tick) | — | ❌ (float) | 🟡 | ✅ (Fraction+SMPTE) |
| NLE split/trim/ripple/slip/slide/roll/speed + linked + locks | ✅ | 🟡 (via interchange, não foco) | ✅ (edit pura + sync_lock) | — | 🟡 (same-track, sem sync) | — | ✅ (7 ops + linked + locks; roll/speed parcial) |
| Interchange FCP7/FCPXML/OTIO/EDL/AAF | ✅ | ✅ (via filmcraft) | ✅ | — | ❌ | 🟡 (OTIO parcial NV) | ❌ |
| Graph Editor value/speed + handles | ✅ | ✅ (626 linhas) | ❌ | — | ❌ | 🟡 (Curve+Dope) | ❌ (stub NV) |
| Efeitos registry + GPU | ✅ | ✅ (306/280 GPU) | ❌ | ✅ (adjustments) | 🟡 (fxpkg NV) | ✅ (OFX) | ❌ (adapters) |
| Máscaras/mattes/parenting/precomp | ✅ | ✅ | — (tracks) | ✅ (vector mask) | 🟡 | ✅ (roto) | 🟡 (linked, sem masks/nested) |
| Texto animado + Essential Graphics | ✅ | ✅ (templates .ectemplate) | 🟡 (captions) | ✅ (text layers) | 🟡 (overlay bug) | ❌ | ❌ |
| Motion blur / 3D câmera/luz | ✅ | ✅ (Classic+Advanced PBR) | — | — | ❌ | 🟡 (3D parcial) | 🟡 (Three.js DOM, sem render) |
| Tracking/estabilização/roto | ✅ | ✅ (NCC/LK, Warp Subspace, SfM, graph-cut + MobileSAM) | — | — | ❌ | ✅ (tracker) | ❌ |
| Raster PSD/ICC/tiles/brush | ✅ (PS) | ✅ (psd crate) | — | ✅ (byte-identical, 16 adj, CoW, ICC, 55 tools) | ❌ | ❌ | ❌ (só PNG inspect) |
| Vetor procedural nodal | ✅ (AI) | 🟡 (svg/pdf) | — | 🟡 (vector) | ❌ | ❌ | 🟡 (sanitize ×3) |
| Render queue + cache + farm | ✅ (Media Encoder) | ✅ (RAM+disk OPFS + Auto GPU) | ✅ (render+golden) | ✅ (CPU+GPU) | 🟡 (jobs NV) | ✅ (tiled + farm) | 🟡 (FFmpeg real + adapters parcial) |
| Scripting/expressões agente | ✅ (ExtendScript/Expressions) | ✅ (boa + AE matchnames + ScriptUI) | ✅ (commands) | ✅ | 🟡 (loop budget, 228 tools) | ✅ (Python) | 🟡 (skills, sem __query/__exec) |
| Preview aprovável + dry-run | ✅ | ✅ (render_frame + history) | ✅ | ✅ | ✅ (loop confirm/dry-run — melhor UX) | ❌ | ✅ (edit_plan preview + PARTIAL) |
| WASM/browser | — | ✅ (web + workers) | ✅ (web) | ✅ (web) | ✅ (nativo web) | ❌ | ✅ (Electron preview) |

**Leitura:** Hermes lidera em autoridade/verificação/integração (nenhum concorrente tem TaskRun+Policy+ArtifactStore+409); perde em efeitos/render/tracking/raster/vetor/interchange/graph — todos cobertos por WRAP/ADAPT sem reimplementar.
