from __future__ import annotations

from collections import Counter
from datetime import datetime
import math
import statistics

from workstation.control_plane.metrics import ORAMetrics, calculate_volc

from .models import TelemetryEventType, TelemetryEventV1


def _event_identity(event):
    if event.call_id:
        return event.event_type, event.session_id, event.call_id
    return event.event_type, event.session_id, event.dedupe_key or event.event_id


def project_ora_volc(events: list[TelemetryEventV1]):
    verified_operations: set[str] = set()
    deterministic: set[str] = set()
    reasoned: set[str] = set()
    unverified = 0
    provider_calls = 0
    input_tokens = 0
    output_tokens = 0
    tool_calls = 0
    system1 = {"calls": 0, "successful": 0, "abstained": 0, "fallback": 0, "error": 0}
    superseded = wakes = 0
    tokens_known = True
    cost_known = True
    cost = 0.0
    seen = set()
    usage_calls = {(e.session_id, e.call_id) for e in events
                   if e.event_type == TelemetryEventType.PROVIDER_USAGE_RECORDED and e.call_id}
    for event in events:
        key = _event_identity(event)
        if key in seen:
            continue
        seen.add(key)
        if event.event_type == TelemetryEventType.SYSTEM1_COMPLETED:
            system1["calls"] += 1
            for key in ("successful", "abstained", "fallback", "error"):
                system1[key] += event.payload.get(key) is True
        if event.event_type == TelemetryEventType.AUTHORITY_SUPERSEDED:
            superseded += 1
        if event.event_type == TelemetryEventType.LLM_WOKEN:
            wakes += 1
        if event.event_type == TelemetryEventType.PROVIDER_CALLED:
            provider_calls += event.provider_calls if event.provider_calls is not None else 1
        if (event.event_type == TelemetryEventType.PROVIDER_USAGE_RECORDED or
                event.event_type == TelemetryEventType.PROVIDER_CALLED
                and (event.session_id, event.call_id) not in usage_calls):
            input_tokens += event.input_tokens or 0
            output_tokens += event.output_tokens or 0
            tokens_known = tokens_known and event.input_tokens is not None and event.output_tokens is not None
            cost_known = cost_known and event.cost_usd is not None
            cost += event.cost_usd or 0.0
        if event.tool_calls is not None:
            tool_calls += event.tool_calls
        if event.event_type == TelemetryEventType.VERIFICATION_COMPLETED:
            if event.status == "VERIFIED":
                key = (event.task_id, event.run_id, event.operation_id or event.event_id)
                verified_operations.add(key)
                if event.route in {"deterministic", "execute", "native_browser", "composite"}:
                    deterministic.add(key)
                else:
                    reasoned.add(key)
            else:
                unverified += 1
    ora = ORAMetrics(verified_transitions_deterministic=len(deterministic),
                     verified_transitions_reasoned=len(reasoned),
                     unverified_transitions=unverified)
    ora.system1_calls = system1["calls"]
    ora.system1_successful_decisions = system1["successful"]
    ora.system1_abstentions = system1["abstained"]
    ora.system1_fallbacks = system1["fallback"]
    ora.system1_errors = system1["error"]
    ora.system2_wake_count = ora.llm_wake_count = wakes
    ora.authority_superseded_count = superseded
    ora.tokens_consumed = input_tokens + output_tokens if tokens_known else None
    ora.total_cost_usd = cost if cost_known and provider_calls else None
    volc = calculate_volc(len(verified_operations), llm_calls=provider_calls,
                          tokens=input_tokens + output_tokens if tokens_known else None, tool_calls=tool_calls,
                          tokens_cost_usd=cost if cost_known and provider_calls else None)
    return ora, volc


def project_operation_economics(events: list[TelemetryEventV1]) -> dict:
    """Local event projection. Missing usage/prices stay unknown; no modeled savings.

    Durations sum instrumented calls, including overlap. Admission latency starts
    on the server; it excludes transport/UI time and is never end-user latency.
    """
    unique, seen = [], set()
    for e in events:
        identity = _event_identity(e)
        if identity not in seen:
            seen.add(identity)
            unique.append(e)
    calls = [e for e in unique if e.event_type == TelemetryEventType.PROVIDER_CALLED]
    usage = {(e.session_id, e.call_id): e for e in unique
             if e.event_type == TelemetryEventType.PROVIDER_USAGE_RECORDED and e.call_id}
    billed = [usage.get((e.session_id, e.call_id), e) for e in calls]
    tools = [e for e in unique if e.event_type == TelemetryEventType.TOOL_COMPLETED and e.tool_calls]
    verified = {(e.task_id, e.run_id, e.operation_id or e.event_id): e for e in unique
                if e.event_type == TelemetryEventType.VERIFICATION_COMPLETED and e.status == "VERIFIED"}
    def total(items, field):
        values = [getattr(e, field) for e in items]
        return sum(values) if values and all(v is not None for v in values) else None
    priced = bool(billed) and all(e.cost_usd is not None and e.cost_source for e in billed)
    cost = sum(e.cost_usd for e in billed) if priced else None
    names = Counter(e.payload.get("tool_name") for e in tools)
    reads = Counter((e.task_id, e.run_id, e.payload.get("tool_name"), e.payload["read_fingerprint"])
                    for e in tools if e.payload.get("read_fingerprint"))
    starts = {}
    for e in unique:
        if e.event_type == TelemetryEventType.TURN_STARTED:
            starts.setdefault((e.task_id, e.run_id), []).append(e)
    latencies = []
    for (task, run, _), e in verified.items():
        finished = datetime.fromisoformat(e.occurred_at)
        preceding = [t for t in starts.get((task, run), [])
                     if datetime.fromisoformat(t.occurred_at) <= finished
                     and (not e.turn_id or t.turn_id == e.turn_id)]
        # Without shared turn lineage, multiple starts are ambiguous: do not
        # assign a late verification to the most recent unrelated request.
        if len(preceding) == 1:
            latencies.append((finished - datetime.fromisoformat(preceding[0].occurred_at)).total_seconds() * 1000)
    latencies.sort()
    return {
        "provider_calls": len(calls), "tool_calls": len(tools),
        "calls_without_id": sum(not e.call_id for e in [*calls, *tools]),
        "calls_without_run_id": sum(not e.run_id for e in [*calls, *tools]),
        "terminal_calls": names["terminal"],
        "skill_calls": sum(names[n] for n in ("skill_view", "skills_list", "skill_search")),
        "snapshot_calls": names["browser_snapshot"], "console_calls": names["browser_console"],
        "repeated_browser_queries": sum(n - 1 for n in reads.values()),
        "verified_operations": len(verified),
        "failed_verifications": sum(e.event_type == TelemetryEventType.VERIFICATION_COMPLETED
                                    and e.status in {"FAILED", "CONFLICT", "STALE"} for e in unique),
        "uncertain_effects": sum(e.event_type == TelemetryEventType.MUTATION_DISPATCHED
                                 and (not e.operation_id or (e.task_id, e.run_id, e.operation_id) not in verified)
                                 for e in unique),
        "input_tokens": total(billed, "input_tokens"), "output_tokens": total(billed, "output_tokens"),
        "cache_read_tokens": total(billed, "cache_read_tokens"), "cache_write_tokens": total(billed, "cache_write_tokens"),
        "provider_request_bytes": total(calls, "request_bytes"), "provider_result_bytes": total(calls, "result_bytes"),
        "browser_request_bytes": total([e for e in tools if e.route == "native_browser"], "request_bytes"),
        "browser_result_bytes": total([e for e in tools if e.route == "native_browser"], "result_bytes"),
        "system2_call_ms": total(calls, "duration_ms"),
        "system1_call_ms": total([e for e in unique if e.event_type == TelemetryEventType.SYSTEM1_COMPLETED], "duration_ms"),
        "browser_call_ms": total([e for e in tools if e.route == "native_browser"], "duration_ms"),
        "other_tool_ms": total([e for e in tools if e.route != "native_browser"], "duration_ms"),
        "admission_to_verified_ms": latencies,
        "admission_to_verified_median_ms": statistics.median(latencies) if latencies else None,
        "admission_to_verified_p95_ms": latencies[math.ceil(len(latencies) * .95) - 1] if latencies else None,
        "cost_usd": cost, "cost_sources": sorted({e.cost_source for e in billed if e.cost_source}),
        "cost_per_verified_outcome_usd": cost / len(verified) if cost is not None and verified else None,
    }


def project_native_browser_profile(events: list[TelemetryEventV1]) -> dict:
    """Summarize measured native-browser attempts; never mistake ACK for outcome.

    Timing scope is Python loopback boundary; CPU/RSS are Electron main process
    snapshots. All missing data remain None, not zero.
    """
    browser = [e for e in events
               if e.event_type == TelemetryEventType.BROWSER_OPERATION_OBSERVED
               and e.route == "native_browser"]
    attempted = [e for e in browser if e.status == "REQUEST_ATTEMPTED"]
    finished = [e for e in browser if e.status != "REQUEST_ATTEMPTED"]

    def identity(e: TelemetryEventV1) -> tuple:
        return (e.session_id, e.task_id, e.run_id, e.operation_id, e.phase)

    attempt_ids = {identity(e) for e in attempted if e.operation_id}
    terminal_ids = {identity(e) for e in finished if e.operation_id}
    delays = sorted(e.duration_ms for e in finished
                    if e.duration_ms is not None and math.isfinite(e.duration_ms)
                    and e.duration_ms >= 0)
    source = Counter(e.payload.get("snapshot_source") for e in finished
                     if e.payload.get("snapshot_source"))
    cdp = [e.payload["cdp_calls"] for e in finished
           if isinstance(e.payload.get("cdp_calls"), int)]
    snapshots = [e for e in finished if e.payload.get("snapshot_source")]
    cache = [e for e in finished if isinstance(e.payload.get("cached"), bool)]
    return {
        "attempts": len(attempted),
        "terminal_observations": len(finished),
        "unresolved_attempts": len(attempt_ids - terminal_ids),
        "uncertain_batches": sum(e.phase == "browser_batch_actions"
                                 and e.status == "UNCERTAIN" for e in finished),
        "acknowledged_actions": sum(e.status == "ACKNOWLEDGED" for e in finished),
        "local_verified_batches": sum(e.status == "LOCAL_VERIFIED" for e in finished),
        "failed_actions": sum(e.status == "ERROR" for e in finished),
        "verified_external_outcomes": None,
        "latency_scope": "python_loopback_and_electron",
        "latency_samples": len(delays),
        "latency_ms_p50": statistics.median(delays) if delays else None,
        "latency_ms_p95": delays[math.ceil(.95 * len(delays)) - 1] if delays else None,
        "cdp_calls_known": len(cdp),
        "cdp_calls_total_observed": sum(cdp) if cdp else None,
        "snapshot_engines": dict(source),
        "snapshot_samples": len(snapshots),
        "cache_observations": len(cache),
        "cache_hits": sum(e.payload["cached"] for e in cache),
        "response_bytes_total": sum(e.result_bytes for e in finished
                                    if e.result_bytes is not None),
    }
