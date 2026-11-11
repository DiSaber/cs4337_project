"""D3 training: run the pinned YOLOv5 v7.0 train.py on the prepared train/val export."""

from __future__ import annotations

import csv
import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path

from .assets import _definition, _local_output, _verified, load_model
from .records import load_config, project_revision, sha256_file, workspace_path, write_json

ASSETS_CONFIG = Path("configs/assets.yaml")
CLASS_NAMES = ["car", "pedestrian", "traffic_light"]
REQUIRED = ("label", "weights", "imgsz", "batch", "epochs", "workers", "seed", "budget_gpu_hours", "optimizer", "noautoanchor", "patience", "hyp")
NOMINAL_BATCH = 64  # upstream train.py: nbs = 64
# Runs the unchanged train.py after restoring numpy.trapz, which NumPy 2.4 removed;
# pinned utils/metrics.py still calls it when computing validation AP.
LAUNCHER = (
    "import runpy, sys, numpy; numpy.trapz = numpy.trapezoid; "
    "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')"
)


def _relative(path: Path) -> str:
    return path.resolve().relative_to(Path.cwd().resolve()).as_posix()


def _file(path: Path) -> dict:
    return {"path": _relative(path), "sha256": sha256_file(path)}


def _prepared_data(profile_path: Path, source: Path) -> tuple[Path, dict]:
    """Check the train/val export against the profile hashes; the test split is never passed."""
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    prepared = profile_path.parent
    for name in ("manifest.train.jsonl", "manifest.val.jsonl", "yolo/dataset.yaml"):
        if sha256_file(prepared / name) != profile["exports"][name]:
            raise ValueError(f"{prepared / name} no longer matches {profile_path}; prepare a new profile instead of editing it.")
    dataset_yaml = prepared / "yolo/dataset.yaml"
    dataset = load_config(dataset_yaml)
    if dataset.get("names") != CLASS_NAMES or dataset.get("nc") != 3 or "test" in dataset:
        raise ValueError("dataset.yaml must list only train/val and the three canonical classes.")
    # Upstream resolves a relative dataset path from its own source folder.
    if (source / dataset["path"]).resolve() != (prepared / "yolo").resolve():
        raise ValueError(f"dataset.yaml path does not point at {prepared / 'yolo'} from {source}.")
    record = {
        "profile": _file(profile_path),
        "profile_id": profile["profile_id"],
        "partitions": ["train", "val"],
        "manifests": {name: _file(prepared / f"manifest.{name}.jsonl") for name in ("train", "val")},
        "dataset_yaml": _file(dataset_yaml),
        "yolo_label_trees": {name: profile["exports"][f"yolo/labels/{name}"] for name in ("train", "val")},
        "counts": profile["counts"],
    }
    return dataset_yaml, record


def _environment(device: str) -> dict:
    import torch

    hardware = {"processor": platform.processor() or platform.machine(), "torch_cuda": torch.version.cuda}
    if device == "cuda:0":
        hardware["gpu"] = torch.cuda.get_device_name(0)
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "hardware": hardware,
        "installed": sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()),
    }


def _run_upstream(command: list[str], source: Path, env: dict, log_path: Path, budget_seconds: float) -> tuple[int, bool, float]:
    """Run train.py, copying its output to the console and train.log; stop it at the budget."""
    over_budget = threading.Event()
    started = time.monotonic()
    with log_path.open("wb") as log, subprocess.Popen(command, cwd=source, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:

        def stop() -> None:
            over_budget.set()
            process.kill()

        timer = threading.Timer(budget_seconds, stop)
        timer.start()
        try:
            # read1 returns whatever is available, so tqdm's carriage-return updates stay live.
            while chunk := process.stdout.read1(65536):
                log.write(chunk)
                sys.stdout.buffer.write(chunk)
                sys.stdout.flush()
            returncode = process.wait()
        finally:
            timer.cancel()
            if process.poll() is None:  # Ctrl+C in this process: stop the child too.
                process.kill()
                process.wait()
    return returncode, over_budget.is_set(), time.monotonic() - started


def _history(results_csv: Path) -> list[dict]:
    if not results_csv.is_file():
        return []
    with results_csv.open(newline="", encoding="utf-8") as source:
        # Upstream pads column names and values with spaces.
        return [{key.strip(): float(value) for key, value in row.items()} for row in csv.DictReader(source, skipinitialspace=True)]


def train(args, settings: dict) -> None:
    missing = [key for key in REQUIRED if key not in settings]
    if missing:
        raise ValueError(f"Training config is missing: {', '.join(missing)}")
    if settings["label"] not in ("smoke", "baseline"):
        raise ValueError("label must be smoke or baseline.")
    # These trackers would start automatically if installed and may upload data.
    trackers = [name for name in ("wandb", "clearml", "comet_ml") if importlib.util.find_spec(name)]
    if trackers:
        raise ValueError(f"Uninstall unrequested experiment trackers before training: {', '.join(trackers)}")

    run_dir = args.run_dir
    record_path = run_dir / "run.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    asset_settings = load_config(workspace_path(ASSETS_CONFIG))
    source_receipt = _verified("source", _definition(asset_settings, "source"))
    weights_asset = _definition(asset_settings, "weights")
    weights_receipt = _verified("weights", weights_asset)
    source = _local_output(source_receipt["path"])
    weights = _local_output(weights_asset["path"])
    if workspace_path(settings["weights"]) != weights:
        raise ValueError(f"weights must be the verified initial checkpoint {weights_asset['path']}.")
    dataset_yaml, data_record = _prepared_data(args.profile, source)

    # Upstream reads hyperparameters from a file; keep the exact input beside the run.
    import yaml

    hyp_path = run_dir / "hyp.input.yaml"
    hyp_path.write_text(yaml.safe_dump(settings["hyp"], sort_keys=False), encoding="utf-8")
    command = [
        sys.executable, "-c", LAUNCHER, str(source / "train.py"),
        "--data", str(dataset_yaml),
        "--weights", str(weights),
        "--hyp", str(hyp_path),
        "--epochs", str(settings["epochs"]),
        "--batch-size", str(settings["batch"]),
        "--imgsz", str(settings["imgsz"]),
        "--workers", str(settings["workers"]),
        "--seed", str(settings["seed"]),
        "--optimizer", settings["optimizer"],
        "--patience", str(settings["patience"]),
        "--device", "cpu" if args.device == "cpu" else "0",
        # Write straight into this run directory (it already exists, hence --exist-ok).
        "--project", str(run_dir.parent), "--name", run_dir.name, "--exist-ok",
        # Pinned plotting calls font.getsize, which Pillow 10+ removed; results.csv keeps the history.
        "--noplots",
    ]
    if settings["noautoanchor"]:
        command.append("--noautoanchor")
    config_dir = _local_output("artifacts/yolo-config")
    config_dir.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ,
        YOLOv5_AUTOINSTALL="false",
        YOLOV5_CONFIG_DIR=str(config_dir),
        # torch>=2.6 loads only plain tensors by default; the pinned train.py loads
        # full pickled models (the verified initial weights and its own checkpoints).
        TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD="1",
    )

    batch = settings["batch"]
    accumulate = max(round(NOMINAL_BATCH / batch), 1)
    record.update(
        label=settings["label"],
        reportable_accuracy=settings["label"] == "baseline",
        project_revision=project_revision(),
        model_source={"version": source_receipt["definition"]["version"], "path": source_receipt["path"], "tree_sha256": source_receipt["tree_sha256"]},
        initial_weights={"version": weights_asset["version"], "path": weights_asset["path"], "sha256": weights_receipt["sha256"]},
        data=data_record,
        upstream_command=["python", "-c", "<LAUNCHER>", *(_relative(Path(part)) if Path(part).is_absolute() else part for part in command[3:])],
        effective_batch={
            "batch": batch,
            "nominal_batch": NOMINAL_BATCH,
            "accumulate": accumulate,
            "weight_decay": settings["hyp"]["weight_decay"] * batch * accumulate / NOMINAL_BATCH,
            "note": "Upstream ramps gradient accumulation from 1 to this value during warmup and scales weight decay by batch*accumulate/64.",
        },
        seed={"config": settings["seed"], "upstream_init_seeds": settings["seed"] + 1, "deterministic_requested": True},
        nondeterminism=[
            "Upstream init_seeds(seed+1) seeds Python/NumPy/torch/CUDA and calls torch.use_deterministic_algorithms(True) with cudnn.deterministic.",
            "Results can still differ across GPU models, drivers, CUDA/cuDNN and library versions; workers=0 avoids loader-order differences.",
        ],
        environment=_environment(args.device),
        compatibility=[
            "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 for the upstream process: pinned train.py loads full pickled models.",
            "numpy.trapz = numpy.trapezoid before train.py runs: NumPy 2.4 removed trapz; pinned validation AP still calls it.",
            "--noplots: pinned plotting needs Pillow font.getsize (removed in Pillow 10); history is results.csv.",
            "train.py runs from the source folder, so its GitHub update check finds no .git and is skipped.",
            "Upstream downloads Arial.ttf into artifacts/yolo-config on first use and writes labels/*.cache files beside the prepared YOLO labels.",
        ],
        budget={"gpu_hours": settings["budget_gpu_hours"], "device": args.device},
        log=_relative(run_dir / "train.log"),
    )
    write_json(record_path, record)

    returncode, over_budget, elapsed = _run_upstream(command, source, env, run_dir / "train.log", settings["budget_gpu_hours"] * 3600)
    history = _history(run_dir / "results.csv")
    record["budget"]["elapsed_hours"] = round(elapsed / 3600, 4)
    record["history"] = {"path": _relative(run_dir / "results.csv"), "epochs_completed": len(history)} if history else None
    upstream_files = {name: _file(run_dir / name) for name in ("opt.yaml", "hyp.yaml") if (run_dir / name).is_file()}
    record["upstream_settings"] = upstream_files
    write_json(record_path, record)
    if over_budget:
        raise TimeoutError(f"Training passed the {settings['budget_gpu_hours']}-hour budget after {len(history)} of {settings['epochs']} epochs.")
    if returncode != 0:
        raise RuntimeError(f"Upstream train.py exited with code {returncode}; see {record['log']}.")
    if len(history) != settings["epochs"]:
        raise RuntimeError(f"results.csv has {len(history)} epochs, expected {settings['epochs']}.")

    # Upstream keeps best.pt only when fitness is strictly higher, so the first maximum is the chosen epoch.
    # strip_optimizer resets the epoch inside best.pt, so the epoch comes from results.csv.
    fitness = [0.1 * row["metrics/mAP_0.5"] + 0.9 * row["metrics/mAP_0.5:0.95"] for row in history]
    best_index = fitness.index(max(fitness))
    best_path, last_path = run_dir / "weights/best.pt", run_dir / "weights/last.pt"
    model = load_model(asset_settings, args.device, best_path)
    names = list(model.names.values()) if isinstance(model.names, dict) else list(model.names)
    head_classes = model.model[-1].nc
    if names != CLASS_NAMES or head_classes != len(CLASS_NAMES):
        raise ValueError(f"best.pt has head names {names} and {head_classes} classes; expected {CLASS_NAMES}.")
    record.update(
        checkpoints={"best": _file(best_path), "last": _file(last_path)},
        selection={
            "rule": "Upstream validation fitness 0.1*mAP@0.5 + 0.9*mAP@0.5:0.95; earliest epoch on ties.",
            "epoch": int(history[best_index]["epoch"]),
            "fitness": fitness[best_index],
            "val_map_50": history[best_index]["metrics/mAP_0.5"],
            "val_map_50_95": history[best_index]["metrics/mAP_0.5:0.95"],
            "note": "Upstream validation numbers, not the project evaluator; smoke values are never reported.",
        },
        head={"names": names, "classes": head_classes, "loaded_on": args.device},
    )
    write_json(record_path, record)
    print(f"Training {settings['label']} run completed; chosen epoch {record['selection']['epoch']} saved as {record['checkpoints']['best']['path']}.")
