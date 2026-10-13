"""Fail-closed durable head compare-and-swap for canonical CreativeDocument edits.

A narrow opt-in publication seam. It does not grant TaskRun authority or
retrofit unrelated legacy producers. Callers must complete authorization and
native source verification before committing here. Never bypass the head CAS
by directly writing an existing canonical project with save_creative_document.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import uuid
from typing import Any, Iterator

from workstation.creative_project_store import (
    CreativeConflictError, CreativeProjectRevision,
    _identifier, _json_bytes, _root,
    load_creative_revision, load_creative_document, save_creative_document,
)
from workstation.creative_document import document_to_dict


@contextmanager
def _exclusive_project_lock(project_id: str) -> Iterator[None]:
    """Crash-released cross-process OS lock; never removed while in use."""
    base = _root()
    locks = base / ".publish-locks"
    locks.mkdir(parents=True, exist_ok=True)
    if locks.is_symlink() or locks.resolve() != locks:
        raise PermissionError("Creative lock directory redirected")
    lock_path = locks / f"{_identifier(project_id)}.lock"
    if lock_path.is_symlink():
        raise PermissionError("Creative project lock redirected")
    flags = os.O_CREAT | os.O_RDWR
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock_path, flags, 0o600)
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def load_creative_head(project_id: str) -> CreativeProjectRevision | None:
    """Validate durable head pointer; for legacy lineages require a unique leaf."""
    project = _root() / _identifier(project_id)
    if not project.exists():
        return None
    if project.is_symlink() or project.resolve() != project:
        raise ValueError("Creative project was redirected")
    head_path = project / "head.json"
    if head_path.exists() or head_path.is_symlink():
        if head_path.is_symlink() or not head_path.is_file() or head_path.stat().st_size > 2048:
            raise ValueError("Invalid Creative head pointer")
        payload = json.loads(head_path.read_bytes())
        if not isinstance(payload, dict) or set(payload) != {"revision_id", "etag", "operation_id"}:
            raise ValueError("Invalid Creative head metadata")
        revision = load_creative_revision(project_id, _identifier(payload["revision_id"]))
        if revision.etag != payload["etag"] or revision.operation_id != payload["operation_id"]:
            raise ValueError("Creative head pointer integrity mismatch")
        return revision

    # Absence of HEAD after ANY revision is not a commit signal. The last
    # manifest might be an orphan written just before a process crashed.
    # Never auto-promote an apparent unique leaf; legacy adoption requires
    # an explicit, independently audited migration.
    revisions_dir = project / "revisions"
    if revisions_dir.exists() or revisions_dir.is_symlink():
        if revisions_dir.is_symlink() or not revisions_dir.is_dir():
            raise ValueError("Creative revisions path redirected")
        if any(revisions_dir.iterdir()):
            raise CreativeConflictError(
                "409 Conflict: legacy or interrupted Creative project without canonical HEAD"
            )
    return None


def _same_payload(revision: CreativeProjectRevision, doc: Any,
                  native_files: dict[str, bytes] | None) -> bool:
    stored = load_creative_document(revision.project_id, revision.revision_id)
    if document_to_dict(stored) != document_to_dict(doc):
        return False
    submitted = {
        name: hashlib.sha256(data).hexdigest()
        for name, data in (native_files or {}).items()
    }
    return submitted == dict(revision.native_files)


def _persist_head(revision: CreativeProjectRevision) -> None:
    project = revision.manifest_path.parent.parent.parent
    head = project / "head.json"
    if head.is_symlink():
        raise ValueError("Creative head redirected")
    temp = project / f".head-{uuid.uuid4().hex}.tmp"
    payload = {
        "revision_id": revision.revision_id,
        "etag": revision.etag,
        "operation_id": revision.operation_id,
    }
    try:
        with temp.open("xb") as stream:
            stream.write(_json_bytes(payload))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, head)
    finally:
        if temp.exists():
            temp.unlink()


def publish_creative_document_cas(
    doc: Any, *, expected_head_revision: str | None = None,
    expected_etag: str | None = None, operation_id: str,
    native_files: dict[str, bytes] | None = None,
) -> CreativeProjectRevision:
    """Serialize concurrent human/agent publications against durable head.

    Historical operation-ID replay is idempotent only if every source byte and
    CreativeDocument field match; stale parents fail without writing a revision.
    This does not yet provide global distributed multi-engine rollback/undo.
    """
    try:
        operation_id = _identifier(operation_id)
    except ValueError as exc:
        raise ValueError("Invalid Creative operation identifier") from exc
    project_id = _identifier(doc.project_id)
    if expected_head_revision is not None:
        _identifier(expected_head_revision)
    with _exclusive_project_lock(project_id):
        latest = load_creative_head(project_id)
        used = _read_operation_receipt(project_id, operation_id)
        if used is not None:
            if not _revision_in_ancestry(latest, used):
                raise CreativeConflictError("409 Conflict: interrupted or foreign operation receipt")
            if _same_payload(used, doc, native_files):
                return used
            raise CreativeConflictError("409 Conflict: reused operation with different payload")
        # Backward compatibility only for HEAD created before operation indexing:
        # a reused head identifier still must never be applied twice.
        if latest and latest.operation_id == operation_id:
            if _same_payload(latest, doc, native_files):
                return latest
            raise CreativeConflictError("409 Conflict: reused operation with different payload")
        if latest:
            if (expected_head_revision != latest.revision_id
                    or expected_etag != latest.etag):
                raise CreativeConflictError("409 Conflict: stale canonical Creative head")
        elif expected_head_revision is not None or expected_etag is not None:
            raise CreativeConflictError("409 Conflict: initial Creative head does not exist")

        committed = save_creative_document(
            doc, parent_revision=latest.revision_id if latest else None,
            if_match=latest.etag if latest else None,
            operation_id=operation_id, native_files=native_files,
        )
        _persist_operation_receipt(committed)
        _persist_head(committed)
        return committed


def _command_digest(tx: Any) -> str:
    """Stable fingerprint of the actual typed commands, independent of timestamps."""
    import json
    from workstation.creative_transactions import CreativeTransaction
    if not isinstance(tx, CreativeTransaction) or not 1 <= len(tx.commands) <= 64:
        raise ValueError("Invalid canonical Creative command batch")
    if tx.expected_revision is not None:
        raise ValueError("Use canonical revision_id/ETag, not a local integer revision")
    entries = []
    for cmd in tx.commands:
        if (not isinstance(cmd.command_id, str) or not cmd.command_id
                or not isinstance(cmd.idempotency_key, str) or not cmd.idempotency_key
                or not isinstance(cmd.params, dict)
                or cmd.actor.actor_type not in {"human_mouse", "hermes_agent", "headless_automation"}
                or not cmd.actor.actor_id):
            raise ValueError("Invalid canonical Creative command")
        entries.append({
            "id": cmd.command_id, "params": cmd.params,
            "actor": cmd.actor.actor_id, "actor_type": cmd.actor.actor_type,
            "idempotency": cmd.idempotency_key,
        })
    try:
        serialized = json.dumps(entries, ensure_ascii=False, sort_keys=True,
                                allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid Creative command serialization") from exc
    if len(serialized) > 131_072:
        raise ValueError("Creative command batch exceeds size bound")
    return hashlib.sha256(b"hermes-creative-commands-v1\0" + serialized).hexdigest()


def publish_creative_command_batch_cas(
    project_id: str, tx: Any, *, expected_head_revision: str,
    expected_etag: str, native_files: dict[str, bytes] | None = None,
) -> CreativeProjectRevision:
    """Single canonical human/agent batch: atomic reducers then HEAD CAS.

    TaskRun admission, authorization, identity assurance and native engine
    staging remain the caller's responsibilities. This is NOT a distributed
    two-engine transaction or persistent undo/redo history.
    """
    from workstation.creative_transactions import CreativeTransaction
    if not isinstance(tx, CreativeTransaction):
        raise ValueError("Invalid CreativeTransaction")
    fingerprint = _command_digest(tx)
    operation_id = _identifier(tx.transaction_id)
    head = load_creative_head(project_id)
    if head is None:
        raise CreativeConflictError("409 Conflict: missing canonical Creative head")
    used = _read_operation_receipt(project_id, operation_id)
    if used is not None:
        if not _revision_in_ancestry(head, used):
            raise CreativeConflictError("409 Conflict: interrupted or foreign batch operation")
        old = load_creative_document(project_id, used.revision_id)
        receipt = old.metadata.get("_hermes_command_receipt")
        if (isinstance(receipt, dict)
                and receipt.get("digest") == fingerprint
                and receipt.get("parent_revision") == expected_head_revision
                and used.parent_revision == expected_head_revision):
            return used
        raise CreativeConflictError("409 Conflict: reused batch operation with different payload")
    if head.operation_id == operation_id:
        prior_doc = load_creative_document(project_id, head.revision_id)
        receipt = prior_doc.metadata.get("_hermes_command_receipt")
        if (isinstance(receipt, dict)
                and receipt.get("digest") == fingerprint
                and receipt.get("parent_revision") == expected_head_revision):
            return head
        raise CreativeConflictError("409 Conflict: reused batch operation with different payload")
    if expected_head_revision != head.revision_id or expected_etag != head.etag:
        raise CreativeConflictError("409 Conflict: stale canonical Creative head")

    # No mutations to the caller's document: operate on a fully loaded clone.
    doc = load_creative_document(project_id, head.revision_id)
    tx.apply(doc)
    doc.metadata["_hermes_command_receipt"] = {
        "digest": fingerprint, "parent_revision": head.revision_id,
        "operation_id": operation_id,
    }
    return publish_creative_document_cas(
        doc, expected_head_revision=head.revision_id, expected_etag=head.etag,
        operation_id=operation_id, native_files=native_files,
    )


def _operation_receipt_path(project_id: str, operation_id: str) -> Path:
    return _root() / _identifier(project_id) / "operations" / f"{_identifier(operation_id)}.json"


def _read_operation_receipt(project_id: str, operation_id: str) -> CreativeProjectRevision | None:
    """Use an O(1) per-operation lookup, validating revision and source hashes."""
    path = _operation_receipt_path(project_id, operation_id)
    parent = path.parent
    if parent.is_symlink():
        raise PermissionError("Creative operation index redirected")
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024:
        raise ValueError("Creative operation receipt missing, redirected or oversized")
    receipt = json.loads(path.read_bytes())
    if (not isinstance(receipt, dict)
            or set(receipt) != {"operation_id", "revision_id", "etag"}
            or receipt["operation_id"] != operation_id):
        raise ValueError("Invalid Creative operation receipt")
    revision = load_creative_revision(project_id, _identifier(receipt["revision_id"]))
    if revision.operation_id != operation_id or revision.etag != receipt["etag"]:
        raise ValueError("Creative operation receipt integrity mismatch")
    return revision


def _revision_in_ancestry(
    latest: CreativeProjectRevision | None, earlier: CreativeProjectRevision,
) -> bool:
    """A completed operation must be an ancestor of the published HEAD."""
    if latest is None:
        return False
    current = latest
    visited: set[str] = set()
    for _ in range(65536):
        if current.revision_id == earlier.revision_id:
            return True
        if current.revision_id in visited:
            raise CreativeConflictError("409 Conflict: Creative revision cycle")
        visited.add(current.revision_id)
        if current.parent_revision is None:
            return False
        current = load_creative_revision(current.project_id, current.parent_revision)
    raise CreativeConflictError("409 Conflict: Creative ancestry verification budget exceeded")


def _persist_operation_receipt(revision: CreativeProjectRevision) -> None:
    """Write durable operation ID BEFORE HEAD; orphan receipts never count as published."""
    path = _operation_receipt_path(revision.project_id, revision.operation_id)
    folder = path.parent
    folder.mkdir(parents=True, exist_ok=True)
    if folder.is_symlink() or folder.resolve() != folder or path.is_symlink():
        raise PermissionError("Creative operation receipt directory redirected")
    receipt = {
        "operation_id": revision.operation_id,
        "revision_id": revision.revision_id,
        "etag": revision.etag,
    }
    try:
        with path.open("xb") as stream:
            stream.write(_json_bytes(receipt))
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise CreativeConflictError("409 Conflict: reused Creative operation ID") from exc
