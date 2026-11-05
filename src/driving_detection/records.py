"""Small file helpers shared by the pipeline commands."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


def workspace_path(value: str | Path) -> Path:
    """Resolve paths from the workspace (commands run from the repository root)."""
    return Path(value).expanduser().resolve()


def load_config(path: Path) -> dict:
    """Read a YAML mapping; each handler validates its own required settings."""
    import yaml

    try:
        settings = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(settings, dict) or any(not isinstance(key, str) for key in settings):
        raise ValueError(f"Config must contain a mapping with string keys: {path}")
    return settings


def sha256_file(path: Path) -> str:
    """Hash the actual file bytes without loading a large asset into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    """Replace a small JSON record atomically; reject nonfinite output numbers."""
    content = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def save_config(path: Path, settings: dict) -> str:
    """Save effective settings and return the SHA-256 of the saved YAML bytes."""
    import yaml

    path.write_text(yaml.safe_dump(settings, sort_keys=True), encoding="utf-8")
    return sha256_file(path)


def create_run_dir(run_id: str) -> Path:
    """Reserve a new run directory, refusing unsafe names and any existing ID."""
    reserved = {"CON", "PRN", "AUX", "NUL"}
    reserved.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10))
    if (
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id)
        or run_id.endswith(".")
        or run_id.split(".")[0].upper() in reserved
    ):
        raise ValueError("Run ID must be a safe name of 1–128 letters/digits/dots/dashes/underscores, starting with a letter or digit.")
    workspace = Path.cwd().resolve()
    runs = workspace_path("artifacts/runs")
    if not runs.is_relative_to(workspace):
        raise ValueError("artifacts/runs must stay inside the workspace.")
    runs.mkdir(parents=True, exist_ok=True)
    run_dir = runs / run_id
    try:
        run_dir.mkdir()
    except FileExistsError as exc:
        raise ValueError(f"Run already exists: {run_dir}. Retry with a new --run-id.") from exc
    return run_dir


def resolve_device(requested: str | None, settings: dict) -> str:
    """Honor the requested/configured device without falling back from CUDA."""
    device = requested if requested is not None else settings.get("device", "cpu")
    if device not in ("cpu", "cuda:0"):
        raise ValueError("Device must be cpu or cuda:0.")
    if device == "cuda:0":
        import torch

        if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
            raise ValueError("Requested device cuda:0 is unavailable. Check the GPU, driver and installed torch build.")
    return device
