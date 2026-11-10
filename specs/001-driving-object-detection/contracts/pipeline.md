# Pipeline Rules

These rules preserve correctness while keeping the implementation small. Use direct functions and the six commands in [cli.md](cli.md), with the small files in [records.md](records.md).

## Data preparation

1. Verify asset source/version, published checksum where available and extracted members; reject unsafe archive extraction paths. Accept authorized existing archives with the same checks. Keep verified assets and restart only incomplete downloads.
2. Use BDD100K 100K keyframes with Detection 2020 annotations. Reject an unexpected annotation release rather than silently substitute it. Record source/eligible/excluded counts. Decode image dimensions and check annotation correspondence.
3. Canonical classes: car=0, pedestrian=1, traffic_light=2. Map source traffic light to traffic_light, person to pedestrian where the declared version supports it, ordinary van/caravan aliases to car, and bike/motor aliases to excluded bicycle/motorcycle. Count ordinary non-target classes without treating them as targets. Unknown categories quarantine samples.
4. Exclude whole images containing ignored-region categories (other person, other vehicle, trailer) or explicit ignore/crowd boxes; disclose this simplification. Retain ordinary occluded/truncated target boxes and valid negatives. Missing annotation records are errors; explicit empty labels are negatives.
5. Convert source inclusive xyxy to half-open [x1,y1,x2+1,y2+1] once. Reject nonfinite/reversed coordinates; intersect with decoded image bounds, log clipping, reject empty intersections and retain source boxes. Both YOLO/COCO exports derive from this geometry.
6. Use explicit videoName if present, otherwise full filename stem only for the documented one-keyframe-per-video archive. Quarantine ambiguous provenance, duplicate sequence identities and exact duplicate image content before selection. Do not use arbitrary filename prefixes as sequence identity.
7. Rank eligible sequences by SHA256(UTF8("cs4337-v1:4337:"+sequence_id)), tie-breaking lexically. Take first 5,000 from official train. From official labeled val, first 1,000 become project val and next 1,000 become project test. Keep negatives; do not select only target-bearing scenes.
8. Check requested counts, all target classes in each evaluated partition and zero sequence/content/parent overlap before freezing manifests. Fix failures with a recorded new profile before training; never change membership in response to model results. Training gets only train/val exports. The holdout is a project subset, not the official BDD benchmark.

Preparation performs these checks itself and records counts and reasons; a separate validation command/service is unnecessary. A reviewer checks those records and a few label overlays from the real run.

## Training and inference

Call the pinned external YOLO train module with argument arrays, not interpolated shell strings. Disable runtime dependency installation (YOLOv5_AUTOINSTALL=false) and unrequested trackers. The train module writes an ordinary run record, captures resolved upstream settings/logs and locates the selected checkpoint. No backend protocol or custom resume controller.

Baseline: 20 epochs, size 640, batch 8, seed 4337, workers 0, one GPU and <=8 GPU-hours. Choose batch 4/2 before the reported run if required; preserve effective batch/accumulation/LR behavior. Use SGD lr0=0.01, lrf=0.01, momentum=0.937, weight_decay=0.0005, warmup_epochs=3.0 and remaining values from pinned hyp.scratch-low.yaml, fully saved. Disable early stopping within the planned run and autoanchor. Select by upstream validation fitness 0.1*AP50+0.9*AP50:95, earliest epoch for ties. Never use test data for training or checkpoint choice.

Training augmentation: horizontal flip 0.5, HSV gains 0.015/0.7/0.4; disable mosaic, mixup, copy-paste, translation, scaling, rotation, shear, perspective and vertical flip. Seed Python/NumPy/torch/CUDA and request deterministic behavior where supported; disclose exceptions. Budget interruption remains interrupted rather than completed.

Inference uses the direct YOLO loader/NMS functions. Validate checkpoint head names and class count. A trained head uses the canonical classes. An explicitly marked reference COCO head maps source 2→car 0, source 0→pedestrian 1, source 9→traffic_light 2 and filters other classes. Reference results are development aids, not a trained baseline.

Decode/channel-convert correctly, deterministic aspect-preserving square-letterbox, infer in FP32, use class-aware NMS IoU 0.6, confidence floor 0.001 and cap 300 detections/image. Restore/clamp predicted boxes to original-image coordinates; reject invalid boxes with diagnostic counts. Display threshold 0.25 does not truncate AP predictions.

Save complete image/frame records, including empty detections and explicit errors, plus annotated media. Check output video can be reopened with expected dimensions/frame count; missing encoders and partial processing are failures. No live stream or GUI requirement.

## Evaluation and manual verification

Use pycocotools bbox COCOeval: IoUs 0.50:0.05:0.95, 101 recall points, all sizes, maxDets=[1,10,100]. Report aggregate/per-class AP50 and AP50:95, sample/class coverage and exact settings. Include every expected image, including negatives and empty predictions. Reject incomplete membership; normalize undefined/sentinel results to null with a reason. Missing expected classes fail actual-profile coverage.

For fixed P/R, take the top 100 post-NMS predictions/image, retain score>=0.25, and greedily match within class/image by descending score to an unmatched GT with maximum IoU>=0.50. Break score ties by class/box and equal IoU ties by annotation ID. TP is a match, unmatched prediction FP, unmatched GT FN. Report per-class and aggregate micro P=TP/(TP+FP), R=TP/(TP+FN); zero denominators are null/reason. Do not relabel COCO average recall or YOLO's selected-F1 P/R as this fixed operating point.

There are no automated tests (constitution Principle VII). Verification uses normal runs and manual review:
- Data: review preparation's recorded counts and reasons (unknown/ignored/invalid annotations, negatives, provenance/duplicate overlap, class coverage), a few label overlays including a small or edge box, and identical manifest hashes on a repeat run.
- Metrics: on a few evaluated images (including a no-object image where available), a reviewer draws labels and predictions, hand-counts matches, misses, false detections and duplicates under the rules above, and compares them with the reported counts. A duplicate ranked after full recall need not reduce interpolated AP but is FP at the operating point.

One short smoke training run uses the normal `train` command (one epoch, size 320, batch 2) on the prepared data before the baseline. Its checkpoint is then run through `infer` and `evaluate` to connect the pipeline early. Never treat its accuracy as a project result. Repeat it only when the connected pipeline materially changes.

Check setup reuse/failure recovery and inspect output media by running the commands. Ordinary input/hash checks in the pipeline remain where required; they are part of the solution, not tests.

## One timing measurement

Evaluation also times inference on the first 100 samples of its evaluated partition in manifest order, using 10 warm-up iterations, FP32/batch 1. Actual-data timing requires at least 10 samples. Smoke may time fewer or leave timing unavailable without a speed claim.

Decode images before the measured interval; start the timer before preprocessing and stop after NMS. Include preprocessing, device transfer, model forward and NMS; exclude disk decoding, drawing and encoding. Synchronize CUDA before/after the interval. One total elapsed duration yields mean ms/image and images/s; record sample-list hash/count, warm-up, device/hardware, input size, batch/precision and boundaries. No per-stage instrumentation, p95 traces or separate benchmark command. This is inference-pipeline speed, not complete video-processing throughput.

The baseline/candidate comparison uses the identical validation sample list/device/precision/environment. Final test timing uses its own declared samples and is not used for selection.

## Review, compare, and final test

A human checks that real D1–D5 evidence exists and shares model/data identities: prepared partitions, completed baseline, image/video inference, validation metrics/timing, and representative successes/failures. Record the review in ordinary experiment notes; no core-check command or core-gate record.

After that review, run evaluate twice on validation with sizes 640 and 960, same checkpoint and all other settings. Put result references and a tradeoff table in results/comparison.md. Choose 960 only if AP50:95 gain>=0.005 absolute and mean timed latency ratio<=1.5; otherwise keep 640. A failed/worse attempt stays visible; missing quantitative evidence leaves comparison status partial.

Save results/selected.yaml before final testing with chosen checkpoint/config/profile/manifests/environment paths and byte hashes, validation references, reason and recorded time. Ordinary evaluate --partition test --selection PATH checks those fields and uses only the selected configuration. Save started/completed/failed status in the same ordinary run log; do not implement an exposure ledger or lifecycle engine. A human reviews that selection preceded test inspection. Later tuning after exposure is exploratory on that holdout; exact replays are labeled reproduction.

Select at least one available success and failure per class by a repeatable rule such as first matching manifest sample. Preserve original/predicted/labeled examples and explain unavailable cases, lighting/weather/perspective/visibility limitations and untested conditions.

## Course and optional footage

D7/D8 use course checklist and reviewed materials with pending human submissions/access/follow-up explicit. Students author report prose. D9 reuses infer and, only if labeled, evaluate with an independent capture profile; ordinary experiment notes hold camera/scene conditions and unknowns. No capture-registration command or new storage system.

