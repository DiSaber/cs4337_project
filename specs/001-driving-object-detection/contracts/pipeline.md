# Pipeline and Backend Contract v1

This contract freezes the semantics needed for parallel D2/D3/D4/D5 work. [cli.md](cli.md) defines invocation; [records.md](records.md) defines serialization.

## 1. Acquisition and data preparation

1. Validate public source/version/checksum and required archive members. Extract into a verified staging location with path-traversal checks; promote only complete assets. Existing authorized local archives follow the same checks.
2. Accept Detection 2020 by default; fail on unexpected annotation release rather than guess. Decode image dimensions and resolve image/annotation correspondence. Missing annotation records are errors; an explicit labels=[] record is a valid negative.
3. Map target and documented aliases to canonical IDs. Count excluded ordinary categories. Quarantine unknown categories/invalid annotations; exclude entire samples containing ignored-region categories, ignore/crowd boxes, or uncertain sequence provenance. Retain ordinary occluded/truncated target objects. Record source/eligible/excluded counts before subset selection.
4. Convert source inclusive boxes to half-open xyxy by advancing x2/y2 by one, then intersect with [0,width]×[0,height]. Record any clipping and retain source boxes. Reject source inversion, nonfinite values, and empty intersections; do not repair reversed coordinates silently. Test one-pixel boxes and image-edge behavior.
5. Determine sequence ID from explicit videoName, otherwise full filename stem only in the documented single-keyframe detection archive. No prefix heuristics. Quarantine duplicate sequence identities and exact duplicate content before selection; document counts across official pools. Transformed children inherit parent partition.
6. Rank eligible sequences by SHA256(UTF8(`cs4337-v1:4337:`+sequence_id)), tie-break by sequence_id. Select first 5,000 official-train sequences. Select first 1,000 official-val sequences for project val and next 1,000 for project test. Requested/actual image and sequence counts must match the one-keyframe profile. Retain negatives.
7. Require every target class in every partition, zero sequence/content/parent overlap, and requested eligible counts before freezing. Failure is a pretraining data-integrity error. Fix via a versioned profile/selection rule before experiments; never adjust membership in response to model results.
8. Generate one canonical manifest set, YOLO training labels and COCO ground truth from the same boxes. Trainer data YAML exposes train/val only. Freeze profile/class-map/manifest hashes and keep original images unchanged. The test portion is explicitly a project-held-out subset of official labeled validation, not official BDD benchmark results.

Synthetic fixtures use a separate profile prefix, fixed 24/12/12 partitions and known geometry; they are never treated as evidence of driving-scene accuracy.

## 2. Backend interface and training

`DetectorMetadata` declares source commit, checkpoint/hash, head classes, canonical class map/remap, model kind and trained run identity. `DetectorBackend.load(metadata, device)` validates it before inference. `predict(images, resolved_config)` accepts original decoded RGB arrays and returns canonical original-coordinate detections in input order, including empty lists. No evaluator depends on backend tensor internals.

`TrainingBackend.train(profile, initial_weights, resolved_config, run_directory)` consumes frozen train/val exports and produces status/history/checkpoint references plus verified ModelArtifact metadata. It receives no test manifest. D1 defines the metadata/protocol and lifecycle helpers; D3 implements training, D4 inference. Importing the CLI/data/evaluator must not download a model or require CUDA.

Training invokes the external pinned YOLO train module in a subprocess with argument arrays, isolated output paths and known environment. Pin required packages during setup; set upstream auto-install disabled (`YOLOv5_AUTOINSTALL=false`) and disable unrequested W&B/ClearML/Comet/network experiment integrations. Do not use moving hub code. Record upstream stdout/stderr without secrets.

Baseline resolved profile:

| Setting | Value / rule |
| --- | --- |
| Model/init | YOLOv5s v7.0, official COCO weights; replace head for three project classes |
| Training | 20 epochs, size 640, batch 8, workers 0, seed 4337, single GPU, <=8 GPU-hours |
| Optimizer | SGD, lr0=0.01, lrf=0.01, momentum=0.937, weight_decay=0.0005, warmup_epochs=3.0; remaining values from pinned hyp.scratch-low.yaml, fully resolved and recorded |
| Augmentation | HSV gains 0.015/0.7/0.4, horizontal flip 0.5; all geometric transforms, mosaic/mixup/copy-paste and vertical flip disabled |
| Preprocess | Deterministic aspect-preserving square letterbox outside seeded training augmentation; anchors fixed from pinned model, autoanchor disabled |
| Selection | Upstream validation fitness 0.1*AP50+0.9*AP50:95; earliest epoch wins ties; no early stopping within the planned run |
| Determinism | Seed Python/NumPy/torch/CUDA and worker generators; disable cuDNN benchmarking, request deterministic algorithms where supported, record exceptions and upstream behavior |
| Output | Complete resolved hyperparameters, effective batch/accumulation/LR scaling, dependency lock, logs, best/last checkpoint hashes, ModelArtifact and completion status |

Effective optimizer/LR behavior includes upstream nominal-batch accumulation and scaling; capture the effective values rather than imply that changing batch leaves training identical. A memory fallback batch is chosen before the reported run; preserve failed attempts separately. A budget timer interrupts with status=interrupted and retains recovery information. Smoke uses size 320/batch 2/one epoch/workers 0 on CPU and no autoanchor; smoke validation is synthetic only.

## 3. Inference semantics

- Decode inputs, preserve original dimensions, convert channel order correctly, letterbox to exact configured square size without training augmentation, and retain inverse scale/padding for coordinate restoration.
- Run FP32 model inference and class-aware NMS at IoU 0.6. Keep score>=0.001 and maximum 300 detections/image for metric predictions. The ordinary display/P-R threshold is 0.25 and cannot erase low-floor predictions used for AP.
- Remap reference COCO head IDs explicitly or validate trained project head. Restore/clamp predicted boxes to original bounds, discard nonfinite/empty boxes with recorded diagnostic counts, and sort by declared stable tie-breaks.
- Process image sets deterministically and video frames in order. Preserve one status record per expected input/frame. A no-detection result is completed with []; unreadable/failed frames have error status. Validate written media by reopening it and checking readable dimensions/frame count; a missing encoder is actionable failure, not a successful empty file.
- Reference-model outputs are valid integration aids, never trained-baseline evidence. Unlabeled new scenes/capture clips support qualitative inspection only.

## 4. Evaluation correctness

Use project-generated COCO ground truth and pycocotools bbox evaluation. AP settings: IoU=[0.50,0.55,...,0.95], recall=[0.00,0.01,...,1.00], area=all, maxDets=[1,10,100]. Report AP50 and AP50:95 globally and per canonical class. Every expected image appears even if it has no ground truth or predictions. Treat class-absent/sentinel outputs as undefined with reasons; coverage failure prevents a completed reportable profile.

For operating-point P/R, take each image's top 100 canonical predictions by score after NMS, then retain score>=0.25. For each class/image, visit predictions in descending score order, match the unmatched ground-truth box with maximum IoU>=0.50, and break equal-IoU ties by annotation ID. One match is TP; unmatched predictions are FP; unmatched ground truth is FN. Aggregate micro P=ΣTP/(ΣTP+ΣFP), R=ΣTP/(ΣTP+ΣFN). Per-class uses the same formula on that class. Zero denominator produces null/reason. COCO average recall is not this recall.

Required controlled cases:

| Case | Expected public outcome |
| --- | --- |
| One perfect target/prediction | AP50/AP50:95=1 for that supported class; TP1 FP0 FN0; P=R=1 |
| One missed target, no predictions | TP0 FP0 FN1; recall 0, precision null; supported-class AP 0 |
| Prediction on a negative image | FP1; no invented TP; recall undefined if no GT exists in the whole fixture |
| Two predictions for one target | First match TP, duplicate FP at the operating point; AP may remain 1 when duplicate ranks after full recall |
| Wrong-class prediction | FP for predicted class, FN for target class; no cross-class match |
| Empty inputs/results | Explicit valid-empty or no-samples status; no evaluator crash or misleading complete coverage |
| Absent ground-truth class | Null/reason for that class; reportable profile coverage gate fails |
| Exact IoU threshold | Inclusive >=0.50 match for fixed P/R; below boundary does not match |
| One-pixel/source-edge box | Canonical area/IoU agree between YOLO/COCO exports; no off-by-one drift |

Duplicate-detection metric fixtures feed canonical predictions directly to the evaluator so NMS does not hide matching errors. Normalize completely empty prediction sets before invoking backend paths that assume at least one result. The three-class subset is not claimed equivalent to the full BDD evaluator.

## 5. Timing and evidence

Benchmark the first 100 project-validation samples in manifest order (or all if fewer, minimum 10), with 10 warm-ups, batch 1 and FP32. Baseline and candidate use identical sample membership/hash, device, precision and lock. CUDA work is synchronized before/after timed boundaries. Record separately decode, preprocessing, host/device transfer+forward, NMS, rendering/encoding, and total wall duration. Selection latency is preprocess+transfer+forward+NMS. Include stage definitions, median/p95 ms and throughput based on total measured duration. If stages overlap, explain that per-stage sums may differ from wall time; default sequential implementation avoids that ambiguity.

Baseline/candidate validation evaluation uses all 1,000 validation samples; the timing subset is separate and fixed. Select at least one available success/failure per class by a declared reproducible rule (e.g. first manifest sample satisfying the case), preserving originals/predictions/labels and class-specific counts. Explain missing cases, weather/lighting/perspective/visibility limits and untested conditions. Do not choose a few visual examples as evidence of overall accuracy.

## 6. Core, candidate, selection, and holdout guards

Core acceptance binds completed real setup/preparation/baseline artifacts, image+video inference using that baseline, validation metrics/timing, and representative examples. Verify all identities and reject synthetic/reference-only records. D6/D9 require this gate; course outline/access preparation does not.

Candidate comparison reruns validation/timing at size 640 and 960 with the same checkpoint and all other settings. Choose 960 only when delta AP50:95>=0.005 absolute and median compute latency ratio<=1.5; otherwise keep 640. Candidate has <=1 GPU-hour budget. A failed/missing candidate may justify baseline retention only with an actual attempted experiment/failure record; it cannot satisfy a claim that a complete quantitative comparison was performed. Completion status remains partial if the comparison requirement is not verified.

Write immutable selection with comparison/core-gate references and exact selected model/profile/val/test/config/lock hashes before test exposure. Ordinary evaluate is val-only. final-evaluate validates selection, writes exposure state before processing, then evaluates only selected configuration on heldout. Independent inference against a recognized test manifest must use the same guard. These are workflow safeguards, not filesystem security against manual data inspection.

An exact final rerun is a labeled reproduction tied to the same selection. Changed inference/model settings after test exposure are exploratory unless a genuinely untouched holdout is established. Never delete/reset exposure after a failed test run. Failure/interruption keeps logs/status and invalidates completion claims until appropriate evidence exists.

## 7. Course and optional-capture boundary

No code generates student report prose or marks external submissions complete. D7/D8 material readiness and course submission/follow-up statuses remain distinct. Track original/verified course instructions, roles, links/access and receipts. Optional capture registration/inference is D9 only; evaluation requires actual labels. Unknown camera settings and uncompleted stretch work stay explicit.
