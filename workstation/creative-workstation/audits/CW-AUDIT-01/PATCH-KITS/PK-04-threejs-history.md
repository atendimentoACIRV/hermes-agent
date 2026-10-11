# PK-04 — Three.js Scene + Editor History (RC-12, ADAPT_CODE, MIT)

**Origem:** `referências/01-Criacao-Visual-Video-3D/mrdoob--three.js/src/scenes/Scene.js:Scene` + `src/renderers/WebGLRenderer.js` + `editor/js/{Editor.js,History.js,Command.js}` · SHA `11738a9d55e5` · MIT (copiável com `LICENSE` preservada) · **Destino:** `workstation/creative_scene_adapters.py` (ThreeJs adapter) + frontend `apps/desktop/src/app/creative-workspace/` · **NÃO APLICADO.**

## O que copiar
- `Scene` graph (object hierarchy, transform, layers) como modelo de `ThreeJsSceneConfig` — já existe `creative_3d.py`, estender com `parent/children` + `matrixAutoUpdate`.
- `editor/js/History.js` undo-stack (`execute/undo/redo`, `goToState`) como referência para `CreativeHistory` branching (alternativa a RC-03 para o frontend).
- `Command.js` (`SetPositionCommand` etc: `execute/undo/toJSON/fromJSON`) como padrão comando serializável — mapear para `CreativeCommand{command_id,params,inverse}`.

## Adaptação
JS→TS no frontend (tipar `interface`), Python só guarda `scene JSON` + `sha256` (nunca executa JS no backend). `WebGLRenderer` via CDN pinado + SRI, origem isolada, sem Electron privilegiado. `GLBValidator` Hermes já cobre segurança — reutilizar budgets.

## Testes/build/licença/rollback
Testes: `scene seek determinístico` (já existe) + `history goToState byte-eq` + `command JSON round-trip`. Build: pin `three@<versão>` + SRI (quando autorizado; NADA instalado nesta missão). Licença MIT — incluir `THIRD_PARTY_NOTICES` + `LICENSE` three.js. Rollback: remover adapter 3D, manter SVG/Canvas.
