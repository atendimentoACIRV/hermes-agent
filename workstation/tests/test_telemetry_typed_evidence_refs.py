"""Typed canonical evidence must not break durable telemetry writes."""

from workstation.contracts import EvidenceRef
from workstation.telemetry import TelemetryEventType, emit_event, set_telemetry_sink
from workstation.telemetry.sqlite_sink import SQLiteTelemetrySink, TelemetryQuery


def test_canonical_evidence_ref_is_projected_to_uri_without_metadata_leak(tmp_path, caplog):
    path = tmp_path / "typed_refs.sqlite"
    sink = SQLiteTelemetrySink(path)
    set_telemetry_sink(sink)
    try:
        event = emit_event(
            TelemetryEventType.OUTCOME_ACCEPTED,
            source_owner="workstation.test", task_id="task-e", run_id="run-e",
            evidence_refs=(EvidenceRef(
                kind="verification", uri="artifact://tasks/task-e/receipt-1",
                summary="CANARY_PRIVATE_SUMMARY_NOT_FOR_TELEMETRY",
            ), "artifact://tasks/task-e/receipt-2"),
        )
    finally:
        set_telemetry_sink(None)
    assert event.evidence_refs == (
        "artifact://tasks/task-e/receipt-1", "artifact://tasks/task-e/receipt-2",
    )
    rows = TelemetryQuery(path).events(task_id="task-e", run_id="run-e")
    assert len(rows) == 1
    assert rows[0].evidence_refs == event.evidence_refs
    raw = b"".join(p.read_bytes() for p in tmp_path.glob("typed_refs.sqlite*"))
    assert b"CANARY_PRIVATE_SUMMARY_NOT_FOR_TELEMETRY" not in raw
    assert "Workstation telemetry emission failed" not in caplog.text
