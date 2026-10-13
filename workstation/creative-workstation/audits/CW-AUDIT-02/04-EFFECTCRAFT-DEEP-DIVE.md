# 04 — EffectCraft deep dive revalidado no código local

Alvo: referências/01-Criacao-Visual-Video-3D/effectcraft-main. Cargo.toml:1–12 workspace 0.7.0, Rust edition 2024, rust-version 1.95 e licença declarada MIT OR Apache-2.0. É snapshot sem .git, SHA NÃO VERIFICADO. Arch CW-AUDIT-01/03-EFFECTCRAFT-DEEP-DIVE é índice de pesquisa anterior; esta revalidação leu arquivos de engine, commands, batch, history, keyframe e Graph. Não compilado nem qualificado no Windows desta sessão.

## Camadas e owners
Cargo.toml:3 members crates/*, apps/*, xtask. Crates lógicos time/geom/color, raster/path/keyframe, project/text/effects/track, render/media/export/expr, engine/script/host, egui/automation, desktop/CLI/web. Essa separação permite tratar engine como um **candidato de processo headless** sem incorporar interface egui. A referência NÃO deve ser owner do CreativeDocument Hermes: .ecproj e CreativeDocument têm esquemas distintos. Não impor .ecproj como canonical project.

## Command Registry — o maior retorno inicial
- crates/engine/src/commands/mod.rs:94 CommandSpec descreve id, label, menu, shortcut, params, enabled, run e journal. :131 command_specs agrega specs; :339 check_params controla parâmetros; engine/src/lib.rs:572 Session::execute, :598 execute_checked, :604 is_enabled.
- Mesmo comando é acessível a UI/CLI/MCP/script segundo código e docs de automação CW-AUDIT-01/03; para paridade exata dos caminhos remotos ainda exige teste integrado.
- Comparação: workstation/creative_commands.py:52 CommandRegistry e :67 default_handlers fornece dispatch e inverses mas não oferece no contrato observado um strict schema discoverable para cada comando ao agente. Portanto ADAPT_CONTRACT Schema+enabled(reason)+list(filter)+describe individual.
- Não exportar 2.000 comandos no contexto LLM. Expor lista de famílias inicialmente, recuperar schema de 2–8 comandos pela seleção e objetivo. Lado humano usar ID estável igual, não click como caminho obrigatório.
- Negative: unknown command/unknown param, layer locked, actor sem scope e revision incorreta não executam nada. Pré-check nunca substitui gate no momento do commit.

## Atomic batch + one undo
- crates/engine/src/commands/batch.rs:16 reference resolve $N/path de resultado anterior; :42 substitute percorre JSON; :54 batch recebe steps, atomic default true e tira snapshot project/history/state; :97 fold condensa histórico; :106 specs; :127 teste batch_refs_one_undo_step_and_rollback.
- Rollback do EffectCraft atua no estado da Session (snapshots), e idempotência/concorrência do Hermes exige CAS durável. Não copiar diretamente rollback Rust no Python. ADAPT_CONTRACT com result references e gramática, mantendo CreativeTransaction.apply:32 (clone, all-or-nothing).
- Em comandos de exportação, nunca pretender rollback de efeito externo por snapshot do projeto. Separar journal de render e limpeza de arquivo com receipt próprio.

## História, operações contínuas e branching
- crates/engine/src/history.rs:27 History, :40 Branch, :50 HistoryNode; :193 record, :201 abandon_redo, :276 goto_history. Permite branching visual não-linear e merge de arrastos.
- Hermes creative_transactions.py:74 CreativeHistory tem stacks, revision e idempotency em RAM. Comparação importante: Hermes é mais forte em intenção de CAS/409, EffectCraft em usabilidade/history tree. ADAPT_ALGORITHM: merge_key para arrasto de mouse/ângulos e branch preview; persistir no mesmo source owner. Pós-crash history deverá reabrir sem duplicar comando.
- NÃO adicionar outro history store ao renderer (PR #77 tem undoHistory/redoHistory próprios, que deverão virar apresentação do histórico canônico).

## Tempo e keyframes
- crates/keyframe/src/lib.rs:23 Interp Linear/Bezier/Hold, :43 Ease, :60 Keyframe, :167 bez, :177 solve_u, :220 ease_progress, :228 SpatialSeg, :295 spatial_tangents, :394 retime_roving, :461 evaluate, :533 velocity, :541 speed. Há testes no próprio arquivo :602, :613, :628, :643, :655, :679 e outros.
- EffectCraft time/src/lib.rs Tick i64 racional para mídia e drop-frame. Não substituir creative_time.py Fraction/CanonicalTime apenas por preferência. ADAPT_CONTRACT timeBase layer/comp e snapping; ADAPT_ALGORITHM interpolation/roving/spatial arc-length sob a representação Hermes.
- Testes: 30000/1001 e 60 fps; hold/linear/bezier; equal influence, valores extremos e NaN; speed graph derivada; último frame no intervalo half-open; seeks [70,0,10,70] têm hashes invariantes.

## Graph Editor: solução forte, não drop-in
- crates/ui-egui/src/panels/graph.rs:33 Handle, :44 KeyPt, :54 Curve, :68 speed_graph, :105 curves, :188 show, :521 fit_selection, :601 HandleGrab::ease. Interação egui + matemática keyframe; controle gráfico de value/speed, handles drag com merge, seleção e comandos keys.
- React/Electron do Hermes não pode importar widgets egui diretamente. Melhor desenho: render editor React SVG/Canvas com seleção de propriedade IDs + comandos keyframe.update/ease/velocity; math avaliada pelo engine canônico (não inventar duas curvas distintas). Graph Editor e Inspector leem mesmo revision.
- As tangentes devem ser editáveis por humano e IA, e a animação exportada usa exatamente o mesmo algoritmo de interpolação que o preview. Validar divergência epsilon e pixels.

## Efeitos, composição, 3D, máscaras
- Relatório CW-AUDIT-01/03 descreve crates/render/src/lib.rs Renderer::comp_frame, layers/masks/effect/matte/blend/motion blur e crates/effects registry, GLB/OBJ, shadow/lighting. O número 306 efeitos e 280 GPU é declaração do projeto e catálogo anterior, NÃO benchmark realizado aqui.
- Preferir WRAP_ENGINE para efeitos especializados, sujeito a licença, custo de bootstrap, IPC, representação de frames e fidelidade reversível do projeto. Não transplantar 306 algoritmos para Python.
- Limites: partes da paridade auto-declarada, codec limitations e desempenho real GPU desconhecido neste Windows. Importações .aep e paridade AE não confirmadas por esta auditoria.
- Viewer cache LayerCache e out-of-order frame reference (auditoria anterior) são candidatos ADAPT_ALGORITHM quando houver perf trace; não adicionar cache especulativo.

## Automação, script e segurança
- CW-AUDIT-01 documentou __query vs __exec e beginUndoGroup/script matchnames. Separar leitura de escrita facilita agente: inspect current selection/properties sem tocar documento; mutate apenas sob command registry + owner/TaskRun/policy/expectedRevision.
- Não executar scripts arbitrários LLM em renderer Electron privilegiado. Caso preserve código procedural (HTML/JS), node é opaque, assets seguros, sandbox CSP, seed/time/ready e declarative params. Alterações externas no arquivo não voltam automaticamente ao source editable.

## Hipóteses A–H — respostas
A. **Algoritmos:** interpolation temporal Bezier/spatial/velocity/roving, merge drag/history branching, caches após medição; REUSE matemática/arquitetura, não bytes sem licença.
B. **Contratos:** CommandSpec, schema strict, enabled(reason), list/describe, engine.batch $N.refs+one undo e __query/__exec — prioridade P0 com alto retorno.
C. **Serviço Rust:** arquiteturalmente plausível via CLI/MCP/processo; teste binário próprio + JSON/frames e sandbox necessário. Não afirmar latência, portabilidade ou licença da cadeia sem build.
D. **Graph Editor:** SIM, é referência relevante: show/handles + keyframe math; portar interação a React, math a evaluator Hermes ou wrapper Rust, provar frame parity.
E. **Humano/IA:** mesmo Session::execute é superior como contrato de interface; Hermes mantém superioridade potencial na autoridade/TaskRun/ETag, ambos devem convergir.
F. **Seleção:** ADAPT_CONTRACT registry/batch; ADAPT_ALGORITHM Graph/interpolation/history/cache; WRAP_ENGINE renderer de efeitos condicionado; REFERENCE_ONLY widgets egui e modelo .ecproj como canon; REJECT copiar editor inteiro.
G. **Riscos:** snapshot SHA ausente, young project, dependências Rust, data/asset interchange, compilação 1.95, sandbox/IPC, licença transitiva/artefatos, perf não medida, parity auto-declarada.
H. **Entrega rápida:** schemas+list/describe+strict e result references, depois Graph easing. Trabalho caro: camada de effects Rust/FFI, source roundtrip .ecproj, render 3D profissional, media full interchange.

## POC contratual proposta
Given CreativeDocument rev=7 + layerId/title: HUMAN drag x=30 issues creative.layer.set(x=30, expectedRevision=7, actor=human)→rev8; AI receives selection and rev8, executes batch set x=40 + opacity key→rev9; undo restores rev8. Inject concurrent human rev10 before delayed AI rev9 commit; 409+explicit rebase, no lost edit. Test no GUI coords in AI command path. Só depois EffectCraft CLI pode receber cópia read-only e render frame, comparando PNG visual contra Hermes.
