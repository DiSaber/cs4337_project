# Research: Driving Scene Object Detection

**Date**: 2026-11-05. **Scope**: Phase 0 decisions for [spec.md](spec.md). Research used primary documentation; no dependency installation, dataset download, training, or benchmark was performed. Pins below are compatibility targets to verify in D1, not a tested lockfile. The user selected single-NVIDIA-GPU/Colab training with CPU smoke checks.

**Scope revision**: The user approved a smaller implementation after review. The decisions below retain data/model/evaluation correctness but use direct wrappers, six command handlers, compact files, a human-reviewed comparison/selection, and one timing interval. Tests are limited to focused data/metric checks and one opt-in CPU pipeline smoke test. The current [plan](plan.md) and contracts implement this reduction.

**Testing revision (2026-11-10)**: Constitution v2.0.0 Principle VII forbids automated tests. All test modules, fixtures and pytest were removed from the plan. Mentions of pytest, test fixtures and the opt-in smoke test below are historical. Verification is now by normal runs and manual review, plus one short smoke training run with the normal `train` command; see the [plan](plan.md).

## R1 — Model and runtime

**2026-11-05 runtime revision**: The user authorized Python 3.10–3.14, including reported Colab 3.13 and observed local 3.14.7 / 3.10. The original exact targets below are historical research, superseded by the bounded dependencies in `pyproject.toml` and the current plan. D1 resolves and locks the actual CPU/GPU environments; no full runtime compatibility is claimed yet. The [official torchvision matrix](https://github.com/pytorch/vision) lists torch 2.9 / torchvision 0.24 for Python 3.10–3.14. Modern integration must address [torch loading defaults](https://docs.pytorch.org/docs/stable/notes/serialization) and [removed Pillow text APIs](https://pillow.readthedocs.io/en/stable/deprecations.html). This authorizes necessary compatibility changes while preserving the pinned model source identity and recording any local adaptations.

**Decision**: Use COCO-pretrained YOLOv5s from release v7.0, source commit `915bbf294bb74c859f0b41f1c23bc395014ea679`. Keep the checkout outside Git and call its training/inference routines through direct wrappers. Start with Python 3.11, torch 2.5.1, torchvision 0.20.1, numpy 1.26.4, Pillow 9.5.0, opencv-python 4.10.0.84, PyYAML 6.0.2, pycocotools 2.0.10, and pytest 8.3.5. D1 records complete CPU/GPU environment versions after imports/checkpoint checks; training compatibility is verified by the single connected smoke run when available. No broad platform test matrix, moving master or runtime torch.hub downloads.

**Rationale**: Preserves the suggested model and keeps the implementation small. The pinned historical release uses Pillow's older text-size interface and a checkpoint loader affected by newer torch defaults. The torch/torchvision pair has documented Python 3.11 and Windows/Linux wheel support. CUDA 12.1 is the initial GPU profile; the readiness check must confirm compatibility with the actual GPU/driver. A newer matched torch/vision profile is allowed only as a recorded, smoke-tested compatibility change if the device requires it; use the same resulting lock for comparisons.

**Alternatives considered**: Current YOLO packages change the source surface; Faster R-CNN changes the brief and compute needs. An unpinned latest install is not reproducible. CPU is retained for fixtures, not promised as a practical full-training target.

Sources: [immutable model source](https://github.com/ultralytics/yolov5/commit/915bbf294bb74c859f0b41f1c23bc395014ea679), [checkpoint loader](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/models/experimental.py), [Pillow usage](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/utils/plots.py), [PyTorch wheel matrix](https://docs.pytorch.org/get-started/previous-versions/), [torchvision compatibility](https://github.com/pytorch/vision), [versioned upstream requirements](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/requirements.txt).

## R2 — Asset acquisition and attribution

**Decision**: Acquire only BDD100K 100K images plus Detection 2020 annotations, the pinned YOLO source, and official `yolov5s.pt`. Asset configuration records official URLs, version, published checksum where available, terms/citation references, expected extracted members, and measured SHA-256. Dataset URLs may be supplied locally without storing credentials. Support existing archives as well as automated downloading; stage and verify before atomic promotion. Never overwrite a different valid asset silently.

**Rationale**: Required detection inputs do not need the roughly terabyte-scale raw-video collection. Official data documentation publishes archive checksums and recommends revised annotations. The documented download host was not verified usable during research; acquisition must fail actionably or ingest existing authorized archives. Capture weight SHA-256 on first official acquisition and share the accepted asset identity before reported runs, rather than invent an unpublished digest.

**Alternatives considered**: Mirror downloads without provenance are rejected. A separately identified legacy-label profile can be added only before manifest freeze, never silently mixed with Detection 2020. Raw BDD videos and Roboflow accounts are unnecessary core dependencies.

**Update (2026-11-10, D2)**: Detection 2020 labels could not be obtained. The official hosts are offline, no archived or mirrored copy matches the published MD5, and the author mirror's file of that name contains images rather than labels. `bdd-subset-v1` therefore uses the separately identified 2018 per-image label release (`BDD100K-2018-labels-per-image`) for the same 100K keyframes, chosen before any manifest was frozen. Both archives come from the dataset author's HTTP mirror and are pinned by SHA-256. Evidence and differences are in [references](../../docs/references.md).

Sources: [official dataset downloads](https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst), [dataset/code terms](https://github.com/bdd100k/bdd100k/blob/master/doc/source/license.rst), [official weights](https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt), [release license](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/LICENSE). Preserve the chosen release's GPL-3.0 notice separately from dataset and project notices; do not infer its terms from current master.

## R3 — Labels, geometry, and ignored examples

**Decision**: Canonical IDs are `0=car`, `1=pedestrian`, `2=traffic_light`. Map `traffic light` to `traffic_light`, and version-declared `person` to `pedestrian`. Map documented ordinary aliases `van`/`caravan` to car, `bike` to excluded bicycle, and `motor` to excluded motorcycle when present. Count known non-target labels without turning them into targets. Quarantine unknown labels. Exclude whole samples containing ignored-region categories (`other person`, `other vehicle`, `trailer`) or explicit ignore/crowd boxes from the initial simplified dataset; retain exclusion reasons/counts. Keep ordinary occluded/truncated target boxes.

**Rationale**: Ignored regions cannot safely become unannotated negatives. Whole-sample exclusion avoids building a second ignore-region evaluator and is a disclosed dataset limitation. Source inclusive-endpoint boxes become continuous half-open `xyxy` once at ingestion: `[x1,y1,x2+1,y2+1]`; intersect with image bounds only under a recorded clipping rule, reject inverted/nonfinite/empty boxes, and retain original coordinates. Both training and evaluation derive from this representation.

**Alternatives considered**: Dropping ignored boxes while retaining the image biases false-positive counts. Leaving coordinate semantics implicit makes area/IoU inconsistent. Native BDD evaluation is broader than the project's three-class subset and is not claimed.

Sources: [official detection mappings](https://github.com/bdd100k/bdd100k/blob/master/bdd100k/configs/det.toml), [official coordinate definition](https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst).

## R4 — Split, scale, and training budget

**Decision**: Default `bdd-subset-v1` uses 5,000 eligible official-training sequences, 1,000 project-validation sequences, and 1,000 project-held-out sequences from official labeled validation. After integrity/exclusion checks, rank sequence IDs by SHA-256 of UTF-8 `cs4337-v1:4337:` followed by the sequence ID, breaking hash ties lexically. Take first 5,000 from official train; first 1,000 from official val become project validation and next 1,000 become project test. Retain negative images; do not select only target-bearing scenes. Fail readiness on inadequate counts/class coverage or cross-partition sequence/content duplicates. Fix these issues through a versioned pretraining manifest change, never by model results.

**Rationale**: The detection archive contains one keyframe per source video. Use explicit videoName if present, otherwise the full filename stem only for this documented archive, recording that provenance. Do not use arbitrary filename prefixes as sequences. The holdout is a project subset, not the official benchmark test. Hash and freeze manifests before training; inspect test labels only for pretraining integrity/coverage, not model selection.

**Budget**: Baseline 20 epochs, image size 640, batch 8, seed 4337, workers 0, single GPU, at most 8 GPU-hours including training validation. Smoke: one opt-in connected CPU test using tiny internal BDD-shaped fixtures, one epoch, batch 2, size 320, never reportable accuracy. No separate synthetic-data product or fixed-size synthetic profile is required. Disable early stopping for the planned 20 epochs. Select baseline checkpoint by upstream validation fitness `0.1*AP50 + 0.9*AP50:95`, ties earliest epoch. Budget exhaustion is an interrupted run, not completed baseline evidence. If memory is insufficient, select batch 4 or 2 before the reported run and preserve the resolved config; never silently vary batch mid-comparison.

**Alternatives considered**: Full data/multiple architectures consume course time. CPU-only full training is not the chosen target. Larger subsets or additional runs require a new recorded profile; no accuracy target is promised.

Source for checkpoint fitness: [versioned YOLO metric code](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/utils/metrics.py). Split sizes, seeds, and budget are project design decisions, not upstream recommendations.

## R5 — Preprocessing and augmentation

**Decision**: Local deterministic conversion and aspect-preserving square letterboxing are the required path. Do not permanently resize original assets. Training augmentation is seeded and explicit: horizontal flip probability 0.5, HSV gains h=0.015/s=0.7/v=0.4; disable mosaic, mixup, copy-paste, translation, scaling, rotations, shears, perspective, and vertical flip for the baseline. Record all remaining upstream hyperparameters in a complete resolved configuration, including optimizer/schedule. Validation/test have deterministic letterboxing only. Disable autoanchor for smoke and baseline to keep anchors/settings fixed.

**Rationale**: Simple transformations preserve the project focus and avoid hidden augmentation defaults. Roboflow stays optional; if explored later, split first, retain parent sequence lineage/export version/checksums, and avoid accidental duplicate online augmentation.

**Alternatives considered**: Mandatory hosted preprocessing adds access/setup dependencies. Offline augmented copies complicate lineage and consume storage without a required benefit.

Sources: [YOLO training hyperparameters](https://raw.githubusercontent.com/ultralytics/yolov5/v7.0/data/hyps/hyp.scratch-low.yaml), [Roboflow training-only augmentation](https://docs.roboflow.com/datasets/versions/dataset-versions/image-augmentation.md).

## R6 — Evaluation and timing

**Decision**: Use direct pycocotools bbox COCOeval for AP, not an additional TorchMetrics wrapper. Pin its package and export stable integer image IDs and category IDs 1–3. Use IoUs 0.50:0.05:0.95, 101 recall points, all object sizes, maxDets [1,10,100]. Record per-class AP50/AP50:95 and macro AP. AP predictions retain confidence >=0.001, class-aware NMS IoU 0.6, at most 300 detections/image before evaluator limits. Compute operating-point precision/recall separately at confidence >=0.25, IoU >=0.50, using class-specific score-descending greedy one-to-one matching. Report aggregate micro and per-class P/R with TP/FP/FN.

**Rationale**: AP integrates ranked predictions; display thresholds must not truncate it. YOLO's default returned P/R is at a selected F1 operating point, not necessarily confidence 0.25. Normalize undefined quantities to null with reasons; explicitly handle empty results. A duplicate after a true positive is FP for operating-point counts, but need not reduce interpolated AP if it ranks after full recall.

**Timing**: Integrate one timer in evaluation: batch 1, same device/precision, FP32, 10 warm-ups, then the first 100 images of the evaluated partition (minimum 10 for actual-data timing). Synchronize CUDA around the interval. Include preprocessing, transfer, model forward and NMS; exclude disk decoding, drawing and encoding. Record total elapsed time/count, mean ms/image, throughput, hardware/input/batch/precision and timing boundaries. Baseline/candidate use the same validation samples. No separate benchmark command, per-stage traces, percentiles or full-video speed claim is required.

**Alternatives considered**: Handwritten AP risks correctness; retained custom P/R count logic is small and fixture-tested. GPU forward-only timing cannot stand in for complete image/video speed.

Sources: [COCO evaluator](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/cocoeval.py), [official pycocotools 2.0.10 distribution](https://pypi.org/project/pycocotools/2.0.10/), [PyTorch reproducibility limitations](https://pytorch.org/docs/stable/notes/randomness.html).

## R7 — Bounded optimization and final holdout

**Decision**: Run ordinary validation evaluation at sizes 640 and 960 with the same trained checkpoint, membership, NMS, scores, device and FP32 batch-1 timing. Review a comparison table; choose 960 only if AP50:95 improves by at least 0.005 absolute and mean timed latency is no more than 1.5 times baseline, otherwise retain 640. Missing/failed attempts stay visible and leave quantitative comparison incomplete. A human saves selected.yaml with the chosen checkpoint/data/config/environment byte hashes, validation references and decision time before ordinary test evaluation; test evaluation checks those fields. No orchestrator, core-check, custom final command or exposure ledger. Candidate validation/timing has a 1 GPU-hour budget; reserve 1 GPU-hour for final testing/demonstrations, for a planned ceiling of 10 GPU-hours excluding setup.

**Rationale**: Tests small-object benefits versus latency without another training campaign. Thresholds are declared selection rules, not success promises. The final test remains independent of tuning.

**Alternatives considered**: Architecture sweeps, hyperparameter searches, and repeated holdout testing are unnecessary for the bounded course scope.

## R8 — Interfaces, coursework, and remaining external prerequisites

**Decision**: Build one Python package with ordinary functions and six command handlers, no web service/database. Document shared data/class/prediction shapes for parallel work without backend protocols or a generic schema framework. Use a dataset profile/manifests, one run.json per run, predictions and metrics files, a comparison table and selected.yaml. Hash artifact/config bytes; avoid linked record digests, registries and lifecycle engines. Internal test helpers replace a public fixture generator; focused data/metric tests plus one opt-in smoke replace duplicate test layers. Local ignored data/artifacts/external directories hold large outputs; tracked summaries provide retrieval instructions. Keep `docs/course-deliverables.md` separate from Spec Kit quality checklists.

**Rationale**: Avoids external service orchestration and makes interfaces reviewable. Requirements FR-001–036 define a 36-item required completion inventory with evidence; FR-037–039 are excluded stretch scope. Report completion as satisfied requirements/36, explicitly a requirement count rather than effort or guaranteed course credit. Student report authorship, account/deadline verification, and external submissions remain separate from code merge status.

**Alternatives considered**: A notebook-only implementation makes automated runs and boundaries less clear; Colab may serve as a thin launcher of the same CLI. Automatic emails/permission changes/uploads are outside this planning invocation.

**Resolution status**: All technical design choices are resolved. D1 still has execution gates (install compatibility, asset availability, actual hardware and dependency lock); these are planned checks, not claimed results. Instructor identity/hosting, Canvas timezone/current deadlines, presentation deadline, and later audience feedback remain explicitly tracked external course prerequisites already identified by the spec, not unresolved implementation design.
