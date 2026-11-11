"""Prepare the frozen three-class BDD100K subset: convert, select, check and export."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import uuid

from .assets import _definition, _local_output, _tree, _verified
from .records import load_config, sha256_file, workspace_path, write_json

PARTITIONS = ("train", "val", "test")


def _relative(path: Path) -> str:
    return path.relative_to(Path.cwd().resolve()).as_posix()


def _check_settings(settings: dict) -> None:
    for key in ("profile_id", "assets", "output", "images", "labels"):
        if not isinstance(settings.get(key), str) or not settings[key]:
            raise ValueError(f"Data config needs {key}.")
    if settings.get("classes") != ["car", "pedestrian", "traffic_light"]:
        raise ValueError("Canonical classes must be [car, pedestrian, traffic_light].")
    if set(settings.get("targets", {}).values()) != set(settings["classes"]):
        raise ValueError("targets must map source categories onto all three canonical classes.")
    for key in ("non_targets", "ignored_regions", "non_box_prefixes"):
        if not isinstance(settings.get(key), list):
            raise ValueError(f"Data config needs a {key} list.")
    selection = settings.get("selection", {})
    if not isinstance(selection.get("key_prefix"), str) or any(
        not isinstance(selection.get(name), int) or selection[name] < 1 for name in PARTITIONS
    ):
        raise ValueError("selection needs key_prefix and positive train/val/test counts.")


def _convert_box(box: dict, width: int, height: int) -> tuple[list[float], list[float], bool]:
    """Turn an inclusive-endpoint source box into a half-open box inside the image."""
    source = [box.get(key) for key in ("x1", "y1", "x2", "y2")]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in source):
        raise ValueError("nonfinite_box")
    x1, y1, x2, y2 = source
    if x2 < x1 or y2 < y1:
        raise ValueError("reversed_box")
    # BDD endpoints are inclusive pixels, so the box covers up to x2 + 1.
    converted = [x1, y1, x2 + 1, y2 + 1]
    clipped = [
        min(max(converted[0], 0), width), min(max(converted[1], 0), height),
        min(max(converted[2], 0), width), min(max(converted[3], 0), height),
    ]
    if clipped[2] <= clipped[0] or clipped[3] <= clipped[1]:
        raise ValueError("empty_box_after_clipping")
    return clipped, source, clipped != converted


def _read_sample(name: str, split: str, label_path: Path, image_path: Path, settings: dict) -> dict:
    """Return an eligible sample, or a record with kind=excluded/quarantined and a reason."""
    from PIL import Image

    rejected = {"sample_id": name, "source_partition": split}
    try:
        record = json.loads(label_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return rejected | {"kind": "quarantined", "reason": "unreadable_annotation"}
    if record.get("name") != name:
        return rejected | {"kind": "quarantined", "reason": "annotation_name_mismatch"}
    frames = record.get("frames")
    if not isinstance(frames, list) or len(frames) != 1 or not isinstance(frames[0].get("objects"), list):
        return rejected | {"kind": "quarantined", "reason": "unexpected_frames"}
    try:
        # Opening reads only the header; selected images are fully decoded later.
        with Image.open(image_path) as image:
            width, height = image.size
    except OSError:
        return rejected | {"kind": "quarantined", "reason": "unreadable_image"}

    targets = settings["targets"]
    class_ids = {name: index for index, name in enumerate(settings["classes"])}
    annotations, non_targets, clipped_count = [], Counter(), 0
    for position, obj in enumerate(frames[0]["objects"]):
        category = obj.get("category")
        attributes = obj.get("attributes") or {}
        if category in settings["ignored_regions"] or attributes.get("crowd"):
            return rejected | {"kind": "excluded", "reason": "ignored_region", "detail": category}
        box = obj.get("box2d")
        if box is None:
            if isinstance(category, str) and category.startswith(tuple(settings["non_box_prefixes"])):
                continue
            return rejected | {"kind": "quarantined", "reason": "unknown_category", "detail": category}
        if category in settings["non_targets"]:
            non_targets[category] += 1
            continue
        if category not in targets:
            return rejected | {"kind": "quarantined", "reason": "unknown_category", "detail": category}
        try:
            bbox, source_bbox, clipped = _convert_box(box, width, height)
        except ValueError as exc:
            return rejected | {"kind": "quarantined", "reason": "invalid_box", "detail": str(exc)}
        clipped_count += clipped
        annotations.append({
            "annotation_id": f"{name}:{position}",
            "class_id": class_ids[targets[category]],
            "bbox_xyxy": bbox,
            "source_category": category,
            "source_bbox_xyxy": source_bbox,
            "clipped": clipped,
            "occluded": attributes.get("occluded"),
            "truncated": attributes.get("truncated"),
        })
    return {
        "sample_id": name,
        "image_path": _relative(image_path),
        "width": width,
        "height": height,
        "source_partition": split,
        # The 100K keyframe archive holds one frame per video, so the file stem is the video ID.
        "sequence_id": name,
        "sequence_provenance": "filename_stem_one_keyframe_per_video",
        "attributes": record.get("attributes") or {},
        "annotations": annotations,
        "non_target_boxes": dict(sorted(non_targets.items())),
        "clipped_boxes": clipped_count,
    }


def _collect(settings: dict) -> tuple[dict, list[dict], Counter]:
    """Read official train/val; return eligible samples by split and rejected records."""
    eligible = {"train": [], "val": []}
    rejected = []
    source_counts = Counter()
    for split in ("train", "val"):
        label_dir = workspace_path(settings["labels"]) / split
        image_dir = workspace_path(settings["images"]) / split
        labels = {path.stem: path for path in label_dir.glob("*.json")}
        images = {path.stem: path for path in image_dir.glob("*.jpg")}
        source_counts[f"{split}_labels"] = len(labels)
        source_counts[f"{split}_images"] = len(images)
        for name in sorted(images.keys() - labels.keys()):
            rejected.append({"sample_id": name, "source_partition": split, "kind": "quarantined", "reason": "missing_annotation"})
        for name in sorted(labels.keys() - images.keys()):
            rejected.append({"sample_id": name, "source_partition": split, "kind": "quarantined", "reason": "missing_image"})
        names = sorted(labels.keys() & images.keys())
        print(f"Reading {len(names)} official {split} samples...", flush=True)
        for count, name in enumerate(names, 1):
            sample = _read_sample(name, split, labels[name], images[name], settings)
            if "kind" in sample:
                rejected.append(sample)
            else:
                sample["image_sha256"] = sha256_file(images[name])
                eligible[split].append(sample)
            if count % 10000 == 0:
                print(f"  {count}/{len(names)}", flush=True)

    # Quarantine anything whose sequence ID or image content appears more than once.
    sequences = Counter(s["sequence_id"] for split in eligible.values() for s in split)
    contents = Counter(s["image_sha256"] for split in eligible.values() for s in split)
    for split in eligible:
        kept = []
        for sample in eligible[split]:
            if sequences[sample["sequence_id"]] > 1:
                reason = "duplicate_sequence"
            elif contents[sample["image_sha256"]] > 1:
                reason = "duplicate_content"
            else:
                kept.append(sample)
                continue
            rejected.append({"sample_id": sample["sample_id"], "source_partition": split, "kind": "quarantined", "reason": reason})
        eligible[split] = kept
    return eligible, rejected, source_counts


def _rank(prefix: str, sequence_id: str) -> tuple[str, str]:
    return hashlib.sha256((prefix + sequence_id).encode("utf-8")).hexdigest(), sequence_id


def _select(eligible: dict, selection: dict) -> dict:
    """Pick sequences by hash rank; fail rather than shrink a partition."""
    ranked = {
        split: sorted(samples, key=lambda s: _rank(selection["key_prefix"], s["sequence_id"]))
        for split, samples in eligible.items()
    }
    needed_val = selection["val"] + selection["test"]
    if len(ranked["train"]) < selection["train"] or len(ranked["val"]) < needed_val:
        raise ValueError(
            f"Not enough eligible samples: train {len(ranked['train'])}/{selection['train']}, "
            f"val {len(ranked['val'])}/{needed_val}. Record a new profile instead of changing the split."
        )
    chosen = {
        "train": ranked["train"][:selection["train"]],
        "val": ranked["val"][:selection["val"]],
        "test": ranked["val"][selection["val"]:needed_val],
    }
    for partition, samples in chosen.items():
        for sample in samples:
            sample["partition"] = partition
        samples.sort(key=lambda s: s["sample_id"])
    return chosen


def _integrity(chosen: dict, selection: dict, classes: list[str]) -> dict:
    """The required checks; any failure stops preparation before outputs are promoted."""
    from PIL import Image

    failures = []
    print("Decoding selected images...", flush=True)
    for samples in chosen.values():
        for sample in samples:
            try:
                with Image.open(sample["image_path"]) as image:
                    image.load()
                    if image.size != (sample["width"], sample["height"]):
                        failures.append(f"{sample['sample_id']}: decoded size differs from header")
            except OSError as exc:
                failures.append(f"{sample['sample_id']}: image does not decode ({exc})")
    counts = {p: len(chosen[p]) for p in PARTITIONS}
    for partition in PARTITIONS:
        if counts[partition] != selection[partition]:
            failures.append(f"{partition} has {counts[partition]} samples, expected {selection[partition]}")
    overlap = {}
    for field in ("sequence_id", "image_sha256"):
        sets = {p: {s[field] for s in chosen[p]} for p in PARTITIONS}
        shared = (sets["train"] & sets["val"]) | (sets["train"] & sets["test"]) | (sets["val"] & sets["test"])
        overlap[field] = len(shared)
        if shared:
            failures.append(f"{len(shared)} {field} values cross partitions")
    coverage = {}
    for partition in PARTITIONS:
        present = {a["class_id"] for s in chosen[partition] for a in s["annotations"]}
        coverage[partition] = [classes[i] for i in sorted(present)]
        if len(present) != len(classes):
            failures.append(f"{partition} is missing classes {sorted(set(classes) - set(coverage[partition]))}")
    if failures:
        raise ValueError("Integrity checks failed:\n  " + "\n  ".join(failures))
    return {"status": "passed", "cross_partition_overlap": overlap, "class_coverage": coverage, "decoded_selected_images": sum(counts.values())}


def _partition_summary(samples: list[dict], classes: list[str]) -> dict:
    boxes, images, non_targets = Counter(), Counter(), Counter()
    for sample in samples:
        present = set()
        for annotation in sample["annotations"]:
            boxes[classes[annotation["class_id"]]] += 1
            present.add(classes[annotation["class_id"]])
        images.update(present)
        non_targets.update(sample["non_target_boxes"])
    return {
        "samples": len(samples),
        "negatives": sum(not s["annotations"] for s in samples),
        "boxes_per_class": {c: boxes[c] for c in classes},
        "images_per_class": {c: images[c] for c in classes},
        "clipped_boxes": sum(s["clipped_boxes"] for s in samples),
        "non_target_boxes": dict(sorted(non_targets.items())),
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    lines = [json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False) for row in rows]
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")


def _write_yolo(stage: Path, final: Path, chosen: dict, classes: list[str], source: Path) -> None:
    """YOLO export for train/val only; the held-out partition never reaches training."""
    for partition in ("train", "val"):
        image_dir = stage / "yolo" / "images" / partition
        label_dir = stage / "yolo" / "labels" / partition
        image_dir.mkdir(parents=True)
        label_dir.mkdir(parents=True)
        for sample in chosen[partition]:
            # YOLO finds labels by swapping /images/ for /labels/, so each image
            # needs a path here; a hard link avoids copying the bytes.
            target = image_dir / f"{sample['sample_id']}.jpg"
            try:
                os.link(sample["image_path"], target)
            except OSError:
                shutil.copyfile(sample["image_path"], target)
            lines = []
            for a in sample["annotations"]:
                x1, y1, x2, y2 = a["bbox_xyxy"]
                w, h = sample["width"], sample["height"]
                lines.append(f"{a['class_id']} {(x1 + x2) / 2 / w:.6f} {(y1 + y2) / 2 / h:.6f} {(x2 - x1) / w:.6f} {(y2 - y1) / h:.6f}\n")
            # An empty label file marks a valid negative image.
            (label_dir / f"{sample['sample_id']}.txt").write_text("".join(lines), encoding="utf-8")
    # YOLOv5 resolves a relative dataset path from its own source directory.
    dataset = {
        "path": Path(os.path.relpath(final / "yolo", source)).as_posix(),
        "train": "images/train",
        "val": "images/val",
        "nc": len(classes),
        "names": classes,
    }
    import yaml

    (stage / "yolo" / "dataset.yaml").write_text(yaml.safe_dump(dataset, sort_keys=False), encoding="utf-8")


def _coco(samples: list[dict], classes: list[str]) -> dict:
    images, annotations = [], []
    for image_id, sample in enumerate(samples, 1):
        images.append({"id": image_id, "sample_id": sample["sample_id"], "file_name": sample["image_path"], "width": sample["width"], "height": sample["height"]})
        for a in sample["annotations"]:
            x1, y1, x2, y2 = a["bbox_xyxy"]
            annotations.append({
                "id": len(annotations) + 1, "image_id": image_id, "category_id": a["class_id"] + 1,
                "bbox": [x1, y1, x2 - x1, y2 - y1], "area": (x2 - x1) * (y2 - y1), "iscrowd": 0,
                "annotation_id": a["annotation_id"],
            })
    categories = [{"id": i + 1, "name": name} for i, name in enumerate(classes)]
    return {"images": images, "annotations": annotations, "categories": categories}


def _export_hashes(stage: Path) -> dict:
    hashes = {}
    for name in [*(f"manifest.{p}.jsonl" for p in PARTITIONS), "quarantine.jsonl", "coco.val.json", "coco.test.json", "yolo/dataset.yaml"]:
        hashes[name] = sha256_file(stage / name)
    for partition in ("train", "val"):
        tree, count = _tree(stage / "yolo" / "labels" / partition)
        hashes[f"yolo/labels/{partition}"] = {"tree_sha256": tree, "files": count}
    return hashes


def prepare(args, settings: dict) -> None:
    _check_settings(settings)
    classes = settings["classes"]
    output = _local_output(settings["output"])
    asset_settings = load_config(workspace_path(settings["assets"]))
    print("Checking image and label assets against their receipts (file count and size)...", flush=True)
    assets = {}
    for name in ("images", "labels"):
        receipt = _verified(name, _definition(asset_settings, name))
        assets[name] = {k: receipt.get(k) for k in ("path", "sha256", "tree_sha256", "file_count")}
        assets[name]["version"] = receipt["definition"]["version"]
    source = _local_output(_definition(asset_settings, "source")["path"])

    eligible, rejected, source_counts = _collect(settings)
    chosen = _select(eligible, settings["selection"])
    integrity = _integrity(chosen, settings["selection"], classes)

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = _local_output(str(output.parent / f".{output.name}-stage-{uuid.uuid4().hex}"))
    stage.mkdir()
    try:
        for partition in PARTITIONS:
            _write_jsonl(stage / f"manifest.{partition}.jsonl", chosen[partition])
        rejected.sort(key=lambda r: (r["source_partition"], r["sample_id"]))
        _write_jsonl(stage / "quarantine.jsonl", rejected)
        for partition in ("val", "test"):
            write_json(stage / f"coco.{partition}.json", _coco(chosen[partition], classes))
        _write_yolo(stage, output, chosen, classes, source)
        exports = _export_hashes(stage)

        rejected_counts = Counter(f"{r['source_partition']}:{r['kind']}:{r['reason']}" for r in rejected)
        profile = {
            "profile_id": settings["profile_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "label_release": assets["labels"]["version"],
            "assets": assets,
            "settings": settings,
            "class_ids": {name: i for i, name in enumerate(classes)},
            "coco_category_ids": {name: i + 1 for i, name in enumerate(classes)},
            "rules": {
                "geometry": "Inclusive source xyxy -> half-open [x1, y1, x2+1, y2+1], clipped to the decoded image; empty or invalid boxes quarantine the sample.",
                "sequence_identity": "Full filename stem (one keyframe per source video in the 100K archive).",
                "negatives": "Images with no target boxes are kept with annotations=[] and empty YOLO label files.",
                "ignored_regions": "Images containing an ignored-region category or crowd box are excluded whole.",
                "selection": "Rank eligible sequences by SHA256(key_prefix + sequence ID), ties by ID; first train from official train; first val then next test from official val.",
                "holdout": "Project held-out subset of official labeled val; not the official BDD test benchmark.",
            },
            "counts": {
                "source": dict(source_counts),
                "eligible": {split: len(samples) for split, samples in eligible.items()},
                "rejected": dict(sorted(rejected_counts.items())),
                "requested": {p: settings["selection"][p] for p in PARTITIONS},
                "partitions": {p: _partition_summary(chosen[p], classes) for p in PARTITIONS},
            },
            "integrity": integrity,
            "exports": exports,
        }

        if output.exists():
            previous = json.loads((output / "profile.json").read_text(encoding="utf-8"))
            if previous.get("exports") != exports or previous.get("settings") != settings or previous.get("assets") != assets:
                raise ValueError(f"{_relative(output)} already holds a different frozen profile. Use a new profile_id and output; never overwrite reported membership.")
            print(f"Reusing identical frozen profile: {_relative(output)}")
            return
        write_json(stage / "profile.json", profile)
        stage.rename(output)
        stage = None
    finally:
        if stage is not None and stage.exists():
            # Removes the staging links/copies only; raw images are untouched.
            shutil.rmtree(stage)

    for partition in PARTITIONS:
        summary = profile["counts"]["partitions"][partition]
        print(f"{partition}: {summary['samples']} samples, {summary['negatives']} negatives, boxes {summary['boxes_per_class']}")
    print(f"Rejected: {dict(rejected_counts)}")
    print(f"Integrity checks passed. Frozen profile: {_relative(output / 'profile.json')}")
