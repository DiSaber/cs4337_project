# Implementation Plan: Driving Scene Object Detection

**Branch**: `main` (actual branch at planning); feature context `001-driving-object-detection` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: The complete project specification. Revised after the user's scope review to minimize implementation and review work. The nine deliverables and all 39 requirements remain; this document plans their implementation without creating tasks or application code.

## Summary

Build a small Python package with direct wrappers around pinned YOLOv5 training/inference and pycocotools evaluation. Prepare a fixed three-class BDD100K subset, train one baseline, demonstrate image/video inference, compare two inference sizes, and evaluate the selected configuration on held-out data. Keep report/presentation handoffs separate and dashcam work optional.

Use ordinary functions, a few configuration files, and small run records. Core acceptance and candidate selection are documented reviews. No backend framework, plugin registration, generic schema validator, experiment orchestrator, custom resume system, or exposure-tracking service is required.

## Technical Context

**Language/Version**: Python 3.11; record the actual interpreter build.

**Primary Dependencies**: YOLOv5 v7.0 source commit `915bbf294bb74c859f0b41f1c23bc395014ea679`; initial compatibility targets torch 2.5.1 / torchvision 0.20.1, numpy 1.26.4, Pillow 9.5.0, opencv-python 4.10.0.84, PyYAML 6.0.2, pycocotools 2.0.10, pytest 8.3.5. D1 verifies imports/checkpoint loading and records tested environment versions; these pins have not been installed or tested during planning. Disable upstream automatic installation and unrequested external trackers. Preserve licenses and citations.

**Storage**: Local files. Ignore `data/`, `external/`, `artifacts/` and credentials. Track configurations, compact summaries, references, and instructions to retrieve team-accessible large artifacts. Hash assets, dataset manifests, checkpoints and saved resolved configs for identity; do not build a linked graph of record digests.

**Testing**: Focused data-integrity and metric-correctness tests, plus one opt-in CPU pipeline smoke test. Small fixtures are private test helpers. No separate contract-test layer, public fixture generator, model-architecture tests, or repeated training as a routine PR check.

**Target Platform**: Single NVIDIA GPU/Linux or Colab for reported training; local Windows CPU setup/smoke checks. User confirmed this target. CUDA 12.1 is an initial installation profile subject to actual GPU/driver compatibility. Keep a tested environment file for each execution platform used, without a broad cross-platform CI matrix.

**Project Type**: One CLI package with six commands: assets sync, check, data prepare, train, infer, evaluate. No web service/database.

**Performance Goals**: Measure accuracy and speed without inventing a target. Baseline: size 640, batch 8, 20 epochs, seed 4337, at most 8 GPU-hours including training validation. Choose batch 4/2 before the reported run if needed and record it. Allow up to 1 GPU-hour for the validation comparison and reserve 1 for final testing/demonstrations; record actual use and any incomplete work. Smoke: one small CPU epoch at size 320/batch 2, never accuracy evidence.

**Constraints**: Core D1–D5 before optimization/stretch; sequence-disjoint partitions; select on validation before test; idempotent asset setup; student-authored three-page report; 5–10 minute presentation. Saved report deadline December 2, 2026, 11:59 p.m. requires current Canvas/timezone verification.

**Scale/Scope**: 5,000 eligible training sequences/images from official train, 1,000 project validation and 1,000 project test from official labeled val. Three classes: car, pedestrian, traffic light. One baseline, one inference-size candidate, one final selected configuration.

## Constitution Check

PASS means the design supplies controls, not that experiments or submissions have occurred.

| Gate | Design status | Control and evidence |
| --- | --- | --- |
| I Reproducible experiments | PASS | Dataset/manifest identities, preprocessing, model/initial weights, tested versions, seeds, settings, commands, hardware and nondeterminism in a run record |
| II Reliable evaluation | PASS | Disjoint frozen splits, focused integrity/metric checks, validation-only selection, recorded selection before final test, defined AP/P/R and timing |
| III Core first | PASS | D1–D5 integration reviewed before D6/D9; D9 has no required dependents |
| IV Evidence for claims | PASS | Preserved results, checkpoint/config identities, successes/failures and limitations; failed attempts remain visible |
| V Simple implementation | PASS | Direct established-library calls, six command handlers, local files, small checks; no general framework |
| VI Integrity/AI transparency | PASS | Citations, per-task AI log, student report authorship |
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
tests/
├── conftest.py                # tiny generated fixtures
├── test_data.py
├── test_metrics.py
└── test_smoke.py              # opt-in, one CPU pipeline pass
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

Each PR includes appropriate verification, usage updates, citations and its AI-use entry. Materially changed source/metric behavior warrants focused checks; routine prose/config edits do not justify new test suites.

| Unit / requirement ownership | Implementation scope | Evidence required to merge |
| --- | --- | --- |
| D1 / FR-001–004 | Packaging/CLI skeleton, asset download/import and reuse, tested environment notes, ignored paths and setup docs | Fresh/repeat setup and failed-download recovery checks; imports/official checkpoint loading; no training compatibility pipeline duplicated here |
| D2 / FR-005–010 | BDD conversion, class mapping, geometry, eligible subset, split/manifests and YOLO/COCO exports | Focused integrity tests, repeatable manifests, real preparation counts and class coverage |
| D3 / FR-011–014 | Direct upstream training wrapper, resolved settings and compact run record | Completed declared GPU baseline, loadable checkpoint and reproducibility evidence; the connected CPU smoke waits until D4/D5 are available |
| D4 / FR-015–017 | Direct inference/NMS wrapper, canonical predictions, image/video outputs and error handling | Image/video/empty/invalid examples; baseline integration verified when D3 is available |
| D5 / FR-018–022 | Established AP evaluator, fixed P/R counts, one timing measurement, examples | Focused metric cases, baseline validation results and timing; manual review confirms integrated D1–D5 evidence |
| D6 / FR-023–025 | Two ordinary validation evaluations, comparison table, selected configuration, ordinary test evaluation | Same checkpoint/protocol/device; recorded decision before final test; preserved negative/failed attempts |
| D7 / FR-026–032 | Code handoff, completion inventory, course checklist, student report materials | Required report/code review; names/roles/references/links and pending external actions explicit |
| D8 / FR-033–036 | Presentation materials/rehearsal, upload handoff, audience answers | Four topics, 5–10 minute readable/audible recording; submissions/follow-up pending until evidenced |
| D9 / FR-037–039 | Optional capture notes and existing inference/evaluation commands | Capture conditions, qualitative limits or real labels for accuracy, evidence or explicit skip |

**Dependencies and parallel work**: D1 → D2 → D3. D4 can develop after D1 and agreed D2 mapping using the official COCO checkpoint as a clearly marked reference. D5 metrics can develop against tiny canonical fixtures independently of training; actual baseline evidence needs D2/D3. D3/D4/D5 own separate modules. Manually review the integrated core before D6 or D9. D7/D8 preparation may start early; final claims use results or disclose partial completion. D9 cannot delay required work.

## Minimal verification and evidence

- Automated data checks cover readability/annotation correspondence, target/excluded/unknown labels, inclusive-to-half-open box conversion, valid negatives, ignored samples, sequence/content overlap, class coverage, and repeatable selection. Combine related cases rather than duplicate unit/contract/integration tests of the same outcome.
- Automated metric checks use known predictions for perfect/missed/false/duplicate/wrong-class/empty/IoU-boundary cases and absent-class handling. Reuse pycocotools AP; do not test upstream model internals.
- One opt-in CPU smoke test trains a tiny fixture for one epoch, loads it, runs image/video inference, and invokes evaluation. It requires model assets, is run when the connected pipeline is available or materially changes, and does not repeat for every PR. Private fixtures use the same BDD-shaped importer, not another dataset product.
- Verify setup reuse/checksum failures and inspect saved media with small operational checks. Add dedicated automation only if implementation complexity or a real failure warrants it.
- Keep ordinary input checks where files are consumed: class/head compatibility, required values, hashes, finite boxes/scores and complete evaluation membership. No generic schema/lifecycle test suite.
- Real measured claims require the actual GPU baseline, validation comparison and selected final test, not more synthetic tests. Full retraining is unnecessary for unrelated changes.

Keep the reproducibility fields required by FR-012 in one `run.json` beside resolved settings, logs, predictions and `metrics.json`. Hash file bytes for identity; avoid a custom canonical serialization scheme. Never overwrite an existing run directory. Preserve failed/interrupted status in the same record; restart with a new run ID rather than implement custom resume lineage.

## Selection, timing, and course handoff

Evaluation records one synchronized batch-1 inference duration over a fixed subset of its evaluated partition after warm-up; comparison timing uses identical validation samples. Its declared stages are preprocessing, transfer, model forward and NMS; decoding, drawing and encoding are excluded. Report mean ms/image and throughput, sample/warm-up counts, hardware/input/batch/precision and timing boundaries. No per-stage/p95 profiling or separate benchmark command.

Compare sizes 640/960 on the same validation membership/checkpoint. Choose 960 only if AP50:95 improves by at least 0.005 and mean measured latency is at most 1.5× baseline; otherwise keep 640. A human records the two evaluation references, choice and reason in `results/comparison.md`, and saves `results/selected.yaml` identifying checkpoint, manifests, environment and resolved config hashes before testing. Test evaluation checks those few fields against its actual inputs. Record any attempted test in the ordinary run log; no exposure ledger or custom state machine. Later tuning cannot be reported as unbiased testing on the same holdout.

`docs/course-deliverables.md` tracks FR-001–036 with owner/status/evidence and satisfied-count/36, explicitly a requirement count rather than effort/grading credit; optional D9 is separate. Track the three-page report, roles/front page, citations/links/access, verified deadlines/timezones, one report submitter, upload/comments evidence, presentation recording/slides/video link/incognito playback and Top 10 responses. Keep account/hosting conflicts and pending human actions visible. Students author the report and perform external actions unless separately authorized.

## Complexity Tracking

No constitution exceptions. Do not reintroduce a backend protocol, generic schema framework, command registry, experiment orchestrator, custom resume/exposure machinery, fixture-generation CLI, or separate contract-test suite during task generation. Add structure only when an implemented requirement demonstrates the need.

