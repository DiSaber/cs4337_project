# Data Model: Driving Scene Object Detection

This design defines file-backed entities for [plan.md](plan.md). There is no database. Concrete serialization and identifiers are in [contracts/records.md](contracts/records.md); algorithm rules are in [contracts/pipeline.md](contracts/pipeline.md).

## Common validity and identity

All records have `schema_version=1`, a nonempty ID, UTC timestamps where applicable, and an explicit status. JSON uses finite numbers only; undefined quantities are `null` with a reason, never NaN or evaluator sentinel -1. Hashes are lowercase SHA-256 hex. Canonical digest input is UTF-8 JSON with keys sorted, compact separators, no NaN, and the digest field itself excluded. JSONL membership files use deterministic sample-ID order and LF newlines; their digest is of actual file bytes. Hash-bearing records are immutable after completion; changes create a new ID/record.

Paths in stored records are relative to the workspace root, never credentials or session-specific download URLs. A transferable artifact locator can reference team storage in a compact tracked summary. Links/access evidence must be sufficient for another teammate; local absolute paths are not the only handoff reference. Different content cannot reuse an existing ID/output directory.

## Asset

**Fields**: asset_id, kind (dataset_images/dataset_labels/model_source/initial_weights), source URL or public source identifier, source version/commit, license/citation references, expected checksum (algorithm/value if published), measured SHA-256, expected members, local relative path, size, acquired_at, validation result, manual prerequisites, status.

**Relationships**: DatasetVersion references image/label Assets. ModelArtifact and ExperimentRun reference source/weight Assets.

**Validation**: Verify published checksums where present, extracted members/readability, source commit and asset type. If no published SHA exists, first acquisition records the observed identity and provenance; subsequent uses must match the accepted identity. Reject unsafe archive paths outside the destination. Staging remnants do not count as ready assets.

**Transitions**: missing → acquiring → verified; acquiring → failed/interrupted; failed/interrupted → acquiring on explicit retry. Valid verified assets are reused. A digest mismatch needs a new asset identity or reacquisition; never overwrite accepted content silently.

## DatasetVersion and DatasetProfile

**DatasetVersion fields**: dataset_id, provider BDD100K, annotation release (`det_2020` default), asset references/hashes, source partition metadata, adapter version, source coordinate convention, terms/citation references.

**DatasetProfile fields**: profile_id, dataset_id, class-map ID/hash, inclusion/exclusion rules, split algorithm/version/seed, requested/actual sequence/image counts, preprocessing definition, selected sequence IDs, manifest paths/hashes, summary/integrity result, created_at, status, synthetic flag.

**Relationships**: A profile contains Samples and three PartitionManifests. Runs reference a frozen profile digest, not an editable YAML path alone.

**Validation**: Profile freeze requires valid assets, requested eligible counts, all target classes in every partition, zero sequence/content overlap, and no unresolved invalid records entering the selected subset. Include raw and post-exclusion counts and negative-image counts. Synthetic smoke profiles use separate IDs and can never be cited as baseline accuracy.

**Transitions**: draft → validated → frozen. Validation failure keeps draft with reasons. Frozen content cannot mutate; changed membership/annotations/rules create a new profile ID/digest before training.

## ClassMap

**Fields**: class_map_id, canonical classes (`0:car`, `1:pedestrian`, `2:traffic_light`), version-specific source aliases, known excluded classes, ignored-region policies, COCO export mapping (`0→1`, `1→2`, `2→3`), optional pretrained-reference head mapping.

**Validation**: Canonical IDs are contiguous and stable. Preserve a version-declared mapping for every encountered source category; unknown strings quarantine samples. No silent merging of rider/truck/bus into required classes. A reference-COCO detector has an explicit remapping and is labeled reference-only.

## Sample and Annotation

**Sample fields**: sample_id, dataset/profile identity, original relative image path and SHA-256, decoded width/height, source official partition, source video/sequence ID, provenance method, optional parent IDs, annotations, weather/scene/timeofday if supplied, excluded-category counts, eligibility status/reasons, project partition.

**Annotation fields**: annotation_id unique within sample, source category/coordinates, canonical class ID, canonical bbox_xyxy, source attributes (occluded/truncated/etc.), geometry conversion/clipping record, computed area.

**Validation**: Canonical box is half-open continuous coordinates with `0<=x1<x2<=width`, `0<=y1<y2<=height`. Inclusive source x2/y2 become exclusive by adding 1 once; clip to decoded dimensions with a logged adjustment, rejecting nonfinite/inverted/empty boxes. One-pixel source boxes must have positive area. Keep valid negative samples with annotations `[]`. Samples containing ignore/crowd regions are excluded wholesale for this initial profile; preserve why rather than converting ignored targets into negatives.

**Sequence identity**: Explicit videoName wins; otherwise only the documented single-keyframe archive allows full filename stem as source-video identity, with provenance recorded. Parent/derived samples inherit the sequence partition. Exact image-content duplicates cannot cross partitions; duplicate identities are quarantined before selection.

## PartitionManifest

**Fields**: profile_id/digest, partition (train/val/test), ordered sample membership, sample/source sequence counts, per-class object/image counts, negative-image count, byte digest, geometry/class-map versions, export references.

**Relationships**: Project train derives from eligible official train; project val/test derive from different sequences of eligible official val. The official unlabelled test set is not used for project accuracy.

**Validation**: A sample appears once; sequences, parents, and content duplicates do not cross partitions. Coverage checks occur before freeze. New-scene demonstration input is not automatically a new evaluation partition.

## ExperimentRun

**Fields**: run_id, kind (smoke/baseline/candidate/final/reproduction), dataset/profile/manifest hashes, class-map hash, model source/weight identities, resolved training and inference config/hashes, command argv, package/source commit and dirty indicator, interpreter/dependency lock and freeze, seeds, hardware/device/driver, nondeterminism settings/notes, start/end time, status, budget/actual resources, history/checkpoint/output references, failure reason.

**Relationships**: Training runs create ModelArtifacts; evaluation/prediction records reference a model and run. A candidate may reference the same baseline model with a different inference configuration.

**Validation**: Required reproducibility fields cannot be omitted on completed reportable runs. A baseline uses only train/validation. A new output ID is required rather than overwriting an existing run. A planned retry/resume keeps lineage and records optimizer/scheduler/seed state and changed circumstances.

**Transitions**: planned → running → completed/failed/interrupted. Budget exhaustion → interrupted. Continuing an interrupted run records resume provenance; a fresh retry gets a new run ID. Status updates are atomic; no partially written record can appear completed.

## ModelArtifact

**Fields**: model_id, kind (reference_coco/trained_project), training_run_id if trained, architecture/source commit, initial-weight asset, checkpoint relative path/hash, canonical class-map hash, source-head IDs/names and remap, selected epoch/validation fitness, load verification, retrieval locator, status.

**Validation**: A trained artifact has exactly the declared three-class mapping. A reference checkpoint may have an 80-class head but must declare filtering/remapping. Load checks validate metadata, hash, and head compatibility before use. A local filename such as best.pt alone does not identify a model.

## PredictionSet

**Fields**: prediction_set_id, run/model/config identities and hashes, source kind (manifest/images/video), partition/profile when applicable, image-size/letterbox/NMS/score/cap settings, ordered input records, annotated output references, status/failed inputs.

**Per-input fields**: sample_id or input_id, optional video frame index and timestamp, source digest, original dimensions, predictions array of detection_id/class_id/score/bbox_xyxy, processing status and reason. Predictions are restored to original-image canonical coordinates. Empty predictions `[]` are valid; a missing record is a processing failure, not an empty result.

**Validation**: Finite score in [0,1], valid project class and box, consistent frame ordering/dimensions. AP evaluates every expected image including negatives/empty outputs. Incomplete sets cannot produce a completed reported evaluation. A visualization threshold does not overwrite the low-floor AP predictions.

## EvaluationRecord and ComparisonRecord

**Evaluation fields**: evaluation_id, model/profile/prediction/config hashes, partition/purpose, metric implementation/version, IoU/recall/maxDet/area settings, class/sample counts, aggregate and per-class AP/P/R, TP/FP/FN, null reasons, timing protocol/device/precision/stage statistics, example pointers and limitations, output digest/status.

**Comparison fields**: comparison_id, hypothesis, baseline/candidate configuration/evaluation IDs, common validation membership and timing conditions, budget/status, selection rule, measured tradeoff, choice/reason.

**Validation**: AP and operating-point recall are different measures. A zero denominator yields null/reason; absent classes fail the reportable profile's coverage gate. Comparisons cannot use test metrics or differing membership without explicit non-comparable status. Missing/worse candidate results remain preserved and cannot become invented improvements.

## SelectionFreeze and FinalTestRecord

**Freeze fields**: selection_id, comparison_id, selected model hash, profile and val/test manifest hashes, inference/evaluation config hashes, environment lock, frozen_at, rationale, immutable digest, test-exposure status.

**Final record fields**: final_run/evaluation ID, selection digest, exact selected configuration, test manifest digest, start/end, result/status, exposure timestamp, reproduction/exploratory designation.

**Validation**: Final evaluation requires a pre-existing valid freeze, exact hashes, completed core gate and candidate decision, and matching test manifest. Record exposure when evaluation begins, including failed attempts; do not pretend a failed run left a tunable holdout untouched. An exact reproduction may follow; changed model/settings after exposure require a fresh untouched holdout or explicit exploratory status.

**Transitions**: comparison_ready → selection_frozen → test_started → test_completed/test_failed. Tuning after exposure cannot reset exposure; it changes the interpretation of later results.

## CourseDeliverable and CaptureRecord

**Course fields**: requirement/deliverable ID, required versus stretch, student owner, contributors/roles, source instruction, target date/time/timezone and verification status, material/source path or access-controlled link, review evidence/date/reviewer, status (pending/partial/verified/submitted/blocked_external), external action, submission receipt/pointer, instructor identity/hosting resolution.

**Validation**: D7/D8 material PRs can merge while external actions remain pending. FR-001–036 form a transparent 36-item required inventory; optional FR-037–039 never inflate it. The checklist must not claim external submission/access from code completion alone. A report remains student-authored; do not store generated report prose as a substitute.

**Capture fields**: capture_id, local footage path/hash, team-captured flag, date if known, mounting/viewpoint, camera/settings/resolution/fps or explicit unknown, scene/weather/lighting, source/training differences, annotation availability, inference/evaluation references, limitations, stretch status.

**Validation**: Quantitative capture accuracy requires labels and the evaluation contract. Uncontrolled scenes support observations, not camera-setting causal claims. Unknowns and skipped work remain explicit.
