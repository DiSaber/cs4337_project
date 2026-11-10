"""Verified local asset setup and model readiness; no implicit model downloads."""

from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import sys
from types import SimpleNamespace
import uuid
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile

from .records import sha256_file, workspace_path, write_json


def _relative(path: Path) -> str:
    return path.relative_to(Path.cwd().resolve()).as_posix()


def _local_output(value: str) -> Path:
    path = workspace_path(value)
    root = Path.cwd().resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError("Asset outputs must stay inside the workspace.")
    if path.relative_to(root).parts[0] not in ("data", "external", "artifacts"):
        raise ValueError("Asset outputs must be under data/, external/ or artifacts/.")
    return path


def _definition(settings: dict, name: str) -> dict:
    asset = settings["assets"][name]
    if asset.get("kind") not in ("file", "zip"):
        raise ValueError(f"Invalid asset kind: {name}")
    for key in ("version", "path", "terms"):
        if not isinstance(asset.get(key), str) or not asset[key]:
            raise ValueError(f"Asset {name} needs {key}.")
    _local_output(asset["path"])
    for key, length in (("md5", 32), ("sha256", 64)):
        digest = asset.get(key)
        if digest is not None and (not isinstance(digest, str) or len(digest) != length or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError(f"Invalid {key} checksum for {name}.")
    if asset.get("url"):
        url = urlsplit(asset["url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("Use public HTTPS URLs without credentials or signed query strings.")
    if not isinstance(asset.get("expected"), list):
        raise ValueError(f"Asset {name} needs expected members.")
    return asset


def _checksum(path: Path, asset: dict) -> str:
    observed = sha256_file(path)
    if asset.get("sha256") and observed != asset["sha256"]:
        raise ValueError(f"SHA-256 mismatch for {path.name}; preserve the file and obtain the correct source version.")
    if asset.get("md5"):
        digest = hashlib.md5(usedforsecurity=False)
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != asset["md5"]:
            raise ValueError(f"Publisher MD5 mismatch for {path.name}; expected the declared archive release.")
    return observed


def _member_path(value: str) -> PurePosixPath:
    member = PurePosixPath(value)
    if (
        member.is_absolute() or not member.parts or ".." in member.parts
        or "\\" in value or any(":" in part for part in member.parts)
        or any(part.endswith((".", " ")) for part in member.parts)
        or any(part.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10))} for part in member.parts)
    ):
        raise ValueError("Unsafe archive member path.")
    return member


def _extract(archive: Path, destination: Path, asset: dict) -> None:
    """Validate all ZIP names/types before writing any member into staging."""
    prefix = asset.get("strip_prefix", "")
    prefix_parts = _member_path(prefix).parts if prefix else ()
    with zipfile.ZipFile(archive) as source:
        members = []
        seen = set()
        for info in source.infolist():
            # ZipInfo normalizes Windows backslashes in filename; inspect the
            # original header value so ambiguous input cannot bypass validation.
            path = _member_path(info.orig_filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
                raise ValueError("Archive links/special files are not supported.")
            if prefix_parts and path.parts[:len(prefix_parts)] != prefix_parts:
                raise ValueError("Archive source root differs from the configured source/version.")
            parts = path.parts[len(prefix_parts):]
            if not parts:
                continue
            target = destination.joinpath(*parts)
            identity = str(target).casefold()
            if identity in seen:
                raise ValueError("Duplicate/case-colliding archive member.")
            seen.add(identity)
            members.append((info, target))
        for info, target in members:
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(info) as stream, target.open("xb") as output:
                    shutil.copyfileobj(stream, output)
    _expected(destination, asset)


def _expected(path: Path, asset: dict) -> None:
    for member in asset["expected"]:
        expected = path.joinpath(*_member_path(member).parts)
        if not expected.exists() or (expected.is_dir() and not any(expected.iterdir())):
            raise ValueError(f"Missing/empty expected member: {member}")


def _tree(path: Path) -> tuple[str, int]:
    """Content inventory for extracted files; caches never enter asset identity."""
    digest = hashlib.sha256()
    count = 0
    for entry in sorted(path.rglob("*")):
        if entry.is_symlink():
            raise ValueError("Asset directory contains a symbolic link.")
        if "__pycache__" in entry.parts or entry.suffix == ".pyc":
            continue
        if entry.is_file():
            name = entry.relative_to(path).as_posix()
            digest.update(name.encode("utf-8") + b"\0" + bytes.fromhex(sha256_file(entry)))
            count += 1
    return digest.hexdigest(), count


def _receipt_path(name: str) -> Path:
    return _local_output(f"artifacts/asset-receipts/{name}.json")


def _verified(name: str, asset: dict) -> dict:
    path = _local_output(asset["path"])
    receipt_path = _receipt_path(name)
    if not path.exists() or not receipt_path.is_file():
        raise ValueError(f"{name} is not verified; run assets sync. Existing unverified outputs must be moved aside manually.")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["definition"] != asset:
        raise ValueError(f"{name} source/config changed; use a new destination and preserve earlier assets.")
    if asset["kind"] == "file":
        if _checksum(path, asset) != receipt["sha256"]:
            raise ValueError(f"{name} content changed; preserve it and recover the original asset.")
    else:
        _expected(path, asset)
        tree_hash, count = _tree(path)
        if tree_hash != receipt["tree_sha256"] or count != receipt["file_count"]:
            raise ValueError(f"{name} extracted content changed; preserve it and recover the original asset.")
    return receipt


def _download(name: str, asset: dict) -> Path:
    if not asset.get("url"):
        raise ValueError(f"{name} requires an authorized local archive. Read docs/references.md and supply --{name}-archive PATH; no access credentials belong in config.")
    cache = _local_output(f"external/downloads/{name}{'.zip' if asset['kind'] == 'zip' else '.pt'}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        _checksum(cache, asset)
        return cache
    partial = cache.with_suffix(cache.suffix + ".part")
    print(f"Downloading {name} from its configured public source...", flush=True)
    try:
        with urlopen(Request(asset["url"], headers={"User-Agent": "cs4337-driving-detection/0.1"}), timeout=60) as response, partial.open("wb") as output:
            expected = response.headers.get("Content-Length")
            received = 0
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                received += len(chunk)
            if expected is not None and received != int(expected):
                raise ValueError("Download ended before its declared length.")
    except Exception as exc:
        raise RuntimeError(f"Download failed for {name} ({type(exc).__name__}); retry sync or consult docs/references.md for authorized local inputs.") from None
    _checksum(partial, asset)
    partial.replace(cache)
    return cache


def _sync_one(name: str, asset: dict, local_archive: Path | None) -> dict:
    destination = _local_output(asset["path"])
    if destination.exists():
        receipt = _verified(name, asset)
        if local_archive is not None and _checksum(local_archive, asset) != receipt["sha256"]:
            raise ValueError(f"Different local archive supplied for existing {name}; use a new destination.")
        print(f"Reusing verified {name}: {asset['path']}")
        return receipt
    if local_archive is not None and not (asset.get("sha256") or asset.get("md5")):
        raise ValueError(f"Local {name} inputs require an expected checksum to verify source identity.")
    archive = local_archive if local_archive is not None else _download(name, asset)
    observed = _checksum(archive, asset)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Staging is created under the destination parent, so promotion stays on one volume.
    with _staging(destination.parent, name) as temp:
        staged = temp / "payload"
        receipt = {"definition": asset, "path": asset["path"], "sha256": observed, "status": "verified"}
        if asset["kind"] == "zip":
            staged.mkdir()
            _extract(archive, staged, asset)
            receipt["tree_sha256"], receipt["file_count"] = _tree(staged)
        else:
            shutil.copyfile(archive, staged)
        if destination.exists():
            raise ValueError(f"Destination appeared during setup: {destination}")
        staged.rename(destination)
    receipt_path = _receipt_path(name)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(receipt_path, receipt)
    print(f"Verified {name}: {asset['path']}")
    return receipt


@contextmanager
def _staging(parent: Path, name: str):
    # Normal mkdir inherits the parent's Windows ACL. Python 3.14's private
    # TemporaryDirectory ACL would survive rename and restrict the promoted asset.
    stage = _local_output(str(parent / f".{name}-stage-{uuid.uuid4().hex}"))
    stage.mkdir()
    try:
        yield stage
    finally:
        if stage.is_symlink() or stage.resolve().parent != parent.resolve():
            raise ValueError("Staging path changed; refusing cleanup.")
        shutil.rmtree(stage)


def sync(args, settings: dict) -> None:
    inventory_path = _local_output(settings["inventory"])
    inventory = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else {"assets": {}}
    names = ("source", "weights") if args.only == "model" else ("source", "weights", "images", "labels")
    for name in names:
        asset = _definition(settings, name)
        local_archive = getattr(args, f"{name}_archive", None)
        try:
            receipt = _sync_one(name, asset, local_archive)
            inventory["assets"][name] = receipt
        except (Exception, KeyboardInterrupt) as exc:
            inventory["assets"][name] = {"status": "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed", "path": asset["path"], "reason": type(exc).__name__}
            raise
        finally:
            inventory_path.parent.mkdir(parents=True, exist_ok=True)
            inventory["updated_at"] = datetime.now(timezone.utc).isoformat()
            write_json(inventory_path, inventory)


def load_reference_model(settings: dict, device: str):
    """Load only the verified official checkpoint; keep upstream source unchanged."""
    import functools
    import torch

    source_asset = _definition(settings, "source")
    weight_asset = _definition(settings, "weights")
    _verified("source", source_asset)
    _verified("weights", weight_asset)
    source = _local_output(source_asset["path"])
    weights = _local_output(weight_asset["path"])
    os.environ["YOLOv5_AUTOINSTALL"] = "false"
    os.environ["YOLOV5_CONFIG_DIR"] = str(_local_output("artifacts/yolo-config"))
    Path(os.environ["YOLOV5_CONFIG_DIR"]).mkdir(parents=True, exist_ok=True)
    # The pinned loader serializes a full nn.Module. Scope the legacy loading
    # behavior to the verified official asset instead of changing torch globally.
    sys.path.insert(0, str(source))
    try:
        experimental = importlib.import_module("models.experimental")
        if not Path(experimental.__file__).resolve().is_relative_to(source):
            raise ValueError("A different models module is already imported; use a fresh process.")
        # Initialize yolo before changing experimental.torch: its pinned wildcard
        # import from experimental would otherwise copy the temporary adapter.
        importlib.import_module("models.yolo")
        original_load = torch.load
        original_torch = experimental.torch
        experimental.torch = SimpleNamespace(
            load=functools.partial(original_load, weights_only=False),
            tensor=torch.tensor, zeros=torch.zeros, argmax=torch.argmax,
        )
        try:
            model = experimental.attempt_load(str(weights), device=torch.device(device), fuse=False)
        finally:
            experimental.torch = original_torch
        _pillow_compatibility()
        return model
    finally:
        sys.path.remove(str(source))


def _font_size(font, text, *args, **kwargs):
    left, top, right, bottom = font.getbbox(text, *args, **kwargs)
    return right - left, bottom


def _pillow_compatibility() -> None:
    # v7.0 calls getsize on fonts; Pillow >=10 exposes getbbox instead. Restore
    # only this removed method, preserving old height semantics including top offset.
    from PIL import ImageFont

    for font_type in (ImageFont.FreeTypeFont, ImageFont.ImageFont):
        if not hasattr(font_type, "getsize"):
            font_type.getsize = _font_size


def check(args, settings: dict) -> None:
    inventory_path = _local_output(settings["inventory"])
    inventory = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else {"assets": {}}
    report = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "device": args.device, "status": "failed"}
    try:
        if not (3, 10) <= sys.version_info[:2] < (3, 15):
            raise ValueError("Python 3.10–3.14 is required.")
        versions = {}
        for package, module in (("torch", "torch"), ("torchvision", "torchvision"), ("numpy", "numpy"), ("Pillow", "PIL"), ("opencv-python", "cv2"), ("PyYAML", "yaml"), ("pycocotools", "pycocotools.coco")):
            importlib.import_module(module)
            versions[package] = importlib.metadata.version(package)
        report["versions"] = versions
        import torch

        # Real allocation catches device/runtime errors beyond is_available().
        torch.zeros(1, device=args.device)
        from torchvision.ops import nms

        nms(torch.tensor([[0., 0., 1., 1.]], device=args.device), torch.tensor([1.], device=args.device), 0.5)
        report["hardware"] = {"processor": platform.processor(), "torch_cuda": torch.version.cuda}
        if args.device == "cuda:0":
            report["hardware"]["gpu"] = torch.cuda.get_device_name(0)
        model = load_reference_model(settings, args.device)
        names = model.names
        if len(names) != 80 or names[0] != "person" or names[2] != "car" or names[9] != "traffic light":
            raise ValueError("Official reference checkpoint has an unexpected class head.")
        report["reference_classes"] = len(names)
        report["compatibility"] = ["Verified official checkpoint loaded with explicit weights_only=False; upstream files unchanged.", "Removed Pillow font.getsize restored via getbbox for pinned YOLO plotting."]
        report["datasets"] = {}
        for name in ("images", "labels"):
            try:
                inventory["assets"][name] = _verified(name, _definition(settings, name))
                report["datasets"][name] = "verified"
            except ValueError as exc:
                report["datasets"][name] = str(exc)
        report["installed"] = sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions())
        report["status"] = "completed"
        print(f"Model ready on {args.device}; official 80-class reference checkpoint loaded.")
        print("Dataset readiness (separate): " + json.dumps(report["datasets"]))
    except Exception as exc:
        report["reason"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory["readiness"] = report
        inventory["updated_at"] = datetime.now(timezone.utc).isoformat()
        write_json(inventory_path, inventory)
