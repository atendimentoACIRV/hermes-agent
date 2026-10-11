# PK-01 — Strict schemas + bounded discovery (RC-01, ADAPT_CONTRACT)

**Origem:** `effectcraft-main/crates/engine/src/commands/mod.rs:93-359` (MIT OR Apache-2.0, ArtCraft Team) · **Destino:** `workstation/creative_commands.py:CommandRegistry` · **NÃO APLICADO ao runtime.**

## Fragmento origem (conceito, não cópia literal Rust→Python)
```rust
struct CommandSpec { id, label, menu, shortcut, params, enabled: Enabled, run: Run, journal: bool }
find(id) -> Option<&CommandSpec>; check_params(spec, params) -> Result<(), UnknownKeys{accepted}>
```

## Adaptação proposta (Python, esqueleto para implementadora)
```python
@dataclass(frozen=True)
class CreativeCommandSpec:
    command_id: str; label: str; menu_path: str = ""; shortcut: str = ""
    params_schema: dict = field(default_factory=dict)  # JSON Schema
    enabled_reason: str = ""  # por que habilitado/desabilitado agora
class CommandRegistry:
    def describe(self, command_id: str) -> CreativeCommandSpec: ...
    def list_commands(self, *, filter: str = "", enabled_only: bool = False) -> list[CreativeCommandSpec]: ...
    def execute_checked(self, cmd: CreativeCommand, revision: int) -> CommandResult:
        spec = self.describe(cmd.command_id)
        unknown = set(cmd.params) - set(spec.params_schema.get("properties", {}))
        if unknown:
            raise UnknownCommandParam(sorted(unknown), accepted=sorted(spec.params_schema.get("properties", {})))
        return execute_command(cmd, revision)
```

## Destino/símbolo a substituir
`workstation/creative_commands.py:CommandRegistry.execute_command` — adicionar `describe/list_commands/execute_checked`; `CreativeCommand.params: dict` passa a validado por schema. Imports: `jsonschema` (já? verificar `pyproject.toml`; senão validação manual mínima sem nova dep). Contratos I/O: entrada `CreativeCommand{command_id,params,actor,idempotency_key}` + `expected_revision`; saída `CommandResult{success,error,accepted_keys?}` + `denial_reason` quando desabilitado.

## Testes
- `test_unknown_param_rejected_with_accepted_list` · `test_list_filter_enabled_only` · `test_describe_schema_validates` (usar `test_creative_commands.py` como base).
## Build/licença/rollback
Sem build (só Python). Licença origem MIT/Apache — ADAPT_CONTRACT (ideia, não cópia literal) + atribuição em NOTICE se literal. Rollback: remover `execute_checked/describe`, manter `execute_command` legado.
