"""Command-line entry point; model dependencies load only when needed."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
import sys

from .records import (
    create_run_dir,
    load_config,
    resolve_device,
    save_config,
    workspace_path,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Driving-scene object detection pipeline.")
    commands = parser.add_subparsers(dest="command", required=True)

    assets = commands.add_parser("assets", help="Acquire and verify external assets.")
    sync = assets.add_subparsers(dest="action", required=True).add_parser("sync", help="Reuse, download or import verified assets.")
    sync.add_argument("--config", required=True, type=Path)
    sync.add_argument("--images-archive", type=Path)
    sync.add_argument("--labels-archive", type=Path)
    sync.add_argument("--only", choices=("model",))

    check = commands.add_parser("check", help="Check model, environment and device readiness.")
    check.add_argument("--config", required=True, type=Path)
    check.add_argument("--device", choices=("cpu", "cuda:0"))

    data = commands.add_parser("data", help="Prepare the frozen dataset.")
    prepare = data.add_subparsers(dest="action", required=True).add_parser("prepare", help="Convert, select, validate and export data.")
    prepare.add_argument("--config", required=True, type=Path)

    train = commands.add_parser("train", help="Train a reproducible baseline.")
    train.add_argument("--profile", required=True, type=Path)

    infer = commands.add_parser("infer", help="Predict and annotate images or prerecorded video.")
    infer.add_argument("--model", required=True, type=Path)
    infer.add_argument("--input", required=True, type=Path)
    infer.add_argument("--reference-coco", action="store_true")

    evaluate = commands.add_parser("evaluate", help="Evaluate accuracy and inference speed.")
    evaluate.add_argument("--model", required=True, type=Path)
    evaluate.add_argument("--profile", required=True, type=Path)
    evaluate.add_argument("--partition", choices=("val", "test"), default="val")
    evaluate.add_argument("--selection", type=Path)

    for command in (train, infer, evaluate):
        command.add_argument("--config", required=True, type=Path)
        command.add_argument("--run-id", required=True)
        command.add_argument("--device", choices=("cpu", "cuda:0"))
    return parser


def _load_handler(args: argparse.Namespace):
    # Explicit dispatch keeps the six component owners visible without a registry.
    if args.command == "assets":
        module_name, function_name = "assets", "sync"
    elif args.command == "check":
        module_name, function_name = "assets", "check"
    elif args.command == "data":
        module_name, function_name = "data", "prepare"
    else:
        module_name = function_name = args.command
    qualified_name = f"driving_detection.{module_name}"
    try:
        module = import_module(qualified_name)
    except ModuleNotFoundError as exc:
        if exc.name != qualified_name:
            raise
        raise NotImplementedError(f"{args.command} is not implemented yet; its handler belongs to a later task.") from exc
    return getattr(module, function_name)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(arguments)
    if args.command == "evaluate" and args.partition == "test" and args.selection is None:
        parser.error("--partition test requires --selection PATH")

    run_dir = None
    record = None
    exit_code = 0
    try:
        # A missing handler fails before reading configs or creating output directories.
        handler = _load_handler(args)
        for name, value in vars(args).items():
            if isinstance(value, Path):
                setattr(args, name, workspace_path(value))
        if hasattr(args, "run_id"):
            run_dir = args.run_dir = create_run_dir(args.run_id)
            record = {
                "id": args.run_id,
                "kind": args.command,
                "status": "started",
                "started_at": _timestamp(),
                "command": ["driving-detection", *arguments],
            }
            write_json(run_dir / "run.json", record)
        settings = load_config(args.config)
        if hasattr(args, "device"):
            args.device = resolve_device(args.device, settings)
            settings["device"] = args.device
        if run_dir is not None:
            config_path = run_dir / "resolved-config.yaml"
            record["config_path"] = config_path.relative_to(Path.cwd().resolve()).as_posix()
            record["config_sha256"] = save_config(config_path, settings)
            write_json(run_dir / "run.json", record)
        # Handlers consume args/settings, write their domain outputs and raise on
        # partial processing. They may add domain fields to the existing run.json.
        handler(args, settings)
        status, reason = "completed", None
    except KeyboardInterrupt:
        status, reason, exit_code = "interrupted", "Interrupted by user.", 130
    except Exception as exc:
        status, reason, exit_code = "failed", f"{type(exc).__name__}: {exc}", 1

    if record is not None:
        try:
            path = run_dir / "run.json"
            # Preserve fields written by the component handler.
            import json

            saved = json.loads(path.read_text(encoding="utf-8"))
            saved.update(status=status, finished_at=_timestamp())
            if reason is not None:
                saved["failure_reason"] = reason
            write_json(path, saved)
        except Exception as exc:
            print(f"Error saving run status: {exc}", file=sys.stderr)
            exit_code = exit_code or 1
    if reason is not None:
        print(f"Error: {reason}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
