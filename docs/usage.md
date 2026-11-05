# Usage

Run commands from the repository root; relative input/config paths and output
paths resolve from that workspace. Quote paths containing spaces.

## Current implementation: Phases 1–2

Use Python 3.10–3.14. To install only the current CLI skeleton in an isolated
environment without downloading model dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --no-deps -e .
python -m driving_detection --help
driving-detection --help
python -m driving_detection assets sync --help
python -m driving_detection check --help
python -m driving_detection data prepare --help
python -m driving_detection train --help
python -m driving_detection infer --help
python -m driving_detection evaluate --help
```

On Linux, activate with `source .venv/bin/activate`. The build backend may need
to be installed by pip. Help needs no torch, CUDA, PyYAML, weights or dataset.
The six component handlers remain unimplemented; invoking one currently reports
that fact on stderr and exits 1 without reading configs or creating run outputs.
Invalid/missing arguments exit 2. Asset setup and tested CPU/GPU dependency locks
follow in Phase 3; this skeleton-only install is not model readiness evidence.

## Shared behavior for component implementation

Implemented handlers consume a YAML mapping; PyYAML is needed when reading it.
Each handler checks its required settings and input files where used. Train,
infer and evaluate accept `--device cpu` or `--device cuda:0`; otherwise the
configuration's `device` is used, defaulting to CPU if omitted. An unavailable
requested CUDA device fails rather than switching to CPU. Evaluation defaults to
validation; `--partition test` requires `--selection PATH`. Final selection/hash
checks belong to the evaluation handler and are not implemented yet.

Train/infer/evaluate reserve `artifacts/runs/<run-id>/` before processing.
Run IDs start with a letter or digit, contain only letters/digits/dots/dashes/
underscores, have at most 128 characters, and cannot end in a dot or use Windows
reserved device names. Existing directories are refused; retries need a new ID.
For implemented handlers, the CLI saves effective device/config settings to
`resolved-config.yaml` with a byte SHA-256 reference in `run.json`. Handlers add
their domain-specific settings/evidence and resave resolved settings if they add
defaults or overrides. The CLI starts the record with `status=started` and writes
`completed`, `failed` or `interrupted` on exit, preserving handler-added fields.
Failures include a reason and exit nonzero; Ctrl+C exits 130.

Large inputs belong in ignored `data/` and `external/`; generated outputs belong
in ignored `artifacts/`. Keep secrets out of configs and command arguments, which
may be preserved in run records. Track small configs and results/retrieval notes.

The [future quickstart](../specs/001-driving-object-detection/quickstart.md)
describes the later pipeline interfaces and checks. Model acquisition, training,
predictions, evaluation results and full runtime compatibility are not yet verified.
