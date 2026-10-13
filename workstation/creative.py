"""Opt-in Creative CLI; inherits session/profile identity from Hermes, never mints it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from gateway.session_context import get_session_env
from hermes_constants import get_hermes_home
from hermes_cli.config import load_config_readonly
from tools.approval_context import get_current_session_key
from tools.browser_workstation import WorkstationBrowserError
from workstation.config import WorkstationConfig
from workstation.creative_project_runtime import CreativeEffectUncertain, CreativeRunContext, save_project_for_run
from workstation.creative_project_store import load_creative_revision
from workstation.creative_render import render_project_for_run
from workstation.creative_video import CreativeStillVideoRequest, encode_still_video
from workstation.creative_video_process import CreativeVideoEngines


def _execute(args, config, context, workspace):
    def save():
        source_path = args.source.resolve(strict=True)
        if (not source_path.is_file() or not source_path.is_relative_to(workspace)
                or source_path.stat().st_size > 262_144):
            raise PermissionError("Creative input source is outside workspace or oversized")
        return save_project_for_run(config, context, json.loads(source_path.read_bytes()),
                                    project_id=args.project_id, parent_revision=args.parent_revision)

    def inspect():
        revision = load_creative_revision(args.project_id, args.revision_id)
        if not revision.source_path.is_relative_to(workspace):
            raise PermissionError("Creative project is outside TaskRun workspace")
        return {"project_id": revision.project_id, "revision_id": revision.revision_id,
                "source_sha256": revision.source_sha256, "parent_revision": revision.parent_revision,
                "source": json.loads(revision.source_path.read_bytes())}

    def apply_batch():
        # Only the existing canonical TaskRun can deliver this bounded source
        # file. Actor labels are trace metadata, not an authority grant.
        from workstation.creative_commands import Actor, CreativeCommand
        from workstation.creative_transactions import CreativeTransaction
        from workstation.creative_project_runtime import publish_creative_command_batch_for_run

        request = args.commands_file
        if request.is_symlink():
            raise PermissionError("Creative command source redirected")
        request = request.resolve(strict=True)
        if (not request.is_file() or not request.is_relative_to(workspace)
                or request.stat().st_size > 131_072):
            raise PermissionError("Creative command source outside TaskRun or oversized")
        payload = json.loads(request.read_bytes())
        if not isinstance(payload, dict) or set(payload) != {"transaction_id", "commands"}:
            raise ValueError("Invalid Creative command batch envelope")
        raw = payload["commands"]
        if not isinstance(raw, list) or not 1 <= len(raw) <= 64:
            raise ValueError("Invalid Creative command batch length")
        commands = []
        for command in raw:
            if (not isinstance(command, dict)
                    or set(command) != {"command_id", "params", "actor", "idempotency_key"}
                    or not isinstance(command["actor"], dict)
                    or set(command["actor"]) != {"actor_id", "actor_type"}
                    or not isinstance(command["params"], dict)):
                raise ValueError("Invalid Creative typed command")
            commands.append(CreativeCommand(
                command_id=command["command_id"],
                params=command["params"],
                actor=Actor(**command["actor"]),
                idempotency_key=command["idempotency_key"],
            ))
        tx = CreativeTransaction(commands=commands, transaction_id=payload["transaction_id"])
        return publish_creative_command_batch_for_run(
            config, context, project_id=args.project_id, transaction=tx,
            expected_head_revision=args.expected_revision_id, expected_etag=args.if_match,
        )

    def canonical_create():
        from workstation.creative_document import load_document_from_dict
        from workstation.creative_project_runtime import create_canonical_document_for_run

        source_file = args.source
        if source_file.is_symlink():
            raise PermissionError("Creative document source redirected")
        source_file = source_file.resolve(strict=True)
        if (not source_file.is_file() or not source_file.is_relative_to(workspace)
                or source_file.stat().st_size > 262_144):
            raise PermissionError("Creative document outside TaskRun workspace or oversized")
        doc = load_document_from_dict(json.loads(source_file.read_bytes()))
        return create_canonical_document_for_run(config, context, doc)

    def canonical_open():
        from workstation.creative_revision_cas import load_creative_head

        context.validate(config)
        revision = load_creative_head(args.project_id)
        if revision is None or revision.engine != "creative-document":
            raise ValueError("Canonical CreativeDocument HEAD is unavailable")
        if not revision.source_path.is_relative_to(workspace):
            raise PermissionError("Canonical CreativeDocument outside TaskRun workspace")
        return {
            "project_id": revision.project_id, "revision_id": revision.revision_id,
            "parent_revision": revision.parent_revision, "etag": revision.etag,
            "source": json.loads(revision.source_path.read_bytes()),
        }

    handlers = {
        "save": save, "inspect": inspect, "apply-batch": apply_batch,
        "canonical-create": canonical_create, "canonical-open": canonical_open,
        "render": lambda: render_project_for_run(config, context, project_id=args.project_id,
            revision_id=args.revision_id, browser_task_id=args.browser_task_id),
        "video": lambda: encode_still_video(config, context, CreativeStillVideoRequest(
            args.project_id, args.revision_id, str(args.source_png), args.source_sha256,
            args.width, args.height, args.duration_seconds, args.fps), CreativeVideoEngines.from_config(config)),
    }
    return handlers[args.command]()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hermes Creative projects (explicit opt-in required)")
    parser.add_argument("--task-id", required=True, help="Existing canonical Kanban task")
    parser.add_argument("--run-id", required=True, type=int, help="Existing live TaskRun")
    commands = parser.add_subparsers(dest="command", required=True)
    save = commands.add_parser("save", help="Append an editable source revision")
    save.add_argument("--source", required=True, type=Path)
    save.add_argument("--project-id")
    save.add_argument("--parent-revision")
    inspect = commands.add_parser("inspect", help="Read a recorded project revision")
    canonical_create = commands.add_parser("canonical-create", help="Create a canonical CreativeDocument in an admitted TaskRun")
    canonical_create.add_argument("--source", required=True, type=Path)
    canonical_open = commands.add_parser("canonical-open", help="Read the latest canonical HEAD within the owning TaskRun")
    canonical_open.add_argument("--project-id", required=True)
    batch = commands.add_parser("apply-batch", help="Publish a typed command batch via canonical TaskRun and HEAD CAS")
    batch.add_argument("--commands-file", required=True, type=Path)
    batch.add_argument("--project-id", required=True)
    batch.add_argument("--expected-revision-id", required=True)
    batch.add_argument("--if-match", required=True)
    render = commands.add_parser("render", help="Render through an already-owned native BrowserTask")
    video = commands.add_parser("video", help="Encode an owned PNG using explicitly pinned media engines")
    for command in (inspect, render, video):
        command.add_argument("--project-id", required=True)
        command.add_argument("--revision-id", required=True)
    render.add_argument("--browser-task-id", required=True)
    video.add_argument("--source-png", required=True, type=Path)
    video.add_argument("--source-sha256", required=True)
    video.add_argument("--width", required=True, type=int)
    video.add_argument("--height", required=True, type=int)
    video.add_argument("--duration-seconds", default=8, type=int)
    video.add_argument("--fps", default=30, type=int)
    args = parser.parse_args(argv)
    config = WorkstationConfig(load_config_readonly())
    context = CreativeRunContext(str(get_hermes_home()), get_current_session_key(default=""),
                                 get_session_env("HERMES_SESSION_ID", ""), args.task_id, args.run_id)
    try:
        workspace = context.validate(config)
        result = _execute(args, config, context, workspace)
    except (OSError, ValueError, PermissionError, RuntimeError) as error:
        # Do not print external engine/controller text or credentials to the terminal.
        failure = {"success": False, "error_type": type(error).__name__,
                   "retryable": False, "instruction": "Inspect the owner journal before retrying"}
        if isinstance(error, WorkstationBrowserError):
            failure.update(error_code=error.error_code, state_changed=error.state_changed)
        if isinstance(error, CreativeEffectUncertain):
            failure.update(error_code="EFFECT_UNCERTAIN", state_changed=True, operation_id=error.operation_id)
        print(json.dumps(failure), file=sys.stderr)
        return 1
    print(json.dumps({"success": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
