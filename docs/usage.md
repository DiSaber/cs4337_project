# Usage

Run commands from the repository root; relative input/config paths and output
paths resolve from that workspace. Quote paths containing spaces.

## Windows CPU setup (verified Python 3.14.7)

The exact tested lock is for Windows amd64/Python 3.14.7. Confirm `python --version`
before using it; other allowed interpreters need separate resolution/verification.
From the repository root, use the global pip to populate an isolated environment:

```powershell
python -m venv --without-pip .venv
python -m pip --python .venv/Scripts/python.exe install -r requirements/cpu-lock.txt
python -m pip --python .venv/Scripts/python.exe install --no-deps -e .
.venv/Scripts/python.exe -m driving_detection assets sync --config configs/assets.yaml --only model
.venv/Scripts/python.exe -m driving_detection check --config configs/assets.yaml --device cpu
```

The author used global pip 26.1.2 (`--python` requires pip 22.3 or later). The
resolved versions and wheel provenance are in [requirements](../requirements/README.md).
Repeat sync/check to verify reuse. The check imports libraries, allocates on the
requested device, checks the torchvision NMS operator and loads the verified
official 80-class COCO reference model. It does not train or measure accuracy.
Missing data is reported separately and does not prevent model-only readiness.

For Linux GPU/Colab, use the separate [Colab handoff](colab-setup.md), not this
Windows lock. That environment and independent teammate review remain pending.

## External assets

Review [sources, licensing and access prerequisites](references.md). Model sync
downloads only the pinned official source archive and checkpoint. To acquire all
required inputs, supply authorized BDD100K image and Detection 2020 archives:

```powershell
.venv/Scripts/python.exe -m driving_detection assets sync --config configs/assets.yaml --images-archive "C:/Datasets/bdd100k_images_100k.zip" --labels-archive "C:/Datasets/bdd100k_det_20_labels.zip"
```

The dataset's public download route is not verified available, so its config URLs
are unset. Running full sync without local archives gives an actionable access
error. A verified public HTTPS URL can be configured; embedded credentials/signed
query URLs are rejected. Model SHA-256 pins are measured official-download
identities; dataset MD5s come from the publisher. Supplied local archives must
match their declared checksums and expected members.

Outputs are `external/yolov5-v7.0`, `external/weights/yolov5s.pt`,
`data/raw/images/bdd100k/images/100k/`, and
`data/raw/labels/bdd100k/labels/det_20/`. `artifacts/assets.json` stores asset
identities/readiness; `artifacts/asset-receipts/` stores verified receipts.
Sync stages assets before promotion and refuses existing unverified/changed
destinations. Repeated sync hashes extracted contents, so checking large data
still reads the files but does not download duplicates. Python bytecode caches
are excluded from extracted-content identity.

Download caches live under `external/downloads/`. An interrupted `.part` is
unverified; retry restarts its download rather than resuming. A corrupt completed
cache, changed extraction, missing receipt or changed asset definition requires
manual recovery: preserve/move the affected asset/cache/receipt aside before
retrying, or use a new configured destination. Do not remove unrelated outputs
or user-supplied archives. Setup never silently overwrites them. Preserve receipt
files when transferring verified assets between machines.

Runtime adapters allow the pinned checkpoint loader to use explicit
`weights_only=False` only for verified official weights and restore Pillow's
removed font sizing method. Upstream source is unchanged; later training still
needs its own integration verification.

## CLI help and package-only setup

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
Asset sync and readiness check are implemented. Data/train/infer/evaluate still
report an unimplemented-handler error and exit 1 without reading configs or
creating run outputs. Invalid/missing arguments exit 2. The package-only install
above is enough for help, but model readiness requires the full runtime setup.

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
describes the later pipeline interfaces and checks. Local CPU model acquisition
and loading have been verified; training, predictions, evaluation and Linux GPU
compatibility are not yet verified.
