# Implementation Plan: Driving Scene Object Detection

**Branch**: `main` (actual `.git/HEAD`); setup resolves feature context `001-driving-object-detection` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-driving-object-detection/spec.md`. Planning ends at Phase 1 design. No implementation tasks, source implementation, model training, account changes, or submissions are completed by this document.

## Summary

Build a small Python CLI around a pinned YOLOv5s release for a reproducible three-class BDD100K subset. Prepare sequence-disjoint manifests, train a baseline on a single NVIDIA GPU/Colab, expose image/video inference, evaluate with explicit COCO-style AP and fixed-operating-point P/R, compare one input-size candidate, and freeze the selected configuration before final held-out testing. Keep report/presentation handoffs distinct, with captured dashcam footage optional.

Deliver the nine cohesive PR units D1–D9 below. Common contracts are defined here and implemented in D1; later components own separate modules. The dependency graph permits training, inference, and evaluator development in parallel without treating fixtures as measured project results.

## Technical Context

**Language/Version**: Python 3.11; initial reproducibility target 3.11.9. Record exact interpreter build. Windows PowerShell for local setup/CPU checks; Linux/Colab for GPU training using the same package/configurations.

**Primary Dependencies**: YOLOv5 v7.0 at `915bbf294bb74c859f0b41f1c23bc395014ea679`, torch 2.5.1 + torchvision 0.20.1, numpy 1.26.4, Pillow 9.5.0, opencv-python 4.10.0.84, PyYAML 6.0.2, pycocotools 2.0.10, pytest 8.3.5. These are research-backed initial targets, not a tested environment. D1 resolves complete CPU/CUDA locks and records any necessary compatibility adjustment before experiments; disable runtime dependency auto-install and external experiment trackers.

**Storage**: Files only. Tracked YAML configs/schema definitions and compact result summaries; ignored `data/` (archives/raw/prepared), `external/` (pinned model code/weights), `artifacts/` (runs/checkpoints/predictions/videos). Every external artifact has identity/hash and acquisition/retrieval instructions. Configuration and stored paths are relative to an explicit workspace root; secrets come from local environment without being logged.

**Testing**: pytest fixtures for data integrity, coordinate/label conversion, matching correctness, contract validation, lifecycle/holdout guards; tiny CPU train/load/image/video integration; a declared GPU baseline, validation comparison, and final held-out run for measured claims. Tests never require bulk data or GPU by default. No artificial full-model accuracy target.

**Target Platform**: Windows x86-64 CPU readiness and smoke; Linux x86-64 NVIDIA GPU, ideally >=8 GB VRAM, including Colab. User confirmed single-GPU/Colab. CUDA 12.1 wheel profile is provisional until hardware readiness succeeds. Avoid reliance on Colab's changing global interpreter/dependencies; install an isolated supported interpreter/environment and record it. GUI windows are not required.

**Project Type**: Single installable CLI/research pipeline; no HTTP service, authentication system, or database. Optional thin Colab launcher uses the same commands.

**Performance Goals**: Measure accuracy and latency honestly, not promise real time. Train size 640/batch 8/20 epochs with seed 4337, <=8 GPU-hours; compare inference sizes 640/960 within 1 GPU-hour; reserve 1 GPU-hour for final evaluation/demos. Batch 4/2 fallback is selected and recorded before a reported training run if needed. Exhausted budget means interrupted status and a new explicitly declared run/profile if continued.

**Constraints**: Core before optimization/stretch; disjoint frozen partitions; heldout guarded until frozen selection; no large assets/credentials in Git; idempotent acquisition with manual-access fallback; student-authored three-page report; 5–10 minute presentation; displayed report cutoff December 2, 2026, 11:59 p.m., subject to Canvas timezone/date verification.

**Scale/Scope**: Default eligible subset 5,000 train / 1,000 validation / 1,000 heldout, three classes. Synthetic smoke profile 24/12/12, one CPU epoch at size 320/batch 2; no measured accuracy claim. New-scene image set and short video for demonstration. Nine deliverables, 36 required functional requirements and three optional requirements.

## Constitution Check

Pre-research gate review accepted the required scope with no conflict. Post-design review below verifies each principle has a concrete planned control. PASS means design compliance, not that future execution evidence already exists.

| Gate | Before research | After design | Required control / evidence |
| --- | --- | --- | --- |
| I Reproducible experiments | PASS | PASS | Immutable asset identities, resolved configs/locks, seeds/commands, run records, hashes, hardware and nondeterminism; [records contract](contracts/records.md) |
| II Reliable evaluation | PASS | PASS | Sequence/content integrity, frozen manifests, final-selection guard, controlled metric fixtures, explicit AP/P/R and timing; [pipeline contract](contracts/pipeline.md) |
| III Core first | PASS | PASS | D1–D5 integration gate before D6/D9; D9 absent from required dependency chains |
| IV Evidence for claims | PASS | PASS | Results tied to run/model/data hashes, successes/failures and limitations; failed attempts preserved; [data model](data-model.md) |
| V Simple implementation | PASS | PASS | Established model, one CLI, local files, pinned external checkout, idempotent assets, docs and focused checks; no services |
| VI Integrity/AI transparency | PASS | PASS | Per-PR AI log and source notices; students author report; external course actions remain separately evidenced |
| Course constraints/governance | PASS | PASS | Separate deliverables checklist, three-page interpretation retained, account/date conflicts tracked; no constitution amendment |

No unjustified violations or unresolved technical decisions remain. Dataset availability, actual dependency compatibility/hardware, and course access/date confirmations are explicit execution prerequisites with fail/report behavior, not assumed successes.

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

`tasks.md` is a later `$speckit-tasks` artifact and is deliberately not generated here.

### Source Code (repository root — proposed, not yet implemented)

```text
pyproject.toml
requirements/                 # validated cpu/cuda locks, constraints
configs/
├── assets.yaml
├── data/bdd-subset.yaml
├── data/smoke.yaml
├── train/baseline.yaml
├── train/smoke.yaml
├── evaluation/default.yaml
└── experiments/input-size.yaml
src/driving_detection/
├── __main__.py                # lazy subcommand routing
├── common/                    # config, hashes, records, errors
├── assets/                    # acquisition/readiness
├── data/                      # BDD conversion/manifests/validation
├── backends/
│   ├── contracts.py           # common detector/training metadata protocols
│   ├── yolov5_train.py
│   └── yolov5_infer.py
├── training/
├── inference/
├── evaluation/
└── experiments/               # compare/freeze/final guards, optional capture study
tests/
├── fixtures/                  # tiny synthetic images/labels/video recipes
├── unit/
├── contract/
└── integration/
docs/
├── setup.md
├── data.md
├── experiments.md
├── inference.md
├── evaluation.md
├── course-deliverables.md
├── references.md
├── ai-use-log.md
├── report/                    # student-authored source, submission pointers
└── presentation/              # slides/source, recording/review pointers
data/                         # ignored archives/raw/prepared
external/                     # ignored source/weights
artifacts/                    # ignored runs/results/annotated media
results/                      # tracked small summaries + retrieval instructions
```

**Structure Decision**: One package with command modules and shared contracts avoids large shared-file edits. Heavy detector imports are lazy so setup/data/evaluator fixtures work independently. D1 owns routing and common protocol/schema foundations; D3 and D4 implement separate training/inference adapters. Store course completion tracking outside Spec Kit's quality checklists so an unsubmitted video does not block unrelated implementation.

## Phase 0 — Research decisions

[research.md](research.md) resolves the runtime/asset choices, source label and coordinate semantics, split policy, compute budget, local versus hosted preprocessing, AP/P/R/timing definitions, optimization rule, and course handoff boundaries. All initial unknowns were resolved as decisions or explicit execution prerequisites with failure behavior.

Use local preprocessing rather than mandatory Roboflow, preserving the spec's allowed substitution and documenting why. Direct pycocotools AP plus a focused operating-point count layer is the chosen evaluator. Use existing assets if the official data host is inaccessible; never silently change labels/dataset.

## Phase 1 — Design and contracts

- [data-model.md](data-model.md): entity fields, relationships, validity, immutable identities, and state transitions.
- [contracts/cli.md](contracts/cli.md): user commands, common options, errors, resumability, and artifacts.
- [contracts/records.md](contracts/records.md): versioned on-disk data/run/model/prediction/evaluation/course records.
- [contracts/pipeline.md](contracts/pipeline.md): conversion/splits, training and backend interfaces, evaluation/timing, candidate selection, final-test gate.
- [quickstart.md](quickstart.md): future runnable verification scenarios from setup through final handoff; commands are design contracts until implemented.

Design is complete for task generation. D1 must implement contract validators and independently test the selected environment before accepting actual training outputs. File contracts, not hidden model internals, connect components.

## Delivery sequence and PR acceptance

Every PR includes focused verification, usage updates, citations where needed, and its AI-use entry. It owns only the requirements in its row; later work must not require jumping between unfinished deliverables. This is a handoff plan, not a generated task checklist.

| Unit / requirement ownership | Implementation scope | Evidence required to merge |
| --- | --- | --- |
| D1 / FR-001–004 | Packaging, common config/record validators and backend protocols, lazy CLI dispatch, asset commands, tested environment locks, ignored paths, setup/reference docs | Fresh/repeat acquisition on small fixtures; interrupted/hash-failure handling; official checkpoint load plus tiny compatibility probe; tested CPU profile and declared GPU readiness; no bulk data in Git |
| D2 / FR-005–010 | BDD versioned adapter, class/geometry conversion, eligibility/exclusions, sequence/content checks, deterministic subset and YOLO/COCO exports, manifests | Repeatable hashes; malformed/unknown/negative/ignored and boundary-box fixtures; zero overlap and per-partition class coverage; actual preparation summary |
| D3 / FR-011–014 | Training adapter/wrapper, complete resolved hyperparameters, lifecycle/checkpoint records and validation-only checkpoint selection | CPU smoke integration and a completed declared baseline; loadable checkpoint, command/seed/environment/data records, interruption status; no final test use |
| D4 / FR-015–017 | Inference adapter, class remapping, deterministic preprocessing/NMS, image/video serialization and annotations | Compatible reference-model image/video checks, empty/invalid/partial cases; D3 baseline integration before declaring whole core complete |
| D5 / FR-018–022 | COCO AP adapter, fixed P/R counts, timings, validation summaries and evidence selection | Controlled metric fixtures, baseline validation record, per-class metrics, fixed timing stages and representative success/failure cases |
| D6 / FR-023–025 | Input-size comparison, selection freeze, heldout guard/final command and final evidence | Core integration gate; bounded validation comparison, reasoned choice, frozen hashes, selected model's final heldout result; unsuccessful attempt retained |
| D7 / FR-026–032 | Code handoff review, 36-requirement inventory, course checklist, contributor/citation/link records, student report handoff | Three-page student-authored PDF review or explicit remaining authoring action, understandable code/docs, honest completed/partial status; external access/submission actions pending until evidenced |
| D8 / FR-033–036 | Presentation outline/materials, rehearsal review, recording/upload handoff, later audience follow-up | Four required topics; 5–10 minute timing/readability/audio review; pending student uploads/feedback explicit; separate follow-up PR if feedback arrives later |
| D9 / FR-037–039 | Optional capture metadata, dashcam inference/qualitative review and labeled evaluation only if labels exist | Core already accepted, capture conditions/unknowns recorded, observational limitations, evidence or explicit skip; cannot delay D1–D8 |

**Dependency order**: D1 → D2 → D3; D4 uses D1 contracts and D2 class mapping and can use a reference model while D3 runs; D5 fixtures can start after D1 contracts, then use D2/D3 outputs for measured evidence. D3/D4/D5 develop in parallel after those inputs are fixed. Core acceptance requires all D1–D5 integrated. D6 follows core. D7/D8 preparation can start immediately but final claims consume D6 evidence or disclose partial status. D9 follows core and has no required downstream dependents.

**Reference model rule**: D4 may use the official COCO checkpoint with explicit mapping `{2:0, 0:1, 9:2}` and filtering of other classes. It is marked `reference_coco`, never a trained three-class result. D3's trained head uses project IDs directly. Model metadata makes this distinction machine-checkable.

**Core gate**: Actual prepared profile, baseline training/load, image/video inference, validation metrics, timing and representative examples all share recorded identities. Fixture-only passes do not satisfy the gate.

## Validation and evidence strategy

Default automated checks cover schema compatibility, stable hashes, missing/corrupt assets, geometry conversion/roundtrip, negative images, unknown/excluded labels, ignored samples, sequence and byte-duplicate leakage, per-class coverage, model mapping, deterministic prediction ordering, metric edge cases, empty results, candidate rule, and holdout authorization. Tests assert public outcomes, not implementation call structure.

Run a tiny CPU integration when training/inference interfaces change; run real GPU training only to validate baseline/training changes or support reported findings. Record validation AP/P/R and timing for baseline and candidate on identical partitions/device/precision. Synchronize GPU timing. Inspect actual original/annotated examples, not only metrics. Large artifacts remain ignored, while tracked summaries include artifact hashes and a documented team-accessible storage location; a path on one machine alone is insufficient handoff evidence.

Use immutable run directories and atomic writes. Failed commands preserve status/logs and never masquerade as completed runs. A frozen selection references model, manifest, environment/config hashes, comparison results and timestamp before the final command is allowed. Later reruns for reproduction use the same freeze and are labeled reproductions; new tuning after test exposure requires a new untouched holdout or explicit exploratory labeling.

## Course handoff and completion inventory

`docs/course-deliverables.md` will track each FR-001–036 with owner, pending/partial/verified status, evidence, and review date. Report satisfied requirements/36 with the exact inventory, not an inferred effort percentage or guarantee of grading credit. Optional FR-037–039 is separate. Early checklist/access preparation belongs to D7, even if merged ahead of final report content; no automatic external messages or permissions changes.

Track December 2, 2026, 11:59 p.m. as the saved report deadline pending current Canvas/timezone confirmation. Track report authoring/review, all names/roles on front page, three-page PDF, references and links, instructor identity/hosting conflict, notebook sharing if applicable, one submitter, Canvas report/comment evidence. Presentation tracking includes its independently verified deadline, slides, Unlisted YouTube link/comment, incognito playback, timing/readability/audio, peer-feedback review and Top 10 Response Page answers. Completion remains pending if external actions or audience responses are outstanding.

The three-page interpretation and differing instructor identifiers remain exactly as recorded in the spec; no governance or scope amendment is introduced.

## Complexity Tracking

No constitution violations require an exception. Custom code is limited to acquisition/provenance, versioned data conversion, project interfaces, operating-point counts, lifecycle/holdout guards, and evidence packaging. Training architecture, NMS, and AP reuse established implementations.
