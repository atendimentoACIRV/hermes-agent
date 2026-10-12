"""BAV05 test-only JSON-lines bridge to existing Hermes browser owner.

No new browser/runtime/authority provider. All tool dispatches originate from the
parent harness's authenticated localhost controller and disposable Electron profile.
Never use this protocol on a real user session.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from workstation.memory import ProceduralMemory, ProcedureStep, WebProcedure
from workstation.routines import (
    DeterministicRoutineRunner,
    RoutineExecutionStatus,
    RoutinePromotionService,
)

FINGERPRINT = "bav1-test-fixture-v1"


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def rpc(action: str, args: dict | None = None):
    emit({"rpc": action, "args": args or {}})
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("fixture authority bridge lost")
    result = json.loads(line)
    if not result.get("ok"):
        raise RuntimeError("fixture controller rejected " + action + ": " + str(result.get("error", "")))
    return result.get("result")


def run(mode: str, note: str, site: str, storage: str, fixture_path: str) -> None:
    if mode not in {"seed", "replay"}:
        raise ValueError("unsupported test-only mode")
    if not isinstance(note, str) or not (1 <= len(note) <= 64) or not note.isascii():
        raise ValueError("test note must be 1..64 ASCII characters")
    parsed = urlparse(site)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path != "/form":
        raise ValueError("test-only procedure may access only loopback fixture /form")

    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if fixture["scope"] != {"allowed_hosts": ["127.0.0.1"], "test_only": True}:
        raise ValueError("fixture scope changed")
    memory = ProceduralMemory(storage_path=Path(storage))
    if memory.load_error:
        raise RuntimeError("persistent memory is corrupt: " + memory.load_error)

    ctx: dict = {
        "note": note,
        "site": site,
        "elements": [],
        "snapshot": "",
        "server_before": rpc("test_effect_count"),
    }

    def snapshot() -> dict:
        obs = rpc("browser_snapshot", {"full": True})
        if not isinstance(obs, dict):
            raise ValueError("invalid native browser snapshot")
        ctx["elements"] = obs.get("elements", [])
        ctx["snapshot"] = str(obs.get("snapshot", ""))
        return obs

    def execute_step(step: ProcedureStep, target: str, state: dict) -> None:
        if step.action == "navigate":
            if step.target != "{site}":
                raise ValueError("test-only navigation target changed")
            rpc("browser_navigate", {"url": site})
            snapshot()
        elif step.action == "type":
            if not target or not target.startswith("@e"):
                raise ValueError("semantic type anchor unresolved")
            rpc("browser_type", {
                "ref": target, "text": step.value.replace("{note}", note),
                "clear": True, "semantic_anchor": step.fallback_anchors[0],
            })
            snapshot()
        elif step.action == "click":
            if not target or not target.startswith("@e"):
                raise ValueError("semantic click anchor unresolved")
            rpc("browser_click", {
                "ref": target, "semantic_anchor": step.fallback_anchors[0],
            })
            snapshot()
        elif step.action == "verify":
            snapshot()
            expected = step.expectation.replace("{note}", note)
            if expected not in ctx["snapshot"]:
                raise ValueError("fixture readback mismatch")
        else:
            raise ValueError("unapproved deterministic fixture action: " + step.action)

    def verified_effect() -> bool:
        return (
            "Saved: " + note in ctx["snapshot"]
            and rpc("test_effect_count") == ctx["server_before"] + 1
        )

    if mode == "seed":
        if memory.list_procedures():
            raise ValueError("seed requires empty isolated memory")
        raw = WebProcedure.from_dict(fixture)
        for step in raw.steps:
            if step.action in {"type", "click"}:
                anchor = step.resolve_anchor(ctx["elements"], strict=True)
                if not anchor:
                    # For seeding, use the controller's testid reacquisition with
                    # deliberately invalid ref; native controller must prove it works.
                    anchor = "@e999"
            else:
                anchor = step.target
            execute_step(step, anchor, ctx)
        if not verified_effect():
            raise ValueError("unverified seed effect")
        candidate = memory.record_success(raw.site, raw.intent, raw.steps, name=raw.name)
        candidate.capability_fingerprint = FINGERPRINT
        candidate.scope = raw.scope
        candidate.preconditions = []
        candidate.postconditions = ["fixture-confirmed"]
        memory.update_procedure(candidate)
        promotion = RoutinePromotionService(memory)
        promotion.validate(candidate.id, evidence=[{
            "kind": "test-fixture-server-effect", "uri": "fixture://bav-local-form",
            "effect_delta": 1, "test_only": True,
        }], validator=lambda c: bool(c.scope.get("test_only")) and len(c.steps) == 4)
        promotion.promote(candidate.id)
        assert ProceduralMemory(storage_path=Path(storage)).get_procedure(candidate.id).lifecycle.value == "promoted"
        emit({"done": True, "mode": "seed", "verified": True, "procedure_id": candidate.id})
        return

    result = DeterministicRoutineRunner(memory).run_matching(
        fingerprint=FINGERPRINT,
        scope=fixture["scope"],
        preconditions=[],
        context=ctx,
        execute_step=execute_step,
        check_postcondition=lambda condition, _state: (
            condition == "fixture-confirmed" and verified_effect()
        ),
    )
    if result is None or result.status != RoutineExecutionStatus.COMPLETED:
        raise RuntimeError("persisted routine not completed: " +
                           (str(result.reason) if result else "not promoted/not found"))
    emit({
        "done": True, "mode": "replay", "verified": verified_effect(),
        "completed_steps": result.completed_steps,
        "version": result.version, "procedure_id": result.procedure_id,
    })


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except Exception as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise
