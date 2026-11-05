# CLI Contract v1

One package exposes `python -m driving_detection`; an installed `driving-detection` alias may delegate to the same entry point. These commands are planned, not currently implemented. Records follow [records.md](records.md); algorithms/guards follow [pipeline.md](pipeline.md).

## Common behavior

- Root `--workspace PATH` defaults to the current repository root and resolves all config/record paths. Accept paths containing spaces and Windows/Linux separators. Reject output paths escaping the workspace unless an explicit external asset root is configured; never use shell interpolation to build upstream invocations.
- Every command supports `--help`. Operational commands support `--json` for one machine-readable result object on stdout; progress/errors go to stderr. Do not log secrets, credential-bearing URLs, or full environment variables.
- `--config PATH` loads a YAML mapping with schema_version 1. Reject unknown/misspelled fields. Persist the full resolved config and its hash, not just the input YAML. Relative config asset paths resolve against workspace, not process-specific working directories.
- Computational commands (`train`, `infer`, `evaluate`, `benchmark`, `compare`) accept `--device cpu|cuda:0` as an explicit resolved-config override. The reported default profile uses cuda:0; smoke calls specify CPU. Record overrides in configuration hashes and comparisons; no silent device fallback.
- New run commands require `--run-id ID`, restricted to letters/digits/dash/underscore, max 80 characters. Existing run IDs are an error. Commands never silently overwrite results; resume is explicit and records lineage.
- Success returns 0. Exit 1 = execution/dependency failure; 2 = usage/config/schema error; 3 = unavailable/corrupt asset; 4 = data/integrity/coverage failure; 5 = lifecycle/holdout/comparability guard; 6 = partial image/video processing; 130 = interruption. All nonzero exits preserve actionable reason/status where an output run exists.
- Completed summaries identify command, status, record/output path and digest. Reports with undefined metrics use null/reason. Failure is never represented by fabricated scores.

## Commands and inputs/outputs

| Command | Required inputs | Outputs and behavior | Owning deliverable |
| --- | --- | --- | --- |
| `assets sync --config configs/assets.yaml` | Asset definitions; optional `--images-archive PATH --labels-archive PATH` instead of data download | Verified asset manifest in `artifacts/assets/`; stage/validate/promote, reuse valid assets; manual terms/access prerequisite reported | D1 |
| `check --config configs/assets.yaml [--device cpu\|cuda:0]` | Environment and acquired source/weights; dataset readiness reported separately | Interpreter/lock/import/checkpoint/device readiness summary; requested GPU unavailable fails, never silently switches; absent dataset is informational for model-only readiness | D1 |
| `fixtures create --output data/smoke` | No external dataset | Deterministic synthetic images/labels and short video, three classes/negatives; 24 train / 12 val / 12 synthetic holdout, fixture metadata | D1 |
| `data prepare --config configs/data/bdd-subset.yaml` | Verified dataset assets; frozen split policy | `data/prepared/<profile_id>/profile.json`, manifest JSONL, class map, YOLO train/val export and COCO labels, integrity summary; no model use | D2 |
| `data validate --profile PATH` | Prepared profile and referenced files | Integrity result covering hashes, overlap, eligibility, geometry and coverage; no training or tuning | D2 |
| `train --profile PATH --config PATH --run-id ID [--resume RUN_RECORD]` | Frozen profile, model source/initial weights, explicit device/budget | `artifacts/runs/<ID>/run.json`, resolved configs/history/checkpoints, `model.json`; train/val only | D3 |
| `infer --model PATH --input PATH --config PATH --run-id ID [--capture PATH]` | Model metadata; image/directory/video or manifest; optional capture record | `artifacts/runs/<ID>/predictions.jsonl`, `prediction-set.json`, annotated outputs and per-input statuses; heldout manifest requires matching selection guard | D4 |
| `evaluate --model PATH --profile PATH --partition val --config PATH --run-id ID` | Model and profile; optional `--predictions PATH` with exact expected model/data/config hashes | Validation predictions/evaluation JSON, per-class summary, evidence pointers; test partition refused here | D5 |
| `benchmark --model PATH --profile PATH --config PATH --run-id ID` | Validation profile and model, fixed image list/device/precision | Timing protocol and per-stage/aggregate statistics; no test timing used for candidate selection | D5 |
| `core-check --model PATH --profile PATH --inference PATH --evaluation PATH --timing PATH --run-id ID` | Completed compatible D1–D5 artifacts; repeatable --inference supplies both image and video metadata; real baseline/profile for reportable gate | Core-gate JSON binding model/profile and integration evidence; synthetic/reference-only evidence cannot pass reportable core | D5 integration |
| `compare --model PATH --profile PATH --core-gate PATH --config PATH --run-id ID` | Accepted core; validation-only candidate settings/budget | Baseline/candidate eval/timing references and comparison record; worse/failed candidate preserved | D6 |
| `select --comparison PATH --run-id ID` | Comparable validation evidence or explicitly failed candidate with verified baseline | Immutable `selection.json` and materialized `inference-config.yaml` with deterministic rule and exact hashes; no test metrics permitted; failed candidate leaves D6 partial | D6 |
| `final-evaluate --selection PATH --run-id ID` | Valid frozen selection with exact matching model/test manifest/config | Exposure marker written before processing, selected model's final predictions/metrics/timing and final run record | D6 |
| `capture register --input PATH --config PATH --run-id ID` | Optional team clip and known/unknown camera/scene metadata | Capture JSON; no accuracy claim or automatic upload | D9 |

For a synthetic profile, `data prepare` uses `configs/data/smoke.yaml`. D1's tiny upstream compatibility probe can run directly against generated fixtures without waiting for D2; it is a setup check, not a project training feature or baseline.

`assets sync` accepts public/configured authorized dataset URLs through local environment/config without persisting credentials. Its default scope contains required dataset, source and weights; `--only model` limits acquisition for CPU smoke setup. Download access may require a documented manual portal/terms step. Imported archives still undergo the same checks as downloads.

No report-writing, permission-granting, messaging, Canvas upload, or YouTube upload commands are introduced. D7/D8 use reviewed materials and explicit human course checklist actions.

## Idempotency and interruption

Asset sync and deterministic data preparation are idempotent: identical verified input/config returns existing valid outputs; any changed identity demands a new version/output ID. Interrupted staging can resume or restart only its own unverified temporary files; valid promoted assets/results are preserved. Validate final resolved paths before cleanup and never recursively remove a user-supplied directory.

Experiment commands are immutable by default. `train --resume` references an interrupted run and records resumed optimizer/scheduler/RNG state and environment; a new run ID preserves the parent. If exact resume state is unavailable, perform an explicitly labeled new run instead. Completed model selection never rewrites history.

Partial inference returns 6 and a complete list of succeeded/failed inputs; evaluation rejects partial sets. A stopped final run records test exposure even on failure. An exact replay is labeled reproduction; changes after exposure cannot regain untouched-holdout status.

## Parallel development boundary

D1 implements shared validation, lifecycle foundations, backend protocols and lazy routing. Each command group registers in its own module without importing missing or GPU-heavy groups during unrelated commands. Unsupported commands fail clearly until implemented. D3 owns training adapter; D4 owns inference adapter; D5 consumes canonical records rather than their internal model objects. Reference COCO mapping is explicit and never confused with a trained head.
