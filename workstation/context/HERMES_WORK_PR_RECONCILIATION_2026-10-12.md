# PRs e dependências — snapshot verificado em 2026-10-12

**Repositório:** `kevynlucasprofissional-stack/hermes-agent`. **Main observado:** `a2b56db1bc9e0b5acf48d94fa86a9844a1005842`. Todos os PRs abaixo foram consultados via conector GitHub: **OPEN**, nenhum `merged`. Apenas #70 está `ready`; os demais estão `DRAFT`. Os SHAs e estados são um **snapshot**, não locks futuros.

| PR | Branch / HEAD abreviado | Base | Proposta e evidência reportada | Limite de qualificação |
|---|---|---|---|---|
| [#70](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/70) | `fix/hermes-oneclick-lock-startup-20261011` / `7c24c09ce4` | main | One-Click lock/dependency fingerprint, bypass de reinstalação desnecessária e PowerShell 5.1; Windows local reportado | packaged/offline dogfood e integração |
| [#71](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/71) | `fix/p0-kanban-read-effects-20261011` / `ae14d0ae6d` | main | Leituras Kanban PURE_READ; 18 novos + 84 regressão | CI exact-head, native E2E |
| [#72](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/72) | `fix/boa001-effect-classification-20261011` / `8ca9297a1d` | main | BOA-001; 147 pass, 1 skip; dinâmicos console/todo | UI/Browser ao vivo, CI |
| [#73](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/73) | `fix/p0-denied-mutation-receipts-20261011` / `a491a8f71b` | main | Rail 2; dedupe/review consumível, 49 pass | handoff UI + readback independente |
| [#74](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/74) | `fix/p0-run-supersession-recovery-20261011` / `bf8227a91e` | main | Rail 3; fence tipado + checkpoint pending, 15 pass | integração native/worker |
| [#75](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/75) | `fix/p0-smart-task-admission-20261011` / `e4f9daaf21` | main | D-045: conversation/point_action/durable triage; 80 pass relatados | corpus real e E2E |
| [#76](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/76) | `integration/p0-authority-browser-20261011` / `4e6884d664` | main | Integra #70–#75; correção owner SQLite TaskCompiler; 116 pass | cadeia stacked, CI, native |
| [#77](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/77) | `feat/p0-creative-mvp-20261011` / `1692d50702` | main | Editor vetorial/motion apenas renderer, 10 vitest | backend CAS/MP4/3D não entregues |
| [#79](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/79) | `fix/p0-admission-proof-core-20261011` / `7d5c4df35e` | #76 | Force-work explícito + proof-bound completion, 133 testes selecionados relatados | acceptance tipado completo |
| [#80](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/80) | `fix/p0-proof-bound-completion-20261011` / `0e7fd0760f` | #79 | Backup SQLite consistente / dry-run 19 atuais, 106 históricos, 55 órfãos | nenhuma restauração autorizada |
| [#81](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/81) | `feat/hcw-hybrid-01-20261011` / `a3527baa7a` | main | Bridge Creative IPC/revision-CAS; 15 testes; UI sender attestation | resolveTrustedOwner DENY-ALL, sem TaskRun E2E |
| [#82](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/82) | `feat/experience-compiler-real-reuse-20261011` / `f552c96b78` | main | Owner readback e funil Experience, 21 testes novos; 66 pass/1 skip em suíte existente | 1 falha adjacente reportada; CI/qualificação pendentes |
| [#83](https://github.com/kevynlucasprofissional-stack/hermes-agent/pull/83) | `fix/p0-kanban-browser-authority-20261012` / `22498a09db` | #80 | Browser por sessão, concorrência, restart, handoff e lost-ACK; 34 Python, 58 Vitest, 4 native E2E na última execução | **falta E2E de aprovação UI→verificação tipada→retomada; CI []** |

## Grafo de dependências
- main → #70/#71/#72/#73/#74/#75 → #76 (base main, integração cumulativa).
- #76 → #79 → #80 → #83. **Não mesclar #83 diretamente sem reconsiderar dependências e validação conjunta**.
- #77, #81 e #82 são frentes criativa/compilação independentes sobre main, mas dependem funcionalmente da segurança de autoridade/execução para release.
- O mesmo conjunto de arquivos foi modificado em trilhas concorrentes no histórico BROW/OPC; não inferir escopo por autoria de commit apenas: inspecionar diff por caminho e PR.

## Precisão sobre CI, worktrees e main
GitHub consultado no commit #83 `22498a09db0802c06125f5a5ec4cb5039da9b98f`: `statuses=[]` e `workflow_runs=[]`. Isto significa **não verificado**, não aprovado e tampouco prova de CI falho. Não foi promovido à main.
Na workstation Windows, o checkout `C:\Github\hermes-agent` estava em `fix/hermes-oneclick-lock-startup-20261011`, HEAD local `9fffa7f3ff`, **com alterações não commitadas** em vários componentes renderer/UI e arquivos de dogfood. O worktree #83 separado estava no HEAD publicado. Nunca misturar ou limpar esse checkout sem coordenação.
Arquivos P0 citados no handoff não foram encontrados na main `a2b56...`, mas foram lidos na branch #83. Ao retomar, refazer `git fetch`, diff e revisão de todos os HEADs. Este PR documental não declara merge nem qualificação.
