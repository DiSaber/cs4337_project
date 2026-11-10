# Implementation Plan: Driving Scene Object Detection

**Branch**: `main` (actual branch at planning); feature context `001-driving-object-detection` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: The complete project specification. Revised after the user's scope review to minimize implementation and review work. The nine deliverables and all 39 requirements remain; this document plans their implementation without creating tasks or application code.

## Summary

Build a small Python package with direct wrappers around pinned YOLOv5 training/inference and pycocotools evaluation. Prepare a fixed three-class BDD100K subset, train one baseline, demonstrate image/video inference, compare two inference sizes, and evaluate the selected configuration on held-out data. Keep report/presentation handoffs separate and dashcam work optional.

Use ordinary functions, a few configuration files, and small run records. Core acceptance and candidate selection are documented reviews. No backend framework, plugin registration, generic schema validator, experiment orchestrator, custom resume system, or exposure-tracking service is required.

## Technical Context

**Language/Version**: Allow Python 3.10–3.14, including user-reported Colab 3.13 and observed local 3.14.7 / 3.10. Record the actual interpreter build; allowed metadata is not full pipeline verification.

**Primary Dependencies**: YOLOv5 v7.0 source commit `915bbf294bb74c859f0b41f1c23bc395014ea679`; package bounds are torch >=2.5.1,<3, torchvision >=0.20.1,<1, numpy >=1.26.4,<3, Pillow >=9.5.0,<13, opencv-python >=4.10.0.84,<5, PyYAML >=6.0.2,<7, and pycocotools >=2.0.10,<3. Resolve a matched torch/torchvision pair with wheels for the actual interpreter/device; do not force the old Python-3.11 pins onto newer interpreters. D1 verifies imports/checkpoint loading and records exact tested environment locks. Address modern torch checkpoint-loading defaults and removed Pillow APIs at the pinned YOLO integration points, then verify training with the D3 smoke run. Disable upstream automatic installation and unrequested external trackers. Preserve licenses and citations.

**Storage**: Local files. Ignore `data/`, `external/`, `artifacts/` and credentials. Track configurations, compact summaries, references, and instructions to retrieve team-accessible large artifacts. Hash assets, dataset manifests, checkpoints and saved resolved configs for identity; do not build a linked graph of record digests.

**Testing**: No automated tests, test fixtures, or test dependencies (constitution v2.0.0 Principle VII, revised 2026-11-10). Verify by running the real commands and manually reviewing their outputs: preparation's built-in integrity checks and label overlays (D2), one short labeled smoke training run before the baseline (D3), image/video/empty/invalid inference runs (D4), and a hand count of matches on a few evaluated images (D5). No repeated training as a routine PR check.

**Target Platform**: Single NVIDIA GPU/Linux or Colab for reported training; local Windows CPU setup checks. User confirmed this target. Choose the CUDA wheel profile for the resolved torch version and actual GPU/driver; CUDA 12.1 was the original Python-3.11 proposal, not a fixed requirement. Keep a tested environment file for each execution platform used, without a broad cross-platform CI matrix.

**Project Type**: One CLI package with six commands: assets sync, check, data prepare, train, infer, evaluate. No web service/database.

**Performance Goals**: Measure accuracy and speed without inventing a target. Baseline: size 640, batch 8, 20 epochs, seed 4337, at most 8 GPU-hours including training validation. Choose batch 4/2 before the reported run if needed and record it. Allow up to 1 GPU-hour for the validation comparison and reserve 1 for final testing/demonstrations; record actual use and any incomplete work. Smoke: one small CPU epoch at size 320/batch 2, never accuracy evidence.

**Constraints**: Core D1–D5 before optimization/stretch; sequence-disjoint partitions; select on validation before test; idempotent asset setup; student-authored three-page report; 5–10 minute presentation. Saved report deadline December 2, 2026, 11:59 p.m. requires current Canvas/timezone verification.

**Scale/Scope**: 5,000 eligible training sequences/images from official train, 1,000 project validation and 1,000 project test from official labeled val. Three classes: car, pedestrian, traffic light. One baseline, one inference-size candidate, one final selected configuration.

## Constitution Check

PASS means the design supplies controls, not that experiments or submissions have occurred.

| Gate | Design status | Control and evidence |
| --- | --- | --- |
| I Reproducible experiments | PASS | Dataset/manifest identities, preprocessing, model/initial weights, tested versions, seeds, settings, commands, hardware and nondeterminism in a run record |
| II Reliable evaluation | PASS | Disjoint frozen splits, built-in preparation integrity checks, manual metric review, validation-only selection, recorded selection before final test, defined AP/P/R and timing |
| III Core first | PASS | D1–D5 integration reviewed before D6/D9; D9 has no required dependents |
| IV Evidence for claims | PASS | Preserved results, checkpoint/config identities, successes/failures and limitations; failed attempts remain visible |
| V Simple implementation | PASS | Direct established-library calls, six command handlers, local files, small checks; no general framework |
| VI Integrity/AI transparency | PASS | Citations, per-task AI log, student report authorship |
| VII No added tests | PASS (revised 2026-11-10) | No test modules, fixtures or pytest; normal runs plus manual review of outputs |
| VIII–XI Workflow, comments, plain English, prior assignments | PASS | Applied per change: small reviewed commits, `AI: `/`SAMPLE: ` comment prefixes, plain wording, consult existing course work |
| Course constraints | PASS | Separate course checklist with roles, access, deadlines, submissions, conflicts and audience follow-up |

The authorized simplification preserves constitutional requirements and needs no governance amendment. Data access, actual environment compatibility, and course confirmations remain execution prerequisites.

## Project Structure

### Documentation (this feature)

```text
specs/001-driving-object-detection/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── contracts/
    ├── cli.md
    ├── records.md
    └── pipeline.md
```

`tasks.md` is generated later by `$speckit-tasks`.

### Source Code (proposed)

```text
pyproject.toml
requirements/                  # tested CPU/GPU environment files
configs/
├── assets.yaml
├── data/bdd-subset.yaml
├── train/baseline.yaml
└── evaluation/
    ├── default.yaml           # size 640
    └── size-960.yaml
src/driving_detection/
├── __init__.py
├── __main__.py                # ordinary argparse dispatch
├── assets.py
├── data.py
├── train.py
├── infer.py
├── evaluate.py
└── records.py                 # only shared I/O/config/hash helpers actually used
docs/
├── usage.md                   # setup, inputs, outputs, experiments
├── references.md
├── ai-use-log.md
├── course-deliverables.md
├── report/
└── presentation/
results/                      # small summaries, selected.yaml, artifact retrieval pointers
data/                         # ignored datasets/prepared data
external/                     # ignored model source/initial weights
artifacts/                    # ignored run outputs/checkpoints/media
```

**Structure Decision**: One module per pipeline concern keeps PR ownership clear. Use direct function calls and delayed heavy imports where necessary. The short file contracts are documentation for parallel work, not a reason to create an abstraction or validation framework.

## Research and design outputs

[research.md](research.md) retains the researched model/data decisions and records the approved scope reduction. [data-model.md](data-model.md) describes the small set of persisted information. [CLI](contracts/cli.md), [records](contracts/records.md), and [pipeline](contracts/pipeline.md) documents specify inputs, outputs and domain rules. [quickstart.md](quickstart.md) describes future verification commands; none have been executed during planning.

## Delivery sequence and PR acceptance

Each PR includes appropriate verification, usage updates, citations and its AI-use entry. Verify materially changed source/metric behavior by running it and reviewing the outputs; add no automated tests.

| Unit / requirement ownership | Implementation scope | Evidence required to merge |
| --- | --- | --- |
| D1 / FR-001–004 | Packaging/CLI skeleton, asset download/import and reuse, tested environment notes, ignored paths and setup docs | Fresh/repeat setup and failed-download recovery checks; imports/official checkpoint loading; no training compatibility pipeline duplicated here |
| D2 / FR-005–010 | BDD conversion, class mapping, geometry, eligible subset, split/manifests and YOLO/COCO exports | Built-in integrity check results, reviewed label overlays, repeatable manifests, real preparation counts and class coverage |
| D3 / FR-011–014 | Direct upstream training wrapper, resolved settings and compact run record | A short labeled smoke training run, then the completed declared GPU baseline, loadable checkpoint and reproducibility evidence |
| D4 / FR-015–017 | Direct inference/NMS wrapper, canonical predictions, image/video outputs and error handling | Image/video/empty/invalid examples; baseline integration verified when D3 is available |
| D5 / FR-018–022 | Established AP evaluator, fixed P/R counts, one timing measurement, examples | Hand-checked match counts on a few evaluated images, baseline validation results and timing; manual review confirms integrated D1–D5 evidence |
| D6 / FR-023–025 | Two ordinary validation evaluations, comparison table, selected configuration, ordinary test evaluation | Same checkpoint/protocol/device; recorded decision before final test; preserved negative/failed attempts |
| D7 / FR-026–032 | Code handoff, completion inventory, course checklist, student report materials | Required report/code review; names/roles/references/links and pending external actions explicit |
| D8 / FR-033–036 | Presentation materials/rehearsal, upload handoff, audience answers | Four topics, 5–10 minute readable/audible recording; submissions/follow-up pending until evidenced |
| D9 / FR-037–039 | Optional capture notes and existing inference/evaluation commands | Capture conditions, qualitative limits or real labels for accuracy, evidence or explicit skip |

**Dependencies and parallel work**: D1 → D2 → D3. D4 can develop after D1 and agreed D2 mapping using the official COCO checkpoint as a clearly marked reference. D5 metric code can develop independently of training and first runs on the D3 smoke checkpoint; actual baseline evidence needs D2/D3. D3/D4/D5 own separate modules. Manually review the integrated core before D6 or D9. D7/D8 preparation may start early; final claims use results or disclose partial completion. D9 cannot delay required work.

## Minimal verification and evidence

- No automated tests, test fixtures, or diagnostic-only scripts (Principle VII). Each deliverable is verified by running its real command and reviewing what it produced.
- Data (D2): `data prepare` performs the required integrity checks itself (readability/annotation correspondence, target/excluded/unknown labels, box conversion, valid negatives, ignored samples, sequence/content overlap, class coverage, repeatable selection) and writes counts and reasons. A reviewer inspects those counts, a few label overlays, and a repeat run's identical manifest hashes.
- Smoke (D3): one short training run with the normal `train` command (one epoch, size 320, batch 2, labeled smoke) on the prepared data, before the baseline. It confirms training compatibility only; its scores are never reported.
- Metrics (D5): pycocotools computes AP. A reviewer hand-counts matches, misses, false detections and duplicates on a few evaluated images (including a no-object image where available) and compares them with the reported counts. Do not test upstream model internals.
- Setup reuse/checksum failures and saved media are checked by running the commands and looking at the results.
- Keep ordinary input checks where files are consumed: class/head compatibility, required values, hashes, finite boxes/scores and complete evaluation membership. No generic schema/lifecycle test suite.
- Real measured claims require the actual GPU baseline, validation comparison and selected final test, not more synthetic tests. Full retraining is unnecessary for unrelated changes.

Keep the reproducibility fields required by FR-012 in one `run.json` beside resolved settings, logs, predictions and `metrics.json`. Hash file bytes for identity; avoid a custom canonical serialization scheme. Never overwrite an existing run directory. Preserve failed/interrupted status in the same record; restart with a new run ID rather than implement custom resume lineage.

## Selection, timing, and course handoff

Evaluation records one synchronized batch-1 inference duration over a fixed subset of its evaluated partition after warm-up; comparison timing uses identical validation samples. Its declared stages are preprocessing, transfer, model forward and NMS; decoding, drawing and encoding are excluded. Report mean ms/image and throughput, sample/warm-up counts, hardware/input/batch/precision and timing boundaries. No per-stage/p95 profiling or separate benchmark command.

Compare sizes 640/960 on the same validation membership/checkpoint. Choose 960 only if AP50:95 improves by at least 0.005 and mean measured latency is at most 1.5× baseline; otherwise keep 640. A human records the two evaluation references, choice and reason in `results/comparison.md`, and saves `results/selected.yaml` identifying checkpoint, manifests, environment and resolved config hashes before testing. Test evaluation checks those few fields against its actual inputs. Record any attempted test in the ordinary run log; no exposure ledger or custom state machine. Later tuning cannot be reported as unbiased testing on the same holdout.

`docs/course-deliverables.md` tracks FR-001–036 with owner/status/evidence and satisfied-count/36, explicitly a requirement count rather than effort/grading credit; optional D9 is separate. Track the three-page report, roles/front page, citations/links/access, verified deadlines/timezones, one report submitter, upload/comments evidence, presentation recording/slides/video link/incognito playback and Top 10 responses. Keep account/hosting conflicts and pending human actions visible. Students author the report and perform external actions unless separately authorized.

## Complexity Tracking

No constitution exceptions. Do not reintroduce a backend protocol, generic schema framework, command registry, experiment orchestrator, custom resume/exposure machinery, fixture-generation CLI, or any automated test suite during task generation. Add structure only when an implemented requirement demonstrates the need.

