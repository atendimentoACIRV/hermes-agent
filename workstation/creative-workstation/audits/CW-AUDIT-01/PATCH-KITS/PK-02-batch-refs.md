# PK-02 — Atomic batch $N.key + fold (RC-02, ADAPT_CONTRACT)

**Origem:** `effectcraft-main/crates/engine/src/commands/batch.rs:1-118` (MIT OR Apache-2.0) · **Destino:** `workstation/creative_transactions.py:CreativeTransaction/CreativeHistory` · **NÃO APLICADO.**

## Conceito origem
`engine.batch{steps:[{command,params}],label?,atomic?=true}`; string exatamente `"$N"` ou `"$N.key"` substituída pelo resultado do step N; `NOT_IN_BATCH=[engine.batch,file.runScript,script.run]`; falha → rollback snapshot + erro nomeia step; sucesso → `fold()` 1 undo.

## Adaptação (esqueleto)
```python
BATCH_REF_RE = re.compile(r"^\$(\d+)(?:\.([A-Za-z0-9_]+))?$")
NOT_IN_BATCH = {"engine.batch", "creative.batch"}
def resolve_refs(steps, results):
    # substitui "$1.layer" pelo results[0]["layer"]; erro BatchRefError se N inválido
def apply_batch(commands: list[CreativeCommand], *, label: str, atomic: bool = True) -> CommandResult:
    snapshot = document_to_dict(doc)
    results = []
    for i, cmd in enumerate(commands):
        cmd.params = resolve_refs(cmd.params, results)
        r = apply_single(cmd, snapshot)
        if not r.success and atomic:
            restore(snapshot); return fail(f"step {i+1}/{len(commands)}: {r.error}")
        results.append(r.outputs)
    commit_once(label, inverses_folded=True)
```

## Destino
`CreativeTransaction{commands}` + `CreativeHistory.commit` — adicionar `label/atomic`, resolver refs antes de cada step, fold inverses em 1 entrada undo. Manter `expected_revision` 409 + `seen_idempotency` Hermes (superior — não remover).

## Testes/build/licença/rollback
Testes: `batch_refs_resolve_and_single_undo` + `batch_atomic_rollback_names_step` + `batch_rejects_nested_batch`. Sem deps. MIT/Apache adaptação. Rollback: flag `atomic=False` legado + remover resolver.
