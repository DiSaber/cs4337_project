# Usage

Run commands from the repository root; relative input/config paths and output
paths resolve from that workspace. Quote paths containing spaces.

## Windows CPU setup (verified Python 3.14.7)

The exact tested lock is for Windows amd64/Python 3.14.7. Confirm `python --version`
before using it; other allowed interpreters need separate resolution/verification.
From the repository root, use the global pip to populate an isolated environment:

```powershell
python -m venv --without-pip .venv
python -m pip --python .venv/Scripts/python.exe install -r requirements/cpu-lock.txt
python -m pip --python .venv/Scripts/python.exe install --no-deps -e .
.venv/Scripts/python.exe -m driving_detection assets sync --config configs/assets.yaml --only model
.venv/Scripts/python.exe -m driving_detection check --config configs/assets.yaml --device cpu
```

The author used global pip 26.1.2 (`--python` requires pip 22.3 or later). The
resolved versions and wheel provenance are in [requirements](../requirements/README.md).
Repeat sync/check to verify reuse. The check imports libraries, allocates on the
requested device, checks the torchvision NMS operator and loads the verified
official 80-class COCO reference model. It does not train or measure accuracy.
Missing data is reported separately and does not prevent model-only readiness.

For Linux GPU/Colab, use the separate [Colab setup instructions](colab-setup.md),
not this Windows lock. Python 3.13.16/Tesla T4/CUDA 12.8 passed both readiness
checks; Marc Benamou confirmed review completion. Its exact environment is now
recorded in `requirements/cuda-lock.txt` and `cuda-wheels.json`.

## External assets

Review [sources, licensing and access prerequisites](references.md). Full sync
downloads the pinned YOLO source and checkpoint, plus the BDD100K 100K image
archive (5.7 GB) and the 2018 per-image label archive (190 MB) from the dataset
author's mirror. Allow about 12 GB of free disk for the archives and extracted files.

```powershell
.venv/Scripts/python.exe -m driving_detection assets sync --config configs/assets.yaml
```

If you already have the same archives, import them instead of downloading:

```powershell
.venv/Scripts/python.exe -m driving_detection assets sync --config configs/assets.yaml --images-archive "C:/Datasets/bdd100k_images_100k.zip" --labels-archive "C:/Datasets/bdd100k_labels.zip"
```

The BDD mirror serves plain HTTP because its HTTPS certificate has expired.
Sync accepts an HTTP URL only when a SHA-256 is pinned for it, and checks the
publisher MD5 too where one exists. Embedded credentials and signed query URLs
are rejected. Model SHA-256 pins are measured official-download identities.
Supplied local archives must match the same checksums and expected members.
Detection 2020 labels are no longer downloadable; [references](references.md)
explains the switch to the 2018 labels.

Outputs are `external/yolov5-v7.0`, `external/weights/yolov5s.pt`,
`data/raw/images/100k/`, and `data/raw/labels/100k/`.
`artifacts/assets.json` stores asset
identities/readiness; `artifacts/asset-receipts/` stores verified receipts.
Sync stages assets before promotion and refuses existing unverified/changed
destinations. The first extraction is fully verified: the archive SHA-256 and a
SHA-256 of every extracted file (`tree_sha256` in the receipt). Reuse (repeated
`assets sync`, `check`, `data prepare`) only checks the expected members, file
count and total bytes against the receipt, so it is fast but would not catch an
edit that keeps a file's size. To fully re-verify, move the asset and its receipt
aside and sync again from the cached archive. Receipts written before this size
check existed still get the full per-file hash on reuse. Single-file assets
(weights) are always fully hashed. Python bytecode caches are excluded from
extracted-content identity.

Download caches live under `external/downloads/`. An interrupted `.part` is
unverified; retry restarts its download rather than resuming. A corrupt completed
cache, changed extraction, missing receipt or changed asset definition requires
manual recovery: preserve/move the affected asset/cache/receipt aside before
retrying, or use a new configured destination. Do not remove unrelated outputs
or user-supplied archives. Setup never silently overwrites them. Preserve receipt
files when transferring verified assets between matching platforms. Extracted
tree hashes use native path ordering and can differ across Windows/Linux; transfer
the pinned archives and sync them anew when changing platforms.

Runtime adapters allow the pinned checkpoint loader to use explicit
`weights_only=False` only for verified official weights and restore Pillow's
removed font sizing method. Upstream source is unchanged; later training still
needs its own integration verification.

## Data preparation

`data prepare` builds the frozen three-class subset `bdd-subset-v2` from the
synced BDD assets. It needs only PyYAML and Pillow; no torch or GPU. On Linux
with Python 3.13, a data-only environment can use the matching hash-pinned
entries from the Linux lock (this is how D2 was prepared):

```bash
python3 -m venv .venv
grep -E '^(pyyaml|pillow) ' requirements/cuda-lock.txt > /tmp/data-req.txt
.venv/bin/python -m pip install --require-hashes -r /tmp/data-req.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m driving_detection assets sync --config configs/assets.yaml
.venv/bin/python -m driving_detection data prepare --config configs/data/bdd-subset.yaml
```

On Windows use `.venv/Scripts/python.exe` with the full CPU setup above.
Preparation reads all 80,000 official train/val labels and image headers, takes
about 25 s on the Linux desktop, and writes `data/prepared/bdd-subset-v2/`:
`profile.json` (settings, asset identities, rules, counts, integrity results and
export hashes), `manifest.{train,val,test}.jsonl`, `quarantine.jsonl` (every
rejected image with its reason), `coco.val.json`/`coco.test.json` (category IDs
1–3) and `yolo/` (train/val images as hard links, labels and `dataset.yaml`).
The held-out test partition never reaches the YOLO export.

What it checks: image/label pairing, known categories, box conversion
(inclusive source pixels → half-open boxes clipped to the image), duplicate image
content, exact requested counts, all three classes in every partition, and zero
sequence or content overlap. Any failure stops before output is written.

Sequences: a BDD name is `<session>-<clip>`. The session prefix is the sequence
ID, and only one image per session is selected, so related clips never cross
partitions. Sessions found in both official splits are quarantined. The test
partition is a project holdout from official val, not the official BDD test set.

Running it again with the same inputs prints "Reusing identical frozen profile"
and changes nothing. If the config or assets change, it refuses to overwrite and
asks for a new `profile_id` and output folder. Recorded counts and review are in
[experiments](../results/experiments.md). Known label noise: about 30 boxes come
from zero-size source labels and become 1-pixel-wide slivers.

## Training

`train` runs the pinned YOLOv5 v7.0 `train.py` on the prepared train/val export.
It needs the full runtime (torch); the data-only environment above cannot train.
The smoke run checks that training works end to end; its accuracy is never reported:

```bash
python -m driving_detection train --profile data/prepared/bdd-subset-v2/profile.json \
  --config configs/train/smoke.yaml --run-id smoke-01 --device cuda:0
```

The baseline uses `--config configs/train/baseline.yaml --run-id baseline-01`. Use
`--device cpu` to run on CPU (slow). Before starting, it checks that the source and
initial weights are verified, that the train/val manifests and `dataset.yaml` still
match the profile hashes, and that no experiment tracker (wandb, ClearML, Comet) is
installed. The test partition is never passed to training.

Everything goes into `artifacts/runs/<run-id>/`:

- `run.json`: status, label (smoke or baseline), project commit, source/weights/data
  identities and hashes, the exact upstream command, effective batch (gradient
  accumulation to a nominal batch of 64 and scaled weight decay), seeds,
  nondeterminism notes, installed packages, hardware, budget use, chosen epoch and
  checkpoint hashes.
- `resolved-config.yaml`, `hyp.input.yaml` and upstream's own `opt.yaml`/`hyp.yaml`.
- `train.log` (full console output) and `results.csv` (one row per epoch).
- `weights/best.pt` (chosen checkpoint) and `weights/last.pt`.

The chosen epoch is the one with the highest upstream validation fitness
(0.1 × mAP@0.5 + 0.9 × mAP@0.5:0.95); ties keep the earliest epoch. After training,
`best.pt` is loaded and must have exactly the classes car, pedestrian, traffic_light.
A run that passes `budget_gpu_hours` is stopped and recorded as `interrupted`;
retry with a new run ID (there is no resume). To change the batch size before the
reported run (fallback 4, then 2), edit `batch` in the config; `run.json` records it.

Load a trained checkpoint in Python with
`driving_detection.assets.load_model(load_config(Path("configs/assets.yaml")), "cpu", Path("artifacts/runs/baseline-01/weights/best.pt"))`.

Compatibility settings (upstream files stay unchanged): the training process gets
`TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` because pinned `train.py` loads full pickled
models; a one-line launcher sets `numpy.trapz = numpy.trapezoid` before running
`train.py`, because NumPy 2.4 removed `trapz` and pinned validation AP still calls
it; and `--noplots` is passed because pinned plotting needs a Pillow method removed
in Pillow 10. Upstream also downloads `Arial.ttf` into `artifacts/yolo-config` the first
time and writes `labels/*.cache` files beside the prepared YOLO labels.

## Inference

`infer` runs a checkpoint on one image, a folder of images or a prerecorded video
(`.mp4`, `.avi`, `.mov`, `.mkv`, `.m4v`). Settings come from
`configs/evaluation/default.yaml`: size 640, FP32, class-aware NMS at IoU 0.6, a score
floor of 0.001, at most 300 boxes per image, and a display threshold of 0.25.

```bash
python -m driving_detection infer --model artifacts/runs/baseline-01/weights/best.pt \
  --input data/new-scenes/images --config configs/evaluation/default.yaml --run-id baseline-images-01
python -m driving_detection infer --model external/weights/yolov5s.pt --reference-coco \
  --input data/new-scenes/demo.mp4 --config configs/evaluation/default.yaml --run-id reference-video-01
```

Only two kinds of checkpoint are loaded, because a checkpoint is a pickle that can
run code: one this project trained under `artifacts/runs/`, which must have exactly
the classes car, pedestrian and traffic_light, and the verified official COCO
checkpoint with `--reference-coco`. The reference head maps COCO car, person and
traffic light to our three classes and drops every other class. A box whose best
COCO class is something else, such as truck, is dropped too. Reference and smoke
results are development aids, never reported results; `run.json` marks a model
`reportable` only when its training `run.json` has the label `baseline`.

Each image is letterboxed to a gray-padded 640 × 640 square with its aspect ratio
kept, run in FP32, and its boxes are mapped back to original pixels and clipped to
the image. Boxes with zero width or height after clipping are dropped and counted as
`invalid_boxes`. The run writes into `artifacts/runs/<run-id>/`:

- `predictions.jsonl`: one line per image or video frame, in name or frame order,
  with `status`. A completed line has the size and every box at or above the 0.001
  floor (highest score first); an image with no boxes is a valid empty result
  (`"predictions": []`). A failed line has a `reason` instead.
- `annotated/` (images) or `annotated.mp4` (video, mp4v codec): boxes with score at or
  above 0.25, blue car, red pedestrian, yellow traffic light.
- `run.json`: model path/hash/head/training-run label, input path (and video hash,
  frame rate, size, reported and decoded frames), environment and counts (expected,
  processed, failed, empty, invalid boxes).

In a folder, every visible file is an expected input. A file that is not an image,
or that cannot be decoded, gets a failed line; the other files are still processed,
and the run ends as `failed` with exit code 1. A video that stops decoding before its
reported frame count gets one failed line per missing frame and also fails. The saved
video is reopened to check its size and frame count.

## CLI help and package-only setup

Use Python 3.10–3.14. To install only the current CLI skeleton in an isolated
environment without downloading model dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --no-deps -e .
python -m driving_detection --help
driving-detection --help
python -m driving_detection assets sync --help
python -m driving_detection check --help
python -m driving_detection data prepare --help
python -m driving_detection train --help
python -m driving_detection infer --help
python -m driving_detection evaluate --help
```

On Linux, activate with `source .venv/bin/activate`. The build backend may need
to be installed by pip. Help needs no torch, CUDA, PyYAML, weights or dataset.
Asset sync, readiness check, data preparation and training are implemented.
Infer/evaluate still report an unimplemented-handler error and exit 1 without
reading configs or creating run outputs. Invalid/missing arguments exit 2. The package-only install
above is enough for help, but model readiness requires the full runtime setup.

## Shared behavior for component implementation

Implemented handlers consume a YAML mapping; PyYAML is needed when reading it.
Each handler checks its required settings and input files where used. Train,
infer and evaluate accept `--device cpu` or `--device cuda:0`; otherwise the
configuration's `device` is used, defaulting to CPU if omitted. An unavailable
requested CUDA device fails rather than switching to CPU. Evaluation defaults to
validation; `--partition test` requires `--selection PATH`. Final selection/hash
checks belong to the evaluation handler and are not implemented yet.

Train/infer/evaluate reserve `artifacts/runs/<run-id>/` before processing.
Run IDs start with a letter or digit, contain only letters/digits/dots/dashes/
underscores, have at most 128 characters, and cannot end in a dot or use Windows
reserved device names. Existing directories are refused; retries need a new ID.
For implemented handlers, the CLI saves effective device/config settings to
`resolved-config.yaml` with a byte SHA-256 reference in `run.json`. Handlers add
their domain-specific settings/evidence and resave resolved settings if they add
defaults or overrides. The CLI starts the record with `status=started` and writes
`completed`, `failed` or `interrupted` on exit, preserving handler-added fields.
Failures include a reason and exit nonzero; Ctrl+C exits 130. A handler that
stops at its time budget raises `TimeoutError`, recorded as `interrupted` (exit 1).

Large inputs belong in ignored `data/` and `external/`; generated outputs belong
in ignored `artifacts/`. If the checkout sits inside a Syncthing (or similar) synced
folder, exclude these folders from syncing before downloading anything; Git ignore
rules do not affect sync tools. Archives (`*.zip`, `*.tar*`, `*.7z`) and video
(`*.mp4`, `*.avi`, `*.mov`, `*.mkv`) are Git-ignored anywhere in the tree. Keep secrets out of configs and command arguments, which
may be preserved in run records. Track small configs and results/retrieval notes.

The [future quickstart](../specs/001-driving-object-detection/quickstart.md)
describes the later pipeline interfaces and checks. Local CPU model acquisition
and loading have been verified on the recorded Windows CPU and Colab GPU profiles;
training, predictions, evaluation and other runtime profiles are not yet verified.
