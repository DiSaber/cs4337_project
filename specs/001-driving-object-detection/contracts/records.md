# Record Contract v1

This is the shared on-disk contract for independently developed components. D1 implements validators; later producers/consumers add examples and focused compatibility tests. See [data-model.md](../data-model.md) for full fields, relationships and lifecycle; see [pipeline.md](pipeline.md) for algorithms. These are file interfaces, not HTTP endpoints.

## Encoding, identity, and atomicity

- UTF-8 JSON/JSONL, YAML configuration; schema_version integer 1 required. Arrays preserve declared ordering; object-key order is immaterial except canonical hashing. Reject nonfinite values and unknown enum values.
- Hash record content as sorted-key compact JSON excluding its own digest, UTF-8 without BOM; hash manifest/asset/model bytes directly. Persist the hashing/adapter/config version. Checksums are lowercase hex with an explicit algorithm.
- Paths are workspace-relative with forward slashes in records. Host/device information is separate metadata. Do not store secrets or private signed URLs. Team storage references identify how another contributor obtains the artifact.
- Write to a sibling temporary file then atomically replace only the same run's lifecycle file; promote final immutable records only on complete validation. Existing unrelated IDs cannot be overwritten.
- Required fields below are minimums; the data model defines their content. A v1 producer must not silently change coordinate/class/metric semantics. Incompatible changes require a new schema/profile version and migration guidance.

## Dataset bundle

`profile.json` MUST contain profile_id, schema_version, dataset asset identities, annotation release/adapter, synthetic boolean, class_map/hash, split rule/seed, source/eligible/selected counts, exclusions/reasons, preprocessing, three manifest references/hashes, coverage/integrity result, status=frozen, and digest. Only a validated immutable profile is usable by training.

Each `manifest.<partition>.jsonl` line contains schema_version, sample_id, source image path/hash/dimensions, source official partition, source sequence ID/provenance, project partition, annotations, source attributes, lineage and conversion/exclusion metadata. Only eligible samples appear in membership files; rejected/quarantined samples appear in a separate integrity audit.

Canonical annotation object:

```json
{"annotation_id":"object-1","class_id":0,"bbox_xyxy":[10.0,20.0,31.0,41.0],"source_category":"car","source_bbox_xyxy":[10.0,20.0,30.0,40.0],"source_inclusive":true,"clipped":false}
```

Empty `annotations: []` means a valid negative image. Canonical IDs are car=0, pedestrian=1, traffic_light=2. Box coordinates refer to original decoded images, with half-open continuous area `(x2-x1)*(y2-y1)`.

Training export: YOLO normalized center-x/center-y/width/height plus class 0–2; original-image geometry is the sole source. Empty label files preserve negatives. Train/val paths only enter the training data YAML; holdout is not passed to the trainer.

COCO export: stable integer image IDs assigned by lexical sample-ID order, category ID = canonical ID+1, bbox=`[x1,y1,x2-x1,y2-y1]`, area from canonical geometry, iscrowd=0 because ignored/crowd samples were excluded. Include all images, even negative images. Persist the ID-map/hash so predictions cannot be evaluated against a different mapping.

## Run and model bundles

`artifacts/runs/<run_id>/run.json` MUST contain schema_version, run_id/kind/status, start/end, parent/resume lineage, command argv, package/source state, resolved configs/hashes, dataset/manifest/class-map identities, initial weight/model identities, environment lock/freeze/interpreter, hardware, seed/determinism, budget/use, outputs, failure/recovery details. Final records cannot omit required reproducibility fields merely because a default was used.

`model.json` MUST contain model_id/kind, run/checkpoint/source references, checkpoint SHA-256, head class count/names, canonical mapping/hash, source-to-canonical remap when applicable, selected epoch/fitness and load check, retrieval locator. Model kind is `reference_coco` or `trained_project`. A reference 80-class COCO head filters source IDs 2=car, 0=person, 9=traffic light to project IDs 0,1,2; all other head outputs are excluded. A trained three-class head maps directly. Unknown head metadata is an error, not inferred from filename.

## Prediction bundle

Prediction metadata records prediction_set_id, model/checkpoint/config/profile/manifest hashes, input kind/partition, preprocessing and NMS thresholds/caps, coordinate convention, expected/completed/failed counts, output references and status.

Each JSONL line is one expected image or decoded video frame, including zero-detection cases:

```json
{"schema_version":1,"input_id":"clip-a:000000","frame_index":0,"timestamp_ms":0.0,"width":1280,"height":720,"status":"completed","predictions":[{"detection_id":"d0","class_id":2,"score":0.91,"bbox_xyxy":[100.0,80.0,120.0,140.0]}]}
```

Images use `sample_id` for manifest inputs and an input identity/hash for independent files; frame_index/timestamp are omitted for still images. Sort input records by manifest order or frame index. Sort detections by descending score, then class ID and box coordinates for ties. Scores must be finite in [0,1]. Failed frames use status=failed with reason and may not masquerade as empty predictions. Preserve source video frame rate/dimensions when supported; disclose re-encoding and validate emitted frame count/readability.

AP-floor predictions and annotated display outputs have separate thresholds in metadata. Evaluation cannot consume a display-filtered set and claim full low-floor AP. Partial prediction sets are not reportable evaluations.

## Evaluation, timing, and selection bundles

`evaluation.json` MUST contain evaluation_id/purpose/partition, profile/manifest/model/config/prediction hashes, implementation version, matching/IoU/recall/area/maxDet settings, sample/negative/object/per-class counts, metrics, null_reasons, timing reference, selected example references/limitations, status and digest.

Metrics have named fields `map_50`, `map_50_95`, `precision_micro`, `recall_micro`, `tp`, `fp`, `fn`, and `per_class` keyed by canonical class ID with AP/P/R and counts. Values lie in [0,1] or are null with reasons. COCO average recall must not be mislabeled as operating-point recall. Missing expected classes trigger coverage failure even if an evaluator averages the remaining classes.

`timing.json` records protocol version, model/config/validation image-list hashes, device/hardware/driver, precision, batch/input size, warm-up count, measured count, stage inclusions, CUDA synchronization policy, per-image/per-stage samples or retrieval reference, median/p95 ms and images/s. Compute-only selection latency and complete wall-time speed are separately named. Throughput is measured count/total measured duration, not an average of instantaneous FPS.

`core-gate.json` contains model/profile/config identities and verified setup, preparation, completed baseline, image/video inference, validation/timing/example references. It states whether evidence is real or synthetic/reference-only; only real integrated evidence permits D6/D9.

`comparison.json` contains comparison_id/hypothesis/status, baseline and candidate model/config/eval/timing hashes, common validation membership, budgets, failures, declared rule, chosen configuration and rationale. Incomparable inputs cannot produce an ordinary successful choice.

`selection.json` contains selection_id, comparison/core-gate references, selected model/inference/evaluator/environment hashes, profile/class map and val/test manifest hashes, deterministic decision, frozen_at and digest. `test-exposure.json` is created before any final evaluation begins and binds selection/test hashes, first exposure time, attempt IDs and outcomes. Final/reproduction records reference it. It is audit state, not an access-control boundary against arbitrary direct file inspection.

## Course and optional capture records

`docs/course-deliverables.md` uses one row per required FR-001–036 with owner/status/evidence/review date and distinct external-action rows. It includes the original account/hosting conflict, verified resolution, current deadlines/timezones, all contributors/roles, report and presentation/source links, access tests, designated submitter, receipts/comments, and Top 10 follow-up. Optional FR-037–039 are separate. A percentage must name satisfied-count/36 and explain that requirements differ in effort.

Capture JSON records schema_version, capture_id, input path/hash, known/unknown camera and scene metadata, ground-truth availability, model/prediction/evaluation references, observational limitations and optional status. No metric is populated from unlabeled footage.

## Compatibility checks

D1 provides valid/invalid small record examples and validators for shared shapes. D2 checks dataset export/import roundtrips; D3/D4 verify model metadata and mappings; D5 checks evaluation input completeness/hashes and metric semantics; D6 verifies immutable selection and exposure guards. Do not generate elaborate HTTP/OpenAPI scaffolding for this file-based project.
