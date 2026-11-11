"""D4 inference: run a YOLOv5 checkpoint on images or a prerecorded video.

load_detector, read_image and detect are also used by evaluation.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import platform
import sys
from pathlib import Path

from .assets import _definition, _local_output, load_model
from .records import load_config, project_revision, sha256_file, workspace_path, write_json
from .train import ASSETS_CONFIG, CLASS_NAMES

# The official COCO checkpoint is only a development reference. Its classes map to
# ours as car 2 -> 0, person 0 -> 1, traffic light 9 -> 2; other classes are dropped.
REFERENCE_MAP = {2: 0, 0: 1, 9: 2}
REQUIRED = ("imgsz", "precision", "nms_iou", "score_floor", "max_detections", "display_threshold")
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
VIDEO_TYPES = {".mp4", ".avi", ".mov", ".mkv", ".m4v"}
COLORS = {0: (255, 160, 0), 1: (0, 0, 255), 2: (0, 220, 255)}  # BGR: car blue, pedestrian red, light yellow


def _relative(path: Path) -> str:
    path = path.resolve()
    workspace = Path.cwd().resolve()
    return path.relative_to(workspace).as_posix() if path.is_relative_to(workspace) else str(path)


def _upstream():
    """Import the pinned YOLOv5 letterbox, NMS and box-scaling functions."""
    source = _local_output(_definition(load_config(workspace_path(ASSETS_CONFIG)), "source")["path"])
    sys.path.insert(0, str(source))
    try:
        augmentations = importlib.import_module("utils.augmentations")
        general = importlib.import_module("utils.general")
    finally:
        sys.path.remove(str(source))
    if not Path(general.__file__).resolve().is_relative_to(source):
        raise ValueError("A different utils module is already imported; use a fresh process.")
    return augmentations.letterbox, general.non_max_suppression, general.scale_boxes


def load_detector(model_path: Path, device: str, reference_coco: bool):
    """Load a checkpoint and check its class head. Returns the model and a head record.

    Checkpoints are pickles that can run code, so only the verified official
    checkpoint or one this project trained under artifacts/runs is loaded.
    """
    asset_settings = load_config(workspace_path(ASSETS_CONFIG))
    official = _local_output(_definition(asset_settings, "weights")["path"])
    model_path = model_path.resolve()
    if reference_coco != (model_path == official):
        raise ValueError(f"--reference-coco is for the official COCO checkpoint {_relative(official)} only, and that checkpoint needs it.")
    if not reference_coco and not model_path.is_relative_to(workspace_path("artifacts/runs")):
        raise ValueError("A trained checkpoint must be one this project wrote under artifacts/runs.")
    if not model_path.is_file():
        raise ValueError(f"Checkpoint not found: {model_path}")
    model = load_model(asset_settings, device, None if reference_coco else model_path)
    names = list(model.names.values()) if isinstance(model.names, dict) else list(model.names)
    classes = model.model[-1].nc
    if reference_coco:
        if classes != 80 or [names[i] for i in REFERENCE_MAP] != ["car", "person", "traffic light"]:
            raise ValueError("The reference checkpoint does not have the expected 80-class COCO head.")
        head = {"kind": "reference_coco", "classes": classes,
                "mapping": {names[source]: CLASS_NAMES[target] for source, target in REFERENCE_MAP.items()},
                "note": "Other COCO classes are dropped. A box whose best class is not one of these is dropped too."}
    else:
        if names != CLASS_NAMES or classes != len(CLASS_NAMES):
            raise ValueError(f"Checkpoint head has names {names} and {classes} classes; expected {CLASS_NAMES}.")
        head = {"kind": "trained", "names": names, "classes": classes}
    return model, head


def read_image(path: Path):
    """Decode an image as 3-channel BGR. Returns (image or None, SHA-256 of the file bytes)."""
    import cv2
    import numpy as np

    data = path.read_bytes()
    # imdecode instead of imread: imread cannot open non-ASCII paths on Windows.
    # IMREAD_COLOR turns grayscale/alpha/16-bit files into 8-bit BGR.
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    return image, hashlib.sha256(data).hexdigest()


def detect(model, head: dict, image, settings: dict, device: str) -> tuple[list[dict], int]:
    """Predict boxes for one BGR image in its original pixel coordinates.

    Returns the predictions (highest score first, at or above the AP score floor)
    and the number of invalid boxes dropped.
    """
    import numpy as np
    import torch

    letterbox, non_max_suppression, scale_boxes = _upstream()
    # Square letterbox: keep the aspect ratio and pad to imgsz x imgsz with gray.
    padded = letterbox(image, settings["imgsz"], auto=False)[0]
    tensor = np.ascontiguousarray(padded[:, :, ::-1].transpose(2, 0, 1))  # BGR HWC -> RGB CHW
    tensor = torch.from_numpy(tensor).to(device).float().div(255)[None]
    with torch.no_grad():
        output = model(tensor)
        # Class-aware NMS: boxes of different classes never suppress each other.
        found = non_max_suppression(
            output, conf_thres=settings["score_floor"], iou_thres=settings["nms_iou"],
            classes=list(REFERENCE_MAP) if head["kind"] == "reference_coco" else None,
            max_det=settings["max_detections"],
        )[0]
    found[:, :4] = scale_boxes(tensor.shape[2:], found[:, :4], image.shape[:2])  # also clips to the image
    predictions, invalid = [], 0
    for x1, y1, x2, y2, score, cls in found.cpu().tolist():
        if not all(math.isfinite(v) for v in (x1, y1, x2, y2, score)) or x2 <= x1 or y2 <= y1 or not 0 <= score <= 1:
            invalid += 1
            continue
        class_id = REFERENCE_MAP[int(cls)] if head["kind"] == "reference_coco" else int(cls)
        predictions.append({"class_id": class_id, "score": score, "bbox_xyxy": [x1, y1, x2, y2]})
    return predictions, invalid


def draw(image, predictions: list[dict], threshold: float):
    """Return a copy with boxes at or above the display threshold drawn on it."""
    import cv2

    annotated = image.copy()
    for prediction in predictions:
        if prediction["score"] < threshold:
            continue
        x1, y1, x2, y2 = (round(v) for v in prediction["bbox_xyxy"])
        color = COLORS[prediction["class_id"]]
        label = f"{CLASS_NAMES[prediction['class_id']]} {prediction['score']:.2f}"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        (width, height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(y1 - height - 4, 0)
        cv2.rectangle(annotated, (x1, top), (x1 + width + 4, top + height + 4), color, -1)
        cv2.putText(annotated, label, (x1 + 2, top + height + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return annotated


def _environment(device: str) -> dict:
    import cv2
    import torch

    environment = {"python": sys.version.split()[0], "platform": platform.platform(),
                   "torch": torch.__version__, "opencv": cv2.__version__, "device": device}
    if device == "cuda:0":
        environment["gpu"] = torch.cuda.get_device_name(0)
    return environment


def _images(paths: list[Path], run_dir: Path, model, head: dict, settings: dict, device: str, output) -> dict:
    import cv2

    annotated_dir = run_dir / "annotated"
    annotated_dir.mkdir()
    counts = {"expected": len(paths), "processed": 0, "failed": 0, "empty": 0, "invalid_boxes": 0}
    for number, path in enumerate(paths, 1):
        line = {"input_id": path.name}
        if path.suffix.lower() not in IMAGE_TYPES:
            line.update(status="failed", reason=f"Unsupported file type {path.suffix or '(none)'}.")
        else:
            image, line["sha256"] = read_image(path)
            if image is None:
                line.update(status="failed", reason="File could not be decoded as an image.")
            else:
                predictions, invalid = detect(model, head, image, settings, device)
                encoded, data = cv2.imencode(path.suffix, draw(image, predictions, settings["display_threshold"]))
                if not encoded:
                    line.update(status="failed", reason=f"Annotated image could not be encoded as {path.suffix}.")
                else:
                    (annotated_dir / path.name).write_bytes(data.tobytes())
                    line.update(width=image.shape[1], height=image.shape[0], status="completed", predictions=predictions)
                    counts["invalid_boxes"] += invalid
                    counts["empty"] += not predictions
        counts["processed" if line["status"] == "completed" else "failed"] += 1
        output.write(json.dumps(line, allow_nan=False) + "\n")
        print(f"[{number}/{len(paths)}] {path.name}: {line['status']}" + (f", {len(line['predictions'])} boxes" if "predictions" in line else f" ({line['reason']})"))
    return counts


def _video(path: Path, run_dir: Path, model, head: dict, settings: dict, device: str, output) -> tuple[dict, dict]:
    import cv2

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Video could not be opened: {path}")
    fps = capture.get(cv2.CAP_PROP_FPS)
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    reported = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if not (fps > 0 and width > 0 and height > 0):
        capture.release()
        raise ValueError(f"Video reports no usable frame rate or size (fps {fps}, {width}x{height}).")
    annotated_path = run_dir / "annotated.mp4"
    writer = cv2.VideoWriter(str(annotated_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        capture.release()
        raise RuntimeError("No mp4v video encoder is available in this OpenCV build.")

    counts = {"expected": reported, "processed": 0, "failed": 0, "empty": 0, "invalid_boxes": 0}
    index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            line = {"input_id": f"{path.stem}:{index:06d}", "frame_index": index}
            if frame.shape[:2] != (height, width):
                line.update(status="failed", reason=f"Frame is {frame.shape[1]}x{frame.shape[0]}, video reports {width}x{height}.")
            else:
                predictions, invalid = detect(model, head, frame, settings, device)
                writer.write(draw(frame, predictions, settings["display_threshold"]))
                line.update(width=width, height=height, status="completed", predictions=predictions)
                counts["invalid_boxes"] += invalid
                counts["empty"] += not predictions
            counts["processed" if line["status"] == "completed" else "failed"] += 1
            output.write(json.dumps(line, allow_nan=False) + "\n")
            index += 1
            if index % 50 == 0:
                print(f"{index}/{reported} frames")
    finally:
        capture.release()
        writer.release()
    # Frames the container reports but the decoder never returned are failures, one record each.
    for missing in range(index, reported):
        output.write(json.dumps({"input_id": f"{path.stem}:{missing:06d}", "frame_index": missing, "status": "failed",
                                 "reason": f"Decoder stopped after {index} of {reported} reported frames."}) + "\n")
        counts["failed"] += 1
    counts["expected"] = max(reported, index)

    # Reopen the saved video to confirm it plays back with the expected size and length.
    check = cv2.VideoCapture(str(annotated_path))
    written = 0
    while check.read()[0]:
        written += 1
    saved = {"path": _relative(annotated_path), "codec": "mp4v", "fps": fps,
             "width": int(check.get(cv2.CAP_PROP_FRAME_WIDTH)), "height": int(check.get(cv2.CAP_PROP_FRAME_HEIGHT)),
             "frames_read_back": written, "frames_written": counts["processed"]}
    check.release()
    if (saved["width"], saved["height"], written) != (width, height, counts["processed"]):
        raise RuntimeError(f"Annotated video reads back as {saved['width']}x{saved['height']} with {written} frames; "
                           f"expected {width}x{height} with {counts['processed']}.")
    saved["sha256"] = sha256_file(annotated_path)
    video = {"fps": fps, "width": width, "height": height, "reported_frames": reported, "decoded_frames": index}
    return counts, {"video": video, "annotated": saved}


def infer(args, settings: dict) -> None:
    missing = [key for key in REQUIRED if key not in settings]
    if missing:
        raise ValueError(f"Inference config is missing: {', '.join(missing)}")
    if settings["precision"] != "fp32":
        raise ValueError("Only precision fp32 is supported.")

    source = args.input
    if source.is_dir():
        # One folder level, sorted by name; every visible file is an expected input.
        paths = sorted(p for p in source.iterdir() if p.is_file() and not p.name.startswith("."))
        if not paths:
            raise ValueError(f"No files in {source}")
        kind = "images"
    elif source.is_file() and source.suffix.lower() in IMAGE_TYPES:
        paths, kind = [source], "images"
    elif source.is_file() and source.suffix.lower() in VIDEO_TYPES:
        kind = "video"
    elif not source.exists():
        raise ValueError(f"Input not found: {source}")
    else:
        raise ValueError(f"Unsupported input {source.name}; use an image, a folder of images or a {'/'.join(sorted(VIDEO_TYPES))} video.")

    run_dir = args.run_dir
    record_path = run_dir / "run.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    model, head = load_detector(args.model, args.device, args.reference_coco)
    # A trained checkpoint sits in artifacts/runs/<id>/weights/; its run.json says smoke or baseline.
    training_run = {}
    if head["kind"] == "trained":
        train_record = args.model.resolve().parent.parent / "run.json"
        if train_record.is_file():
            saved = json.loads(train_record.read_text(encoding="utf-8"))
            training_run = {"id": saved.get("id"), "label": saved.get("label"), "status": saved.get("status")}
    record.update(
        project_revision=project_revision(),
        model={"path": _relative(args.model), "sha256": sha256_file(args.model), "head": head,
               "training_run": training_run, "reportable": training_run.get("label") == "baseline",
               "note": "Only a baseline training run is reportable; reference COCO and smoke checkpoints are development aids."},
        input={"path": _relative(source), "kind": kind, **({"sha256": sha256_file(source)} if kind == "video" else {})},
        environment=_environment(args.device),
        predictions=_relative(run_dir / "predictions.jsonl"),
    )
    write_json(record_path, record)

    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as output:
        if kind == "images":
            counts = _images(paths, run_dir, model, head, settings, args.device, output)
            record["annotated"] = _relative(run_dir / "annotated")
        else:
            counts, video_record = _video(source, run_dir, model, head, settings, args.device, output)
            record.update(video_record)
    record["counts"] = counts
    write_json(record_path, record)
    print(f"Processed {counts['processed']} of {counts['expected']} {'frames' if kind == 'video' else 'inputs'}; "
          f"{counts['empty']} with no boxes, {counts['failed']} failed.")
    if counts["failed"]:
        raise RuntimeError(f"{counts['failed']} of {counts['expected']} inputs failed; see predictions.jsonl for reasons.")
