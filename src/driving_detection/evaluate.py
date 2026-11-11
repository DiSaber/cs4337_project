"""D5 evaluation: COCO AP, a fixed precision/recall point and one timing measurement."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

from .infer import REQUIRED, _environment, _relative, detect, load_detector, model_record, read_image
from .records import project_revision, sha256_file, write_json
from .train import CLASS_NAMES

# Fixed operating point for precision/recall (contracts/pipeline.md).
PR_TOP_K = 100
PR_SCORE = 0.25
PR_IOU = 0.5
TIMING_SAMPLES = 100
TIMING_WARMUP = 10
TIMING_MINIMUM = 10


def _inputs(profile_path: Path, partition: str) -> tuple[list[dict], dict, dict]:
    """Load the manifest and COCO ground truth after checking them against the profile."""
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    prepared = profile_path.parent
    manifest_path, coco_path = prepared / f"manifest.{partition}.jsonl", prepared / f"coco.{partition}.json"
    for path in (manifest_path, coco_path):
        if sha256_file(path) != profile["exports"][path.name]:
            raise ValueError(f"{path} no longer matches {profile_path}; prepare a new profile instead of editing it.")
    samples = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines()]
    coco = json.loads(coco_path.read_text(encoding="utf-8"))
    expected = profile["counts"]["partitions"][partition]["samples"]
    sample_ids = [sample["sample_id"] for sample in samples]
    if len(samples) != expected or sorted(image["sample_id"] for image in coco["images"]) != sorted(sample_ids):
        raise ValueError(f"Manifest has {len(samples)} samples and COCO {len(coco['images'])} images; the profile expects {expected} of the same samples.")
    if [category["name"] for category in sorted(coco["categories"], key=lambda c: c["id"])] != CLASS_NAMES:
        raise ValueError(f"COCO categories must be {CLASS_NAMES} with IDs 1–3.")
    record = {
        "profile": {"path": _relative(profile_path), "sha256": sha256_file(profile_path), "id": profile["profile_id"]},
        "partition": partition,
        "manifest": {"path": _relative(manifest_path), "sha256": sha256_file(manifest_path)},
        "ground_truth": {"path": _relative(coco_path), "sha256": sha256_file(coco_path)},
    }
    return samples, coco, record


def _coco_ap(coco: dict, detections: list[dict]) -> tuple[dict, dict]:
    """Run pycocotools bbox evaluation. Returns aggregate and per-class AP; undefined values are null."""
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    if not detections:
        reason = "No predictions at or above the score floor."
        empty = {"map_50": None, "map_50_95": None, "reason": reason}
        return empty, {name: dict(empty) for name in CLASS_NAMES}
    ground_truth = COCO()
    ground_truth.dataset = coco
    ground_truth.createIndex()
    evaluation = COCOeval(ground_truth, ground_truth.loadRes(detections), "bbox")
    # Defaults are the contract: IoU 0.50:0.05:0.95, 101 recall points, all/small/medium/large, maxDets 1/10/100.
    evaluation.params.imgIds = sorted(image["id"] for image in coco["images"])  # include negatives
    evaluation.evaluate()
    evaluation.accumulate()
    evaluation.summarize()

    def value(number: float) -> tuple[float | None, str | None]:
        # pycocotools uses -1 when a value is undefined (no ground truth for it).
        return (None, "No ground truth for this value.") if number < 0 else (float(number), None)

    aggregate = {}
    for key, number in (("map_50_95", evaluation.stats[0]), ("map_50", evaluation.stats[1])):
        aggregate[key], reason = value(number)
        if reason:
            aggregate[f"{key}_reason"] = reason
    # precision[iou, recall, class, area=all, maxDets=100]
    precision = evaluation.eval["precision"][:, :, :, 0, 2]
    per_class = {}
    for index, name in enumerate(CLASS_NAMES):
        values = precision[:, :, index]
        result = {}
        result["map_50_95"], reason_95 = value(values[values > -1].mean() if (values > -1).any() else -1)
        at_50 = values[0]
        result["map_50"], reason_50 = value(at_50[at_50 > -1].mean() if (at_50 > -1).any() else -1)
        if reason_95 or reason_50:
            result["reason"] = reason_95 or reason_50
        per_class[name] = result
    return aggregate, per_class


def _iou(a: list[float], b: list[float]) -> float:
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    if width <= 0 or height <= 0:
        return 0.0
    overlap = width * height
    return overlap / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - overlap)


def match_image(predictions: list[dict], truths: list[dict]) -> dict:
    """Greedy matching at the fixed operating point for one image.

    Keep the top 100 predictions, then those with score >= 0.25. In descending score
    order (ties by class, then box), each prediction takes the unmatched ground-truth
    box of its class with the highest IoU >= 0.5 (IoU ties by annotation ID).
    Returns per-class TP/FP/FN counts.
    """
    ranked = sorted(predictions, key=lambda p: (-p["score"], p["class_id"], p["bbox_xyxy"]))[:PR_TOP_K]
    counts = {class_id: {"tp": 0, "fp": 0, "fn": 0} for class_id in range(len(CLASS_NAMES))}
    unmatched = sorted(truths, key=lambda t: t["annotation_id"])
    for prediction in ranked:
        if prediction["score"] < PR_SCORE:
            continue
        best, best_iou = None, PR_IOU
        for truth in unmatched:
            if truth["class_id"] != prediction["class_id"]:
                continue
            overlap = _iou(prediction["bbox_xyxy"], truth["bbox_xyxy"])
            if overlap > best_iou or (overlap == best_iou and best is None):
                best, best_iou = truth, overlap
        if best is None:
            counts[prediction["class_id"]]["fp"] += 1
        else:
            unmatched.remove(best)
            counts[prediction["class_id"]]["tp"] += 1
    for truth in unmatched:
        counts[truth["class_id"]]["fn"] += 1
    return counts


def _precision_recall(tp: int, fp: int, fn: int) -> dict:
    result = {"tp": tp, "fp": fp, "fn": fn,
              "precision": tp / (tp + fp) if tp + fp else None,
              "recall": tp / (tp + fn) if tp + fn else None}
    if result["precision"] is None:
        result["precision_reason"] = "No predictions at the operating point (TP+FP=0)."
    if result["recall"] is None:
        result["recall_reason"] = "No ground-truth boxes (TP+FN=0)."
    return result


def _cpu_name() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
            for line in cpuinfo:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def _timing(model, head: dict, samples: list[dict], settings: dict, device: str) -> dict:
    """Time preprocessing through NMS on the first samples, with decoding done beforehand."""
    import torch

    chosen = samples[:TIMING_SAMPLES]
    ids = [sample["sample_id"] for sample in chosen]
    record = {
        "device": device, "hardware": _environment(device).get("gpu", _cpu_name()), "cpu_threads": torch.get_num_threads(),
        "precision": settings["precision"],
        "input_size": settings["imgsz"], "batch": 1, "samples": len(chosen),
        "sample_list_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "sample_rule": f"First {TIMING_SAMPLES} samples in manifest order.", "warmup": TIMING_WARMUP,
        "included": "letterbox, BGR-to-RGB and normalization, transfer to the device, forward pass, NMS, "
                    "mapping boxes back to original pixels and converting them to Python values",
        "excluded": "reading and decoding image files, drawing, encoding, writing outputs",
    }
    if len(chosen) < TIMING_MINIMUM:
        return {**record, "elapsed_s": None, "mean_ms": None, "images_per_s": None,
                "reason": f"Only {len(chosen)} samples; timing needs at least {TIMING_MINIMUM}."}
    images = [read_image(Path(sample["image_path"]))[0] for sample in chosen]
    for index in range(TIMING_WARMUP):
        detect(model, head, images[index % len(images)], settings, device)
    if device == "cuda:0":
        torch.cuda.synchronize()
    started = time.perf_counter()
    for image in images:
        detect(model, head, image, settings, device)
    if device == "cuda:0":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    return {**record, "elapsed_s": elapsed, "mean_ms": 1000 * elapsed / len(images), "images_per_s": len(images) / elapsed}


def evaluate(args, settings: dict) -> None:
    missing = [key for key in REQUIRED if key not in settings]
    if missing:
        raise ValueError(f"Evaluation config is missing: {', '.join(missing)}")
    if settings["precision"] != "fp32":
        raise ValueError("Only precision fp32 is supported.")
    if args.partition == "test":
        # AI: T024 adds the --selection checks; until then test images are never read.
        raise ValueError("Test evaluation needs the selection checks from T024, which are not implemented yet.")

    run_dir = args.run_dir
    record_path = run_dir / "run.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    samples, coco, data_record = _inputs(args.profile, args.partition)
    model, head = load_detector(args.model, args.device, reference_coco=False)
    record.update(project_revision=project_revision(), model=model_record(args.model, head), data=data_record,
                  environment=_environment(args.device), predictions=_relative(run_dir / "predictions.jsonl"))
    write_json(record_path, record)

    image_ids = {image["sample_id"]: image["id"] for image in coco["images"]}
    truths_by_image = {image["id"]: [] for image in coco["images"]}
    for annotation in coco["annotations"]:
        x, y, width, height = annotation["bbox"]
        truths_by_image[annotation["image_id"]].append({"annotation_id": annotation["annotation_id"], "class_id": annotation["category_id"] - 1,
                                                        "bbox_xyxy": [x, y, x + width, y + height]})
    detections, failures, empty, invalid = [], [], 0, 0
    totals = {class_id: {"tp": 0, "fp": 0, "fn": 0} for class_id in range(len(CLASS_NAMES))}
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as output:
        for number, sample in enumerate(samples, 1):
            line = {"input_id": sample["sample_id"]}
            image, digest = read_image(Path(sample["image_path"]))
            if digest != sample["image_sha256"]:
                line.update(status="failed", reason="Image bytes differ from the manifest hash.")
            elif image is None or image.shape[:2] != (sample["height"], sample["width"]):
                line.update(status="failed", reason="Image could not be decoded at the manifest size.")
            else:
                predictions, dropped = detect(model, head, image, settings, args.device)
                line.update(width=sample["width"], height=sample["height"], status="completed", predictions=predictions)
                invalid += dropped
                empty += not predictions
                image_id = image_ids[sample["sample_id"]]
                for prediction in predictions:
                    x1, y1, x2, y2 = prediction["bbox_xyxy"]
                    detections.append({"image_id": image_id, "category_id": prediction["class_id"] + 1,
                                       "bbox": [x1, y1, x2 - x1, y2 - y1], "score": prediction["score"]})
                for class_id, counts in match_image(predictions, truths_by_image[image_id]).items():
                    for key in counts:
                        totals[class_id][key] += counts[key]
            if line["status"] == "failed":
                failures.append(sample["sample_id"])
            output.write(json.dumps(line, allow_nan=False) + "\n")
            if number % 100 == 0:
                print(f"{number}/{len(samples)} images")
    counts = {"expected": len(samples), "processed": len(samples) - len(failures), "failed": len(failures),
              "empty": empty, "invalid_boxes": invalid, "predictions": len(detections),
              "ground_truth_per_class": {name: sum(1 for a in coco["annotations"] if a["category_id"] == i + 1) for i, name in enumerate(CLASS_NAMES)},
              "negatives": sum(1 for truths in truths_by_image.values() if not truths)}
    record["counts"] = counts
    write_json(record_path, record)
    if failures:
        raise RuntimeError(f"{len(failures)} of {len(samples)} images failed (first: {failures[0]}); metrics need the full partition.")
    missing_classes = [name for name, number in counts["ground_truth_per_class"].items() if not number]
    if missing_classes:
        raise ValueError(f"The {args.partition} partition has no ground truth for {missing_classes}.")

    aggregate, per_class_ap = _coco_ap(coco, detections)
    micro = _precision_recall(*(sum(totals[c][key] for c in totals) for key in ("tp", "fp", "fn")))
    per_class = {name: {**per_class_ap[name], **_precision_recall(**totals[index])} for index, name in enumerate(CLASS_NAMES)}
    print("Timing ...")
    timing = _timing(model, head, samples, settings, args.device)
    metrics = {
        "model": record["model"], "data": data_record, "config": {"path": record["config_path"], "sha256": record["config_sha256"]},
        "counts": counts,
        "evaluator": {"pycocotools": importlib.metadata.version("pycocotools"), "iou_type": "bbox"},
        "definitions": {
            "map_50_95": "COCO AP averaged over IoU 0.50:0.05:0.95, 101 recall points, area all, maxDets 100.",
            "map_50": "COCO AP at IoU 0.50, otherwise as map_50_95.",
            "precision_recall": f"Top {PR_TOP_K} predictions per image, then score >= {PR_SCORE}; greedy matching in descending score "
                                f"(ties by class, box) to the unmatched same-class box with highest IoU >= {PR_IOU} (ties by annotation ID). "
                                "Micro precision TP/(TP+FP) and recall TP/(TP+FN). This is not COCO average recall.",
            "per_class_ap": "Mean of COCO precision[iou, recall, class, all, maxDets 100] over defined entries.",
        },
        "map_50": aggregate["map_50"], "map_50_95": aggregate["map_50_95"],
        "precision_micro": micro["precision"], "recall_micro": micro["recall"],
        "tp": micro["tp"], "fp": micro["fp"], "fn": micro["fn"],
        "per_class": per_class,
        "undefined": {key: value for key, value in {**aggregate, **micro}.items() if key.endswith("reason")},
        "timing": timing,
    }
    write_json(run_dir / "metrics.json", metrics)
    record["metrics"] = _relative(run_dir / "metrics.json")
    write_json(record_path, record)

    def show(number):
        return "null" if number is None else f"{number:.4f}"

    print(f"AP50 {show(metrics['map_50'])}, AP50:95 {show(metrics['map_50_95'])}, precision {show(metrics['precision_micro'])}, "
          f"recall {show(metrics['recall_micro'])} (TP {micro['tp']}, FP {micro['fp']}, FN {micro['fn']}).")
    if timing["mean_ms"] is not None:
        print(f"Timing: {timing['mean_ms']:.1f} ms/image, {timing['images_per_s']:.2f} images/s on {timing['hardware']} over {timing['samples']} images.")
