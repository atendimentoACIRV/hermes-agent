# PK-03 — Penpot AI Kit skills COPY_DIRECT (RC-11, CC-BY-4.0)

**Origem:** `referências/01-Criacao-Visual-Video-3D/penpot--penpot-ai-kit/skills/penpot-{build-screen,build-deck,router}/SKILL.md` + `skills.json/lock` · SHA `fe4f99e51c71` · Licença CC-BY-4.0 (COPY permitido com atribuição) · **Destino:** `skills/creative/penpot-*` (novo, fora runtime) + patterns em `workstation/creative_edit_plan.py` docs · **NÃO APLICADO.**

## Instruções
1. Copiar cada `SKILL.md` integralmente (NÃO reescrever); preservar header frontmatter.
2. Adicionar atribuição no topo: `Source: penpot-ai-kit <SHA> (CC-BY-4.0, Penpot)` + link + `skills.json` pin.
3. Adaptar apenas `workflows/` paths Hermes (`CreativeDocument` + `SemanticEditPlan` em vez de API proprietária) em seção `## Hermes binding` separada — nunca alterar o original copiado.
4. Registrar em `workstation/SOURCE_MATRIX.md` (quando autorizado) + `ATTRIBUTION`-like.

## Contratos/testes/rollback
I/O: skill instrui → `SemanticEditPlan{intent,targetIds,commands}` → preview → approval. Testes: skill lint (frontmatter) + 1 E2E design→plan sem mutação. Rollback: remover pasta `skills/creative/penpot-*`.
**Atenção:** Penpot engine (MPL-2.0 Clojure) NÃO copiar — só WRAP MCP (`mcp/packages/common/src/index.ts`, SHA `10955f17e279`) via `creative_apps.py` probe.
