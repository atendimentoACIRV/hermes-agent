# 01 — Repository Inventory (CW-AUDIT-01)

**Baseline Hermes:** HEAD `80e3a0724b1c939bfbcbb4801434fb31661eea70` · branch `feat/workstation-browser-optimization-c2c` · D-043 pin canônico `f21e803b3525b70ee6be2305e579c1cc1f930e74`
**Base dir:** `referências/01-Criacao-Visual-Video-3D` (25 entradas) · **Data:** 2026-10-11 · **Status:** FACT para paths/SHA com git; SNAPSHOT sem git marcado NOT_VERIFIED para SHA
**Regra:** não foi executado `git pull`, nenhuma dependência instalada, nenhum código externo executado. Leitura read-only.

## Legenda
- `SHA` = `git -C <repo> rev-parse HEAD` (12 chars). Quando `HasGit=False`, SHA do parent Hermes vaza (`80e3a0724b1c`) — registrado como `NOT_VERIFIED (snapshot sem .git)`.
- `Lic` = arquivos de licença observados no root, não interpretação jurídica (ver `11-LICENSE-AND-INTEGRATION-RISKS.md`).

## 4.1 Projetos originalmente catalogados (20)

| # | Pasta local | SHA | HasGit | Licença observada | Linguagem/Build | Maturidade |
|---|---|---|---|---|---|---|
| 1 | penpot--penpot | `10955f17e279` | True | LICENSE (MPL-2.0) | Clojure/JVM + shadow-cljs + Rust + TS | FACT — monólito design ativo (#12172 get-file-tokens) |
| 2 | penpot--penpot-ai-kit | `fe4f99e51c71` | True | LICENSE (CC-BY-4.0) | TS/Node content-only, skills markdown | FACT — kit instrucional v0.5.1 |
| 3 | remotion-dev--remotion | `32af7e8f8ac6` | True | LICENSE.md (Remotion dual Free/Company) | TS React+Node+Bun+Rust+Go turbo | FACT — video-as-code |
| 4 | remotion-dev--skills | `32b241b97f4e` | True | sem LICENSE própria (private:true) | Markdown SKILL.md | FACT — 12 skills, herda Remotion License |
| 5 | mrdoob--three.js | `11738a9d55e5` | True | LICENSE (MIT) | TS/JS npm WebGL/WebGPU | FACT — scene-graph + editor |
| 6 | FFmpeg--FFmpeg | `1f7228e4fcc4` | True | LICENSE.md + COPYING.* (LGPL/GPL dual) | C Makefile/configure | FACT — libav* + fftools |
| 7 | blender--blender | `aed2b5972fc2` | True | COPYING (GPL-2.0) | C/C++/Python CMake | FACT — DCC monolítico |
| 8 | inkscape--inkscape | `1232eac68aff` | True | sem LICENSE local (STUB) | STUB — só README.md+png, sem src/ | PARTIAL — mirror vazio 2022, upstream real no GitLab |
| 9 | GraphiteEditor--Graphite | `7477cd2fab31` | True | LICENSE-MIT + LICENSE-APACHE | Rust Cargo + TS/Svelte frontend | FACT — node-graph procedural |
| 10 | BOMWiki--partmode | `fe88558a34c8` | True | LICENSE (AGPL-3.0-only) | TS Node≥22 tsc | FACT — CAD browser + MCP |
| 11 | sgenoud--replicad | `e4b05f67dc4e` | True | LICENSE (MIT) v1.1.0 | TS wrapper OpenCascade WASM | FACT — CAD paramétrico |
| 12 | GNOME--gimp | `0774955bfe1c` | True | LICENSE + COPYING (GPL-3.0) | C meson GTK/GEGL/BABL | FACT |
| 13 | KDE--krita | `3ee2270d8ead` | True | COPYING (GPL-3.0-only) + LICENSES/REUSE | C++/Qt CMake | FACT |
| 14 | godotengine--godot | `232e6b14abf6` | True | LICENSE.txt (MIT, sem COPYING no root listado) | C++ SCons + GDScript | FACT — game-engine |
| 15 | pixijs--pixijs | `65552017d232` | True | LICENSE (MIT) | TS WebGL/WebGPU | FACT — 2D engine |
| 16 | processing--p5.js | `8ae967b59c49` | True | license.txt (LGPL-2.1) | JS npm canvas/WebGL | FACT |
| 17 | Tonejs--Tone.js | `de9df332ca75` | True | LICENSE.md (MIT) v15.5.57 | TS WebAudio npm | FACT |
| 18 | tidalcycles--strudel | `8a8ae9ac9659` | True | LICENSE (AGPL-3.0) mas STUB | STUB — só README+LICENSE+MOVED_TO_CODEBERG | PARTIAL — mudou para codeberg, sem packages/ |
| 19 | scribusproject--scribus | `969c3fe4bedb` | True | COPYING (GPL-2.0+) | C++/Qt CMake | FACT — DTP |
| 20 | n8n-io--n8n | `7424f0ca0452` | True | LICENSE.md (Sustainable Use + EE) | TS pnpm+turbo | FACT — workflow, sem nodes Penpot/Remotion |

## 4.2 Cinco projetos adicionais obrigatórios (snapshots sem .git)

| # | Pasta local | SHA git | Versão observada | Licença observada | Status |
|---|---|---|---|---|---|
| 21 | effectcraft-main | NOT_VERIFIED (sem .git) | workspace `0.7.0`, edition 2024, rust 1.95 (`Cargo.toml:1-10`) | LICENSE-MIT + LICENSE-APACHE (`Cargo.toml:9 MIT OR Apache-2.0`) + NOTICE + ATTRIBUTION.md | FACT (snapshot) — 32 crates, docs/architecture.md L0-L6, docs/agents.md 652 linhas |
| 22 | openreel-video-main | NOT_VERIFIED (sem .git) | package.json MIT 2024-2026 Augustus Otu | LICENSE (MIT) | FACT (snapshot) — React+TS+Zustand+MediaBunny, 228 tools |
| 23 | filmcraft-main | NOT_VERIFIED (sem .git) | workspace `0.6.0`, edition 2024 | LICENSE-MIT + LICENSE-APACHE + NOTICE + ATTRIBUTION.md | FACT (snapshot) — Cargo members crates/* apps/* xtask, 650+ commands |
| 24 | Natron-RB-2.6 | NOT_VERIFIED (sem .git) | branch snapshot RB-2.6 | LICENSE.txt GPLv2 + LICENSE_SHORT.txt | FACT (snapshot) — fork Natron, Engine/Gui/Renderer/HostSupport |
| 25 | photocraft-main | NOT_VERIFIED (sem .git) | workspace `0.7.0` | LICENSE-MIT + LICENSE-APACHE + README:413 | FACT (snapshot) — L0-L6, 500+ commands, 55 tools |

## Notas de proveniência
- Pastas `effectcraft-main`, `filmcraft-main`, `photocraft-main`, `openreel-video-main`, `Natron-RB-2.6` não contêm `.git` (verificado `Test-Path .git = False`). Não inferir upstream apenas pelo nome. `effectcraft-main/Cargo.toml`, `filmcraft-main/Cargo.toml`, `photocraft-main/Cargo.toml` indicam workspaces Craft `storytold/*` por estrutura/docs, mas remote Git não verificável localmente → registrar como `snapshot local, upstream NÃO confirmado por remote`.
- `inkscape--inkscape` e `tidalcycles--strudel` são STUBs: sem `src/`/`packages/`. Classificados PARTIAL/REJECT para code-to-code, sem converter NV em AUSENTE.
- Nenhum clone foi atualizado (`git pull` proibido pela missão §4.3). SHAs acima são o estado do clone = fonte de verdade.
