# EVIDENCE — EffectCraft Agent Integration Direct Read (CW-AUDIT-01)

**Arquivos auditados:**  
- `effectcraft-main/docs/agents.md` (primeiras 80 linhas lidas via run_command)  
- `effectcraft-main/docs/control-protocol.md` (144 linhas, completo)  
- `effectcraft-main/docs/web.md` (483 linhas, completo)  
- `effectcraft-main/docs/gaps.md` (230 linhas, completo)  
**Data:** 2026-10-11  
**Método:** leitura direta read-only

---

## agents.md — Três entradas para agentes (FACT)

| Interface | Melhor para | Precisa de janela |
|---|---|---|
| MCP (`effectcraft-cli mcp`) | Claude Code e outros MCP clients | Não (headless), ou sim com `--bridge` |
| CLI (`effectcraft-cli exec/get/set/...`) | scripting one-shot e CI; JSON com `--json` | Não |
| Control channel (`effectcraft --control 9877`) | driving e vendo a UI live | Sim |

**MCP headless:** `effectcraft-cli mcp [--demo|--project file.ecproj|--gpu|--autosave]` — startup instant, CPU por padrão, GPU via `--gpu`.  
**Bridge mode:** `effectcraft-cli mcp --bridge 9877` — drives running desktop, adiciona `screenshot` e `ui_*` tools.  
**Autosave headless:** `--autosave` — checkpoint antes de cada reply; EOF/transport error flusham mudanças pendentes.

---

## control-protocol.md — Protocolo TCP (FACT)

**Transport:** TCP em `127.0.0.1`, JSON object por linha, conexões persistentes.  
**Porta padrão:** 9877 (`effectcraft --control 9877` ou `EFFECTCRAFT_CONTROL_PORT=9877`).  
**Request:** `{"id": 1, "method": "engine.execute", "params": {...}}`  
**Reply:** `{"id": 1, "ok": true, "result": ...}` ou `{"id": 1, "ok": false, "error": "message"}`  
**Segurança:** só `127.0.0.1`, máximo 16 conexões, sem autenticação — habilitar só durante uso.  
**Timeout:** 60s por request.

### Métodos disponíveis (amostra verificada):

| Método | Params | Resultado |
|---|---|---|
| `engine.execute` | `{command, params?}` | resultado do comando engine |
| `engine.commands` | `{filter?, enabledOnly?}` | lista com id/label/menu/shortcut/params/enabled/why |
| `render.frame` | `{comp?, time?, max_side?, path?, base64?}` | `{comp,time,width,height,path}` ou `{...,png: "<base64>"}` |
| `ui.inspect` | `{}` | window size, fps, UiState, playback, time, active comp, selection |
| `ui.elements` | `{prefix?}` | lista de widgets com id/label/rect |
| `ui.click`, `ui.drag`, `ui.key`, `ui.type` | targets + modifiers | input sintético |
| `ui.screenshot` | `{path?, panel?, id?}` | `{path,width,height}` PNG |

### IDs de elemento estáveis (seleção):
- `timeline.layer.<id>.bar`, `timeline.layer.<id>.twirl`, `timeline.key.<uid>.<frame>`
- `timeline.prop.<uid>.stopwatch`, `effectControls.prop.<uid>.value`
- `viewer.motionPath.<layer>.<key>[.in|.out]`, `viewer.mask.<uid>.vertex.<i>`
- `tools.Selection`, `panel.Timeline`, `panel.tab.EffectControls`

**CONCLUSÃO PARA HERMES:** O protocolo TCP do EffectCraft permite controle total — cada widget tem ID estável. Para integração HCW, o padrão `engine.execute → reply JSON` é o mesmo que Hermes já usa para comunicação com browsers. A bridge mode (`--bridge 9877`) é o caminho de integração com menor overhead: Hermes passa comandos via TCP, EffectCraft responde com resultados + render frames.

---

## web.md — Arquitetura WASM (FACT)

**Build:** `cargo xtask web` → `wasm32-unknown-unknown`, ~58MB raw → ~17MB gzip → ~10MB Brotli. L0-L4 + `ui-egui` compilam para WASM.

**Sem SharedArrayBuffer:** builds em stable Rust sem `wasm-bindgen-rayon`. Concorrência via Web Workers com instâncias separadas do engine:
- **Job workers:** renders, análises, Roto Brush — cada um com WebGPU próprio
- **Frame workers (2 por padrão):** frames do viewer, cada um com WebGPU próprio
- **Projeto diff:** primeira sync = JSON completo; subsequentes = diff objeto-a-objeto (arrastar slider envia ~centenas de bytes, não o projeto inteiro)

**GPU deferred readbacks:**
- Browser não permite `await` de GPU readback durante render síncrono
- Solução: cada readback tem chave de conteúdo; miss → placeholder + `map_async`; `settled()` → re-render; até 24 passes → CPU fallback

**`window.effectcraft` API:**
```js
await effectcraft.execute("layer.newSolid", {color: "#ff8800"});
await effectcraft.renderFrame({base64: true}); // -> {png: "...base64..."}
await effectcraft.saveToBrowser("/my-project.ecproj");
```

**PARA HERMES (Electron):** A `window.effectcraft` API pode ser usada dentro de um WebContentsView se EffectCraft web rodar em iframe/panel. Mas: 58MB WASM + egui não é substituto do React — recomendação é WRAP via CLI/MCP headless, não embed.

---

## gaps.md — Lacunas honestas do EffectCraft (FACT)

| Dimensão | Estimativa | Status |
|---|---|---|
| Breadth de features | ~95%+ | 306 efeitos, 3 plataformas, tracking, expressões, scripting |
| Comporta como AE | ~60-80% | 8 casos de Rotation testados contra AE real; todo o resto NÃO medido |
| Abrir projetos AE | ~0% | `.aep`/`.aepx` não suportado; scripts/expressões portam bem |
| Estabilidade | melhorando | 23 never-crash PRs em 04/Oct; ~285k linhas Rust agent-written, ~2050 testes |
| UX real | ~70%, desigual por plataforma | 50+ bugs reportados e corrigidos entre 04-09/Oct 2026 |
| Performance | desconhecida vs AE | só números internos; nenhum projeto real 4K testado |
| Formatos de mídia | ~80% | H.264/ProRes/HEVC/AV1 existem; sem B-frames, sem formatos câmera |
| AI tools | ~50% | Roto Brush MobileSAM (IoU 0.989), Face Tracking MediaPipe (0.85px) |
| Maturidade | early | primeiro commit 01/Oct/2026 |

**INSIGHT CRÍTICO:** O número "99% parity" é auto-avaliado por agentes que construíram as features. Estimativa real de "can do real work" é **30-50%**. Nenhum projeto grande (4K, centenas de layers) foi testado.

**Para Hermes:** NÃO usar EffectCraft como "solução completa". Usar como **referência de contrato** (CommandSpec, batch, history, keyframe math) e como **motor externo** (via MCP/CLI headless) para capacidades de rendering que Hermes não tem. Fidelidade AE das 8 amostras de Rotation é promissora mas insuficiente para certificar o engine como production-ready.
