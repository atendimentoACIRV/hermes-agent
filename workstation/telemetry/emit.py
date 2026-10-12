from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from workstation.contracts import EvidenceRef

from .models import TelemetryEventType, TelemetryEventV1
from .privacy import sanitize_payload
from .sink import NullTelemetrySink, TelemetrySink, safe_emit

_sink: TelemetrySink = NullTelemetrySink()


def set_telemetry_sink(sink: TelemetrySink | None) -> None:
    global _sink
    _sink = sink or NullTelemetrySink()


def get_telemetry_sink() -> TelemetrySink:
    return _sink


def emit_event(event_type: TelemetryEventType, *, source_owner: str,
               occurred_at: str | None = None, **fields: Any) -> TelemetryEventV1:
    now = datetime.now(UTC).isoformat()
    fields["payload"] = sanitize_payload(fields.get("payload") or {})
    refs = fields.get("evidence_refs")
    if isinstance(refs, (tuple, list)):
        # Canonical owners may supply EvidenceRef objects; the telemetry schema
        # stores URI identifiers only, never summaries or verifier metadata.
        fields["evidence_refs"] = tuple(
            ref.uri if isinstance(ref, EvidenceRef) else ref for ref in refs
        )
    event = TelemetryEventV1(event_type=event_type, occurred_at=occurred_at or now,
                             recorded_at=now, source_owner=source_owner, **fields)
    safe_emit(_sink, event)
    return event
