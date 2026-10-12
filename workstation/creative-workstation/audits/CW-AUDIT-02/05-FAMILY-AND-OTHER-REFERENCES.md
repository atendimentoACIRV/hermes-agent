# 05 — Família Craft, demais referências e decisões de integração

**Fotos dos fontes locais:** 01-INVENTORY.md/SOURCE_INVENTORY.json = 26 diretórios, 0 ZIP no instante da auditoria; manifests SPDX/roots e .git por entrada. Fonte ignorada pelo Hermes Git: paths e SHAs git dos clones locais NÃO representam versões do main. Nenhum projeto foi buildado nesta fase. Afirmações funcionais além dos símbolos rechecados são do índice CW-AUDIT-01 e carecem de testes de integração.

## Relação Craft factual
- EffectCraft Cargo.toml:7 version 0.7.0, license MIT OR Apache-2.0, :74–93 declara dependências git storyTold/filmcraft com rev exata 2c5ba7a72619935f0481f99d59409e0d1844b234, envolvendo codecs/media/frame/color/time/interchange/project/geom. **Dependência cruzada real confirmada.**
- FilmCraft Cargo.toml:7 version 0.6.0. crates/edit/src/lib.rs:95 split_track_at, :434 ripple_delete_items, :705 trim, :863 roll, :910 slip, :923 slide, :1003 rate_stretch; crates/project/src/lib.rs:805,1092 check() assegura invariantes. Usar ADAPT_ALGORITHM no creative_timeline.py, não substituir diretamente o schema Hermes por Sequence.
- PhotoCraft Cargo.toml:7 version 0.7.0. crates/doc/src/lib.rs:548 LayerContent e :776 Document; crates/raster/src/lib.rs:40 Tile e :87 Surface. ADAPT_ALGORITHM non-destructive adjustment + tile CoW + ICC para compositor raster, guardando fonte nativa.
- LightCraft Cargo.toml:6 version 0.6.0, rust-version 1.90; crates/develop/denoise/raw/inpaint/lensdb/preview presentes; dependência explícita craft-ui git storyTold/craft-libs rev 5c874d... . É pipeline de foto RAW/revelação, não uma base MoGraph. WRAP_ENGINE opcional P2; benchmark e licença de modelos/RAW antes.
- VectorCraft Cargo.toml:7 version 0.9.0, rust-version 1.95; crates/doc/src/lib.rs:345 Artboard, :535 Document; crates/pathops/, vector, text, svg, effects, three-d disponíveis. Também importa craft-ui git pin 5c874d.... ADAPT_ALGORITHM boolean paths/artboards/snapping + fonte editável no Hermes; não eleger segundo documento.
- Nem LightCraft nem VectorCraft têm .git no snapshot extraído, por isso suas SHAs próprias NÃO são conhecidas. Sem evidência de dependência direta EffectCraft→LightCraft/VectorCraft nem de equivalência de documento entre os cinco. Não atribuir integração automática à família pelo nome.

## Inventário completo, decisão preliminar por projeto
| Projeto | Capacidade técnica mais relevante | Classificação para o primeiro produto | Confiança e ressalvas |
|---|---|---|---|
| effectcraft-main | registry/batch/history/keyframe/comp effects | ADAPT_CONTRACT/ALGORITHM, WRAP_ENGINE eventual | símbolos críticos revalidados; sem build |
| filmcraft-main | Sequence.check/edit, linked media, interchange | ADAPT_ALGORITHM/CONTRACT | símbolos críticos revalidados; sem build |
| photocraft-main | Raster tiles, layer adjustments, CMS ICC | ADAPT_ALGORITHM | símbolos doc/raster verificados; sem pixel teste |
| lightcraft-main | RAW/inpaint/denoise/develop pipeline | WRAP_ENGINE opcional P2 | Cargo e crates verificados; sem runtime |
| vectorcraft-main | artboard, bool paths, vectors/3D | ADAPT_ALGORITHM | Cargo/doc/crates verificados; sem renderer |
| GraphiteEditor--Graphite | grafo procedural vetor/raster | ADAPT_CONTRACT/REFERENCE_ONLY | mais forte em nodes; integração não qualificada |
| penpot--penpot | design, componentes, colaboração e MCP | WRAP_ENGINE para import/reference | MPL-2.0; a UI não deve virar fonte de verdade |
| penpot--penpot-ai-kit | workflows e schemas de IA para design | ADAPT_CONTRACT / COPY condicionado a atribuição | CC-BY-4.0 no package root; analisar arquivos individuais |
| inkscape--inkscape | path SVG e editor vetorial | REFERENCE_ONLY / EXTERNAL_PROCESS | root licença não resolvida pela inspeção automática; verificar licença antes |
| GNOME--gimp | pixels, cor, máscaras/filters | REFERENCE_ONLY/EXTERNAL_PROCESS | GPL observada; sem copiar módulo |
| KDE--krita | pintura, brushes e animação 2D | REFERENCE_ONLY/EXTERNAL_PROCESS | GPL observada; sem copiar |
| scribusproject--scribus | tipografia/CMYK e prepress | REFERENCE_ONLY | GPL, fora do primeiro vertical |
| openreel-video-main | web NLE action executor, agent host/loop | REFERENCE_ONLY / ADAPT_CONTRACT | MIT manifest; revisar bugs ripple e float |
| Natron-RB-2.6 | OFX + DAG de composição | REFERENCE_ONLY / EXTERNAL_PROCESS | GPL; sem linking no produto |
| remotion-dev--remotion | composition/react + codec render | WRAP_ENGINE com aprovação legal | licença própria; não copiar como MIT |
| remotion-dev--skills | boas práticas Remotion | REFERENCE_ONLY; licença UNVERIFIED | snapshot local sem root SPDX |
| FFmpeg--FFmpeg | encode/decode/ffprobe de vídeo e áudio | EXTERNAL_PROCESS existente, KEEP | root GPL não diz flags da build instalada; verificar executável/licença real |
| mrdoob--three.js | scene graph, WebGL render e Editor Commands | ADAPT_CONTRACT + uso de runtime isolado | MIT; três segmentos precisam de frame parity |
| blender--blender | edição/rig/mesh/render specialist | EXTERNAL_PROCESS isolado P2 | GPL, performance/distribuição desconhecida |
| godotengine--godot | engine 3D/scene e animação | REFERENCE_ONLY, adapter candidato P3 | licença root não classificada pelo scanner; validar arquivo |
| pixijs--pixijs | Canvas/WebGL 2D com sprites/filters | WRAP_ENGINE ou ADAPT_CONTRACT | MIT; não trocar documento |
| processing--p5.js | sketches e criação procedural | REFERENCE_ONLY/ADAPT_ALGORITHM | LGPL; JS sandbox/CSP antes de incluir |
| sgenoud--replicad | geometria CAD por API | WRAP_ENGINE módulo opcional | MIT; não priorizar CAD antes do 3D GLB básico |
| BOMWiki--partmode | CAD/3D | REFERENCE_ONLY | AGPL-3.0-only; sem copy/link P0 |
| tidalcycles--strudel | música sequencial procedural | REFERENCE_ONLY/adapter de áudio opcional | licença root AGPL no snapshot; código candidata da varredura limitado; não alegar paridade |
| Tonejs--Tone.js | instrumentos e sinais WebAudio | ADAPT_CONTRACT, opcional P2 | MIT; áudio timeline core FilmCraft/FFmpeg tem precedência |

## Confrontos de código específicos
- **FilmCraft contra Hermes:** pure NLE edit API e Sequence.check fornecem invariantes reutilizáveis; Hermes já tem creative_timeline.py e comandos NLE, não migrar às cegas. Testar linked audio, locked tracks, speed/reverse e 29.97. Código: FilmCraft crates/edit/src/lib.rs:95,434,705,863,910,923,1003 vs Hermes creative_commands.py:456–541.
- **Three.js contra Hermes:** Three editor/js/commands/AddObjectCommand.js:4 e editor/js/History.js:3 são referências de comandos e history; Hermes creative_3d.py:137 protege parsing de GLB, mas creative_scene_adapters.py:133 não renderiza pixels; combinar isolamento WebGL + Hermes command owner.
- **OpenReel:** packages/core/src/actions/action-executor.ts:1015 caso clip/rippleDelete e packages/agent/src/loop.ts:91 runTurn confirmados. Aproveitar abstração host/approval, não algoritmos sem testar linked media e regras float.
- **VectorCraft contra Graphite/Penpot:** VectorCraft pathops/artboard é candidato a algoritmo geométrico; Graphite melhor referência node procedural; Penpot melhor interoperabilidade colaborativa. Nenhum justifica 3 novos documentos no Hermes.
- **Raster:** PhotoCraft CoW Tile/Document evidencia técnica para raster; LightCraft não é substituto de editor geral, serve RAW e desenvolvimento fotográfico como specialist opt-in.

## Critérios de licenciamento
Licença da raiz é PRELIMINAR. Sempre validar license do arquivo/snippet, build/dependências/NOTICE, assets/modelos/fonts, atribuição, patentes/codecs e estratégia de empacotamento. GPL/AGPL exigem revisão rigorosa de obrigações por forma de integração; não é correto supor que subprocesso elimina automaticamente toda obrigação. MPL-2.0 tem obrigações por arquivos modificados e distribuição. Remotion e skills requerem análise de licença específica e restrições comerciais. Nenhuma cópia recomendada foi aplicada nesta auditoria.
