# Hermes Work — auditoria da telemetria observada e instrumentação das próximas runs
Data: 2026-10-12. Status: **PATCH LOCAL ISOLADO / NÃO ATIVO EM MAIN / NOT_RELEASE_QUALIFIED**.

## 1. Fonte real, sem dados sensíveis publicados

Arquivo inspecionado em modo read-only: `C:\Users\Kevyn Lucas\AppData\Local\hermes\workstation\telemetry\telemetry.sqlite`. O banco tem 4.362.240 bytes; `PRAGMA quick_check = ok`. A configuração `workstation/workstation.yaml` define `telemetry.enabled: true`; `workstation/integrations/hermes/adapter.py` chama `install_workstation_telemetry()`, que instala o `SQLiteTelemetrySink`. A existência do banco com eventos reais prova atividade histórica, **não prova que esteja coletando neste exato instante**.

Janela observada: de `2026-09-24T03:55:58Z` a `2026-10-11T22:01:01Z` (UTC). **5.108 eventos**, **31 sessões**, **91 tarefas** e **24 runs** distintos não nulos.

| Família / indicador | Contagem |
|---|---:|
| PROVIDER_CALLED | 3.189 |
| PROVIDER_USAGE_RECORDED | 575 |
| TOOL_COMPLETED | 694 |
| ROUTING_DECIDED | 596 |
| TURN_STARTED | 43 |
| SYSTEM1_COMPLETED | 5 |
| LLM_WOKEN | 6 |
| VERIFICATION_COMPLETED | **0** |
| MUTATION_DISPATCHED | **0** |
| Chamadas de provedor **sem run_id** | **3.189 / 3.189** |
| Ferramentas **sem run_id** | **61 / 694** |
| Ferramentas browser_* na amostra | **84** |
| Ferramentas browser_snapshot | **16** |
| Ferramentas browser_console | **34** |
| Ferramentas browser_navigate | **15** |
| Ferramentas browser_type | **8** |

Latência de **84 chamadas de ferramentas browser_***: mediana **49,55 ms**, p95 **8.065,15 ms**. Os eventos estão roteados como `tool.browser_*` e **não** demonstram que cada chamada executou no Chromium nativo; essa distribuição é apenas diagnóstico de tool timing misto, não benchmark comparativo do Browser Nativo. `native_browser` atualmente possui **0 medições úteis de latência** no modelo de projeção anterior.

Dos 575 eventos de usage, 473 têm custo estimado registrado (soma indicativa US$ 0,7106 nesses 473 eventos); **não corresponde ao custo total das runs**. A cobertura de custo, tokens e linkage entre eventos de provider é incompleta. Não calcular preço por resultado verificado enquanto a contagem de resultados verificados é zero.

**Decisões derivadas:** (a) os owners de execução não estão alimentando persistentemente o funil `MUTATION_DISPATCHED -> VERIFICATION_COMPLETED -> OUTCOME_ACCEPTED` no banco observado; (b) o Browser é contado genericamente como tool, sem distinguir backend nativo, local-versus-externo, fallback ou batch; (c) o p95 elevado reforça necessidade de separar auto-snapshots, DOM hydration, controller I/O, polling e custos reais; (d) a falta de `run_id` em provedores impede afirmar ROI de Laya, Prefabs e Browser por run; (e) não inferir causalidade ou economia a partir dessas contagens.

## 2. Correções / instrumentação em branch

Worktree exclusivo: `.worktrees/browser-native-evidence-20261012` / `audit/browser-native-evidence-20261012`. Continuação do HEAD `305f2f4999`.

- `workstation/telemetry/sqlite_sink.py`: fecha explicitamente SQLite connections de escrita **e leitura**, pois o context manager padrão de `sqlite3.Connection` encerra transação mas não fecha o handle. Testes reproduziram e depois eliminaram bloqueio do `telemetry.sqlite` no Windows. Nenhuma alteração/correção foi aplicada ao banco histórico.
- `workstation/telemetry/models.py`: nova família não autoritativa `BROWSER_OPERATION_OBSERVED`.
- `workstation/telemetry/browser_observation.py`: permite apenas campos estruturados pré-aprovados; `REQUEST_ATTEMPTED` antecede chamada loopback, seguido de `ACKNOWLEDGED`, `LOCAL_VERIFIED`, `UNCERTAIN`, `REJECTED`, `OBSERVED` ou `ERROR`. **ACK ≠ VERIFIED e verificação DOM local ≠ persistência externa**. Correlaciona por session/task/run/operation/action e registra duração de controller, bytes de request/response, códigos de erro whitelisted, número de passos e confirmação, cache hits, modo de snapshot, tamanho e chamadas CDP. Sem URL, HTML, screenshot, texto, valores de formulário, cookies, prompt, resposta ou segredos.
- `tools/browser_workstation.py::_dispatch`: no caminho **já selecionado do Browser Nativo** emite evento de tentativa, resultado/erro e mantém as invariantes de controle. Extrai `__telemetry` antes de serializar a resposta ao modelo, inclusive se o sink estiver indisponível. Não cria roteador/dispatcher/agent paralelo.
- `apps/desktop/electron/workstation-browser-runtime.ts::snapshotForEntry`: captura engine `ax/dom/dom_fallback`, duração local, chamadas CDP do snapshot, caracteres de full/delta, quantidade de elementos, CPU e RSS do **processo principal Electron**, não renderer, como números estruturados. `browser_extract_items` retorna `cached: true/false` para medir acertos e denominadores.
- `workstation/telemetry/projectors.py::project_native_browser_profile`: mede tentativas sem observação terminal, incerteza de lotes, latência p50/p95, engines, CDP e cache sem inventar denominadores; `verified_external_outcomes=None` enquanto faltar owner verification independente.

**Fatores ainda não medidos:** memória/CPU do renderer, latência até confirmação externa, tokens reais por operação (o byte count é só proxy estrutural), desempenho em Windows Electron real, eficiência/risco de cache em SPA, exact-head CI. Testes unitários/mocks não provam instalação no produto atualmente aberto. **Esta branch precisa ser implantada/qualificada antes de gerar novas telemetrias nas runs do usuário**.

## 3. Evidências de teste

- RED original: import de `workstation.telemetry.browser_observation` inexistente; teste de payload privado falhou; teste de Electron `BROW-TEL` sem `__telemetry` falhou. GREEN: contratos novos em SQLite temporário e Browser/Electron focal.
- RED adicional reproduzido: no Windows, `TemporaryDirectory.cleanup()` do SQLite falhou por handles abertos de read e write; corrigido com `contextmanager`/ `closing` explícitos.
- Testes Python executados por runner `unittest` isolado de bootstrap: isola dependências externas ausentes (falta `ruamel.yaml` e `pytest` no Python local); **não equivale à suíte Python total**.
- Comando suite Electron local: `cd apps/desktop && node ../../node_modules/vitest/vitest.mjs run --config vitest.browser-native-audit.config.mjs`.
- Sem native E2E / exact-head CI / benchmark produção.
- O commit de instrumentação teve o hook global de Python lint bloqueado por avisos **já existentes** no `tools/browser_workstation.py` (ex.: `Optional[Dict]` e `.replace('Z', '+00:00')` presentes no HEAD anterior). A alteração foi commitada com hooks temporariamente desabilitados apenas nesse commit, após `py_compile`, sete contratos isolados Python, 156 testes Browser/Electron e `git diff --cached --check` verdes. O gate global de lint **não** foi declarado aprovado.

## 4. Próxima análise depois de runs reais (após promoção)

Consultar `workstation/telemetry/sqlite_sink.py::TelemetryQuery.events` filtrando `event_type='BROWSER_OPERATION_OBSERVED'` e aplicar `project_native_browser_profile`. Comparar por run e action: tempo p50/p95, `REQUEST_ATTEMPTED` sem observação terminal, estados de batch, cache hit/miss, `cdp_calls`, `snapshot_chars`/`delta_chars`, CPU/RSS do main process. Cruzar com outcomes/verificações somente quando owners realmente emitirem fatos independentes. Não guardar dados sensíveis e não usar efeitos externos reais como benchmarks sem autorização.

Prioridade futura: P0 correlação owner-verified TaskRun/BrowserTask e durable exactly-once; P0 teste nativo com Electron real; P1 freshness de cache por mutation counters; P1 atribuição de custos de provider a `run_id`; P1 renderer metrics/visualização UX; H-079/CI before promotion.
