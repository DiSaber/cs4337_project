# Data Model: Driving Scene Object Detection

This is a small file-based research pipeline. These concepts describe the data already needed by the work, not separate classes, schema engines, repositories, or state machines. See [records](contracts/records.md) for file shapes and [pipeline rules](contracts/pipeline.md) for processing.

## External assets

Keep one asset inventory with type, public source, version/commit, published checksum if available, measured SHA-256, expected extracted files, local path, citation/terms reference, and verification outcome. It covers BDD images/Detection 2020 labels, the pinned YOLO source, and initial weights.

Reuse verified files. Incomplete downloads remain unverified; retry their temporary files without damaging valid assets. Authorized existing archives undergo the same checks. Record manual access prerequisites and keep secrets out of configuration/logs.

## Prepared dataset

A profile describes source asset identities, annotation version, class mapping, conversion/preprocessing rules, split seed/selection policy, selected counts, exclusions, integrity outcome, and manifest/export paths and byte hashes.

Each sample records image identity/path/hash/dimensions, source official partition, source video/sequence identity and provenance, project partition, annotations and available scene attributes. Source annotations retain category/box/occlusion/truncation and any clipping/conversion note. Children inherit the parent sequence partition if derived images are ever used.

Canonical classes are car=0, pedestrian=1, traffic_light=2. Convert inclusive source endpoints once to half-open continuous boxes with positive area inside decoded image dimensions. Annotations=[] is a valid negative; missing annotations are not assumed negative. Exclude samples with ignore/crowd regions for the initial simplified profile and disclose counts. Unknown classes/provenance and invalid boxes quarantine samples.

Freeze the profile/manifests before training. Check zero sequence/content overlap, all three classes in each evaluated partition, and sufficient eligible samples. Changes require a new profile, not silently changing a reported dataset. The default is 5,000 train / 1,000 validation / 1,000 heldout; the heldout comes from official labeled validation and is not the official BDD test benchmark.

## Runs and model identity

Each run directory has a single run.json with command, kind, status, timestamps, resolved settings, data/manifest identities, model source/initial weights/checkpoint identity, dependency versions, interpreter, seeds, hardware, nondeterminism, budget/use, output references and any failure reason. Preserve configuration files, upstream logs/history and checkpoint byte hashes alongside it.

Training uses train/validation only and records chosen checkpoint/epoch and validation selection rule. The checkpoint's head names/count must agree with the project classes; an explicitly marked reference COCO checkpoint uses a documented remapping. No separate model registry or model.json is required.

Do not overwrite existing run directories. Use status=completed/failed/interrupted in run.json; a retry gets a new ID. If manual upstream recovery is used, record its checkpoint/command and limitations in that run. Custom resume orchestration is outside required scope.

## Predictions and evaluation

Predictions have one record per expected image or decoded video frame, including valid empty detections, with original dimensions, identity/frame index, status, canonical class/score/box values and any error. Restore predictions to original-image coordinates. AP retains low-confidence predictions separately from display filtering.

metrics.json contains data/model/config identity references, metric definitions/counts, aggregate/per-class AP and fixed-threshold P/R, undefined-value reasons, one timing summary, examples and limitations. Reject incomplete evaluation inputs. Undefined values are null with reasons, not NaN or evaluator sentinel values.

The timing summary records device/hardware, input size, batch/precision, sample list/count, warm-up, included/excluded stages, elapsed time, mean ms/image and throughput. It does not require per-stage traces or percentiles.

## Comparison and final selection

Two ordinary validation results feed a human-reviewed comparison table. A small selected.yaml records chosen checkpoint/hash, frozen profile/manifest hashes, resolved evaluation config/hash, environment reference/hash, validation result references, choice reason and recorded time. Save it before final test evaluation.

The test command checks the selection's fields against actual inputs. Ordinary run logs identify test attempts, including failures. Further tuning after seeing test results is exploratory on that holdout; an exact rerun is labeled reproduction. No special exposure record or lifecycle engine is required.

## Course and capture information

The course checklist tracks required FR-001–036 ownership/status/evidence, roles, materials/links, verified dates/timezones, access and actual submission/follow-up actions. Optional FR-037–039 are separate. A merged materials PR does not prove an upload happened; students write report prose themselves.

If D9 is attempted, ordinary experiment notes record footage path/hash, team capture, viewpoint, known/unknown settings, resolution/frame rate, scene conditions, model/config and output references, labels if any, and observational limitations. Reuse infer/evaluate; no capture-registration product is needed.

