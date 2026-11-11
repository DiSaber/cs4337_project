# CS4337 Driving Scene Object Detection

A Python pipeline that detects cars, pedestrians and traffic lights in driving
scenes. It fine-tunes YOLOv5s (pinned v7.0) on a frozen 7,000-image subset of
BDD100K and runs it on new images and prerecorded video. Implementation follows the
[feature plan](specs/001-driving-object-detection/plan.md) and
[task list](specs/001-driving-object-detection/tasks.md).

## Status

| Deliverable | State |
| --- | --- |
| D1 setup and asset sync | Done |
| D2 data preparation (`bdd-subset-v2`: 5,000 train / 1,000 val / 1,000 test) | Done |
| D3 baseline training (`baseline-01`, 20 epochs on a Colab T4) | Done |
| D4 inference on images and video | Done; a real driving-video demo is deferred to the optional dashcam study |
| D5 evaluation and accepted core | Done: validation AP50 0.521, AP50:95 0.239 |
| D6 candidate comparison and final test | Done: size 640 kept; held-out test AP50 0.526, AP50:95 0.236 |
| D7 report and D8 presentation | Course checklist and [presentation outline](docs/presentation/slides.md) ready; report, slides and recording are student work (see the [course checklist](docs/course-deliverables.md)) |
| D9 team dashcam study | Optional, not started |

## The six commands

All run as `python -m driving_detection <command>`; each supports `--help`.

| Command | What it does |
| --- | --- |
| `assets sync`, `check` | Download and verify the YOLOv5 source, weights and BDD archives; check the environment and device |
| `data prepare` | Build the frozen subset, manifests and YOLO/COCO exports with integrity checks |
| `train` | Run pinned YOLOv5 training into `artifacts/runs/<run-id>/` |
| `infer` | Predict and draw boxes on an image, a folder of images or a video |
| `evaluate` | COCO AP, fixed-point precision/recall, timing and examples on validation; the test partition needs a frozen selection |

Setup, every command's inputs and outputs, and current results and limits are in
[usage](docs/usage.md). Asset sources and terms are in [references](docs/references.md),
run evidence in [experiments](results/experiments.md), and the Colab baseline steps in
[Colab setup](docs/colab-setup.md) and `notebooks/t015_baseline_colab.ipynb`.

## Environments

Python 3.10–3.14 is allowed. Two hash-checked locks exist: the
[CPU lock](requirements/cpu-lock.txt) for Windows/Python 3.14.7, and the
[CUDA lock](requirements/cuda-lock.txt) for Linux/Python 3.13 (verified on a Colab
Tesla T4, and used on CPU on the Linux desktop for inference and evaluation). Other
platforms need their own resolution and readiness check.

## Files and storage

Keep datasets in `data/`, model source/initial weights in `external/`, and generated
runs/media in `artifacts/`; these directories are ignored by Git. Track small
configurations in `configs/` and compact summaries/retrieval instructions in
`results/`. Keep credentials out of tracked files. The existing
`.specify/.gitignore` continues to exclude local feature state.
