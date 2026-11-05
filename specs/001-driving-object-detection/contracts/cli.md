# CLI Contract

The package exposes `python -m driving_detection` with argument parsing and lazy dispatch for six command handlers. Phase 2 implements the CLI/shared file helpers; component handlers remain later tasks. The full interfaces below remain the implementation contract. See [records](records.md) and [pipeline](pipeline.md).

## Shared behavior

Use ordinary argparse dispatch and functions; no registration framework or alternate-backend protocol. All commands support --help. Configurations are YAML with documented required fields; report missing/invalid values at the point of use. Store resolved settings, not only filenames. Paths resolve from the repository workspace and must support spaces on Windows/Linux.

Train/infer/evaluate accept --device cpu or cuda:0, defaulting to the configured device, and fail if it is unavailable. A --run-id is a single safe directory name under artifacts/runs; refuse an existing output directory. Progress and errors are readable. Success exits 0; failure/partial processing exits nonzero with a reason in the output/log. No elaborate exit-code taxonomy or universal --json output contract is needed.

| Command | Input and behavior | Output | Owner |
| --- | --- | --- | --- |
| `assets sync --config configs/assets.yaml` | Download or import required assets; optional --images-archive PATH and --labels-archive PATH; --only model skips bulk data | Verified asset inventory, reusable source/weights/data; actionable manual-access failures | D1 |
| `check --config configs/assets.yaml --device cpu` | Verify interpreter/imports/source/checkpoint and requested device; report dataset readiness separately | Readable readiness summary and saved environment versions; missing data does not fail model-only readiness | D1 |
| `data prepare --config configs/data/bdd-subset.yaml` | Convert, select, validate and export data in one operation | profile.json, manifests, YOLO/COCO exports, counts/integrity report | D2 |
| `train --profile PATH --config PATH --run-id ID` | Direct pinned YOLO training wrapper; train/val only | run.json, resolved config/history, weights/best.pt and weights/last.pt | D3 |
| `infer --model PATH --input PATH --config PATH --run-id ID` | Image/directory/prerecorded video with canonical classes; --reference-coco explicitly enables reference head mapping | run.json, predictions.jsonl and annotated outputs | D4 |
| `evaluate --model PATH --profile PATH --partition val --config PATH --run-id ID` | Direct predictions, AP/P-R evaluation and one integrated timing measurement; test requires --selection PATH | run.json, predictions.jsonl, metrics.json and example references | D5/D6 |

--model is the actual checkpoint path; its hash and verified head mapping enter run.json. Trained heads use the three canonical names; raw reference COCO checkpoints require --reference-coco and are never treated as baseline evidence. The evaluator uses the trained head for reportable results.

There is no public synthetic-data command, separate data-validator/benchmark command, or custom core/comparison/selection/final-test/capture command. Preparation validates itself; evaluation times itself. Core review, the comparison table, selected.yaml and capture notes are documented human steps.

## Test-partition use

Ordinary evaluate defaults to val. For --partition test, require --selection results/selected.yaml and check selected checkpoint, profile/test membership, evaluation settings and environment file hashes before processing. Keep partition/run/output arguments outside the saved evaluation settings; reject device/setting overrides that would change the selection. Save the test run's status/time before processing, just as for other runs. A human ensures selection was made before test inspection and labels later reproductions/exploration honestly; this is a research workflow, not an access-control system.

## Reuse and failure handling

Asset sync and identical data preparation reuse verified existing outputs. Detect incomplete downloads, changed inputs and corrupt assets rather than silently accepting them. Stage new assets before promotion; protect valid files and avoid destructive cleanup of user-supplied paths.

Run commands preserve completed/failed/interrupted status and do not overwrite earlier outputs. Retrying uses a new run ID; the project does not implement custom resume lineage. A partial video records failed inputs/frames and exits nonzero; evaluation cannot report complete metrics from a partial set. Valid empty predictions remain successful.

No external messages, account-permission changes, course uploads or report prose generation are automated by these commands.

